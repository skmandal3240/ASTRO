"""
Capability ledger and policy engine.

- ponytail: in-memory ledger by default; future persistor one file away.
- No single-use abstractions; Policy is just a function and a dataclass.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List

from astro.audit import log
from astro.config import DEFAULT_DATA_DIR

HIGH_RISK = {"file_write", "shell", "browser_research", "training_export", "memory_write"}
MEDIUM_RISK = {"browser_fetch", "file_read"}


@dataclass
class Grant:
    capability: str
    scope: str
    risk: str = ""
    approval: str = "always"
    expires_at: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "user"

    def __post_init__(self) -> None:
        if not self.risk:
            self.risk = _default_risk(self.capability)


class Ledger:
    def __init__(self, store_path: Path | None = None) -> None:
        self._store = store_path or DEFAULT_DATA_DIR / "grants.json"
        self._grants: List[Grant] = self._load()

    def _load(self) -> List[Grant]:
        if not self._store.exists():
            return []
        try:
            data = json.loads(self._store.read_text(encoding="utf-8"))
            return [Grant(**g) for g in data]
        except Exception:
            return []

    def _save(self) -> None:
        self._store.parent.mkdir(parents=True, exist_ok=True)
        self._store.write_text(json.dumps([asdict(g) for g in self._grants], indent=2), encoding="utf-8")

    def grant(self, g: Grant) -> None:
        self.revoke(g.capability, g.scope)
        self._grants.append(g)
        self._save()
        log("grant_added", {"capability": g.capability, "scope": g.scope, "risk": g.risk})

    def revoke(self, capability: str, scope: str | None = None) -> int:
        before = len(self._grants)
        self._grants = [
            g
            for g in self._grants
            if not (g.capability == capability and (scope is None or g.scope == scope))
        ]
        removed = before - len(self._grants)
        if removed:
            self._save()
            log("grant_revoked", {"capability": capability, "scope": scope, "count": removed})
        return removed

    def revoke_all(self, capability: str | None = None) -> int:
        if capability is None:
            removed = len(self._grants)
            self._grants.clear()
            self._save()
            log("all_grants_revoked", {"count": removed})
            return removed
        n = self.revoke(capability)
        if n:
            self._save()
        return n

    def list(self, capability: str | None = None) -> List[Grant]:
        if capability:
            return [g for g in self._grants if g.capability == capability]
        return list(self._grants)

    def check(self, capability: str, target: str, action: str) -> dict:
        """Return {allowed, reason, approval_required}."""
        grant = next((g for g in self._grants if g.capability == capability and _matches_scope(g.scope, target)), None)
        if not grant:
            return {"allowed": False, "reason": f"no grant for {capability}:{target}", "approval_required": False}
        if grant.approval == "never":
            return {"allowed": False, "reason": "capability blocked", "approval_required": False}
        if grant.risk == "high" or grant.approval == "always":
            return {"allowed": False, "reason": "requires user approval", "approval_required": True, "grant": grant}
        return {"allowed": True, "reason": "granted", "approval_required": False, "grant": grant}


def _matches_scope(scope: str, target: str) -> bool:
    if scope == "*":
        return True
    if scope == target:
        return True
    try:
        s = Path(scope).resolve()
        t = Path(target).resolve()
        return t == s or str(t).startswith(str(s) + "/")
    except Exception:
        return target.startswith(scope) or target == scope


class PolicyEngine:
    def __init__(self, ledger: Ledger | None = None) -> None:
        self.ledger = ledger or Ledger()

    def propose(self, capability: str, target: str, action: str, payload: Any = None) -> dict:
        """Evaluate a proposed action."""
        result = self.ledger.check(capability, target, action)
        serializable_result = {k: v for k, v in result.items() if not isinstance(v, Grant)}
        if "grant" in result:
            serializable_result["grant"] = {"capability": result["grant"].capability, "scope": result["grant"].scope, "risk": result["grant"].risk}
        log("action_proposed", {"capability": capability, "target": target, "action": action, "result": serializable_result})
        return result

    def approve(self, capability: str, target: str, action: str, payload: Any = None) -> dict:
        """User-approved execution path."""
        log("action_approved", {"capability": capability, "target": target, "action": action})
        return {"allowed": True, "reason": "user_approved"}

    def deny(self, capability: str, target: str, action: str, payload: Any = None) -> dict:
        log("action_denied", {"capability": capability, "target": target, "action": action})
        return {"allowed": False, "reason": "user_denied"}


# shell allowlist: defensive patterns for common safe commands
SAFE_SHELL_PATTERNS = [
    re.compile(r"^ls\b"),
    re.compile(r"^cat\b"),
    re.compile(r"^pwd\b"),
    re.compile(r"^echo\b"),
    re.compile(r"^head\b"),
    re.compile(r"^tail\b"),
    re.compile(r"^find\b"),
    re.compile(r"^grep\b"),
]


def shell_is_allowed(cmd: str) -> bool:
    return any(p.match(cmd.strip()) for p in SAFE_SHELL_PATTERNS)


def _default_risk(capability: str) -> str:
    if capability in HIGH_RISK:
        return "high"
    if capability in MEDIUM_RISK:
        return "medium"
    return "low"


if __name__ == "__main__":  # pragma: no cover
    l = Ledger()
    l.grant(Grant("file_read", "/tmp", approval="rule"))
    print(l.check("file_read", "/tmp/foo", "read"))
    print(_default_risk("shell"))
