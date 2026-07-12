"""Smoke test for web UI."""
from pathlib import Path
import tempfile

from fastapi.testclient import TestClient

from astro.index import Index
from astro.web import app, set_state, _state


class _FakeChat:
    def ask(self, question, vault_path=None, top_k=5):
        return {
            "answer": "A",
            "sources": [{"path": "note.md", "start_line": 1, "end_line": 2}],
            "memories": [{"kind": "fact", "content": "I prefer short answers", "scope": "personal"}],
        }


def test_web_ui_renders_and_accepts_feedback():
    with tempfile.TemporaryDirectory() as td:
        vault = Path(td) / "vault"
        vault.mkdir()
        (vault / "note.md").write_text("ASTRO is a local-first AI.\n")
        idx = Index()
        idx.index_vault(vault)
        set_state(idx, _FakeChat(), default_vault=vault)
        _state["history"] = []
        client = TestClient(app)

        r1 = client.get("/")
        assert r1.status_code == 200
        assert "Save a memory" in r1.text

        r2 = client.post("/ask", data={"question": "Q"})
        assert r2.status_code == 200
        assert "Memories used" in r2.text
        assert "Save as memory" in r2.text

        r3 = client.post("/remember", data={"content": "I prefer short answers", "scope": "personal"})
        assert r3.status_code == 200
        assert "Saved memory" in r3.text

        r4 = client.post("/feedback", data={"question": "Q", "answer": "A", "rating": "positive"})
        assert r4.status_code == 200
        assert "Feedback recorded" in r4.text
