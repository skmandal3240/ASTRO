"""
Agent executor: model proposes a tool, policy evaluates, skill runs.
"""
from __future__ import annotations

from typing import Any

import requests

from astro.capabilities import HIGH_RISK, MEDIUM_RISK, Ledger, PolicyEngine
from astro.config import DEFAULT_OLLAMA_MODEL, OLLAMA_URL
from astro.skills import SKILLS, BrowserFetchSkill, FileReadSkill, FileWriteSkill, ShellSkill

import json


SYSTEM_PROMPT = """You are ASTRO's planner. The user wants to perform a task. Choose ONE tool from the list below and emit ONLY a JSON object with keys: tool, params, reason. Do not add explanation outside the JSON.

Available tools:
- file_read: read a scoped file. params: path, limit
- file_write: write a file (requires approval). params: path, content
- shell: run a safe shell command (requires approval). params: command, cwd
- browser_fetch: GET a URL. params: url

Rules:
- Pick the safest tool that satisfies the request.
- For file_read, only propose paths inside granted scopes.
- For shell, use only safe commands (ls, cat, pwd, echo, head, tail, find, grep).
- Refuse destructive or privacy-violating requests."""


class Agent:
    def __init__(self, policy: PolicyEngine | None = None, model: str = DEFAULT_OLLAMA_MODEL):
        self.policy = policy or PolicyEngine(Ledger())
        self.model = model

    def plan(self, request: str) -> dict:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": self.model, "prompt": request, "system": SYSTEM_PROMPT, "stream": False, "format": "json"},
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        try:
            plan = json.loads(data.get("response", "{}"))
        except Exception:
            plan = {"tool": "unknown", "params": {}, "reason": "parse error"}
        return plan

    def execute(self, plan: dict, approved: bool = False) -> dict:
        tool = plan.get("tool")
        params = plan.get("params", {})
        if tool not in SKILLS:
            return {"ok": False, "error": f"unknown tool: {tool}"}

        capability = SKILLS[tool].schema["capability"]
        target = params.get("path") or params.get("url") or params.get("cwd") or "*"
        decision = self.policy.propose(capability, target, tool, params)

        if not decision["allowed"] and not decision.get("approval_required"):
            return {"ok": False, "error": decision["reason"], "decision": decision}

        if decision.get("approval_required") and not approved:
            preview = SKILLS[tool].run(**params)
            return {"ok": False, "requires_approval": True, "preview": preview.preview, "plan": plan}

        if capability == "file_write":
            return FileWriteSkill.commit(**params).__dict__
        if capability == "shell":
            return ShellSkill.commit(**params).__dict__
        if capability == "browser_fetch":
            return BrowserFetchSkill.commit(**params).__dict__
        # file_read and pre-approved medium-risk
        return FileReadSkill.run(**params).__dict__


# ponytail: json is imported at top; duplicate import below was dead code left by earlier patch
