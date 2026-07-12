"""
ASTRO audit journal — append-only NDJSON log of actions.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from astro.config import DEFAULT_AUDIT_LOG


def log(event_type: str, payload: dict[str, Any], path: Path | None = None) -> None:
    """Append one audit record."""
    path = path or DEFAULT_AUDIT_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        "payload": payload,
    }
    # ponytail: atomic append is enough; rotate when log grows >100 MB.
    line = json.dumps(record, ensure_ascii=False, default=str) + "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)
