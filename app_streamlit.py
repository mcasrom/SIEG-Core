import streamlit as st
import json
import glob
import os
import pandas as pd
from datetime import datetime

# 1. Configuración de pantalla - M. Castillo
st.set_page_config(page_title="S.I.E.G. Global Radar", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    h1, h2, h3 { color: #00ff41 !important; border-bottom: 1px solid #224422; }
    [data-testid="stMetricValue"] { color: #00ff41 !important; }
    .stDataFrame { border: 1px solid #224422; }
    .timestamp-box { color: #00ff41; font-family: monospace; font-size: 0.9em; border: 1px solid #224422; padding: 8px; width: fit-content; background: #1a1c23; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL: TABS RESTAURADOS ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN")
    tab_met, tab_arq, tab_cnt = st.tabs(["Metodología", "Arquitectura", "Contacto"])
    with tab_met:
        st.markdown("### 🔬 S.I.E.G.\nAnálisis OSINT de señales geopolíticas.")
    with tab_arq:
        st.markdown("### 🏗️ Hardware\n- **Nodo:** Odroid-C2\n- **OS:** DietPi\n- **Sincro:** Git/Cron")
    with tab_cnt:
        st.markdown(f"**Analista Jefe:**\nM. Castillo\n\n**Estado:** Operativo")

st.title("🛡️ S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")

# --- PROCESAMIENTO DE DATOS ---
files = sorted(glob.glob('data/geoint_*.json'))
data_list = []
latest_raw_ts = 0

for f in files:
    try:
        with open(f, 'r') as j:
            content = json.load(j)
            nombre = os.path.basename(f)[7:-5].replace("_", " ").upper()
            ts_raw = float(content.get('timestamp', 0))
            if ts_raw > latest_raw_ts: latest_raw_ts = ts_raw
            data_list.append({
                "REGIÓN": nombre, "RIESGO %": float(content.get('score', 0)),
                "DISONANCIA": "⚠️ ALTA" if content.get('disonancia', False) else "✅ BAJA"
            })
    except: continue

# Fecha legible
readable_ts = datetime.fromtimestamp(latest_raw_ts).strftime('%d-%m-%Y %H:%M:%S') if latest_raw_ts > 0 else "N/A"

if data_list:
    df = pd.DataFrame(data_list)
    st.markdown(f"<div class='timestamp-box'>📡 ÚLTIMA SEÑAL RECIBIDA: {readable_ts}</div>", unsafe_allow_html=True)
    
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Riesgo Promedio Global", f"{df['RIESGO %'].mean():.1f}%")
    m_col2.metric("Foco Crítico", df.loc[df['RIESGO %'].idxmax()]['REGIÓN'], f"{df['RIESGO %'].max()}%")

    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.subheader("📊 Tabla de Riesgo")
        st.dataframe(df, hide_index=True, use_container_width=True)
    with col_r:
        st.subheader("📈 Radar Regional")
        st.bar_chart(data=df, x="REGIÓN", y="RIESGO %", color="#00ff41")

    # --- HISTÓRICO CONSOLIDADO ---
    st.divider()
    st.subheader("📉 Análisis de Tendencias Temporales")
    if os.path.exists('data/history_log.csv'):
        df_h = pd.read_csv('data/history_log.csv')
        df_h['timestamp'] = pd.to_datetime(df_h['timestamp'], unit='s', errors='coerce')
        df_h = df_h.dropna(subset=['timestamp']).sort_values('timestamp')
        
        reg_sel = st.selectbox("Región:", sorted(df_h['region'].unique()))
        df_plot = df_h[df_h['region'] == reg_sel]
        
        st.line_chart(data=df_plot, x='timestamp', y='score', color="#00ff41")
        st.caption(f"Registro: {len(df_plot)} puntos históricos.")

st.divider()
st.caption("S.I.E.G. V9.6 | M. CASTILLO 2026")
