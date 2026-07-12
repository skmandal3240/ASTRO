"""Smoke test for web UI."""
from pathlib import Path
import tempfile

import pytest
from fastapi.testclient import TestClient

from astro.index import Index
from astro.chat import Chat
from astro.web import app, set_state


@pytest.fixture
def client():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        p = td / "note.md"
        p.write_text("# Note\n\nDeadline is Friday.\n")
        db = td / "astro.db"
        idx = Index(db_path=db)
        idx.index_vault(td, clear=True)
        chat = Chat(index=idx, model="qwen2.5:0.5b")
        set_state(idx, chat, default_vault=td)
        yield TestClient(app)


def test_home(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "<form" in r.text


def test_ask(client):
    r = client.post("/ask", data={"question": "What is the deadline?"})
    assert r.status_code == 200
    assert "Friday" in r.text
