#!/usr/bin/env bash
# One-time setup script for ASTRO.
set -euo pipefail

python3 -m pip install --upgrade pip
python3 -m pip install -e ".[train]"

mkdir -p "$HOME/.astro"

if ! command -v ollama &>/dev/null; then
    echo "⚠ Ollama not found. Install from https://ollama.com before running ASTRO."
else
    ollama pull qwen2.5:0.5b || true
fi

echo "✓ ASTRO setup complete. Run 'astro --help' to start."
