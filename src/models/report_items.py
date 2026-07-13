from pydantic import BaseModel, Field
from typing import Optional

class ReportItem(BaseModel):
    item_id: Optional[str] = Field(default=None, description="Nomor urut atau ID item dari tabel, contoh: '1', '13.a', 'I'")
    item_name: str = Field(description="Nama pos atau item keuangan, contoh: 'Kas', 'Pendapatan Bunga'")
    item_value: Optional[float] = Field(default=None, description="Nilai nominal item keuangan. Null/None jika di laporan tidak ada nilainya atau strip '-'")