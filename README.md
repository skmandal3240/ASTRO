# ASTRO AI

**ASTRO AI — a local-first, permissioned personal AI platform.**

ASTRO runs a small language model on your device, reads only the files you explicitly allow, and only performs actions you preview and approve. It is built for people who want an AI that knows their notes without leaking private data to the cloud.

Repository: `https://github.com/skmandal3240/ASTRO`

---

## Build status

| Phase | Goal | Status | Key artifacts |
|---|---|---|---|
| 0 | Product, policy, and evaluation | Complete | `docs/phase0/CAPABILITIES.md`, `docs/phase0/THREAT_MODEL.md`, `docs/phase0/EVAL.md`, `eval/eval.py` |
| 1 | Local assistant MVP (daemon + vault chat) | **In progress** | `src/astro/`, `pyproject.toml`, `docs/phase1/README.md` |
| 2 | Permissioned skills and OS actions | Not started | — |
| 3 | Personal memory and feedback learning | Not started | — |
| 4 | Model improvement and release engineering | Not started | — |

Current phase: **Phase 1**.

---

## What ASTRO does

1. **Reads your local vault.** Select an Obsidian-style Markdown folder. ASTRO indexes it locally and answers questions with file/line citations.
2. **Proposes actions safely.** For file edits, shell commands, or network calls, ASTRO shows a preview first and waits for your approval.
3. **Learns only with consent.** Corrections become explicit memories; offline training happens only when you export a reviewed dataset and start a job.
4. **Keeps an audit journal.** Every proposed, approved, and executed action is logged locally.

---

## Repository layout

```
ASTRO/
├── src/astro/
│   ├── __init__.py
│   ├── audit.py          # Audit journal
│   ├── chat.py           # Ollama-backed RAG chat
│   ├── cli.py            # astro index / ask / serve
│   ├── config.py         # Defaults
│   ├── index.py          # sqlite-vec + lexical index
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
│   └── phase1/           # Phase 1 docs
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

### Run Phase 0 evaluation harness

```bash
python eval/eval.py --all
```

---

## Phase 1 exit criteria

- [x] Vault indexing with Markdown parser + embeddings + sqlite-vec.
- [x] Chat answers grounded in retrieved vault context with citations.
- [x] Audit journal logs index and chat events.
- [x] Web UI accepts questions and shows sources.
- [ ] Evaluation on real vault Q&A benchmark meets 50%+ accuracy.
- [ ] Phase 1 marked complete in README.

---

## Contributing

Phase 1 is in progress. Phase 2 (permissioned skills) begins after the Phase 1 benchmark gate is met.

---

*Project ASTRO — local-first AI that you control.*
