import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rag.ingestion import ingest_document
from src.rag.embedding import embed_and_store_chunks
from src.rag.chunking import create_chunks_from_document
from src.models.report import FinancialDocument

def process_single_document(pdf_path: Path, processed_dir: Path) -> bool:
    """Processes a single PDF document through ingestion, chunking, and embedding."""
    print(f"{'='*50}")
    print(f"Memproses file: {pdf_path.name}")
    print(f"{'='*50}")
    
    json_out_path = processed_dir / f"{pdf_path.stem}.json"
    
    try:
        print("Tahap 1: Ekstraksi Data (Ingestion)...")
        ingest_document(str(pdf_path), str(json_out_path))
        
        print("Tahap 2: Melakukan Chunking (Pemotongan Dokumen)...")
        with open(json_out_path, 'r', encoding='utf-8') as f:
            data_dict = json.load(f)
            doc = FinancialDocument(**data_dict)
            
        chunks = create_chunks_from_document(doc)
        
        print("Tahap 3: Embedding ke ChromaDB...")
        embed_and_store_chunks(chunks)
        
        print(f"\nSelesai memproses {pdf_path.name}!\n")
        return True
        
    except Exception as e:
        print(f"\nTerjadi kesalahan saat memproses {pdf_path.name}: {e}\n")
        return False

def run_pipeline():
    """
    Menjalankan proses Ingestion, Chunking, dan Embedding 
    untuk semua file PDF yang ada di dalam folder data/raw/.
    """
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = list(raw_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"Tidak ada file PDF yang ditemukan di {raw_dir.absolute()}")
        return

    print(f"Memulai Pipeline untuk {len(pdf_files)} dokumen...\n")

    success_count = 0
    fail_count = 0

    for pdf_path in pdf_files:
        if process_single_document(pdf_path, processed_dir):
            success_count += 1
        else:
            fail_count += 1

    print(f"Pipeline selesai! Berhasil: {success_count} dokumen. Gagal: {fail_count} dokumen.")

if __name__ == "__main__":
    run_pipeline()
