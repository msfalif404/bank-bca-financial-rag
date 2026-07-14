import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def parse_indonesian_date(date_str: str) -> pd.Timestamp:
    """Parses Indonesian date string like '31 Agustus 2024' into a pd.Timestamp"""
    month_map = {
        "januari": "01", "februari": "02", "maret": "03", "april": "04",
        "mei": "05", "juni": "06", "juli": "07", "agustus": "08",
        "september": "09", "oktober": "10", "november": "11", "desember": "12"
    }
    
    parts = date_str.lower().split()
    if len(parts) >= 3:
        day, month_id, year = parts[-3], parts[-2], parts[-1]
        month = month_map.get(month_id, "01")
        return pd.to_datetime(f"{year}-{month}-{day}")
    return pd.to_datetime("today")

def load_financial_data(processed_dir: Path = Path("data/processed")) -> pd.DataFrame:
    """Loads all JSON files and aggregates the main financial metrics into a DataFrame."""
    records = []
    
    if not processed_dir.exists():
        return pd.DataFrame()
        
    for json_file in processed_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            period_str = data.get("period_date", "")
            date_val = parse_indonesian_date(period_str)
            
            record = {
                "file_name": data.get("file_name"),
                "company_name": data.get("company_name"),
                "period_str": period_str,
                "date": date_val,
                "total_aset": 0.0,
                "total_liabilitas": 0.0,
                "total_ekuitas": 0.0,
                "laba_rugi_bersih": 0.0
            }
            
            for report in data.get("reports", []):
                title = report.get("report_title", "").upper()
                for category in report.get("categories", []):
                    cat_name = category.get("category_name", "").upper()
                    cat_total = category.get("category_total") or 0.0
                    
                    if "NERACA" in title:
                        if "ASET" in cat_name:
                            record["total_aset"] += cat_total
                        elif "LIABILITAS" in cat_name:
                            record["total_liabilitas"] += cat_total
                        elif "EKUITAS" in cat_name:
                            record["total_ekuitas"] += cat_total
                            
                            # Coba ekstrak Laba/Rugi dari items ekuitas jika ada
                            for item in category.get("items", []):
                                if "Laba/rugi" in item.get("item_name", ""):
                                    record["laba_rugi_bersih"] = item.get("item_value") or 0.0
                                    
                    elif "LABA RUGI" in title:
                        # Jika Laba Rugi ada sebagai total report
                        report_tot = report.get("report_total")
                        if report_tot is not None:
                            record["laba_rugi_bersih"] = report_tot
                            
            records.append(record)
            
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values("date").reset_index(drop=True)
    return df

def render_dashboard():
    st.header("📈 Business Insights Dashboard")
    st.markdown("Ringkasan kinerja keuangan berdasarkan data hasil ekstraksi.")
    
    df = load_financial_data()
    if df.empty:
        st.warning("Belum ada data JSON yang diproses di folder `data/processed`.")
        return
        
    latest_data = df.iloc[-1]
    
    # Format numbers (Data in Jutaan Rupiah, so Triliun = value / 1_000_000)
    def fmt_idr(val):
        return f"Rp {val/1_000_000:,.2f} T"
        
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Aset (Terbaru)", fmt_idr(latest_data["total_aset"]))
    col2.metric("Total Liabilitas (Terbaru)", fmt_idr(latest_data["total_liabilitas"]))
    col3.metric("Laba/Rugi (Terbaru)", fmt_idr(latest_data["laba_rugi_bersih"]))
    
    st.divider()
    
    # Chart: Aset vs Liabilitas over time
    st.subheader("Tren Aset & Liabilitas")
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=df["period_str"], y=df["total_aset"], 
        mode='lines+markers', name='Total Aset', 
        line=dict(color='#00C4B4', width=4),
        marker=dict(size=8)
    ))
    fig_trend.add_trace(go.Scatter(
        x=df["period_str"], y=df["total_liabilitas"], 
        mode='lines+markers', name='Total Liabilitas', 
        line=dict(color='#FF4B4B', width=4),
        marker=dict(size=8)
    ))
    fig_trend.update_layout(
        xaxis_title="Periode", 
        yaxis_title="Nilai (Jutaan Rupiah)",
        template="plotly_dark",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_trend, width="stretch")
    
    # Chart: Komposisi
    st.subheader("Komposisi Ekuitas & Liabilitas (Terbaru)")
    fig_pie = px.pie(
        values=[latest_data["total_liabilitas"], latest_data["total_ekuitas"]], 
        names=['Liabilitas', 'Ekuitas'], 
        hole=0.4,
        color_discrete_sequence=['#FF4B4B', '#00C4B4']
    )
    fig_pie.update_layout(
        template="plotly_dark", 
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_pie, width="stretch")
