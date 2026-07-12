"""
Model registry for ASTRO.

Lists base model and locally trained adapters; activates one.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from astro.config import ADAPTERS_DIR, DEFAULT_OLLAMA_MODEL, OLLAMA_URL


class ModelRegistry:
    def __init__(self, adapters_dir: Optional[Path] = None, base_model: str = DEFAULT_OLLAMA_MODEL):
        self.adapters_dir = Path(adapters_dir or ADAPTERS_DIR)
        self.adapters_dir.mkdir(parents=True, exist_ok=True)
        self.base_model = base_model
        self.active_file = self.adapters_dir / ".active"

    def list(self) -> List[dict]:
        entries = [{"name": "base", "path": None, "model": self.base_model}]
        for p in sorted(self.adapters_dir.iterdir()):
            if p.is_dir() and (p / "manifest.json").exists():
                manifest = json.loads((p / "manifest.json").read_text())
                entries.append(
                    {
                        "name": p.name,
                        "path": str(p),
                        "model": manifest.get("base_model", self.base_model),
                        "created_at": manifest.get("created_at"),
                    }
                )
        return entries

    def activate(self, name: str) -> str:
        if name != "base" and not (self.adapters_dir / name).exists():
            raise ValueError(f"unknown adapter: {name}")
        self.active_file.write_text(json.dumps({"name": name}))
        return name

    def active(self) -> str:
        if self.active_file.exists():
            return json.loads(self.active_file.read_text()).get("name", "base")
        return "base"

    def adapter_path(self, name: Optional[str] = None) -> Optional[Path]:
        name = name or self.active()
        if name == "base":
            return None
        p = self.adapters_dir / name
        return p if p.exists() else None

    @staticmethod
    def ollama_model_name(name: Optional[str] = None) -> str:
        """Return the Ollama model string to use."""
        if name is None or name == "base":
            return DEFAULT_OLLAMA_MODEL
        return name  # assume a custom Ollama model was created separately
