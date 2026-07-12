"""
ASTRO skills: filesystem, shell, browser fetch.

All skills receive a policy result and execute only if allowed.
- ponytail: one module, no plugin framework until there are >3 skill types.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict
from urllib.parse import urlparse

import requests

from astro.audit import log
from astro.capabilities import shell_is_allowed


@dataclass
class SkillResult:
    ok: bool
    output: str
    preview: str | None = None
    requires_approval: bool = False


class Skill:
    name: str
    schema: Dict[str, Any]
    run: Callable[..., SkillResult]


class FileReadSkill(Skill):
    name = "file_read"
    schema = {"capability": "file_read", "params": {"path": "file path", "limit": "optional line limit"}}

    @staticmethod
    def run(path: str, limit: int | None = None) -> SkillResult:
        try:
            p = Path(path).resolve()
            text = p.read_text(encoding="utf-8", errors="replace")
            if limit:
                lines = text.splitlines()[:limit]
                text = "\n".join(lines)
            log("file_read", {"path": str(p), "size": len(text)})
            return SkillResult(ok=True, output=text, preview=text[:200])
        except Exception as e:
            return SkillResult(ok=False, output=str(e))


class FileWriteSkill(Skill):
    name = "file_write"
    schema = {"capability": "file_write", "params": {"path": "file path", "content": "text to write"}}

    @staticmethod
    def run(path: str, content: str) -> SkillResult:
        p = Path(path).resolve()
        preview = f"Write {len(content)} bytes to {p}\n---\n{content[:500]}\n---"
        return SkillResult(ok=True, output=str(p), preview=preview, requires_approval=True)

    @staticmethod
    def commit(path: str, content: str) -> SkillResult:
        p = Path(path).resolve()
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            log("file_write", {"path": str(p), "bytes": len(content)})
            return SkillResult(ok=True, output=str(p))
        except Exception as e:
            return SkillResult(ok=False, output=str(e))


class ShellSkill(Skill):
    name = "shell"
    schema = {"capability": "shell", "params": {"command": "shell command", "cwd": "working directory"}}

    @staticmethod
    def run(command: str, cwd: str | None = None, timeout: int = 30) -> SkillResult:
        if not shell_is_allowed(command):
            return SkillResult(ok=False, output=f"Command blocked by allowlist: {command}")
        preview = f"Run shell command:\n{command}\n(cwd: {cwd or '.'})"
        return SkillResult(ok=True, output="", preview=preview, requires_approval=True)

    @staticmethod
    def commit(command: str, cwd: str | None = None, timeout: int = 30) -> SkillResult:
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            log("shell", {"command": command, "cwd": cwd, "rc": result.returncode})
            out = (result.stdout + "\n" + result.stderr).strip()
            return SkillResult(ok=result.returncode == 0, output=out[:2000])
        except Exception as e:
            return SkillResult(ok=False, output=str(e))


URL_ALLOWLIST = {"localhost", "127.0.0.1"}
URL_ALLOW_PATTERNS = [re.compile(r"^https?://([A-Za-z0-9_\-]+\.)?example\.com(/.*)?$")]


def _host_allowed(url: str) -> bool:
    host = urlparse(url).hostname or ""
    if host in URL_ALLOWLIST:
        return True
    return any(p.match(url) for p in URL_ALLOW_PATTERNS)


class BrowserFetchSkill(Skill):
    name = "browser_fetch"
    schema = {"capability": "browser_fetch", "params": {"url": "URL to fetch"}}

    @staticmethod
    def run(url: str) -> SkillResult:
        if not _host_allowed(url):
            return SkillResult(ok=False, output=f"URL not in allowlist: {url}")
        preview = f"GET {url}"
        return SkillResult(ok=True, output="", preview=preview, requires_approval=False)

    @staticmethod
    def commit(url: str, timeout: int = 30) -> SkillResult:
        if not _host_allowed(url):
            return SkillResult(ok=False, output=f"URL not in allowlist: {url}")
        try:
            r = requests.get(url, timeout=timeout)
            text = r.text[:2000]
            log("browser_fetch", {"url": url, "status": r.status_code, "len": len(r.text)})
            return SkillResult(ok=r.status_code < 400, output=text)
        except Exception as e:
            return SkillResult(ok=False, output=str(e))


SKILLS: Dict[str, Skill] = {
    "file_read": FileReadSkill(),
    "file_write": FileWriteSkill(),
    "shell": ShellSkill(),
    "browser_fetch": BrowserFetchSkill(),
}
