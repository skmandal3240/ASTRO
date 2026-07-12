"""
Release check script for ASTRO.

Runs smoke checks before tagging a release:
- pytest
- eval harness
- CLI --help
- Ollama model availability
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str], cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess:
    print("$ " + " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def main() -> int:
    failed = 0

    try:
        run([sys.executable, "-m", "pytest", "tests/", "-q"])
        print("✓ tests pass")
    except subprocess.CalledProcessError as exc:
        print("✗ tests failed\n", exc.stdout, exc.stderr)
        failed += 1

    try:
        run([sys.executable, "eval/eval.py", "--all"])
        print("✓ eval harness passes")
    except subprocess.CalledProcessError as exc:
        print("✗ eval harness failed")
        failed += 1

    try:
        run(["astro", "--help"])
        print("✓ CLI loads")
    except Exception as exc:
        print("✗ CLI failed:", exc)
        failed += 1

    try:
        r = run(["ollama", "list"])
        if "qwen2.5:0.5b" not in r.stdout:
            print("⚠ default Ollama model not present; run `ollama pull qwen2.5:0.5b`")
        else:
            print("✓ default Ollama model available")
    except FileNotFoundError:
        print("⚠ Ollama not installed or not in PATH")
    except subprocess.CalledProcessError:
        print("⚠ Ollama list failed")

    print("\nrelease check done; failures:", failed)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
