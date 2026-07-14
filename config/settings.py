import os
import chromadb
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 1. Load .env (Fallback untuk environment lokal)
load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)

def get_config(key: str, default=None):
    """
    Prioritas:
    1. st.secrets (Wajib untuk Streamlit Cloud)
    2. Environment Variable (.env / OS Env lokal)
    """
    try:
        from streamlit import secrets
        if key in secrets:
            return secrets[key]
    except Exception:
        pass
        
    return os.getenv(key, default)

# Settings
OPENAI_API_KEY = get_config("OPENAI_API_KEY")

CHROMA_HOST = get_config("CHROMA_HOST")
CHROMA_API_KEY = get_config("CHROMA_API_KEY")
CHROMA_TENANT = get_config("CHROMA_TENANT", chromadb.DEFAULT_TENANT)
CHROMA_DATABASE = get_config("CHROMA_DATABASE", chromadb.DEFAULT_DATABASE)
CHROMA_COLLECTION_NAME = get_config("CHROMA_COLLECTION_NAME", "financial_reports")
