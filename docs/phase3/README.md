# ASTRO Phase 3 — Personal Memory and Feedback Learning

## Goal

ASTRO remembers facts and preferences only when the user explicitly confirms, stores them locally with provenance, and supports an opt-in offline training loop.

## Components

| File | Purpose |
|---|---|
| `src/astro/memory.py` | Explicit memory store: CRUD, search, expiry, export/redaction |
| `src/astro/feedback.py` | Thumbs up/down and correction capture from chat |
| `src/astro/curator.py` | Build, review, version, and export training datasets |
| `src/astro/trainer.py` | Offline LoRA adapter training using `peft`/`transformers` |
| `src/astro/model_registry.py` | List adapters and switch active adapter |
| `src/astro/chat.py` | Inject relevant memories into prompts; offer to save facts |

## Data Model

```python
@dataclass
class Memory:
    id: str                # uuid4
    kind: str              # "fact" | "preference" | "correction"
    content: str           # plaintext statement
    source: str            # "user" | "vault:<path>" | "chat:<session_id>"
    scope: str | None      # e.g. "work", "personal", "all"
    confidence: float      # 0.0 - 1.0
    expires_at: str | None # ISO timestamp or None
    created_at: str
    updated_at: str
```

## User Flows

1. **Save a fact**: user says "Remember my dentist is Dr. Rao"; ASTRO previews, user confirms, memory stored.
2. **Correction from chat**: ASTRO answers wrong; user corrects; ASTRO offers to save the correction.
3. **Feedback on answers**: 👍 / 👎 stored with question, answer, sources, model.
4. **Offline training**: `astro dataset build` → review → `astro train --name v1` → `astro model activate v1`; rollback with `astro model activate base`.

## CLI

```
astro memory add "<text>" --kind fact --scope personal --ttl 1y
astro memory list [--scope personal] [--search "dentist"]
astro memory edit <id> "<new text>"
astro memory delete <id>
astro memory export --format jsonl --redacted > memories.jsonl
astro feedback list
astro dataset build --name v1 --min-rating positive
astro dataset review <id>
astro train --dataset <id> --name v1 --epochs 3 --lr 1e-4
astro model list
astro model activate base|v1
```

## Safety Rules

- No memory without explicit confirmation.
- Export is opt-in and redacted by default.
- Audit log records every memory change and every training job.
- Training datasets are signed with a content hash and approval timestamp.
- Adapter rollback is one command.

## Tests

- Memory CRUD, search by embedding, expiry.
- Feedback round-trip.
- Dataset curation filters and redaction.
- Trainer writes a valid adapter directory.
- Chat injects relevant memories into prompt.

## Exit Criteria

- Save/edit/delete/search/export explicit memories.
- Chat offers to save facts/corrections and uses confirmed memories.
- Collect feedback on answers.
- Train and activate a local LoRA adapter; rollback to base.
- All actions logged in audit journal.
