from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

from .report_items import ReportItem
from .report_category import ReportCategory

class FinancialReport(BaseModel):
    file_name: str = Field(description="Path atau nama file  laporan keuangan yang diekstrak")
    company_name: str = Field(description="Nama perusahaan yang tertera di kop laporan")
    report_title: str = Field(description="Judul jenis laporan, contoh: 'LAPORAN POSISI KEUANGAN (NERACA)'")
    period_date: str = Field(description="Tanggal atau periode laporan, contoh: '31 Agustus 2024'")
    audit_status: str = Field(description="Status audit laporan, contoh: 'Tidak Diaudit'")
    scale: Optional[str] = Field(default="Dalam jutaan Rupiah", description="Skala angka yang digunakan, contoh: 'Dalam jutaan Rupiah'")
    categories: list[ReportCategory] = Field(description="Daftar kategori yang ada dalam satu halaman laporan")
    report_total: Optional[float] = Field(default=None, description="Total akhir yang tertera di paling bawah laporan jika ada, contoh: 'TOTAL ASET'")
    insights: Optional[list[str]] = Field(default=None, description="Insight atau analisis tambahan dari GenAI")