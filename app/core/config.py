import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
KB_DIR = DATA_DIR / "knowledge_base"
CACHE_DIR = DATA_DIR / "news_cache"
VECTOR_DIR = DATA_DIR / "vector_store"

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"

# Dual-model strategy: heavy for summaries, light for quick mapping
MODEL_HEAVY = "qwen3.6:latest"     # Deep analysis, summarization
MODEL_LIGHT = "llama3.2:3b"         # Fast MITRE mapping, tactical takeaways

# News sources
NEWS_FEEDS = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://krebsonsecurity.com/feed/",
]