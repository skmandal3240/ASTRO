"""
Ollama-backed chat for ASTRO.

Retrieves relevant chunks, formats a grounded prompt, and streams the answer.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import AsyncIterator, List

import requests

from astro.audit import log
from astro.config import DEFAULT_OLLAMA_MODEL, OLLAMA_URL
from astro.index import Index
from astro.memory import MemoryStore
from astro.model_registry import ModelRegistry


SYSTEM_PROMPT = """You are ASTRO, a local-first AI assistant that answers from the user's own notes and files.
Use only the provided context and confirmed memories to answer. Cite sources as [path:relative/to/vault.md:start-end].
If the context does not contain the answer, say you don't know."""


def _format_context(question: str, results: List[dict], memories: List[dict]) -> str:
    """Build a grounded prompt from retrieved chunks, memories, and the question."""
    blocks = []
    for r in results:
        cite = f"[{r['path']}:{r['start_line']}-{r['end_line']}]"
        blocks.append(f"Source: {cite}\n{r['text']}")
    for m in memories:
        blocks.append(f"Memory [{m['kind']}]: {m['content']}")
    context = "\n\n".join(blocks) if blocks else "(no relevant notes found)"
    return f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"


class Chat:
    def __init__(
        self,
        index: Index | None = None,
        memory_store: MemoryStore | None = None,
        model: str | None = None,
        registry: ModelRegistry | None = None,
    ):
        self.index = index or Index()
        self.memory_store = memory_store or MemoryStore()
        self.registry = registry or ModelRegistry()
        self.model = model or self.registry.active()
        self.url = f"{OLLAMA_URL}/api/generate"

    def ask(self, question: str, vault_path: Path | str | None = None, top_k: int = 5) -> dict:
        results = self.index.search(question, vault_path=vault_path, top_k=top_k)
        memories = [m.__dict__ for m in self.memory_store.search(question, top_k=3)]
        prompt = _format_context(question, results, memories)
        # Resolve adapter name to actual Ollama model tag
        model_name = self.model
        if model_name not in (None, "base") and not self.registry.adapter_path(model_name):
            model_name = DEFAULT_OLLAMA_MODEL
        r = requests.post(
            self.url,
            json={"model": model_name or DEFAULT_OLLAMA_MODEL, "prompt": prompt, "system": SYSTEM_PROMPT, "stream": False},
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        answer = data.get("response", "").strip()
        log("chat", {
            "question": question,
            "model": self.model,
            "sources": [f"{x['path']}:{x['start_line']}-{x['end_line']}" for x in results],
            "memories": [m["id"] for m in memories],
            "answer_preview": answer[:200],
        })
        return {"answer": answer, "sources": results, "memories": memories, "model": self.model}

    async def ask_stream(self, question: str, vault_path: Path | str | None = None, top_k: int = 5) -> AsyncIterator[str]:
        results = self.index.search(question, vault_path=vault_path, top_k=top_k)
        memories = [m.__dict__ for m in self.memory_store.search(question, top_k=3)]
        prompt = _format_context(question, results, memories)
        # stream placeholder: full response as one chunk
        model_name = self.model
        if model_name not in (None, "base") and not self.registry.adapter_path(model_name):
            model_name = DEFAULT_OLLAMA_MODEL
        r = requests.post(
            self.url,
            json={"model": model_name or DEFAULT_OLLAMA_MODEL, "prompt": prompt, "system": SYSTEM_PROMPT, "stream": False},
            timeout=120,
        )
        r.raise_for_status()
        yield r.json().get("response", "").strip()
        # yield source footer after answer
        if results:
            yield "\n\nSources:\n" + "\n".join(
                f"- {x['path']}:{x['start_line']}-{x['end_line']}" for x in results
            )

    def close(self) -> None:
        self.index.close()
