from src.models.report import FinancialDocument

def create_chunks_from_document(doc: FinancialDocument) -> list[dict]:
    """Chunks the FinancialDocument object into context-rich text chunks ready for vectorization."""
    chunks = []
    
    base_metadata = {
        "company_name": doc.company_name,
        "period_date": doc.period_date,
        "file_name": doc.file_name,
        "audit_status": doc.audit_status
    }
    
    if doc.insights:
        insights_text = "\n".join([f"- {ins}" for ins in doc.insights])
        overview_text = f"Ringkasan dan Insight untuk {doc.company_name} ({doc.period_date}):\n{insights_text}"
        chunks.append({
            "id": f"{doc.file_name}_overview",
            "text": overview_text,
            "metadata": {**base_metadata, "type": "overview"}
        })

    for report in doc.reports:
        report_title = report.report_title
        report_metadata = {**base_metadata, "report_title": report_title}
        
        for category in report.categories:
            cat_name = category.category_name
            
            if category.category_total is not None:
                # Tambahkan sinomin atau term umum untuk membantu Lexical Search (BM25)
                extra_keywords = ""
                if "OPERASIONAL" in cat_name:
                    extra_keywords = " Laba Rugi Operasional"
                    
                cat_total_text = (
                    f"Perusahaan: {doc.company_name}\n"
                    f"Laporan: {report_title}\n"
                    f"Periode: {doc.period_date}\n"
                    f"Kategori Grup: {cat_name}\n"
                    f"Total Keseluruhan dari {cat_name}{extra_keywords} adalah {category.category_total} {doc.scale}."
                )
                chunks.append({
                    "id": f"{doc.file_name}_{report_title}_{cat_name}_total",
                    "text": cat_total_text,
                    "metadata": {**report_metadata, "category": cat_name, "type": "category_total", "value": category.category_total}
                })
                
            for item in category.items:
                if item.item_value is None:
                    continue
                    
                item_text = (
                    f"Perusahaan: {doc.company_name}\n"
                    f"Laporan: {report_title}\n"
                    f"Periode: {doc.period_date}\n"
                    f"Kategori Grup: {cat_name}\n"
                    f"Nama Pos/Item: {item.item_name}\n"
                    f"Nilai: {item.item_value} {doc.scale}"
                )
                
                chunks.append({
                    "id": f"{doc.file_name}_{report_title}_{cat_name}_{item.item_name}",
                    "text": item_text,
                    "metadata": {
                        **report_metadata, 
                        "category": cat_name,
                        "item_name": item.item_name,
                        "type": "item",
                        "value": item.item_value
                    }
                })
                
        if report.report_total is not None:
            total_text = f"{doc.company_name} - {report_title}. Grand Total Keseluruhan laporan adalah {report.report_total} {doc.scale}."
            chunks.append({
                "id": f"{doc.file_name}_{report_title}_grand_total",
                "text": total_text,
                "metadata": {**report_metadata, "type": "report_total", "value": report.report_total}
            })
            
    # Assign simple, unique, and deterministic IDs using the chunk index
    for idx, chunk in enumerate(chunks):
        chunk["id"] = f"{doc.file_name}_{idx}"
        
    return chunks
