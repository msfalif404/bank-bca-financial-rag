import base64
from pathlib import Path
from openai import OpenAI

from src.models.report import FinancialReport
from src.prompts.manager import prompt_manager
from config.settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def encode_file_to_base64(file_path: str) -> str:
    """Encodes a file to a base64 string for the API payload."""
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode('utf-8')

def extract_financial_data(file_path: str) -> FinancialReport:
    """Extracts data from a PDF document directly using OpenAI."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")

    base64_data = encode_file_to_base64(str(path))
    ext = path.suffix.lower()
    
    if ext != '.pdf':
        raise ValueError(f"Format file '{ext}' tidak didukung. Harap gunakan format PDF")

    file_content = {
        "type": "file", 
        "file": {
            "file_data": f"data:application/pdf;base64,{base64_data}",
            "filename": path.name
        }
    }

    system_prompt = prompt_manager.extraction_prompt
    
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Ekstrak data dari laporan keuangan ini secara presisi. File sumber: {path.name}"},
                    file_content
                ]
            }
        ],
        response_format=FinancialReport,
        max_tokens=4000
    )
    
    return response.choices[0].message.parsed

def ingest_document(file_path: str, output_json_path: str = None) -> FinancialReport:
    """Wrapper function to read a document and optionally save its extracted JSON."""
    extracted_data = extract_financial_data(file_path)
    
    if output_json_path:
        out_path = Path(output_json_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(extracted_data.model_dump_json(indent=4))
            
    return extracted_data