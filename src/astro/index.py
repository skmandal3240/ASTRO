"""
Vector + lexical index for ASTRO vault using sqlite-vec and SQLite FTS5.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import List

import sqlite_vec
from sentence_transformers import SentenceTransformer

from astro.audit import log
from astro.config import DEFAULT_DB_PATH, DEFAULT_EMBED_MODEL
from astro.vault import Chunk


def _row_id(c: Chunk) -> str:
    return hashlib.sha256(f"{c.path}:{c.start_line}:{c.text}".encode()).hexdigest()


class Index:
    def __init__(self, db_path: Path | None = None, model_name: str | None = None):
        self.db_path = Path(db_path or DEFAULT_DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name or DEFAULT_EMBED_MODEL
        self._model: SentenceTransformer | None = None
        self._conn = self._open_db()

    def _open_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.execute("PRAGMA foreign_keys = ON;")
        self._migrate(conn)
        return conn

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def _migrate(self, conn) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                vault TEXT NOT NULL,
                path TEXT NOT NULL,
                start_line INTEGER NOT NULL,
                end_line INTEGER NOT NULL,
                title TEXT,
                text TEXT NOT NULL,
                tags TEXT,
                links TEXT,
                meta TEXT,
                indexed_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        try:
            conn.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks USING vec0(id TEXT PRIMARY KEY, embedding FLOAT[384])"
            )
        except Exception:
            pass
        try:
            conn.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks USING fts5(path, text, content='chunks', content_rowid='rowid')"
            )
        except Exception:
            pass
        conn.commit()

    def index_vault(self, vault_path: Path | str, clear: bool = False) -> int:
        vault_path = Path(vault_path).resolve()
        from astro.vault import parse_vault

        if clear:
            ids = [r[0] for r in self._conn.execute("SELECT id FROM chunks WHERE vault = ?", (str(vault_path),))]
            for rid in ids:
                try:
                    self._conn.execute("DELETE FROM vec_chunks WHERE id = ?", (rid,))
                except Exception:
                    pass
            self._conn.execute("DELETE FROM chunks WHERE vault = ?", (str(vault_path),))
        chunks = parse_vault(vault_path)
        if not chunks:
            return 0
        vault_id = str(vault_path)
        inserted = 0
        for chunk in chunks:
            row_id = _row_id(chunk)
            emb = self.model.encode(chunk.text, convert_to_numpy=True, normalize_embeddings=True)
            emb_blob = emb.astype("float32").tobytes()
            self._conn.execute(
                """
                INSERT OR REPLACE INTO chunks (id, vault, path, start_line, end_line, title, text, tags, links, meta)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row_id,
                    vault_id,
                    str(chunk.path),
                    chunk.start_line,
                    chunk.end_line,
                    chunk.title,
                    chunk.text,
                    json.dumps(chunk.tags or []),
                    json.dumps(chunk.links or []),
                    json.dumps(chunk.meta or {}),
                ),
            )
            self._conn.execute(
                "INSERT OR REPLACE INTO vec_chunks (id, embedding) VALUES (?, ?)",
                (row_id, emb_blob),
            )
            inserted += 1
        self._conn.commit()
        log("vault_indexed", {"vault": vault_id, "chunks": inserted})
        return inserted

    def search(self, query: str, vault_path: Path | str | None = None, top_k: int = 5) -> List[dict]:
        query_emb = self.model.encode(query, convert_to_numpy=True, normalize_embeddings=True)
        emb_blob = query_emb.astype("float32").tobytes()
        vault_clause = "AND c.vault = ?" if vault_path else ""
        params = (emb_blob, top_k)
        if vault_path:
            params += (str(Path(vault_path).resolve()),)
        rows = self._conn.execute(
            f"""
            SELECT c.id, c.path, c.start_line, c.end_line, c.title, c.text, c.tags, c.links, distance
            FROM vec_chunks
            JOIN chunks c ON c.id = vec_chunks.id
            WHERE vec_chunks.embedding MATCH ? AND k = ? {vault_clause}
            ORDER BY distance
            """,
            params,
        ).fetchall()
        return [
            {
                "id": r[0],
                "path": r[1],
                "start_line": r[2],
                "end_line": r[3],
                "title": r[4],
                "text": r[5],
                "tags": json.loads(r[6] or "[]"),
                "links": json.loads(r[7] or "[]"),
                "distance": r[8],
            }
            for r in rows
        ]

    def close(self) -> None:
        self._conn.close()


import sqlite3  # imported late because sqlite_vec depends on it at import-time load

if __name__ == "__main__":  # pragma: no cover
    import sys

    idx = Index()
    if len(sys.argv) < 2:
        print("usage: python -m astro.index <vault-path> [query]")
        raise SystemExit(1)
    vault = Path(sys.argv[1])
    n = idx.index_vault(vault, clear=True)
    print(f"indexed {n} chunks from {vault}")
    if len(sys.argv) > 2:
        q = sys.argv[2]
        for r in idx.search(q, vault, top_k=3):
            print(f"{r['path']}:{r['start_line']}-{r['end_line']} | {r['text'][:120]}")
    idx.close()
