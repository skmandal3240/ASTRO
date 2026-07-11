# ASTRO AI build plan

## Mission

Build a local-first personal AI platform named **ASTRO AI**. It should reason and act through explicitly granted tools, retrieve from user-controlled local knowledge, and improve from reviewed feedback—without silently training on, uploading, or exposing private user data.

## Product principles

1. **Local by default.** Model inference, embeddings, index, memory, logs, and files stay on the device unless the user deliberately enables a remote provider.
2. **Retrieval before training.** New notes and files improve answers through indexed retrieval immediately. Fine-tuning is an opt-in, versioned offline workflow, not continuous hidden learning.
3. **Least privilege.** Every capability—files, shell, browser, network, calendar, etc.—is separately scoped and revocable.
4. **Plan → preview → execute.** The model may propose actions, but side-effecting tool calls require a policy check and, by default, user approval.
5. **Portable knowledge.** Use a Markdown-first workspace compatible with an Obsidian-style vault: user-owned files, links, metadata, and a local database/index.
6. **Auditable behavior.** Keep a local action journal with tool inputs, outputs, permission decisions, and model/version identifiers.

## Reference baseline

Start by evaluating MiniCPM5-1B as a baseline rather than assuming a model fork is required. Its repository provides a compact local model, fine-tuning/deployment material, tool-use orientation, and a three-stage training recipe. ASTRO’s first differentiator is the trusted local-agent system around the model, then targeted post-training after evaluation proves the gap.

## Phases and exit criteria

### Phase 0 — Product, policy, and evaluation (weeks 1–2)

- Specify supported operating systems and local hardware targets.
- Define permission objects, risk levels, encrypted local storage, and emergency stop/revoke flows.
- Create a benchmark suite: file retrieval, note-grounded Q&A, tool selection, safe refusal, approval behavior, and latency.
- Select baseline checkpoint(s) and an inference runtime.

**Exit:** a reproducible local evaluation report and written threat model.

### Phase 1 — Local assistant MVP (weeks 3–6)

- Ship a desktop daemon/API with local inference and a minimal chat UI.
- Implement an Obsidian-vault connector: Markdown ingestion, incremental indexing, links/tags/frontmatter, citations, and delete/reindex controls.
- Add local embeddings/vector search plus keyword search; do not use user data as training data.
- Provide read-only file and vault skills with provenance shown in answers.

**Exit:** ASTRO can answer questions from a selected vault with file/line citations while all data remains local.

### Phase 2 — Permissioned skills and OS actions (weeks 7–10)

- Build a typed tool protocol with JSON schemas, tool sandboxing, and policy enforcement outside the model.
- Add skills in increasing-risk order: filesystem read, local search, file write, browser research, command execution, and optional integrations.
- Require previews/approval for writes, deletes, commands, network requests, and external messages.
- Add a capability ledger, action replay fixtures, and local audit viewer.

**Exit:** every state-changing action is attributable, previewable, and revocable.

### Phase 3 — Personal memory and feedback learning (weeks 11–14)

- Add explicit memories with source, confidence, scope, retention, and user controls.
- Support user corrections as structured feedback; update retrieval/memory first.
- Build a local dataset curator that redacts secrets, requires review, and produces signed, versioned training datasets.
- Train/evaluate small adapters (for example LoRA) offline; preserve a rollback path to the base model.

**Exit:** a user can inspect, approve, delete, export, and roll back every learned artifact.

### Phase 4 — Model improvement and release engineering (weeks 15+)

- Use benchmark failures and consented, sanitized feedback to target post-training data.
- Compare base, adapter, and candidate checkpoints against safety and task gates.
- Quantize/package for target hardware; publish reproducible model cards, evaluation reports, and licenses.
- Add CI for policy tests, prompt-injection tests, tool-contract tests, and performance regressions.

**Exit:** a versioned release meets defined local latency, accuracy, safety, and reproducibility gates.

## Immediate repository milestones

1. Create the product specification and threat model.
2. Build the local Markdown-vault indexer and cited retrieval CLI.
3. Define the typed skill protocol and policy engine.
4. Add a read-only filesystem skill and audit log.
5. Establish baseline MiniCPM evaluation before any fine-tuning.
