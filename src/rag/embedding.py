import hashlib
import chromadb
from chromadb import Schema, StringInvertedIndexConfig, IntInvertedIndexConfig, FloatInvertedIndexConfig, BoolInvertedIndexConfig, VectorIndexConfig
from chromadb.utils import embedding_functions

from config.settings import CHROMA_TENANT, CHROMA_DATABASE, CHROMA_API_KEY, CHROMA_COLLECTION_NAME, OPENAI_API_KEY

_chroma_client = None

def get_chroma_client() -> chromadb.ClientAPI:
    """Configures the connection to ChromaDB Cloud / Remote Server and caches it."""
    global _chroma_client
    if _chroma_client is None:
        if CHROMA_TENANT and CHROMA_API_KEY:
            _chroma_client = chromadb.CloudClient(
                tenant=CHROMA_TENANT,
                database=CHROMA_DATABASE,
                api_key=CHROMA_API_KEY
            )
        else:
            _chroma_client = chromadb.PersistentClient(path="storage/chroma_db_local")
    return _chroma_client

def get_chroma_schema() -> Schema:
    """Configures ChromaDB Schema to only index necessary metadata fields for performance."""
    schema = Schema()
    
    # 1. Nonaktifkan index bawaan secara global (menghapus index otomatis)
    schema.delete_index(config=StringInvertedIndexConfig())
    schema.delete_index(config=IntInvertedIndexConfig())
    schema.delete_index(config=FloatInvertedIndexConfig())
    schema.delete_index(config=BoolInvertedIndexConfig())
    
    # 2. Daftarkan kembali index string secara spesifik hanya untuk key tertentu
    schema.create_index(config=StringInvertedIndexConfig(), key="category")
    schema.create_index(config=StringInvertedIndexConfig(), key="type")

    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name="text-embedding-3-small"
    )

    schema.create_index(config=VectorIndexConfig(
        space="cosine",
        embedding_function=openai_ef
    ))
    
    return schema


def get_chroma_collection() -> chromadb.Collection:
    """Retrieves the ChromaDB collection equipped with OpenAI embedding function."""
    client = get_chroma_client()
    
    try:
        return client.get_collection(
            name=CHROMA_COLLECTION_NAME
        )
    except Exception:
        return client.create_collection(
            name=CHROMA_COLLECTION_NAME,
            schema=get_chroma_schema()
        )

def embed_and_store_chunks(chunks: list[dict]):
    """Generates embeddings for the provided chunks and saves them to ChromaDB."""
    if not chunks:
        print("Tidak ada data valid yang bisa di-embed.")
        return

    collection = get_chroma_collection()
    
    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
