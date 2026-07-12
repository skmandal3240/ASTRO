"""
ASTRO core configuration and constants.
"""
from pathlib import Path

APP_NAME = "ASTRO"
DEFAULT_DATA_DIR = Path.home() / ".astro"
DEFAULT_DB_PATH = DEFAULT_DATA_DIR / "astro.db"
DEFAULT_VAULTS_DIR = DEFAULT_DATA_DIR / "vaults"
DEFAULT_AUDIT_LOG = DEFAULT_DATA_DIR / "audit.ndjson"
DEFAULT_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_OLLAMA_MODEL = "qwen2.5:0.5b"
OLLAMA_URL = "http://localhost:11434"
