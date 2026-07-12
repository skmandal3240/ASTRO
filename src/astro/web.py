"""
Minimal web UI for ASTRO.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from astro.chat import Chat
from astro.config import DEFAULT_DATA_DIR
from astro.index import Index

app = FastAPI(title="ASTRO AI")

_state: dict[str, Any] = {
    "index": None,
    "chat": None,
    "default_vault": None,
}


def set_state(index: Index, chat: Chat, default_vault: Path | str | None = None) -> None:
    _state["index"] = index
    _state["chat"] = chat
    _state["default_vault"] = str(Path(default_vault).resolve()) if default_vault else None


STATIC_DIR = Path(__file__).parent / "static"
TEMPLATES_DIR = Path(__file__).parent / "templates"

# ensure static/templates dirs exist so StaticFiles doesn't crash
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


_INDEX_HTML = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ASTRO AI</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 760px; margin: 2rem auto; padding: 0 1rem; }
    h1 { font-weight: 600; }
    .msg { margin: 1rem 0; padding: 1rem; border-radius: 8px; }
    .user { background: #e6f3ff; }
    .astro { background: #f3f4f6; }
    .sources { font-size: .85rem; color: #555; margin-top: .5rem; }
    textarea { width: 100%; min-height: 80px; font: inherit; }
    button { padding: .5rem 1rem; font: inherit; cursor: pointer; }
    .vault { color: #666; font-size: .9rem; margin-bottom: 1rem; }
  </style>
</head>
<body>
  <h1>ASTRO AI</h1>
  <p class="vault">Local-first, permissioned personal AI.</p>
  <form method="post" action="/ask">
    <textarea name="question" placeholder="Ask something about your vault..." required></textarea>
    <br><br>
    <button type="submit">Ask ASTRO</button>
  </form>
  {% for q, a, sources in history %}
    <div class="msg user"><strong>You:</strong> {{ q }}</div>
    <div class="msg astro"><strong>ASTRO:</strong> {{ a | safe }}
      {% if sources %}
      <div class="sources">
        Sources:<br>
        {% for s in sources %}- {{ s.path }}:{{ s.start_line }}-{{ s.end_line }}<br>{% endfor %}
      </div>
      {% endif %}
    </div>
  {% endfor %}
</body>
</html>
"""

# ponytail: write the template once if missing
if not (TEMPLATES_DIR / "index.html").exists():
    (TEMPLATES_DIR / "index.html").write_text(_INDEX_HTML, encoding="utf-8")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"history": _state.get("history", [])})


@app.post("/ask", response_class=HTMLResponse)
def ask_post(request: Request, question: str = Form(...)):
    chat = _state["chat"]
    result = chat.ask(question, vault_path=_state.get("default_vault"), top_k=5)
    history = _state.setdefault("history", [])
    history.insert(0, (question, result["answer"].replace("\n", "<br>"), result["sources"]))
    return templates.TemplateResponse(request, "index.html", {"history": history})


@app.get("/health")
def health():
    return {"status": "ok", "vault": _state.get("default_vault")}


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    idx = Index()
    chat = Chat(index=idx)
    set_state(idx, chat)
    uvicorn.run(app, host="127.0.0.1", port=8080)
