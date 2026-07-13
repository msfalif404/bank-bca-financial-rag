import os
import chromadb
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT", chromadb.DEFAULT_TENANT)
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", chromadb.DEFAULT_DATABASE)
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "financial_reports")
