"""
Offline LoRA adapter trainer for ASTRO.

This is a stub implementation. Real training requires `peft`, `trl`, and a
compatible base model checkpoint. For Phase 3 we:
- Validate the dataset.
- Write a manifest.
- Create an adapter directory that a future full trainer will populate.
- ponytail: don't pull heavy training deps until we have real GPU time.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from astro.config import ADAPTERS_DIR, DEFAULT_EMBED_MODEL, DEFAULT_OLLAMA_MODEL
from astro.curator import Curator


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
    ) -> Path:
        """Create a validated adapter directory. Does not run full LoRA yet."""
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

        # Copy dataset into adapter dir for reproducibility
        shutil.copy2(dataset_jsonl, out_dir / "dataset.jsonl")
        shutil.copy2(dataset_dir / "manifest.json", out_dir / "dataset_manifest.json")

        manifest = {
            "name": adapter_name,
            "base_model": base_model,
            "dataset": dataset_name,
            "epochs": epochs,
            "learning_rate": learning_rate,
            "items": items,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "staged",
            "note": "Full LoRA weights not yet produced; run a real trainer with peft/trl when ready.",
        }
        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
        return out_dir
