"""
ASTRO CLI.
"""
from __future__ import annotations

from pathlib import Path

import click

from astro.agent import Agent
from astro.capabilities import Grant, Ledger, PolicyEngine
from astro.chat import Chat
from astro.curator import Curator
from astro.feedback import FeedbackStore
from astro.index import Index
from astro.memory import MemoryStore
from astro.model_registry import ModelRegistry
from astro.trainer import Trainer


@click.group()
def main():
    """ASTRO AI — local-first, permissioned personal AI."""
    pass


@main.command()
@click.argument("capability")
@click.argument("scope")
@click.option("--approval", default="always", show_default=True, help="always | rule | never")
@click.option("--risk", default=None, help="low | medium | high")
def grant(capability: str, scope: str, approval: str, risk: str | None):
    """Grant a capability to ASTRO."""
    ledger = Ledger()
    g = Grant(capability=capability, scope=scope, approval=approval, risk=risk or "")
    ledger.grant(g)
    click.echo(f"Granted {capability} for {scope} (approval={approval})")


@main.command()
@click.argument("capability")
@click.argument("scope", required=False)
def revoke(capability: str, scope: str | None):
    """Revoke a capability grant."""
    ledger = Ledger()
    n = ledger.revoke(capability, scope)
    click.echo(f"Revoked {n} grant(s) for {capability}")


@main.command()
def stop():
    """Emergency stop: revoke all active skills."""
    ledger = Ledger()
    for cap in ("file_write", "shell", "browser_research", "memory_write"):
        ledger.revoke_all(cap)
    click.echo("Stopped all skills.")


@main.command()
@click.argument("request")
@click.option("--model", default="qwen2.5:0.5b", show_default=True)
@click.option("--approve", is_flag=True, help="Pre-approve any proposed action")
def do(request: str, model: str, approve: bool):
    """Ask ASTRO to do something with policy-checked skills."""
    agent = Agent(model=model)
    plan = agent.plan(request)
    click.echo(f"Plan: {plan}")
    result = agent.execute(plan, approved=approve)
    if result.get("requires_approval"):
        click.echo("\n⚠️  This action requires approval.")
        click.echo(result["preview"])
        click.echo("\nRun again with --approve to execute.")
    else:
        if result.get("ok"):
            click.echo(f"Result: ok\n{result.get('output', '')[:500]}")
        else:
            click.echo(f"Result: {result}")


@main.command()
@click.argument("content")
@click.option("--kind", default="fact", show_default=True, help="fact | preference | correction")
@click.option("--source", default="user", show_default=True)
@click.option("--scope", default=None)
@click.option("--ttl", default=None, help="e.g. 1d, 2w, 1M, 1y")
def remember(content: str, kind: str, source: str, scope: str | None, ttl: str | None):
    """Save an explicit memory after user confirmation."""
    store = MemoryStore()
    m = store.add(content, kind=kind, source=source, scope=scope, ttl=ttl)
    click.echo(f"Remembered [{m.id[:8]}]: {content}")
    store.close()


@main.command()
@click.option("--kind")
@click.option("--scope")
@click.option("--search")
@click.option("--limit", default=20, show_default=True)
def memories(kind: str | None, scope: str | None, search: str | None, limit: int):
    """List or search memories."""
    store = MemoryStore()
    if search:
        rows = store.search(search, top_k=limit)
    else:
        rows = store.list(kind=kind, scope=scope, limit=limit)
    for m in rows:
        click.echo(f"{m.id[:8]} | {m.kind} | {m.scope or 'all'} | {m.content[:80]}")
    store.close()


@main.command()
@click.argument("question")
@click.argument("answer")
@click.argument("rating")
@click.option("--correction", default=None)
@click.option("--source", default=None, help="Comma-separated source citations")
@click.option("--model", default="")
def feedback(question: str, answer: str, rating: str, correction: str | None, source: str | None, model: str):
    """Record feedback for an answer."""
    store = FeedbackStore()
    sources = [s.strip() for s in source.split(",")] if source else []
    fb = store.record(question, answer, rating, correction=correction, sources=sources, model=model)
    click.echo(f"Recorded feedback [{fb.id[:8]}]: {rating}")
    store.close()


@main.command()
@click.argument("name")
@click.option("--min-rating", default="positive", show_default=True)
@click.option("--include-memories/--no-include-memories", default=True)
@click.option("--redact/--no-redact", default=True)
def dataset(name: str, min_rating: str, include_memories: bool, redact: bool):
    """Build a reviewed training dataset from feedback and memories."""
    curator = Curator()
    path = curator.build(name, min_rating=min_rating, include_memories=include_memories, redact=redact)
    click.echo(f"Dataset built at {path}")
    report = curator.review(name)
    click.echo("\n" + report)


@main.command()
@click.argument("dataset_name")
@click.argument("adapter_name")
@click.option("--epochs", default=3, show_default=True)
@click.option("--lr", default=1e-4, show_default=True)
def train(dataset_name: str, adapter_name: str, epochs: int, lr: float):
    """Stage an offline LoRA adapter from a dataset."""
    trainer = Trainer()
    path = trainer.train(dataset_name, adapter_name, epochs=epochs, learning_rate=lr)
    click.echo(f"Adapter staged at {path}")


@main.command(name="model")
def model_list():
    """List base model and local adapters."""
    reg = ModelRegistry()
    for e in reg.list():
        marker = "*" if reg.active() == e["name"] else " "
        click.echo(f"{marker} {e['name']} | {e.get('model', '')}")


@main.command()
@click.argument("name")
def activate(name: str):
    """Activate base or a named adapter."""
    reg = ModelRegistry()
    reg.activate(name)
    click.echo(f"Active model: {name}")


@main.command()
@click.argument("vault_path", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--clear", is_flag=True, help="Clear existing index for this vault")
@click.option("--db", type=click.Path(path_type=Path), help="Path to ASTRO database")
@click.option("--model", help="Sentence-transformer embedding model")
def index(vault_path: Path, clear: bool, db: Path | None, model: str | None):
    """Index a Markdown vault."""
    idx = Index(db_path=db, model_name=model)
    n = idx.index_vault(vault_path, clear=clear)
    click.echo(f"Indexed {n} chunks from {vault_path}")
    idx.close()


@main.command()
@click.argument("question")
@click.argument("vault_path", required=False, type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--db", type=click.Path(path_type=Path))
@click.option("--model", help="Ollama model name or adapter name")
@click.option("--top-k", default=5, show_default=True)
def ask(question: str, vault_path: Path | None, db: Path | None, model: str | None, top_k: int):
    """Ask a question using indexed vault context and memories."""
    chat = Chat(index=Index(db_path=db, model_name=None), model=model or "qwen2.5:0.5b")
    try:
        result = chat.ask(question, vault_path=vault_path, top_k=top_k)
        click.echo(result["answer"])
        if result["sources"]:
            click.echo("\nSources:")
            for s in result["sources"]:
                click.echo(f"- {s['path']}:{s['start_line']}-{s['end_line']}")
        if result["memories"]:
            click.echo("\nMemories used:")
            for m in result["memories"]:
                click.echo(f"- {m['kind']}: {m['content'][:80]}")
    finally:
        chat.close()


@main.command()
@click.argument("vault_path", required=False, type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8080, show_default=True)
@click.option("--db", type=click.Path(path_type=Path))
@click.option("--model", help="Ollama model name or adapter name")
def serve(vault_path: Path | None, host: str, port: int, db: Path | None, model: str | None):
    """Run ASTRO web daemon."""
    import uvicorn
    from astro.web import app, set_state

    set_state(Index(db_path=db), Chat(index=Index(db_path=db, model_name=None), model=model or "qwen2.5:0.5b"), default_vault=vault_path)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
