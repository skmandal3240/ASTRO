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
from astro.feedback import FeedbackStore
from astro.index import Index
from astro.memory import MemoryStore

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
    .memories { font-size: .85rem; color: #444; margin-top: .5rem; border-left: 3px solid #3b82f6; padding-left: .5rem; }
    .feedback { margin-top: .5rem; }
    textarea { width: 100%; min-height: 80px; font: inherit; }
    input[type="text"] { width: 100%; font: inherit; padding: .25rem; }
    button { padding: .5rem 1rem; font: inherit; cursor: pointer; }
    .vault { color: #666; font-size: .9rem; margin-bottom: 1rem; }
    .actions { display: flex; gap: .5rem; flex-wrap: wrap; margin-top: .5rem; }
    .actions form { display: inline; }
    .thumb { background: #fff; border: 1px solid #ccc; border-radius: 4px; }
    .thumb:hover { background: #eef; }
    .success { color: green; font-size: .85rem; }
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

  <hr>
  <h2>Save a memory</h2>
  <form method="post" action="/remember">
    <input type="text" name="content" placeholder="e.g. My dentist is Dr. Rao" required>
    <input type="text" name="scope" placeholder="scope (optional)">
    <button type="submit">Remember</button>
  </form>
  {% if saved_memory %}<p class="success">Saved memory {{ saved_memory.id[:8] }}</p>{% endif %}

  {% for item in history %}
    <div class="msg user"><strong>You:</strong> {{ item.question }}</div>
    <div class="msg astro"><strong>ASTRO:</strong> {{ item.answer | safe }}
      {% if item.sources %}
      <div class="sources">
        Sources:<br>
        {% for s in item.sources %}- {{ s.path }}:{{ s.start_line }}-{{ s.end_line }}<br>{% endfor %}
      </div>
      {% endif %}
      {% if item.memories %}
      <div class="memories">
        Memories used:<br>
        {% for m in item.memories %}- {{ m.kind }}: {{ m.content[:120] }}{% if m.scope %} ({{ m.scope }}){% endif %}<br>{% endfor %}
      </div>
      {% endif %}
      <div class="feedback">
        <form method="post" action="/feedback" style="display:inline;">
          <input type="hidden" name="question" value="{{ item.question }}">
          <input type="hidden" name="answer" value="{{ item.answer_plain }}">
          <input type="hidden" name="rating" value="positive">
          <button type="submit" class="thumb">👍</button>
        </form>
        <form method="post" action="/feedback" style="display:inline;">
          <input type="hidden" name="question" value="{{ item.question }}">
          <input type="hidden" name="answer" value="{{ item.answer_plain }}">
          <input type="hidden" name="rating" value="negative">
          <button type="submit" class="thumb">👎</button>
        </form>
        <form method="post" action="/remember" style="display:inline;">
          <input type="hidden" name="content" value="{{ item.answer_plain }}">
          <button type="submit" class="thumb">Save as memory</button>
        </form>
      </div>
      {% if item.feedback_status %}<p class="success">{{ item.feedback_status }}</p>{% endif %}
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
    history.insert(
        0,
        {
            "question": question,
            "answer": result["answer"].replace("\n", "<br>"),
            "answer_plain": result["answer"],
            "sources": result["sources"],
            "memories": result["memories"],
        },
    )
    return templates.TemplateResponse(request, "index.html", {"history": history})


@app.post("/feedback", response_class=HTMLResponse)
def feedback_post(request: Request, question: str = Form(...), answer: str = Form(...), rating: str = Form(...)):
    store = FeedbackStore()
    fb = store.record(question, answer, rating)
    store.close()
    history = _state.setdefault("history", [])
    for item in history:
        if item["question"] == question and item["answer_plain"] == answer:
            item["feedback_status"] = f"Feedback recorded ({rating}) [{fb.id[:8]}]"
            break
    return templates.TemplateResponse(request, "index.html", {"history": history})


@app.post("/remember", response_class=HTMLResponse)
def remember_post(request: Request, content: str = Form(...), scope: str | None = Form(default=None)):
    store = MemoryStore()
    mem = store.add(content, kind="fact", source="web-ui", scope=scope)
    store.close()
    history = _state.setdefault("history", [])
    return templates.TemplateResponse(request, "index.html", {"history": history, "saved_memory": mem})


@app.get("/health")
def health():
    return {"status": "ok", "vault": _state.get("default_vault")}


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    idx = Index()
    chat = Chat(index=idx)
    set_state(idx, chat)
    uvicorn.run(app, host="127.0.0.1", port=8080)
