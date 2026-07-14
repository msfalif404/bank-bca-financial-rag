"""
Evaluation module for the Financial RAG pipeline.

Validates two things:
  1. Retrieval Accuracy — did the search engine pull documents containing the expected numbers?
  2. Answer Exact Match — did the LLM produce those exact numbers in its final response?

Usage:
    python src/utils/evaluate.py
"""

import sys
import json
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

from src.rag.retriever import ask_financial_agent_stream
from src.rag.embedding import get_chroma_collection
from src.rag.hybrid_search import perform_hybrid_search
from src.rag.reranker import rerank_documents

DATASET_PATH = PROJECT_ROOT / "tests" / "evaluation_dataset.json"
REPORT_PATH = PROJECT_ROOT / "tests" / "evaluation_report.json"


def normalize(text: str) -> str:
    """Strip formatting characters so '1.415.407.416' and '1415407416' compare equal."""
    return text.replace(".", "").replace(",", "").replace(" ", "")


def contains_any(haystack: str, candidates: list[str]) -> bool:
    """Return True if any candidate appears in the normalized haystack."""
    normalized = normalize(haystack)
    return any(normalize(c) in normalized for c in candidates)


def retrieve_contexts(query: str) -> list[str]:
    """Run hybrid search + reranker and return the top context strings."""
    collection = get_chroma_collection()
    combined = perform_hybrid_search(collection, query, category=None, top_k=10)
    if not combined:
        return []
    reranked = rerank_documents(query, combined, top_k=3)
    return [doc["text"] for doc in reranked]


def generate_answer(query: str, session_id: str) -> str:
    """Consume the streaming agent and return the full answer."""
    return "".join(ask_financial_agent_stream(query, session_id=session_id))


def evaluate_single(item: dict, index: int) -> dict:
    """Evaluate a single test case and return the result dict."""
    question = item["question"]
    expected_numbers = item["expected_numbers"]

    contexts = retrieve_contexts(question)
    answer = generate_answer(question, session_id=f"eval_{index}")

    retrieval_hit = any(contains_any(ctx, expected_numbers) for ctx in contexts)
    exact_match = contains_any(answer, expected_numbers)

    return {
        "question": question,
        "ground_truth": item["ground_truth"],
        "expected_numbers": expected_numbers,
        "retrieval_hit": retrieval_hit,
        "exact_match": exact_match,
        "answer": answer,
        "contexts": contexts,
    }


def print_summary(results: list[dict]) -> None:
    """Print a concise evaluation summary to stdout."""
    total = len(results)
    retrieval_passed = sum(r["retrieval_hit"] for r in results)
    exact_passed = sum(r["exact_match"] for r in results)

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    for i, r in enumerate(results):
        ret = "PASS" if r["retrieval_hit"] else "FAIL"
        ext = "PASS" if r["exact_match"] else "FAIL"
        print(f"  {i + 1}. [Retrieval: {ret}] [Match: {ext}] {r['question']}")

    print(f"\n  Retrieval Accuracy : {retrieval_passed}/{total} ({retrieval_passed / total:.0%})")
    print(f"  Answer Exact Match : {exact_passed}/{total} ({exact_passed / total:.0%})")
    print("=" * 60)


def save_report(results: list[dict], path: Path) -> None:
    """Persist results as a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nReport saved to {path}")


def main():
    if not DATASET_PATH.exists():
        print(f"Error: dataset not found at {DATASET_PATH}")
        return

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"Running {len(dataset)} test cases...\n")

    results = []
    for i, item in enumerate(dataset):
        print(f"[{i + 1}/{len(dataset)}] {item['question']}")
        result = evaluate_single(item, i)
        results.append(result)

        ret = "PASSED" if result["retrieval_hit"] else "FAILED"
        ext = "PASSED" if result["exact_match"] else "FAILED"
        print(f"   Retrieval: {ret}  |  Exact Match: {ext}\n")

    print_summary(results)
    save_report(results, REPORT_PATH)


if __name__ == "__main__":
    main()
