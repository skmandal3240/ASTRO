# ASTRO Phase 4 — Release Engineering & Packaging

## Goal

ASTRO becomes installable, documented, and reproducible:
- one-command install (`pip install -e .` or future `pip install astro-ai`)
- documented local setup (Ollama, SQLite, optional GPU training)
- simple release smoke test script
- clear next steps in README and PLAN

## Components

1. **Packaging**
   - `pyproject.toml` already defines package metadata and entrypoints.
   - Add `__main__.py` for `python -m astro`.
   - Ensure `MANIFEST.in` includes templates and docs.

2. **Setup / install helper**
   - `scripts/setup.sh` or Makefile target: install base deps, create `~/.astro`, pull default Ollama model.
   - `Makefile` with targets: `install`, `test`, `serve`, `lint`.

3. **Release check script**
   - `scripts/release_check.py`: runs `pytest`, `eval/eval.py`, `astro --help`, checks Ollama model available.

4. **Documentation**
   - Update `README.md` with install, quickstart, phase status (Phase 3 complete, Phase 4 complete).
   - Create `docs/phase4/README.md` summarizing release engineering.

5. **Version bump**
   - Keep version `0.1.0` for first internal release; update when Phase 4 lands.

## Acceptance Criteria

- `pip install -e .` works in a fresh venv.
- `astro --help` lists all commands.
- `make test` passes.
- `python scripts/release_check.py` exits 0.
- README quickstart is copy-pasteable.

## Out of Scope

- PyPI upload (needs account + CI).
- Desktop installer / .deb / AppImage.
- Multi-user server deployment.
