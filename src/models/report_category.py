from pydantic import BaseModel, Field
from typing import Optional

from .report_items import ReportItem

class ReportCategory(BaseModel):
    category_name: str = Field(description="Nama kategori atau blok tabel, contoh: 'ASET', 'LIABILITAS', 'PENDAPATAN'")
    items: list[ReportItem] = Field(description="Daftar pos atau item yang termasuk ke dalam kategori ini")
    category_total: Optional[float] = Field(default=None, description="Total nilai dari kategori ini jika ada disebutkan di bagian bawah grup")