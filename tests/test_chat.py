"""Smoke tests for chat/citations."""
from pathlib import Path
import tempfile

from astro.index import Index
from astro.chat import Chat, _format_context


def test_format_context_includes_citations():
    chunks = [
        {"path": "/tmp/a.md", "start_line": 1, "end_line": 2, "text": "Hello world"}
    ]
    prompt = _format_context("What?", chunks)
    assert "Hello world" in prompt
    assert "Source:" in prompt


def test_chat_index_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        p = td / "note.md"
        p.write_text("# Note\n\nDeadline is Friday.\n")
        db = td / "astro.db"
        idx = Index(db_path=db)
        idx.index_vault(td, clear=True)
        chat = Chat(index=idx, model="qwen2.5:0.5b")
        result = chat.ask("What is the deadline?", vault_path=td, top_k=3)
        assert result["sources"]
        assert "Friday" in result["sources"][0]["text"]
