"""
ASTRO CLI.
"""
from __future__ import annotations

from pathlib import Path

import click

from astro.chat import Chat
from astro.index import Index


@click.group()
def main():
    """ASTRO AI — local-first, permissioned personal AI."""
    pass


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
@click.option("--model", help="Ollama model name")
@click.option("--top-k", default=5, show_default=True)
def ask(question: str, vault_path: Path | None, db: Path | None, model: str | None, top_k: int):
    """Ask a question using indexed vault context."""
    chat = Chat(index=Index(db_path=db, model_name=None), model=model or "qwen2.5:0.5b")
    try:
        result = chat.ask(question, vault_path=vault_path, top_k=top_k)
        click.echo(result["answer"])
        if result["sources"]:
            click.echo("\nSources:")
            for s in result["sources"]:
                click.echo(f"- {s['path']}:{s['start_line']}-{s['end_line']}")
    finally:
        chat.close()


@main.command()
@click.argument("vault_path", required=False, type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8080, show_default=True)
@click.option("--db", type=click.Path(path_type=Path))
@click.option("--model", help="Ollama model name")
def serve(vault_path: Path | None, host: str, port: int, db: Path | None, model: str | None):
    """Run ASTRO web daemon."""
    import uvicorn
    from astro.web import app, set_state

    set_state(Index(db_path=db), Chat(index=Index(db_path=db, model_name=None), model=model or "qwen2.5:0.5b"), default_vault=vault_path)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
