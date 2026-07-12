import json
import shutil
from pathlib import Path

import pytest

from astro.index import Index
from astro.vault import Chunk, parse_file, parse_vault


@pytest.fixture
def sample_vault(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "plan.md").write_text("---\ntitle: Plan\ntags: [astro]\n---\n# Plan\n\nDeadline is Friday.", encoding="utf-8")
    (vault / "notes.md").write_text("# Notes\n\nPricing is $9/mo.", encoding="utf-8")
    return vault


def test_parse_file(sample_vault):
    chunks = parse_file(sample_vault / "plan.md")
    assert len(chunks) >= 1
    assert any("Deadline is Friday" in c.text for c in chunks)
    assert all(c.tags for c in chunks)


def test_index_and_search(sample_vault, tmp_path):
    db = tmp_path / "test.db"
    idx = Index(db_path=db)
    n = idx.index_vault(sample_vault, clear=True)
    assert n >= 1
    results = idx.search("deadline", vault_path=sample_vault, top_k=3)
    assert any("Friday" in r["text"] for r in results)
    idx.close()


def test_index_clear(sample_vault, tmp_path):
    db = tmp_path / "test.db"
    idx = Index(db_path=db)
    idx.index_vault(sample_vault, clear=True)
    idx.index_vault(sample_vault, clear=True)
    results = idx.search("deadline", vault_path=sample_vault, top_k=3)
    assert len(results) >= 1
    idx.close()
