# ASTRO AI

**ASTRO AI — a local-first, permissioned personal AI platform.**

ASTRO runs a small language model on your device, reads only the files you explicitly allow, and only performs actions you preview and approve. It is built for people who want an AI that knows their notes without leaking private data to the cloud.

Repository: `https://github.com/skmandal3240/ASTRO`

---

## Build status

| Phase | Goal | Status | Key artifacts |
|---|---|---|---|
| 0 | Product, policy, and evaluation | ✅ Complete | `docs/phase0/CAPABILITIES.md`, `docs/phase0/THREAT_MODEL.md`, `docs/phase0/EVAL.md`, `eval/eval.py` |
| 1 | Local assistant MVP (daemon + vault chat) | ✅ Complete | `src/astro/`, `pyproject.toml`, vault chat works, 5/5 benchmark pass |
| 2 | Permissioned skills and OS actions | ✅ Complete | `src/astro/capabilities.py`, `src/astro/skills.py`, `src/astro/agent.py`, `docs/phase2/README.md` |
| 3 | Personal memory and feedback learning | ✅ Complete | `src/astro/memory.py`, `src/astro/feedback.py`, `src/astro/curator.py`, `src/astro/trainer.py`, `src/astro/model_registry.py`, `docs/phase3/README.md` |
| 4 | Release engineering and packaging | ✅ Complete | `Makefile`, `scripts/setup.sh`, `scripts/release_check.py`, `docs/phase4/README.md` |

Current phase: **Phase 4**.

---

## What ASTRO does

1. **Reads your local vault.** Select an Obsidian-style Markdown folder. ASTRO indexes it locally and answers questions with file/line citations.
2. **Performs actions safely.** For file edits, shell commands, or network calls, ASTRO checks grants, shows a preview, and waits for approval.
3. **Learns only with consent.** Corrections become explicit memories; offline training happens only when you export a reviewed dataset and start a job.
4. **Keeps an audit journal.** Every proposed, approved, and executed action is logged locally.

---

## Repository layout

```
ASTRO/
├── src/astro/
│   ├── __init__.py
│   ├── agent.py          # Planner + policy executor
│   ├── audit.py          # Audit journal
│   ├── capabilities.py   # Capability ledger and policy engine
│   ├── chat.py           # Ollama-backed RAG chat with memory
│   ├── cli.py            # astro CLI
│   ├── config.py         # Defaults
│   ├── curator.py        # Training dataset builder
│   ├── feedback.py       # Answer feedback store
│   ├── index.py          # sqlite-vec + lexical index
│   ├── memory.py         # Explicit memory store
│   ├── model_registry.py # Base + adapter model switcher
│   ├── skills.py         # File / shell / browser skills
│   ├── trainer.py        # Offline LoRA adapter staging
│   ├── vault.py          # Markdown parser
│   └── web.py            # FastAPI chat UI
├── eval/
│   └── eval.py           # Phase 0 evaluation harness
├── docs/
│   ├── PRD.md            # Full product requirements
│   ├── PLAN.md           # Living build plan
│   ├── ARCHITECTURE.md   # System architecture
│   ├── SAFETY.md         # Safety rules
│   ├── phase0/           # Phase 0 docs
│   ├── phase1/           # Phase 1 docs
│   ├── phase2/           # Phase 2 docs
│   └── phase3/           # Phase 3 docs
├── tests/                # Smoke tests
├── pyproject.toml        # Package metadata and deps
└── README.md             # This file
```

---

## Quick start

### Install

```bash
git clone https://github.com/skmandal3240/ASTRO.git
cd ASTRO
make install
```

Or run the helper script:

```bash
bash scripts/setup.sh
```

### Index your vault

```bash
astro index ~/Documents/obsidian-vault --clear
```

### Ask a question

```bash
astro ask "What did I write about pricing?" ~/Documents/obsidian-vault
```

### Run the web UI

```bash
astro serve ~/Documents/obsidian-vault
# open http://127.0.0.1:8080
```

### Permissioned actions

```bash
# grant a capability
astro grant file_read /home/user/notes --approval always

# ask ASTRO to do something
astro do "list files in /home/user/notes"

# high-risk actions show a preview; run with --approve
astro do "write hello to /tmp/astro-test.txt" --approve

# emergency stop
astro stop
```

### Memory and feedback (Phase 3)

```bash
astro remember "My dentist is Dr. Rao" --scope personal --ttl 1y
astro memories --search "dentist"
astro feedback "question text" "answer text" positive --source note.md:1-2
astro dataset v1
astro train v1 v1-adapter --epochs 3 --lr 1e-4
astro model          # list adapters
astro activate base  # or v1-adapter
```

---

## Phase exit criteria

### Phase 0
- [x] Eval harness runnable.
- [x] Threat model + capability model written.
- [x] Phase 0 marked complete in README.

### Phase 1
- [x] Vault indexing with Markdown parser + embeddings + sqlite-vec.
- [x] Chat answers grounded in retrieved vault context with citations.
- [x] Audit journal logs index and chat events.
- [x] Web UI accepts questions and shows sources.
- [x] Vault Q&A benchmark passes.

### Phase 2
- [x] Capability ledger with grant/revoke/stop.
- [x] Policy engine decides allowed / approval-required / blocked.
- [x] File, shell, browser skills with preview + commit pattern.
- [x] CLI commands: `grant`, `revoke`, `stop`, `do`.
- [x] Automated policy tests pass.
- [x] Phase 2 marked complete in README.

### Phase 3
- [x] Explicit memory CRUD with search, expiry, redaction.
- [x] Feedback loop on chat answers.
- [x] Dataset curation from feedback + memories.
- [x] Offline adapter training staging + model registry.
- [x] Chat injects relevant memories into context.
- [x] Phase 3 marked complete in README.

### Phase 4
- [x] `Makefile` with `install`, `test`, `serve`, `lint`, `release-check`.
- [x] `scripts/setup.sh` for first-time install.
- [x] `scripts/release_check.py` for pre-release validation.
- [x] `docs/phase4/README.md` release notes.
- [x] README quickstart updated.

---

## Contributing

All four phases are complete for the internal 0.1.0 release. PyPI upload and desktop packaging are future work.

---

*Project ASTRO — local-first AI that you control.*
