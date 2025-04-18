# core/corpora_loader.py

import json
import os
from pathlib import Path
import logging

logger = logging.getLogger("CorporaLoader")

CORPORA_DIR = Path("scenarios/corpora")
_cache = {}

def load_corpus(name: str):
    """
    Loads and caches a named corpus from the corpora directory.
    """
    if name in _cache:
        return _cache[name]

    path = CORPORA_DIR / f"{name}.json"
    if not path.exists():
        logger.warning(f"📂 Corpus file not found: {path}")
        return None

    with open(path, "r") as f:
        try:
            data = json.load(f)
            _cache[name] = data
            logger.info(f"📚 Loaded corpus: {name}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse corpus '{name}': {e}")
            return None

def preload_all():
    """
    Preloads all JSON files in the corpora directory.
    """
    logger.info("📦 Preloading all corpora...")
    for file in CORPORA_DIR.glob("*.json"):
        load_corpus(file.stem)

def list_available_corpora():
    return [f.stem for f in CORPORA_DIR.glob("*.json")]
