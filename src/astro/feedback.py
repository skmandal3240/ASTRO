"""
Feedback loop for ASTRO.

Stores user ratings and corrections on answers. Used by the curator to build
reviewed training datasets.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from astro.audit import log
from astro.config import DEFAULT_DATA_DIR


@dataclass
class Feedback:
    id: str
    question: str
    answer: str
    rating: str  # positive | negative | neutral
    correction: Optional[str]
    sources: List[str]
    model: str
    created_at: str


class FeedbackStore:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or DEFAULT_DATA_DIR / "astro.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._migrate()

    def _migrate(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                rating TEXT NOT NULL,
                correction TEXT,
                sources TEXT,
                model TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def record(
        self,
        question: str,
        answer: str,
        rating: str,
        correction: Optional[str] = None,
        sources: Optional[List[str]] = None,
        model: str = "",
    ) -> Feedback:
        fb_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """
            INSERT INTO feedback (id, question, answer, rating, correction, sources, model, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (fb_id, question, answer, rating, correction, json.dumps(sources or []), model, now),
        )
        self._conn.commit()
        log("feedback", {"id": fb_id, "rating": rating, "model": model})
        return Feedback(
            id=fb_id,
            question=question,
            answer=answer,
            rating=rating,
            correction=correction,
            sources=sources or [],
            model=model,
            created_at=now,
        )

    def list(self, rating: Optional[str] = None, limit: int = 100) -> List[Feedback]:
        clauses = []
        params: List[object] = []
        if rating:
            clauses.append("rating = ?")
            params.append(rating)
        where = "WHERE " + " AND ".join(clauses) if clauses else ""
        rows = self._conn.execute(
            f"SELECT * FROM feedback {where} ORDER BY created_at DESC LIMIT ?", (*params, limit)
        ).fetchall()
        return [self._row_to_feedback(r) for r in rows]

    def delete(self, fb_id: str) -> bool:
        cur = self._conn.execute("DELETE FROM feedback WHERE id = ?", (fb_id,))
        self._conn.commit()
        return cur.rowcount > 0

    def _row_to_feedback(self, row) -> Feedback:
        return Feedback(
            id=row[0],
            question=row[1],
            answer=row[2],
            rating=row[3],
            correction=row[4],
            sources=json.loads(row[5] or "[]"),
            model=row[6] or "",
            created_at=row[7],
        )

    def close(self) -> None:
        self._conn.close()
