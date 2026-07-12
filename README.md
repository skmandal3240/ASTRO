# ASTRO AI

**ASTRO AI — a local-first, permissioned personal AI platform.**

ASTRO runs a small language model on your device, reads only the files you explicitly allow, and only performs actions you preview and approve. It is built for people who want an AI that knows their notes without leaking private data to the cloud.

Repository: `https://github.com/skmandal3240/ASTRO`

---

## Build status

| Phase | Goal | Status | Key artifacts |
|---|---|---|---|
| 0 | Product, policy, and evaluation | **In progress** | `docs/phase0/CAPABILITIES.md`, `docs/phase0/THREAT_MODEL.md`, `docs/phase0/EVAL.md`, `eval/eval.py` |
| 1 | Local assistant MVP (daemon + vault chat) | Not started | — |
| 2 | Permissioned skills and OS actions | Not started | — |
| 3 | Personal memory and feedback learning | Not started | — |
| 4 | Model improvement and release engineering | Not started | — |

Current phase: **Phase 0**.

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
├── docs/
│   ├── PRD.md                  # Full product requirements
│   ├── PLAN.md                 # Living build plan (same as PRD)
│   ├── ARCHITECTURE.md         # System architecture
│   ├── SAFETY.md               # Non-negotiable safety rules
│   └── phase0/
│       ├── README.md           # Phase 0 overview
│       ├── CAPABILITIES.md     # Permission model
│       ├── THREAT_MODEL.md     # Threats and mitigations
│       └── EVAL.md             # Evaluation plan
├── eval/
│   └── eval.py                 # Phase 0 evaluation harness
└── README.md                   # This file
```

---

## Quick start

### Run Phase 0 evaluation harness

```bash
# Clone the repo
git clone https://github.com/skmandal3240/ASTRO.git
cd ASTRO

# Run all benchmark categories against the stub model
python eval/eval.py --all

# Run a single category
python eval/eval.py --category retrieval
```

The harness currently uses a stub model. When a real local model backend is added, only the `_ask_model()` function in `eval/eval.py` needs to change.

---

## Phase 0 exit criteria

- [x] Capability and permission model written.
- [x] Threat model and acceptance tests defined.
- [x] Evaluation plan and baseline model candidates documented.
- [x] Minimal runnable evaluation harness with benchmark fixtures.
- [ ] Select baseline model and produce reproducible score report.
- [ ] Mark Phase 0 as complete in README.

---

## Contributing

This is an early-stage project. Phase 1 work will begin after Phase 0 exit criteria are met. Open questions are listed in `docs/PRD.md`.

---

*Project ASTRO — local-first AI that you control.*
