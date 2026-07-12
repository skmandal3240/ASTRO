# ASTRO AI — Build Plan

This is the living build plan for ASTRO AI. See [`PRD.md`](./PRD.md) for the full product definition.

## Phase Status

| Phase | Goal | Status | Exit Criteria |
|---|-:|---|---|
| 0 | Policy, threat model, evaluation | ✅ Complete | Eval harness runnable, threat model written, capability model defined |
| 1 | Local assistant MVP | ✅ Complete | Vault indexing + chat + web UI + citations + audit journal |
| 2 | Permissioned skills and OS actions | ✅ Complete | Scoped grants, file/shell/browser skills, policy engine, CLI commands |
| 3 | Personal memory and feedback learning | 🚧 Planning | Explicit memory, preference feedback, offline training pipeline |
| 4 | Model improvement and release engineering | ⏳ Future | Adapter training, A/B gates, packaging, CI |

## Phase 3 — Personal Memory and Feedback Learning

### Goal

ASTRO remembers facts and preferences only when the user explicitly confirms, stores them locally with provenance, and supports an opt-in offline training loop.

### Scope

**In scope:**
- Explicit memory store: facts, preferences, corrections.
- Memory provenance: source, confidence, scope, TTL, created/updated timestamps.
- Memory operations: add, edit, delete, list, export, redact.
- Chat integration: offer to save a correction or fact after an answer.
- Preference feedback: thumbs up/down on answers; stored as structured feedback.
- Offline dataset curation: collect reviewed, redacted examples; sign and version.
- Offline LoRA adapter training on user-approved local dataset.
- Rollback: switch between base model and trained adapters.

**Out of scope for Phase 3:**
- Silent/implicit memory (anything learned without user confirmation).
- Automatic periodic fine-tuning.
- Cloud training or data upload.
- Long-term planning memory across sessions without explicit save.

### Data Model

```python
@dataclass
class Memory:
    id: str                # uuid
    kind: str              # "fact" | "preference" | "correction"
    content: str           # plaintext statement
    source: str            # "user" | "vault:<path>" | "chat:<session_id>"
    scope: str | None      # e.g. "work", "family", "all"
    confidence: float      # 0.0 - 1.0
    expires_at: str | None # ISO timestamp or None
    created_at: str
    updated_at: str
```

### Components

| Module | Purpose |
|---|---|
| `src/astro/memory.py` | CRUD store backed by SQLite + JSON dump; search by embedding match |
| `src/astro/feedback.py` | Thumbs + correction capture; links to chat session and sources |
| `src/astro/curator.py` | Build, redact, review, version, and export training datasets |
| `src/astro/trainer.py` | Offline LoRA adapter training using `peft` + `trl` or direct `transformers` |
| `src/astro/model_registry.py` | List base model and adapters; activate/rollback adapter |
| `src/astro/chat.py` | Inject relevant memories into context; ask to save facts |

### User Flows

**Flow 1 — Save a fact**
1. User says: "Remember that my dentist is Dr. Rao."
2. ASTRO creates a preview memory: `fact | "dentist: Dr. Rao" | source=user | scope=personal`.
3. User confirms.
4. ASTRO saves to local SQLite + audit log.

**Flow 2 — Correction from chat**
1. ASTRO answers: "The deadline is July 17."
2. User replies: "Wrong, it's July 24."
3. ASTRO offers a correction memory; user approves.
4. Future answers about deadlines use the corrected fact.

**Flow 3 — Feedback on answers**
1. User clicks 👍 or 👎 on an answer.
2. Feedback is stored with question, answer, sources, model, timestamp.
3. Weekly summary shows which questions/models got the most feedback.

**Flow 4 — Offline training**
1. User runs `astro dataset build --min-rating positive`.
2. Curator loads thumbs-up examples + explicit memories; redacts secrets.
3. User reviews dataset in a generated Markdown report.
4. User runs `astro train --dataset <id> --name v1`.
5. Trainer produces an adapter saved to `~/.astro/adapters/<name>/`.
6. User runs `astro model activate <name>`; rollback with `astro model activate base`.

### CLI Additions

```
astro memory add "<text>" --kind fact --scope personal --ttl 1y
astro memory list [--scope personal] [--search "dentist"]
astro memory edit <id> "<new text>"
astro memory delete <id>
astro memory export --format jsonl --redacted > memories.jsonl
astro feedback list
astro dataset build --name v1 --min-rating positive
astro dataset review <id>            # opens report in browser/terminal
astro train --dataset <id> --name v1 --epochs 3 --lr 1e-4
astro model list
astro model activate base|v1
```

### Safety Requirements

- No memory is saved without explicit user confirmation.
- All memories are stored locally; export is opt-in and redacted by default.
- Audit log records every create/update/delete of memory and every training job.
- Training datasets are signed with a content hash and user approval timestamp.
- Adapter rollback is one command.

### Tests

- Unit tests for memory CRUD, search, expiry, redaction.
- Feedback collection round-trip.
- Dataset curation filters and redaction.
- Trainer produces a valid adapter directory.
- Chat integration: memory appears in context after save.

### Exit Criteria

- User can save, edit, delete, search, and export explicit memories.
- Chat offers to save facts/corrections and uses confirmed memories in context.
- Feedback loop collects ratings and corrections.
- Offline LoRA training can produce and activate an adapter.
- Rollback to base model works in one command.

*Last updated: 2026-07-12*
