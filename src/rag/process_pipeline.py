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

def run_pipeline():
    """
    Menjalankan proses Ingestion (PDF -> JSON) dan Embedding (JSON -> ChromaDB)
    sekaligus untuk semua file PDF yang ada di dalam folder data/raw/.
    """
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    
    # Pastikan folder ada
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Ambil semua file PDF dari data/raw
    pdf_files = list(raw_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"Tidak ada file PDF yang ditemukan di {raw_dir.absolute()}")
        return

    print(f"Memulai Pipeline untuk {len(pdf_files)} dokumen...\n")

    success_count = 0
    fail_count = 0

    for pdf_path in pdf_files:
        print(f"{'='*50}")
        print(f"Memproses file: {pdf_path.name}")
        print(f"{'='*50}")
        
        # Tentukan nama file JSON output
        json_filename = f"{pdf_path.stem}.json"
        json_out_path = processed_dir / json_filename
        
        try:
            # 1. Proses Ingestion (Ekstraksi dengan OpenAI)
            print("Tahap 1: Ekstraksi Data (Ingestion)...")
            ingest_document(str(pdf_path), str(json_out_path))
            
            # 2. Proses Chunking (Membaca JSON dan memecah teks)
            print("Tahap 2: Melakukan Chunking (Pemotongan Dokumen)...")
            with open(json_out_path, 'r', encoding='utf-8') as f:
                data_dict = json.load(f)
                doc = FinancialDocument(**data_dict)
            chunks = create_chunks_from_document(doc)
            
            # 3. Proses Embedding (Simpan ke ChromaDB)
            print("Tahap 3: Embedding ke ChromaDB...")
            embed_and_store_chunks(chunks)
            
            print(f"\nSelesai memproses {pdf_path.name}!\n")
            success_count += 1
            
        except Exception as e:
            print(f"\nTerjadi kesalahan saat memproses {pdf_path.name}: {e}\n")
            fail_count += 1

    print(f"Pipeline selesai! Berhasil: {success_count} dokumen. Gagal: {fail_count} dokumen.")

if __name__ == "__main__":
    run_pipeline()
