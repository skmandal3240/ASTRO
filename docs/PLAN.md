# ASTRO AI — Product Requirements Document

## 1. Executive Summary

ASTRO AI is a **local-first, permissioned personal AI platform**. It runs a small language model on the user's own device, lets the model read only the files and notes the user explicitly allows, and only performs actions the user previews and approves. ASTRO is built for people who want an AI assistant that knows their notes, calendar, and files — but never silently uploads data, never trains on private content, and never runs tools without consent.

Target first release: a desktop daemon + minimal chat UI that can answer questions from an Obsidian-style Markdown vault with file/line citations, then gradually add safe file/browser/shell actions.

---

## 2. Problem Statement

### Who has this problem?
- Knowledge workers, students, researchers, small-business operators, and privacy-conscious users who keep local notes, documents, and calendars.
- Users of cloud AI assistants who worry about leaking notes, files, or confidential content to third-party servers.

### What is the problem?
Current AI assistants are either cloud-only (data leaves the device) or local tools that lack retrieval, tool use, and memory in one safe system. Users must choose between:
- **Powerful but leaky** — cloud assistants that read everything on a server.
- **Private but weak** — local models that cannot read the user's vault or perform useful actions.

### Why is it painful?
- Users cannot ask natural-language questions across their own notes without uploading them.
- Local tools that do read notes usually provide no source citations, so answers cannot be trusted.
- Tools that can edit files or run commands often do so without clear previews or revocable permissions.
- Fine-tuning or "memory" features are opaque: users do not know what the model learned, when, or how to delete it.

### Evidence / market signal
- Strong demand for on-device AI (Apple Intelligence, Windows Copilot+, local LLM runners like Ollama/LM Studio).
- Obsidian has 50+ million users who manage knowledge as local Markdown and want plugins for AI that respect file ownership.
- Enterprise and regulated users require audit trails and consent for any automated action.

---

## 3. Target Users & Personas

### Primary: Private Knowledge Worker Priya
- **Role:** Consultant, researcher, or writer.
- **Tech level:** Comfortable with Obsidian or Markdown notes; not a programmer.
- **Goal:** Find insights across years of notes and files without uploading them.
- **Pain:** Cloud search feels creepy; local search is too slow or too literal.
- **ASTRO use:** Ask "What did I write last year about pricing models?" and get cited answers from her vault.

### Secondary: Cautious Developer Dev
- **Role:** Indie developer or technical founder.
- **Tech level:** Uses terminal and local models daily.
- **Goal:** Automate small local tasks (rename files, run tests, summarize documentation) with guardrails.
- **Pain:** Existing agents run commands blindly or require broad API keys.
- **ASTRO use:** Approve file edits and shell commands through a preview/diff UI, with full audit log.

### Tertiary: Compliance-Minded User Clara
- **Role:** Lawyer, accountant, healthcare worker, journalist.
- **Goal:** Use AI on confidential documents with deterministic safety rules.
- **Pain:** Need proof that data never left the device and every action is logged.
- **ASTRO use:** Operate in local-only mode, review the audit journal, and revoke any capability instantly.

---

## 4. Strategic Context

### Business / mission goals
- Build a category-defining **trusted local agent** rather than another chatbot.
- Default to privacy as a competitive moat; only ask for remote access when the user explicitly enables it.
- Establish an open core with clear safety documentation and reproducible evaluation reports.

### Why now?
- 1B-class models are now small enough to run well on consumer laptops.
- Users are actively looking for alternatives after repeated cloud AI privacy scares.
- Local-first tools (Obsidian, Logseq, Zettelkasten) have created a large audience that already owns its knowledge in Markdown.

### Competitive landscape
| Product | Strength | Weakness vs. ASTRO |
|---|---|---|
| ChatGPT / Claude | Powerful, cloud models | Uploads user data; opaque memory |
| Ollama / LM Studio | Easy local inference | No vault integration, no tool safety |
| Obsidian AI plugins | Reads local notes | Plugin-specific, limited tool policy |
| Obscura (existing Saurabh project) | Headless browser/scraping agent | Different scope; ASTRO is personal knowledge + action platform |

### Positioning
ASTRO is not a model. It is a **policy-first agent runtime** wrapped around a small local model, designed for people who value custody of their data.

---

## 5. Solution Overview

### What ASTRO does
ASTRO connects a local small language model to the user's own files, notes, and tools through a deterministic policy layer. It answers questions, performs small tasks, and remembers facts only when the user confirms each step.

### Core user flows

#### Flow A — Ask your vault
1. User selects a local Markdown folder (Obsidian vault or any directory).
2. ASTRO indexes the allowed files locally with hashes, embeddings, and lexical index.
3. User asks a question in the chat UI.
4. ASTRO retrieves relevant passages and cites file path + line range.
5. The local model answers using only retrieved context.
6. User rates the answer; corrections can be saved as explicit memory.

#### Flow B — Do something safely
1. User asks ASTRO to perform an action, e.g., "Rename all .jpeg files in Downloads to .jpg."
2. Planner proposes a typed action with JSON schema: tool, parameters, risk level.
3. Policy engine checks grants, path scope, and risk.
4. ASTRO shows a preview/diff or destination/payload preview.
5. User approves, denies, or edits the action.
6. Skill sandbox executes; result is shown and logged in the audit journal.

#### Flow C — Learn from feedback (opt-in)
1. User gives a correction or repeated preference.
2. ASTRO offers to save it as explicit memory with source, scope, and expiry.
3. Optionally, user can export reviewed, redacted examples into a local training dataset.
4. User chooses when to run an offline adapter training job.
5. New adapter is versioned and can be A/B tested or rolled back.

### Key capabilities
| Capability | Description |
|---|---|
| Local chat | Small model inference on-device; optional remote provider toggle. |
| Vault retrieval | Markdown + frontmatter + wikilinks + tags; cited answers. |
| File skill | Read scoped folders; write only via temp + preview + approval. |
| Shell skill | Run commands with allowlist, working-dir scope, timeout, and approval. |
| Browser skill | Fetch pages in sandbox; network allowlist + payload preview. |
| Memory | Explicit, user-confirmed facts with source, expiry, and delete/export. |
| Audit journal | Append-only local log of proposed/approved/executed actions. |
| Capability ledger | Per-tool grants, scopes, and revocations. |
| Offline training | Optional LoRA adapter training from reviewed, redacted data. |

---

## 6. Success Metrics

### Primary metric
**Vault-grounded answer accuracy** — percentage of user questions answered correctly with correct file/line citations.
- Target for MVP: ≥ 80% on a benchmark of 50 common vault questions.

### Secondary metrics
- **Local-only uptime:** user can complete a chat session without any network call by default.
- **Approval coverage:** 100% of write/delete/shell/network actions show a preview before execution.
- **Citation precision:** ≥ 90% of generated answers include at least one verifiable source link.
- **Index latency:** full reindex of a 5,000-note vault in under 5 minutes on a mid-range laptop.
- **User trust signal:** explicit-memory edits / audit-journal views per active week.

### Guardrail metrics
- No silent uploads or telemetry by default.
- No fine-tuning job runs without user-initiated export + job approval.
- Capability revocation takes effect immediately across all services.

---

## 7. Phased Build Plan

### Phase 0 — Product, policy, and evaluation (weeks 1–2)
- Define supported OS/hardware targets (first target: Linux daemon; later macOS/Windows).
- Finalize permission objects, risk levels, encrypted local storage, and emergency stop/revoke flows.
- Build evaluation harness: retrieval, note-grounded Q&A, tool selection, safe refusal, approval behavior, latency.
- Select baseline model (MiniCPM5-1B / Gemma 3 1B / LFM 2.5 1.2B) and inference runtime.
- **Exit:** reproducible local evaluation report + written threat model.

### Phase 1 — Local assistant MVP (weeks 3–6)
- Desktop daemon with local inference API and minimal chat UI.
- Obsidian/Markdown vault connector: ingestion, incremental indexing, links/tags/frontmatter, citations, delete/reindex.
- Local embeddings + vector search + keyword search; no use of user data as training data.
- Read-only filesystem skill with provenance.
- Audit log for all model/tool interactions.
- **Exit:** ASTRO answers vault questions with citations; all data stays local.

### Phase 2 — Permissioned skills and OS actions (weeks 7–10)
- Typed tool protocol with JSON schemas and policy enforcement outside the model.
- Add skills in order of risk: filesystem read → local search → file write → browser research → command execution → optional integrations.
- Previews/approvals for writes, deletes, commands, network requests, external messages.
- Capability ledger and audit viewer UI.
- **Exit:** every state-changing action is attributable, previewable, and revocable.

### Phase 3 — Personal memory and feedback learning (weeks 11–14)
- Explicit memories: source, confidence, scope, TTL, provenance, export/delete.
- User corrections as structured feedback; retrieval/memory updated first.
- Local dataset curator: redact secrets, require review, sign and version datasets.
- Offline adapter training (LoRA) with rollback path.
- **Exit:** user inspects, approves, deletes, exports, and rolls back every learned artifact.

### Phase 4 — Model improvement and release engineering (weeks 15+)
- Use benchmark failures and consented, sanitized feedback for targeted post-training.
- Compare base, adapter, and candidate checkpoints against safety + task gates.
- Quantize/package for target hardware; publish model cards, eval reports, licenses.
- CI for policy tests, prompt-injection tests, tool-contract tests, performance regressions.
- **Exit:** versioned release meets latency, accuracy, safety, reproducibility gates.

---

## 8. Out of Scope

| Item | Why not now |
|---|---|
| Mobile apps | Desktop-first MVP; mobile is Phase 4+. |
| Native cloud sync | ASTRO may use optional remote model API, but never auto-sync user vault. |
| Real-time multi-user collaboration | Single-user personal agent first. |
| General-purpose autonomous agent | No always-on background task execution without explicit rule + approval. |
| Full browser automation with login credentials | Browser skill is fetch-only/read-only in MVP; credential handling later with vault. |
| Medical/legal compliance certification | Architecture supports it, but formal certification is a future step. |

---

## 9. Dependencies & Risks

### Technical dependencies
- Local inference runtime: `llama.cpp`, `transformers`, or `ollama` bindings.
- Embedding model: small sentence-transformer compatible with CPU.
- Vector store: SQLite + `sqlite-vec` or FAISS.
- UI: web-based local UI (Tauri/Electron or simple browser app served by daemon).

### External dependencies
- Optional remote model providers are opt-in only.
- No mandatory third-party service for core local mode.

### Risks and mitigations
| Risk | Mitigation |
|---|---|
| Small model quality is too low | Set baseline eval gate; only train adapters if gap is measurable. |
| Policy bypass via prompt injection | Run prompt-injection test suite; never let model directly invoke tools. |
| Path traversal or file overwrites | Strict path scoping, temp writes, preview/diff before final move. |
| Secret leakage into logs/context | Redaction pass on memory/audit; secrets never in model context. |
| User confusion about local vs. remote | Clear mode indicator in UI; network calls require explicit grant. |

---

## 10. Open Questions

1. First baseline model: MiniCPM5-1B, Gemma 3 1B, or LiquidAI LFM 2.5 1.2B? → Decide after Phase 0 eval.
2. UI framework: Tauri (Rust) or lightweight web UI served by daemon? → Decide based on team expertise.
3. Packaging: pip installable Python daemon, or standalone binary? → Decide before Phase 1 end.
4. License: Apache-2.0 core + safety artifacts, or copyleft? → Decide before public release.

---

*Last updated: 2026-07-12*
