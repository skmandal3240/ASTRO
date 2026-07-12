"""Tests for feedback, curator, registry, and trainer."""
from pathlib import Path
import tempfile

from astro.curator import Curator
from astro.feedback import FeedbackStore
from astro.model_registry import ModelRegistry
from astro.trainer import Trainer


def test_feedback_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        store = FeedbackStore(Path(td) / "f.db")
        fb = store.record("Q", "A", "positive", sources=["note.md:1-2"], model="qwen2.5:0.5b")
        assert fb.rating == "positive"
        assert store.list(rating="positive")[0].id == fb.id


def test_curator_build_and_review():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        fb = FeedbackStore(td / "f.db")
        fb.record("Q", "A", "positive")
        mem = __import__("astro.memory", fromlist=["MemoryStore"]).MemoryStore(td / "m.db")
        mem.add("fact one", kind="fact")
        curator = Curator(memory_store=mem, feedback_store=fb, datasets_dir=td / "datasets")
        out = curator.build("v1")
        assert (out / "dataset.jsonl").exists()
        report = curator.review("v1")
        assert "Dataset Review: v1" in report


def test_model_registry():
    with tempfile.TemporaryDirectory() as td:
        reg = ModelRegistry(adapters_dir=Path(td) / "adapters")
        assert reg.active() == "base"
        reg.activate("base")
        assert reg.active() == "base"


def test_trainer_stages_adapter():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        fb = FeedbackStore(td / "f.db")
        fb.record("Q", "A", "positive")
        mem = __import__("astro.memory", fromlist=["MemoryStore"]).MemoryStore(td / "m.db")
        curator = Curator(memory_store=mem, feedback_store=fb, datasets_dir=td / "datasets")
        curator.build("v1")
        trainer = Trainer(adapters_dir=td / "adapters")
        out = trainer.train("v1", "adapter1")
        assert (out / "manifest.json").exists()
        assert (out / "dataset.jsonl").exists()
