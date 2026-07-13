import bm25s
from typing import Optional

def get_bm25_retriever(collection, category: Optional[str] = None):
    """Creates a BM25 retriever on-the-fly from ChromaDB documents."""
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
        
    corpus_tokens = bm25s.tokenize(corpus_texts)
    
    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)
    
    return retriever, corpus_objs

def perform_hybrid_search(collection, query: str, category: Optional[str] = None, top_k: int = 10) -> list[dict]:
    """Performs a hybrid search combining Vector Search (Chroma) and Lexical Search (BM25s)."""
    where_filter = {"category": category} if category else None
        
    vector_results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where_filter
    )
    
    vector_docs = []
    if vector_results['documents'] and vector_results['documents'][0]:
        vector_docs = [
            {
                "id": vector_results['ids'][0][i],
                "text": vector_results['documents'][0][i],
                "metadata": vector_results['metadatas'][0][i]
            }
            for i in range(len(vector_results['documents'][0]))
        ]
            
    retriever, corpus_objs = get_bm25_retriever(collection, category)
    bm25_docs = []
    
    if retriever:
        query_tokens = bm25s.tokenize(query)
        k_val = min(top_k, len(corpus_objs))
        
        results, _ = retriever.retrieve(query_tokens, corpus=corpus_objs, k=k_val)
        
        if results.shape[1] > 0:
            bm25_docs = [results[0, i] for i in range(results.shape[1])]
            
    seen_ids = set()
    combined_docs = []
    
    for doc in vector_docs + bm25_docs:
        if doc["id"] not in seen_ids:
            seen_ids.add(doc["id"])
            combined_docs.append(doc)
            
    return combined_docs
