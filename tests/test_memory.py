"""Tests for memory store."""
from pathlib import Path
import tempfile

import pytest

from astro.memory import MemoryStore


def test_add_and_search():
    with tempfile.TemporaryDirectory() as td:
        store = MemoryStore(Path(td) / "m.db")
        m = store.add("My dentist is Dr. Rao", kind="fact", scope="personal")
        assert m.content == "My dentist is Dr. Rao"
        found = store.search("dentist")
        assert len(found) == 1
        assert found[0].id == m.id


def test_list_filter():
    with tempfile.TemporaryDirectory() as td:
        store = MemoryStore(Path(td) / "m.db")
        store.add("work fact", kind="fact", scope="work")
        store.add("personal pref", kind="preference", scope="personal")
        assert len(store.list(scope="work")) == 1
        assert len(store.list(kind="preference")) == 1


def test_edit_and_delete():
    with tempfile.TemporaryDirectory() as td:
        store = MemoryStore(Path(td) / "m.db")
        m = store.add("old")
        updated = store.edit(m.id, "new")
        assert updated and updated.content == "new"
        assert store.delete(m.id)
        assert store.get(m.id) is None


def test_redact():
    text = "Email me at foo@bar.com or use card 1234 5678 9012 3456"
    out = MemoryStore._redact(text)
    assert "<EMAIL>" in out
    assert "<CARD>" in out


def test_ttl():
    from astro.memory import _parse_ttl
    assert _parse_ttl("1d") is not None
    assert _parse_ttl("2w") is not None
    assert _parse_ttl("1M") is not None
    assert _parse_ttl("1y") is not None
    assert _parse_ttl("bad") is None


def test_get_by_prefix():
    with tempfile.TemporaryDirectory() as td:
        store = MemoryStore(db_path=Path(td) / "m.db")
        m = store.add("unique content", kind="fact")
        prefix = m.id[:8]
        found = store.get_by_prefix(prefix)
        assert found and found.id == m.id
        assert store.get_by_prefix("zzzzzzzz") is None
