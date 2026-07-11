# ASTRO AI architecture

## System boundary

ASTRO is an **agent platform**, not a model with unrestricted OS access. The model proposes structured intents; a deterministic controller validates permission, risk, schema, and user approval before a skill runs.

```
User → ASTRO UI → Planner/model → Policy engine → Skill sandbox → OS / local data / network
                  ↘ Local memory + retrieval ↗          ↘ Audit journal
```

## Core components

- **Model runtime:** local 1B-class model behind a stable inference API. Begin with evaluated MiniCPM-compatible checkpoints; support quantized local formats.
- **Planner:** converts user requests into typed proposed actions and cites retrieval sources.
- **Policy engine:** evaluates capability grants, destination, path scope, risk level, rate limits, and approval requirements. It is not controlled by model text.
- **Skill host:** executes signed/allowlisted skills in a restricted process or container. Skills expose narrow JSON schemas and never receive blanket OS credentials.
- **Knowledge service:** Markdown-vault importer, SQLite metadata store, embedding index, lexical index, and source attribution. The original vault stays canonical.
- **Memory service:** explicit user-confirmed preferences/facts with TTL, provenance, export/delete, and no automatic promotion from chat.
- **Audit service:** append-only local records for proposed/approved/executed actions and model/version metadata.
- **UI:** consent prompts, action previews/diffs, capability management, vault selection, memory controls, and a “stop all skills” control.

## Knowledge lifecycle

1. User selects a local folder/vault.
2. ASTRO indexes only permitted files and records content hashes and provenance.
3. Retrieval produces passages and citations for the model context.
4. The model’s answer is grounded in retrieved context.
5. User feedback updates a reviewable memory or index rule.
6. Only an explicit offline training job may produce an adapter/checkpoint.

## OS and network safety model

- No tool is available unless a capability grant exists.
- Reads are scoped to declared paths; writes use temp files plus preview/diff.
- Shell actions run with argument allowlists, working-directory scopes, and time/resource limits.
- Network access uses an allowlist and shows destination + payload preview before sending.
- Secrets are never placed in model context or persisted in chat/audit logs.
- External services are opt-in; local mode must remain functional without them.

## Obsidian compatibility

Treat an Obsidian vault as user-owned Markdown rather than a proprietary memory format. Preserve Markdown, frontmatter, tags, wikilinks, attachments, and folder structure; store indexes and ASTRO metadata separately so the vault remains usable without ASTRO.
