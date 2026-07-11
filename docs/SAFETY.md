# ASTRO AI safety and privacy policy

## Non-negotiable rules

- ASTRO never silently uploads user files, notes, telemetry, prompts, embeddings, or training data.
- ASTRO never silently fine-tunes or changes its own model from user data.
- ASTRO never receives unrestricted filesystem, shell, browser, or network access.
- State-changing actions require a user-visible preview and approval unless the user creates a narrowly scoped automation rule.
- Permissions are explicit, least-privilege, time-bounded where possible, and revocable.

## Learning is three separate mechanisms

| Mechanism | Default | User control |
| --- | --- | --- |
| Retrieval index | Opt-in per folder/vault | Reindex, inspect sources, delete |
| Explicit memory | Off until confirmed | View, edit, expire, export, delete |
| Fine-tuning/adapters | Off | Review dataset, choose job, evaluate, version, roll back |

## Threats to test

- Prompt injection in local notes, files, web pages, and tool output.
- Path traversal, symlink escapes, destructive commands, and unintended file disclosure.
- Cross-origin/network exfiltration and secret leakage.
- Misleading or ungrounded retrieval.
- Unauthorized persistence, training, or capability escalation.

## Release gate

No release passes until it has automated tests for policy enforcement, prompt-injection resistance, source attribution, delete/revoke behavior, and safe handling of tool failures.
