# ASTRO AI — Build Plan

This is the living build plan for ASTRO AI. See [`PRD.md`](./PRD.md) for the full product definition.

## Phase Status

| Phase | Goal | Status | Exit Criteria |
|---|-:|---|---|
| 0 | Policy, threat model, evaluation | ✅ Complete | Eval harness runnable, threat model written, capability model defined |
| 1 | Local assistant MVP | ✅ Complete | Vault indexing + chat + web UI + citations + audit journal |
| 2 | Permissioned skills and OS actions | ✅ Complete | Scoped grants, file/shell/browser skills, policy engine, CLI commands |
| 3 | Personal memory and feedback learning | ✅ Complete | `memory.py`, `feedback.py`, `curator.py`, `trainer.py`, `model_registry.py`, tests, web UI |
| 4 | Release engineering and packaging | ✅ Complete | `Makefile`, `scripts/setup.sh`, `scripts/release_check.py`, `__main__.py`, `MANIFEST.in` |

All four phases are implemented and pushed to `origin/main`.

## Quick Reference

### Install
```bash
git clone https://github.com/skmandal3240/ASTRO.git
cd ASTRO
make install
```

### Index and chat
```bash
astro index ~/Documents/obsidian-vault --clear
astro ask "What did I write about pricing?" ~/Documents/obsidian-vault
astro serve ~/Documents/obsidian-vault
```

### Permissioned actions
```bash
astro grant file_read /home/user/notes --approval always
astro do "list files in /home/user/notes"
astro do "write hello to /tmp/astro-test.txt" --approve
astro stop
```

### Memory, feedback, training
```bash
astro remember "My dentist is Dr. Rao" --scope personal --ttl 1y
astro memories --search "dentist"
astro feedback "question" "answer" positive --source note.md:1-2
astro dataset v1
astro train v1 v1-adapter --epochs 3 --lr 1e-4
astro model
astro activate base
```

### Release validation
```bash
make test
make lint
make release-check
```

## Future Work (not in current release)

- PyPI upload and CI.
- Desktop installer / packaged app.
- Multi-user server mode.
- Real end-to-end LoRA training smoke on a GPU.
- A/B evaluation gates for adapter activation.

*Last updated: 2026-07-12*
