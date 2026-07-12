# ASTRO Production Runbook

## One-line install
```bash
git clone https://github.com/skmandal3240/ASTRO.git
cd ASTRO
make install        # or pip install -e ".[train]"
```

## First-time setup
```bash
scripts/setup.sh
ollama pull qwen2.5:0.5b
```

## Run locally
```bash
astro index ~/Documents/notes --clear
astro serve ~/Documents/notes --host 127.0.0.1 --port 8080
```
Open http://127.0.0.1:8080

## Background service
```bash
scripts/astro-service.sh start   # start
scripts/astro-service.sh stop    # stop
scripts/astro-service.sh status  # status
```

## Systemd (Linux)
```bash
cp scripts/astro.service ~/.config/systemd/user/astro.service
systemctl --user daemon-reload
systemctl --user enable --now astro
systemctl --user status astro
```

## Environment variables
| Variable | Default | Purpose |
|---|---|---|
| `ASTRO_HOME` | `~/.astro` | Data, DB, audit, adapters |
| `ASTRO_OLLAMA_URL` | `http://localhost:11434` | Ollama endpoint |
| `ASTRO_OLLAMA_MODEL` | `qwen2.5:0.5b` | Default chat model |
| `ASTRO_EMBED_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `ASTRO_PORT` | `8080` | Service port (service script only) |
| `ASTRO_VAULT` | `~/Documents/notes` | Default vault (service script only) |

## Release checklist
```bash
make lint
make test
make release-check
```

## PyPI upload (when ready)
```bash
python -m build
python -m twine upload dist/*
```
Then users can `pip install astro-ai`.

## Security notes
- Default web UI binds to `127.0.0.1` only.
- High-risk capabilities (`file_write`, `shell`, `browser_research`, `training_export`) require explicit approval.
- Audit log is append-only NDJSON at `$ASTRO_HOME/audit.ndjson`.
- All data stays local unless user explicitly exports.

## Troubleshooting
- **Ollama not found**: install from https://ollama.com and pull a model.
- **Port in use**: `ASTRO_PORT=8090 scripts/astro-service.sh start`
- **Tests fail on embeddings**: first run downloads `all-MiniLM-L6-v2`; may be slow.
