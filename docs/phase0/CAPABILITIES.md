# ASTRO AI Capability and Permission Model

## Core rule

ASTRO can only use a capability if the user has granted it, and every grant has a **scope** and a **risk level**. High-risk actions require a preview and approval. The model proposes; the policy engine decides.

## Capability categories

| Category | Examples | Default state |
|---|---|---|
| `chat` | Local model inference, optional remote model | Enabled for local model only. Remote provider is opt-in. |
| `vault_read` | Read Markdown files, frontmatter, tags, links | Disabled until user selects a vault/folder. |
| `file_read` | Read files outside the vault, scoped by path | Disabled; granted per folder. |
| `file_write` | Create/edit/rename files in scoped paths | Disabled; high-risk; requires preview + approval. |
| `shell` | Run shell commands with allowlist and timeout | Disabled; high-risk; requires preview + approval. |
| `browser_fetch` | Fetch a web page by URL | Disabled; medium-risk; network allowlist applies. |
| `browser_research` | Search or browse across pages | Disabled; high-risk due to data exfiltration potential. |
| `memory_write` | Save an explicit user-confirmed fact | Disabled; user must confirm each memory. |
| `training_export` | Export reviewed examples for offline training | Disabled; requires explicit dataset review. |

## Permission object

Each grant is stored as a JSON object:

```json
{
  "capability": "file_write",
  "scope": "/home/user/projects/astro-notes",
  "risk": "high",
  "approval": "always",
  "expires_at": null,
  "created_at": "2026-07-12T00:00:00Z",
  "source": "user_prompt"
}
```

Fields:
- `capability`: one of the categories above.
- `scope`: folder path, URL pattern, or wildcard rule.
- `risk`: `low`, `medium`, `high`.
- `approval`: `always`, `rule`, or `never`. `rule` means an allowlist of safe patterns.
- `expires_at`: optional ISO timestamp; if null, grant persists until revoked.
- `created_at`: timestamp.
- `source`: how the grant was created (`user_prompt`, `ui_toggle`, `rule`).

## Risk levels and approval rules

| Risk | Approval required | Examples |
|---|---|---|
| Low | No; logged | Local chat, reading an allowed vault file. |
| Medium | Preview only if auto-allow rule missing | Browser fetch to an allowlisted domain. |
| High | Always preview + explicit approval | File write, shell command, network POST, message send. |

## Emergency controls

- **Stop all skills:** a UI control that immediately revokes all active `shell`, `browser_*`, and `file_write` grants.
- **Revoke by capability:** one-click removal of any grant.
- **Audit journal:** every proposed/approved/denied action is logged locally.

## Non-goals

- ASTRO does not support blanket "full disk access" grants.
- ASTRO does not support silent, always-on background actions without a scoped automation rule.
- The model cannot create or extend its own capabilities.
