# ASTRO AI

**ASTRO AI — a local-first, permissioned personal AI platform.**

ASTRO runs a small language model on your device, reads only the files you explicitly allow, and only performs actions you preview and approve. It is built for people who want an AI that knows their notes without leaking private data to the cloud.

Repository: `https://github.com/skmandal3240/ASTRO`

---

## Build status

| Phase | Goal | Status | Key artifacts |
|---|---|---|---|
| 0 | Product, policy, and evaluation | Complete | `docs/phase0/CAPABILITIES.md`, `docs/phase0/THREAT_MODEL.md`, `docs/phase0/EVAL.md`, `eval/eval.py` |
| 1 | Local assistant MVP (daemon + vault chat) | Complete | `src/astro/`, `pyproject.toml`, vault chat works, 5/5 benchmark pass |
| 2 | Permissioned skills and OS actions | **In progress** | `src/astro/capabilities.py`, `src/astro/skills.py`, `src/astro/agent.py`, `docs/phase2/README.md` |
| 3 | Personal memory and feedback learning | Not started | — |
| 4 | Model improvement and release engineering | Not started | — |

Current phase: **Phase 2**.

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
│   ├── chat.py           # Ollama-backed RAG chat
│   ├── cli.py            # astro CLI
│   ├── config.py         # Defaults
│   ├── index.py          # sqlite-vec + lexical index
│   ├── skills.py         # File / shell / browser skills
│   ├── vault.py          # Markdown parser
│   └── web.py            # FastAPI chat UI
├── eval/
│   └── eval.py           # Phase 0 evaluation harness
├── docs/
│   ├── PRD.md            # Full product requirements
│   ├── PLAN.md           # Living build plan
│   ├── ARCHITECTURE.md   # System architecture
│   ├── SAFETY.md         # Safety rules
│   └── phase0/           # Phase 0 docs
│   └── phase1/           # Phase 1 docs
│   └── phase2/           # Phase 2 docs
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
pip install -e .
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

---

## Phase 1 exit criteria

- [x] Vault indexing with Markdown parser + embeddings + sqlite-vec.
- [x] Chat answers grounded in retrieved vault context with citations.
- [x] Audit journal logs index and chat events.
- [x] Web UI accepts questions and shows sources.
- [x] Vault Q&A benchmark: 5/5 correct on synthetic vault.
- [x] Phase 1 marked complete in README.

## Phase 2 exit criteria

- [x] Capability ledger with grant/revoke/stop.
- [x] Policy engine decides allowed / approval-required / blocked.
- [x] File, shell, browser skills with preview + commit pattern.
- [x] CLI commands: `grant`, `revoke`, `stop`, `do`.
- [ ] Automated policy tests pass.
- [ ] Phase 2 marked complete in README.

---

## Contributing

Phase 2 is in progress. Phase 3 (personal memory and feedback learning) begins after Phase 2 tests pass.

---

*Project ASTRO — local-first AI that you control.*
