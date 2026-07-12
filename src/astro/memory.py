"""
Explicit memory store for ASTRO.

- ponytail: SQLite + sentence-transformer embeddings; reuse Index's model path.
- No implicit memory: every write requires user confirmation upstream.
"""
from __future__ import annotations

import json
import re
import sqlite3
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

import sqlite_vec

from astro.audit import log
from astro.config import DEFAULT_DATA_DIR, DEFAULT_EMBED_MODEL


TTL_RE = re.compile(r"^(\d+)\s*(m|h|d|w|y|M)$")


@dataclass
class Memory:
    id: str
    kind: str  # fact | preference | correction
    content: str
    source: str
    scope: Optional[str]
    confidence: float
    expires_at: Optional[str]
    created_at: str
    updated_at: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_ttl(ttl: Optional[str]) -> Optional[str]:
    if not ttl:
        return None
    m = TTL_RE.match(ttl.strip())
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2)
    from datetime import timedelta

    delta = {
        "m": timedelta(minutes=n),
        "h": timedelta(hours=n),
        "d": timedelta(days=n),
        "w": timedelta(weeks=n),
        "M": timedelta(days=n * 30),
        "y": timedelta(days=n * 365),
    }[unit]
    return (datetime.now(timezone.utc) + delta).isoformat()


class MemoryStore:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or DEFAULT_DATA_DIR / "astro.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = self._open_db()
        self._model: Optional["SentenceTransformer"] = None

    def _open_db(self):
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        self._migrate(conn)
        return conn

    def _migrate(self, conn) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                scope TEXT,
                confidence REAL NOT NULL DEFAULT 1.0,
                expires_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        try:
            conn.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS vec_memories USING vec0(id TEXT PRIMARY KEY, embedding FLOAT[384])"
            )
        except Exception:
            pass
        conn.commit()

    @property
    def model(self) -> "SentenceTransformer":
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(DEFAULT_EMBED_MODEL)
        return self._model

    def add(
        self,
        content: str,
        kind: str = "fact",
        source: str = "user",
        scope: Optional[str] = None,
        confidence: float = 1.0,
        ttl: Optional[str] = None,
    ) -> Memory:
        mem_id = str(uuid.uuid4())
        now = _now()
        expires_at = _parse_ttl(ttl)
        emb = self._embed(content)
        self._conn.execute(
            """
            INSERT INTO memories (id, kind, content, source, scope, confidence, expires_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (mem_id, kind, content, source, scope, confidence, expires_at, now, now),
        )
        self._conn.execute(
            "INSERT OR REPLACE INTO vec_memories (id, embedding) VALUES (?, ?)",
            (mem_id, emb),
        )
        self._conn.commit()
        log("memory_add", {"id": mem_id, "kind": kind, "source": source, "scope": scope})
        return Memory(
            id=mem_id,
            kind=kind,
            content=content,
            source=source,
            scope=scope,
            confidence=confidence,
            expires_at=expires_at,
            created_at=now,
            updated_at=now,
        )

    def _embed(self, text: str) -> bytes:
        import numpy as np

        arr = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return arr.astype("float32").tobytes()

    def get(self, mem_id: str) -> Optional[Memory]:
        row = self._conn.execute("SELECT * FROM memories WHERE id = ?", (mem_id,)).fetchone()
        if not row:
            return None
        return self._row_to_memory(row)

    def list(self, kind: Optional[str] = None, scope: Optional[str] = None, limit: int = 100) -> List[Memory]:
        clauses = []
        params: List[object] = []
        if kind:
            clauses.append("kind = ?")
            params.append(kind)
        if scope:
            clauses.append("scope = ?")
            params.append(scope)
        where = "WHERE " + " AND ".join(clauses) if clauses else ""
        rows = self._conn.execute(
            f"SELECT * FROM memories {where} ORDER BY updated_at DESC LIMIT ?", (*params, limit)
        ).fetchall()
        return [self._row_to_memory(r) for r in rows]

    def search(self, query: str, top_k: int = 5) -> List[Memory]:
        conn = self._open_db()
        try:
            emb = self._embed(query)
            rows = conn.execute(
                """
                SELECT m.* FROM vec_memories
                JOIN memories m ON m.id = vec_memories.id
                WHERE vec_memories.embedding MATCH ? AND k = ?
                ORDER BY distance
                """,
                (emb, top_k),
            ).fetchall()
            return [self._row_to_memory(r) for r in rows]
        finally:
            conn.close()

    def delete(self, mem_id: str) -> bool:
        cur = self._conn.execute("DELETE FROM memories WHERE id = ?", (mem_id,))
        self._conn.execute("DELETE FROM vec_memories WHERE id = ?", (mem_id,))
        self._conn.commit()
        log("memory_delete", {"id": mem_id, "rows": cur.rowcount})
        return cur.rowcount > 0

    def edit(self, mem_id: str, content: str) -> Optional[Memory]:
        now = _now()
        cur = self._conn.execute(
            "UPDATE memories SET content = ?, updated_at = ? WHERE id = ?",
            (content, now, mem_id),
        )
        if cur.rowcount == 0:
            return None
        emb = self._embed(content)
        try:
            self._conn.execute(
                "INSERT OR REPLACE INTO vec_memories (id, embedding) VALUES (?, ?)",
                (mem_id, emb),
            )
        except Exception:
            # sqlite-vec may treat REPLACE as INSERT; delete then insert as fallback
            self._conn.execute("DELETE FROM vec_memories WHERE id = ?", (mem_id,))
            self._conn.execute(
                "INSERT INTO vec_memories (id, embedding) VALUES (?, ?)",
                (mem_id, emb),
            )
        self._conn.commit()
        log("memory_edit", {"id": mem_id})
        return self.get(mem_id)

    def export(self, redact: bool = False) -> List[dict]:
        rows = self._conn.execute("SELECT * FROM memories ORDER BY updated_at DESC").fetchall()
        data = [asdict(self._row_to_memory(r)) for r in rows]
        if redact:
            for d in data:
                d["content"] = self._redact(d["content"])
        return data

    @staticmethod
    def _redact(text: str) -> str:
        # ponytail: naive redaction; upgrade to NER/regex if secrets leak
        for pattern, label in [
            (r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b", "<CARD>"),
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "<EMAIL>"),
            (r"\b\d{3}-\d{2}-\d{4}\b", "<SSN>"),
        ]:
            text = re.sub(pattern, label, text)
        return text

    def _row_to_memory(self, row) -> Memory:
        return Memory(
            id=row[0],
            kind=row[1],
            content=row[2],
            source=row[3],
            scope=row[4],
            confidence=row[5],
            expires_at=row[6],
            created_at=row[7],
            updated_at=row[8],
        )


    def get_by_prefix(self, prefix: str) -> Optional[Memory]:
        """Find a memory by the first few characters of its id."""
        rows = self._conn.execute("SELECT * FROM memories WHERE id LIKE ?", (prefix + "%",)).fetchall()
        if not rows:
            return None
        if len(rows) > 1:
            raise ValueError(f"ambiguous id prefix: {prefix} matches {len(rows)} memories")
        return self._row_to_memory(rows[0])

    def close(self) -> None:
        self._conn.close()


if __name__ == "__main__":  # pragma: no cover
    import sys

    store = MemoryStore()
    if len(sys.argv) < 2:
        for m in store.list(limit=20):
            print(f"{m.id[:8]} | {m.kind} | {m.content[:60]}")
        raise SystemExit
    store.add(" ".join(sys.argv[1:]), kind="fact")
    print("saved")
