# ASTRO Phase 2 — Permissioned Skills and OS Actions

## Goal

ASTRO can perform filesystem, shell, and browser actions only after a deterministic policy check. High-risk actions require explicit approval. Every action is logged.

## Components

| File | Purpose |
|---|---|
| `src/astro/capabilities.py` | Ledger, grants, risk levels, approval rules, shell allowlist. |
| `src/astro/skills.py` | File read/write, shell, browser fetch skills with preview/commit split. |
| `src/astro/agent.py` | Planner + executor: model proposes, policy checks, skill runs. |

## CLI usage

### Grant a capability

```bash
astro grant file_read /home/user/notes --approval always
astro grant shell /home/user --approval always
astro grant file_write /tmp --approval always
astro grant browser_fetch '*' --approval rule
```

### Ask ASTRO to do something

```bash
astro do "list files in /home/user/notes"
```

If the action is high-risk, it shows a preview and asks you to run again with `--approve`.

### Approve and run

```bash
astro do "create a file /tmp/hello.txt with content hi" --approve
```

### Revoke / emergency stop

```bash
astro revoke file_read /home/user/notes
astro stop
```

## Safety rules

- No tool runs without a grant.
- High-risk tools (`file_write`, `shell`, `browser_research`, `training_export`, `memory_write`) always require approval.
- Shell commands must match a safe allowlist: `ls`, `cat`, `pwd`, `echo`, `head`, `tail`, `find`, `grep`.
- Browser fetch uses a URL allowlist; `*` grant still only permits allowlisted hosts.
- `astro stop` revokes all skill grants instantly.

## Exit criteria

- [x] Capability ledger with grant/revoke/stop.
- [x] Policy engine decides allowed / approval-required / blocked.
- [x] File, shell, browser skills with preview + commit pattern.
- [x] CLI commands: `grant`, `revoke`, `stop`, `do`.
- [ ] Automated policy tests pass.
- [ ] Phase 2 marked complete in root README.

## Notes

- The ledger is in-memory for now; persistence is a Phase 3/4 task.
- The planner uses the local Ollama model and emits JSON tool plans.
