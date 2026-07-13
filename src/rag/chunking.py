from src.models.report import FinancialReport

def create_chunks_from_report(report: FinancialReport) -> list[dict]:
    """Chunks the FinancialReport object into context-rich text chunks ready for vectorization."""
    chunks = []
    
    base_metadata = {
        "company_name": report.company_name,
        "report_title": report.report_title,
        "period_date": report.period_date,
        "file_name": report.file_name,
        "audit_status": report.audit_status
    }
    
    if report.insights:
        insights_text = "\n".join([f"- {ins}" for ins in report.insights])
        overview_text = f"Ringkasan dan Insight untuk {report.company_name} - {report.report_title} ({report.period_date}):\n{insights_text}"
        chunks.append({
            "id": f"{report.file_name}_overview",
            "text": overview_text,
            "metadata": {**base_metadata, "type": "overview"}
        })

    for category in report.categories:
        cat_name = category.category_name
        
        if category.category_total is not None:
            cat_total_text = f"Laporan: {report.report_title}\nPerusahaan: {report.company_name}\nTotal dari grup/kategori {cat_name} adalah {category.category_total} {report.scale}."
            chunks.append({
                "id": f"{report.file_name}_{cat_name}_total",
                "text": cat_total_text,
                "metadata": {**base_metadata, "category": cat_name, "type": "category_total", "value": category.category_total}
            })
            
        for item in category.items:
            if item.item_value is None:
                continue
                
            item_text = (
                f"Perusahaan: {report.company_name}\n"
                f"Laporan: {report.report_title}\n"
                f"Periode: {report.period_date}\n"
                f"Kategori Grup: {cat_name}\n"
                f"Nama Pos/Item: {item.item_name}\n"
                f"Nilai: {item.item_value} {report.scale}"
            )
            
            chunks.append({
                "id": f"{report.file_name}_{cat_name}_{item.item_name}",
                "text": item_text,
                "metadata": {
                    **base_metadata, 
                    "category": cat_name,
                    "item_name": item.item_name,
                    "type": "item",
                    "value": item.item_value
                }
            })
            
    if report.report_total is not None:
        total_text = f"{report.company_name} - {report.report_title}. Grand Total Keseluruhan laporan adalah {report.report_total} {report.scale}."
        chunks.append({
            "id": f"{report.file_name}_grand_total",
            "text": total_text,
            "metadata": {**base_metadata, "type": "report_total", "value": report.report_total}
        })
        
    # Assign simple, unique, and deterministic IDs using the chunk index
    for idx, chunk in enumerate(chunks):
        chunk["id"] = f"{report.file_name}_{idx}"
        
    return chunks
