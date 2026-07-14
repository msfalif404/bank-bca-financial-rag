from typing import Any
from src.models.report import FinancialDocument

def _get_base_metadata(doc: FinancialDocument) -> dict[str, Any]:
    return {
        "company_name": doc.company_name,
        "period_date": doc.period_date,
        "file_name": doc.file_name,
        "audit_status": doc.audit_status
    }

def _create_overview_chunk(doc: FinancialDocument, base_metadata: dict[str, Any]) -> dict[str, Any]:
    insights_text = "\n".join([f"- {ins}" for ins in doc.insights])
    overview_text = f"Ringkasan dan Insight untuk {doc.company_name} ({doc.period_date}):\n{insights_text}"
    return {
        "id": f"{doc.file_name}_overview",
        "text": overview_text,
        "metadata": {**base_metadata, "type": "overview"}
    }

def _create_category_total_chunk(doc: FinancialDocument, report_title: str, category: Any, report_metadata: dict[str, Any]) -> dict[str, Any]:
    cat_name = category.category_name
    extra_keywords = " Laba Rugi Operasional" if "OPERASIONAL" in cat_name.upper() else ""
        
    cat_total_text = (
        f"Perusahaan: {doc.company_name}\n"
        f"Laporan: {report_title}\n"
        f"Periode: {doc.period_date}\n"
        f"Kategori Grup: {cat_name}\n"
        f"Total Keseluruhan dari {cat_name}{extra_keywords} adalah {category.category_total} {doc.scale}."
    )
    return {
        "id": f"{doc.file_name}_{report_title}_{cat_name}_total",
        "text": cat_total_text,
        "metadata": {**report_metadata, "category": cat_name, "type": "category_total", "value": category.category_total}
    }

def _create_item_chunk(doc: FinancialDocument, report_title: str, cat_name: str, item: Any, report_metadata: dict[str, Any]) -> dict[str, Any]:
    item_text = (
        f"Perusahaan: {doc.company_name}\n"
        f"Laporan: {report_title}\n"
        f"Periode: {doc.period_date}\n"
        f"Kategori Grup: {cat_name}\n"
        f"Nama Pos/Item: {item.item_name}\n"
        f"Nilai: {item.item_value} {doc.scale}"
    )
    return {
        "id": f"{doc.file_name}_{report_title}_{cat_name}_{item.item_name}",
        "text": item_text,
        "metadata": {
            **report_metadata, 
            "category": cat_name,
            "item_name": item.item_name,
            "type": "item",
            "value": item.item_value
        }
    }

def _create_report_total_chunk(doc: FinancialDocument, report_title: str, report_total: float, report_metadata: dict[str, Any]) -> dict[str, Any]:
    total_text = f"{doc.company_name} - {report_title}. Grand Total Keseluruhan laporan adalah {report_total} {doc.scale}."
    return {
        "id": f"{doc.file_name}_{report_title}_grand_total",
        "text": total_text,
        "metadata": {**report_metadata, "type": "report_total", "value": report_total}
    }

def create_chunks_from_document(doc: FinancialDocument) -> list[dict[str, Any]]:
    """Chunks the FinancialDocument object into context-rich text chunks ready for vectorization."""
    chunks = []
    base_metadata = _get_base_metadata(doc)
    
    if doc.insights:
        chunks.append(_create_overview_chunk(doc, base_metadata))

    for report in doc.reports:
        report_title = report.report_title
        report_metadata = {**base_metadata, "report_title": report_title}
        
        for category in report.categories:
            if category.category_total is not None:
                chunks.append(_create_category_total_chunk(doc, report_title, category, report_metadata))
                
            for item in category.items:
                if item.item_value is not None:
                    chunks.append(_create_item_chunk(doc, report_title, category.category_name, item, report_metadata))
                
        if report.report_total is not None:
            chunks.append(_create_report_total_chunk(doc, report_title, report.report_total, report_metadata))
            
    for idx, chunk in enumerate(chunks):
        chunk["id"] = f"{doc.file_name}_{idx}"
        
    return chunks
