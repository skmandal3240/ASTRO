# ASTRO Phase 4 — Release Engineering & Packaging

## Goal

ASTRO becomes installable, documented, and reproducible:
- one-command install (`pip install -e .` or future `pip install astro-ai`)
- documented local setup (Ollama, SQLite, optional GPU training)
- simple release smoke test script
- clear next steps in README and PLAN

## Status

✅ Complete and pushed to `origin/main`.

## Components

1. **Packaging**
   - `pyproject.toml` includes license, authors, classifiers, project URLs.
   - `src/astro/__main__.py` enables `python -m astro`.
   - `MANIFEST.in` includes templates, scripts, docs.
   - `LICENSE` (MIT) and `CHANGELOG.md` added.

2. **Setup / install helper**
   - `scripts/setup.sh` installs deps, creates `~/.astro`, pulls default Ollama model.
   - `Makefile` targets: `install`, `test`, `serve`, `lint`, `release-check`, `clean`.

3. **Release validation**
   - `scripts/release_check.py`: runs `pytest`, `eval/eval.py`, `astro --help`, checks Ollama model.
   - `.github/workflows/ci.yml` runs CI on Python 3.10/3.11/3.12.

4. **Background runner**
   - `scripts/astro-service.sh` start/stop/status for the web UI.
   - `scripts/astro.service` systemd user unit.

5. **Security / config**
   - `ASTRO_HOME`, `ASTRO_OLLAMA_URL`, `ASTRO_OLLAMA_MODEL`, `ASTRO_EMBED_MODEL` are env-aware.
   - Audit log is append-only NDJSON.
   - Web UI defaults to `127.0.0.1`.

6. **Documentation**
   - `docs/RUNBOOK.md` covers install, service, environment variables, troubleshooting, PyPI upload.
   - `README.md` and `docs/PLAN.md` updated to all phases complete.

## Acceptance Criteria

- `pip install -e .` works in a fresh venv.
- `astro --help` lists all commands.
- `make test` passes.
- `make release-check` exits 0.
- README quickstart is copy-pasteable.
- Package builds with `python -m build`.

## Out of Scope

- PyPI upload (needs account + trusted publisher setup).
- Desktop installer / .deb / AppImage.
- Multi-user server deployment.

For day-to-day operations see [`docs/RUNBOOK.md`](../RUNBOOK.md).
