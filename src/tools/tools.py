from typing import Optional
from src.rag.embedding import get_chroma_collection
from src.rag.hybrid_search import perform_hybrid_search
from src.rag.reranker import rerank_documents

def search_financial_records(query: str, category: Optional[str] = None) -> dict:
    """
    Search for specific financial numerical data within the vector database.
    
    Args:
        query (str): The search query or numerical keyword.
        category (str, optional): The category filter (e.g., "ASET", "LIABILITAS"). Defaults to None.
    """
    collection = get_chroma_collection()
    combined_docs = perform_hybrid_search(collection, query, category, top_k=10)
    
    if not combined_docs:
        return {"status": "error", "message": "Tidak ada data yang ditemukan."}
        
    reranked_docs = rerank_documents(query, combined_docs, top_k=3)
    
    return {
        "status": "success", 
        "data": [doc["text"] for doc in reranked_docs],
        "metadatas": [doc["metadata"] for doc in reranked_docs]
    }

def get_report_overview(company_name: str) -> dict:
    """
    Retrieves the general overview or total category insights of a company's financial report.
    
    Args:
        company_name (str): Name of the company.
    """
    collection = get_chroma_collection()
    results = collection.query(
        query_texts=[f"Ringkasan dan total laporan keuangan {company_name}"],
        n_results=10,
        where={"type": {"$in": ["overview", "report_total", "category_total"]}}
    )
    
    if not results['documents'] or not results['documents'][0]:
        return {"status": "error", "message": f"Tidak ada overview untuk perusahaan {company_name}."}
        
    return {
        "status": "success", 
        "data": results['documents'][0]
    }
