import bm25s
from typing import Optional

_bm25_cache = {}

def get_bm25_retriever(collection, category: Optional[str] = None):
    """Creates a BM25 retriever on-the-fly from ChromaDB documents and caches it."""
    global _bm25_cache
    
    cache_key = category if category else "ALL_DOCS"
    if cache_key in _bm25_cache:
        return _bm25_cache[cache_key]

    where_filter = {"category": category} if category else None
        
    results = collection.get(
        include=["documents", "metadatas"],
        where=where_filter
    )
    
    if not results['documents']:
        return None, []
        
    corpus_texts = results['documents']
    metadatas = results['metadatas']
    ids = results['ids']
    
    corpus_objs = [
        {"id": ids[i], "text": corpus_texts[i], "metadata": metadatas[i]}
        for i in range(len(corpus_texts))
    ]
        
    # Proses ini lambat jika datanya ribuan, jadi kita wajib cache
    corpus_tokens = bm25s.tokenize(corpus_texts)
    
    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)
    
    _bm25_cache[cache_key] = (retriever, corpus_objs)
    return retriever, corpus_objs

def _retrieve_vector_docs(collection, query: str, category: Optional[str], top_k: int) -> list[dict]:
    """Retrieves top_k documents using Chroma vector search."""
    where_filter = {"category": category} if category else None
    
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where_filter
    )
    
    if not results['documents'] or not results['documents'][0]:
        return []
        
    return [
        {
            "id": results['ids'][0][i],
            "text": results['documents'][0][i],
            "metadata": results['metadatas'][0][i]
        }
        for i in range(len(results['documents'][0]))
    ]

def _retrieve_bm25_docs(collection, query: str, category: Optional[str], top_k: int) -> list[dict]:
    """Retrieves top_k documents using BM25 lexical search."""
    retriever, corpus_objs = get_bm25_retriever(collection, category)
    if not retriever:
        return []
        
    query_tokens = bm25s.tokenize(query)
    k_val = min(top_k, len(corpus_objs))
    
    results, _ = retriever.retrieve(query_tokens, corpus=corpus_objs, k=k_val)
    
    if results.shape[1] == 0:
        return []
        
    return [results[0, i] for i in range(results.shape[1])]

def perform_hybrid_search(collection, query: str, category: Optional[str] = None, top_k: int = 10) -> list[dict]:
    """Performs a hybrid search combining Vector Search (Chroma) and Lexical Search (BM25s)."""
    vector_docs = _retrieve_vector_docs(collection, query, category, top_k)
    bm25_docs = _retrieve_bm25_docs(collection, query, category, top_k)
            
    seen_ids = set()
    combined_docs = []
    
    for doc in vector_docs + bm25_docs:
        if doc["id"] not in seen_ids:
            seen_ids.add(doc["id"])
            combined_docs.append(doc)
            
    return combined_docs
