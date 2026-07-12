"""
Offline LoRA adapter trainer for ASTRO.

Implements a local, opt-in training pipeline:
- Loads a base Hugging Face model.
- Loads a curated JSONL dataset (instruction/response format).
- Runs QLoRA via PEFT + TRL SFTTrainer if a GPU is available.
- Falls back to staging-only if no compatible GPU or tiny dataset.
- Saves LoRA weights, tokenizer, and a manifest.
- Provides a helper to create an Ollama-compatible Modelfile template.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from astro.config import ADAPTERS_DIR, DEFAULT_OLLAMA_MODEL
from astro.curator import Curator


def _has_gpu() -> bool:
    try:
        import torch

        return torch.cuda.is_available()
    except Exception:
        return False


class Trainer:
    def __init__(self, adapters_dir: Optional[Path] = None):
        self.adapters_dir = Path(adapters_dir or ADAPTERS_DIR)
        self.adapters_dir.mkdir(parents=True, exist_ok=True)

    def train(
        self,
        dataset_name: str,
        adapter_name: str,
        base_model: str = DEFAULT_OLLAMA_MODEL,
        epochs: int = 3,
        learning_rate: float = 1e-4,
        run_training: bool = True,
    ) -> Path:
        """
        Build or train an adapter.

        Args:
            dataset_name: curated dataset name (from `astro dataset`).
            adapter_name: output adapter name.
            base_model: base model identifier. Supports Ollama-style tags like 'qwen2.5:0.5b'.
            epochs: training epochs when real training runs.
            learning_rate: LoRA learning rate.
            run_training: if True and a GPU is present, run SFT LoRA. Otherwise stage.

        Returns:
            Path to adapter directory.
        """
        dataset_dir = Curator(datasets_dir=self.adapters_dir.parent / "datasets").datasets_dir / dataset_name
        if not dataset_dir.exists():
            raise ValueError(f"dataset not found: {dataset_name}")
        dataset_jsonl = dataset_dir / "dataset.jsonl"
        if not dataset_jsonl.exists():
            raise ValueError(f"dataset.jsonl missing in {dataset_dir}")
        items = sum(1 for _ in dataset_jsonl.open())
        if items == 0:
            raise ValueError("dataset is empty")

        out_dir = self.adapters_dir / adapter_name
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        shutil.copy2(dataset_jsonl, out_dir / "dataset.jsonl")
        shutil.copy2(dataset_dir / "manifest.json", out_dir / "dataset_manifest.json")

        # Map Ollama tag to a real HF checkpoint when we can.
        hf_model = self._ollama_to_hf(base_model)

        manifest = {
            "name": adapter_name,
            "base_model": base_model,
            "hf_model": hf_model,
            "dataset": dataset_name,
            "epochs": epochs,
            "learning_rate": learning_rate,
            "items": items,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "staged",
            "has_gpu": _has_gpu(),
        }

        trained = False
        if run_training and _has_gpu():
            try:
                weights_dir = self._run_lora_sft(hf_model, dataset_jsonl, out_dir, epochs, learning_rate)
                manifest["status"] = "trained"
                manifest["weights_dir"] = str(weights_dir)
                trained = True
            except Exception as exc:
                manifest["status"] = "staged"
                manifest["training_error"] = str(exc)

        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
        (out_dir / "Modelfile").write_text(self._modelfile(base_model, out_dir, trained=trained))
        return out_dir

    @staticmethod
    def _ollama_to_hf(base_model: str) -> str:
        """Best-effort mapping from Ollama model tag to Hugging Face checkpoint."""
        mapping = {
            "qwen2.5:0.5b": "Qwen/Qwen2.5-0.5B-Instruct",
            "qwen2.5:1.5b": "Qwen/Qwen2.5-1.5B-Instruct",
            "qwen2.5:3b": "Qwen/Qwen2.5-3B-Instruct",
            "llama3.2:1b": "meta-llama/Llama-3.2-1B-Instruct",
            "gemma3:1b": "google/gemma-3-1b-it",
        }
        return mapping.get(base_model, base_model)

    def _run_lora_sft(
        self,
        hf_model: str,
        dataset_jsonl: Path,
        out_dir: Path,
        epochs: int,
        learning_rate: float,
    ) -> Path:
        from datasets import Dataset
        from peft import LoraConfig
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
        from trl import SFTTrainer

        # Load dataset
        rows = [json.loads(line) for line in dataset_jsonl.open()]
        ds = Dataset.from_list(rows)

        tokenizer = AutoTokenizer.from_pretrained(hf_model, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        def format(example):
            text = (
                f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['output']}"
            )
            return {"text": text}

        ds = ds.map(format, batched=False)

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype="bfloat16",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
        model = AutoModelForCausalLM.from_pretrained(
            hf_model,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
        model.config.use_cache = False

        lora_config = LoraConfig(
            r=16,
            lora_alpha=32,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
        )

        training_args = TrainingArguments(
            output_dir=str(out_dir / "training_outputs"),
            num_train_epochs=epochs,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=4,
            learning_rate=learning_rate,
            logging_steps=5,
            save_strategy="epoch",
            fp16=False,
            bf16=True,
        )

        trainer = SFTTrainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=ds,
            args=training_args,
            peft_config=lora_config,
            dataset_text_field="text",
            max_seq_length=512,
        )
        trainer.train()

        weights_dir = out_dir / "lora_weights"
        trainer.model.save_pretrained(weights_dir)
        tokenizer.save_pretrained(weights_dir)
        return weights_dir

    def _modelfile(self, base_model: str, out_dir: Path, trained: bool) -> str:
        weights_path = out_dir / "lora_weights"
        relative_weights = str(weights_path.relative_to(out_dir)) if weights_path.exists() else "lora_weights"
        lines = [
            f"FROM {base_model}",
            "",
            "SYSTEM \"\"\"You are ASTRO, a local-first AI assistant fine-tuned on the user's confirmed memories and feedback.\"\"\"",
            "",
        ]
        if trained:
            lines += [
                f"ADAPTER ./{relative_weights}",
                "",
            ]
        lines += [
            "TEMPLATE \"\"\"{{ if .System }}### System:\n{{ .System }}{{ end }}\n{{ if .Prompt }}### Instruction:\n{{ .Prompt }}{{ end }}\n### Response:\n{{ .Response }}\"\"\"",
        ]
        return "\n".join(lines) + "\n"
