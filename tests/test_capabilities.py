"""
Smoke tests for capabilities and skills.
"""
from pathlib import Path

import pytest

from astro.capabilities import HIGH_RISK, Grant, Ledger, PolicyEngine, shell_is_allowed
from astro.skills import BrowserFetchSkill, FileReadSkill, FileWriteSkill, ShellSkill


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    # Ensure every test starts with an isolated empty store.
    store = tmp_path / "grants.json"
    store.write_text("[]")
    monkeypatch.setattr("astro.config.DEFAULT_DATA_DIR", tmp_path)
    return Ledger(store_path=store)


def test_grant_and_check(ledger):
    ledger.grant(Grant("file_read", "/tmp", approval="rule"))
    decision = ledger.check("file_read", "/tmp/foo.txt", "read")
    assert decision["allowed"] is True


def test_always_approval_requires_explicit(ledger):
    ledger.grant(Grant("file_read", "/tmp", approval="always"))
    decision = ledger.check("file_read", "/tmp/foo.txt", "read")
    assert decision["approval_required"] is True


def test_no_grant_blocks(ledger):
    decision = ledger.check("shell", "/tmp", "rm -rf /")
    assert decision["allowed"] is False


def test_revoke_all(ledger):
    ledger.grant(Grant("file_write", "/tmp"))
    ledger.grant(Grant("shell", "/tmp"))
    assert len(ledger.list()) == 2
    ledger.revoke_all()
    assert len(ledger.list()) == 0


def test_shell_allowlist():
    assert shell_is_allowed("ls /tmp")
    assert shell_is_allowed("cat file.txt")
    assert not shell_is_allowed("rm -rf /")


def test_file_write_preview_then_commit(tmp_path):
    p = tmp_path / "out.txt"
    preview = FileWriteSkill.run(str(p), "hello")
    assert preview.requires_approval is True
    commit = FileWriteSkill.commit(str(p), "hello")
    assert commit.ok is True
    assert p.read_text(encoding="utf-8") == "hello"


def test_shell_skill_blocked_command():
    res = ShellSkill.run("rm -rf /")
    assert res.ok is False


def test_browser_fetch_allowlist():
    res = BrowserFetchSkill.run("http://example.com")
    assert res.ok is True
    res_bad = BrowserFetchSkill.run("http://evil.com")
    assert res_bad.ok is False


def test_policy_engine_proposes_approval(ledger):
    policy = PolicyEngine(ledger)
    policy.ledger.grant(Grant("file_write", "/tmp"))
    dec = policy.propose("file_write", "/tmp/x.txt", "write", {"content": "x"})
    assert dec["approval_required"] is True
    assert dec["allowed"] is False


def test_file_read_skill(tmp_path):
    f = tmp_path / "hello.txt"
    f.write_text("world")
    res = FileReadSkill.run(path=f, limit=None)
    assert res.ok
    assert "world" in res.output


def test_file_read_skill_respects_limit(tmp_path):
    f = tmp_path / "hello.txt"
    f.write_text("hello\nworld\nthree\n")
    res = FileReadSkill.run(path=f, limit=2)
    assert "three" not in res.output


def test_high_risk_set():
    assert "file_write" in HIGH_RISK
    assert "shell" in HIGH_RISK
    assert "file_read" not in HIGH_RISK
