"""
Dataset curator for ASTRO.

Builds reviewed, redacted, versioned training datasets from memories and
positive feedback. Keeps everything local.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from astro.config import DEFAULT_DATA_DIR
from astro.feedback import FeedbackStore
from astro.memory import MemoryStore


class Curator:
    def __init__(
        self,
        memory_store: Optional[MemoryStore] = None,
        feedback_store: Optional[FeedbackStore] = None,
        datasets_dir: Optional[Path] = None,
    ):
        self.memory_store = memory_store or MemoryStore()
        self.feedback_store = feedback_store or FeedbackStore()
        self.datasets_dir = Path(datasets_dir or DEFAULT_DATA_DIR / "datasets")
        self.datasets_dir.mkdir(parents=True, exist_ok=True)

    def build(
        self,
        name: str,
        min_rating: str = "positive",
        include_memories: bool = True,
        redact: bool = True,
    ) -> Path:
        """Build a JSONL dataset from feedback + memories."""
        out_dir = self.datasets_dir / name
        out_dir.mkdir(parents=True, exist_ok=True)
        items: List[dict] = []

        # Add positive feedback as instruction/response pairs
        ratings = {"positive": ["positive"], "neutral": ["positive", "neutral"], "any": ["positive", "neutral", "negative"]}
        allowed = ratings.get(min_rating, [min_rating])
        for fb in self.feedback_store.list():
            if fb.rating not in allowed:
                continue
            items.append(
                {
                    "instruction": fb.question,
                    "input": "",
                    "output": fb.correction or fb.answer,
                    "sources": fb.sources,
                    "model": fb.model,
                    "kind": "feedback",
                }
            )

        if include_memories:
            for mem in self.memory_store.export(redact=redact):
                items.append(
                    {
                        "instruction": f"Recall this fact: {mem['content']}",
                        "input": "",
                        "output": mem["content"],
                        "scope": mem.get("scope"),
                        "kind": "memory",
                    }
                )

        if redact:
            for item in items:
                item["output"] = MemoryStore._redact(item["output"])
                item["instruction"] = MemoryStore._redact(item["instruction"])

        jsonl_path = out_dir / "dataset.jsonl"
        with jsonl_path.open("w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        manifest = {
            "name": name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "items": len(items),
            "min_rating": min_rating,
            "include_memories": include_memories,
            "redacted": redact,
            "hash": self._hash_file(jsonl_path),
        }
        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
        return out_dir

    def review(self, name: str) -> str:
        """Return a Markdown review report for a dataset."""
        out_dir = self.datasets_dir / name
        manifest = json.loads((out_dir / "manifest.json").read_text())
        lines = [
            f"# Dataset Review: {name}",
            f"",
            f"- Created: {manifest['created_at']}",
            f"- Items: {manifest['items']}",
            f"- Min rating: {manifest['min_rating']}",
            f"- Include memories: {manifest['include_memories']}",
            f"- Redacted: {manifest['redacted']}",
            f"- Hash: {manifest['hash']}",
            f"",
            f"## Sample items",
            f"",
        ]
        with (out_dir / "dataset.jsonl").open() as f:
            for i, line in enumerate(f):
                if i >= 5:
                    break
                item = json.loads(line)
                lines.append(f"### {item['kind']}")
                lines.append(f"**Q:** {item['instruction']}")
                lines.append(f"**A:** {item['output']}")
                lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _hash_file(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:16]

    def list_datasets(self) -> List[str]:
        return sorted([p.name for p in self.datasets_dir.iterdir() if p.is_dir()])

    def delete(self, name: str) -> bool:
        out_dir = self.datasets_dir / name
        if out_dir.exists():
            shutil.rmtree(out_dir)
            return True
        return False
