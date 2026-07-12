# ASTRO Phase 1 — Local Assistant MVP

## Goal

ASTRO can answer questions from a selected Markdown vault with file/line citations while all data stays local.

## Components

| File | Purpose |
|---|---|
| `src/astro/config.py` | Paths, defaults, model names. |
| `src/astro/vault.py` | Markdown parser: chunks, frontmatter, tags, wikilinks, line ranges. |
| `src/astro/index.py` | `sqlite-vec` + lexical store; embed and search vault chunks. |
| `src/astro/chat.py` | Ollama-backed chat with retrieval-augmented context and citations. |
| `src/astro/audit.py` | Append-only NDJSON audit journal. |
| `src/astro/web.py` | FastAPI web UI for chat. |
| `src/astro/cli.py` | `astro index`, `astro ask`, `astro serve` commands. |

## CLI usage

### 1. Install

```bash
cd ASTRO
pip install -e .
```

### 2. Index a vault

```bash
astro index /path/to/obsidian-vault --clear
```

This creates `~/.astro/astro.db` with chunks and vector embeddings. Nothing is uploaded.

### 3. Ask from the terminal

```bash
astro ask "What are the project deadlines?" /path/to/obsidian-vault
```

### 4. Run the web UI

```bash
astro serve /path/to/obsidian-vault
# open http://127.0.0.1:8080
```

## Exit criteria

- [x] Vault indexing produces cited chunks.
- [x] Chat answers are grounded in retrieved vault context.
- [x] Audit journal logs every chat and index event.
- [x] Web UI accepts questions and shows sources.
- [ ] Evaluation on real vault Q&A benchmark meets 50%+ accuracy.
- [ ] Phase 1 marked complete in root README.

## Notes

- Default local model: `qwen2.5:0.5b` via Ollama. Replace in `config.py` or CLI `--model`.
- Default embedding model: `sentence-transformers/all-MiniLM-L6-v2` (384-dim).
- No file-write, shell, or browser skills yet. Those are Phase 2.
