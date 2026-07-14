import streamlit as st
from sentence_transformers import CrossEncoder

@st.cache_resource(show_spinner="Loading reranker weights...")
def get_reranker_model():
    try:
        return CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    except Exception as e:
        print(f"Failed to load CrossEncoder. Error: {e}")
        return None

def rerank_documents(query: str, documents: list[dict], top_k: int = 5) -> list[dict]:
    """Reranks documents using the ML Cross-Encoder model based on semantic similarity."""
    if not documents:
        return []
        
    reranker_model = get_reranker_model()
    if reranker_model is None:
        return documents[:top_k]
        
    pairs = [[query, doc["text"]] for doc in documents]
    scores = reranker_model.predict(pairs)
    
    for i, doc in enumerate(documents):
        doc["rerank_score"] = float(scores[i])
        
    documents.sort(key=lambda x: x["rerank_score"], reverse=True)
    
    return documents[:top_k]
