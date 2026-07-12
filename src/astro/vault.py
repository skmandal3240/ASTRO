"""
Markdown vault parsing for ASTRO.

Reads Markdown files and extracts:
- raw text chunks by heading
- frontmatter metadata
- tags (#tag or frontmatter tags)
- wikilinks [[...]]
- source path + approximate line range per chunk
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

import frontmatter

TAG_RE = re.compile(r"#([A-Za-z0-9_\-/]+)")
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


@dataclass
class Chunk:
    path: Path
    text: str
    start_line: int
    end_line: int
    title: str = ""
    tags: List[str] | None = None
    links: List[str] | None = None
    meta: dict | None = None

    @property
    def citation(self) -> str:
        return f"{self.path}:{self.start_line}-{self.end_line}"


def _sliding_window(lines: List[str], size: int = 5, step: int = 3) -> List[tuple[int, int, List[str]]]:
    """Return overlapping windows of lines."""
    if not lines:
        return []
    if len(lines) <= size:
        return [(1, len(lines), lines)]
    windows = []
    seen = set()
    for i in range(0, len(lines) - size + 1, step):
        key = (i, i + size)
        if key in seen:
            break
        seen.add(key)
        window = lines[i : i + size]
        if not any(line.strip() for line in window):
            continue
        windows.append((i + 1, min(i + size, len(lines)), window))
    # tail window
    tail_start = max(0, len(lines) - size)
    tail_key = (tail_start, len(lines))
    if tail_key not in seen:
        tail = lines[tail_start:]
        if any(line.strip() for line in tail):
            windows.append((tail_start + 1, len(lines), tail))
    return windows


def parse_file(path: Path, window_size: int = 5, step: int = 3) -> List[Chunk]:
    """Parse a Markdown file into chunks."""
    text = path.read_text(encoding="utf-8", errors="replace")
    post = frontmatter.loads(text)
    body = post.content
    meta = dict(post.metadata) if post.metadata else {}

    tags = set(meta.get("tags", []))
    for t in TAG_RE.findall(body):
        tags.add(t)

    links = WIKILINK_RE.findall(body)

    lines = body.splitlines()
    chunks = []
    for start, end, window in _sliding_window(lines, window_size, step):
        chunk_text = "\n".join(window).strip()
        if not chunk_text:
            continue
        chunks.append(
            Chunk(
                path=path,
                text=chunk_text,
                start_line=start,
                end_line=end,
                title=meta.get("title", path.stem),
                tags=sorted(tags),
                links=sorted(set(links)),
                meta=meta,
            )
        )
    return chunks


def parse_vault(vault_path: Path, window_size: int = 5, step: int = 3) -> List[Chunk]:
    """Parse all .md files under vault_path."""
    vault_path = Path(vault_path)
    chunks: List[Chunk] = []
    for p in vault_path.rglob("*.md"):
        if any(part.startswith(".") for part in p.relative_to(vault_path).parts):
            continue
        chunks.extend(parse_file(p, window_size=window_size, step=step))
    return chunks


if __name__ == "__main__":  # pragma: no cover
    import sys

    for c in parse_vault(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")):
        print(f"{c.citation} | {c.text[:80]}...")
