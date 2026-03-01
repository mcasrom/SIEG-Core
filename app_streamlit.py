import streamlit as st
import json
import glob
import os
import pandas as pd
from datetime import datetime

# 1. Configuración de pantalla
st.set_page_config(page_title="S.I.E.G. Global Radar", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    h1, h2, h3 { color: #00ff41 !important; border-bottom: 1px solid #224422; }
    [data-testid="stMetricValue"] { color: #00ff41 !important; }
    .timestamp-box { color: #888; font-family: monospace; font-size: 0.9em; border: 1px solid #224422; padding: 5px; width: fit-content; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN")
    st.markdown("### 🔬 Metodología S.I.E.G.\nAnalista Jefe: **M. Castillo**\nNodo: **Odroid-C2**")
    st.info("Arquitectura: V9.5 - Procesador de Señales Unix")

st.title("🛡️ S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")

# --- CARGA DE DATOS ---
files = sorted(glob.glob('data/geoint_*.json'))
data_list = []
latest_raw_ts = 0

for f in files:
    try:
        with open(f, 'r') as j:
            content = json.load(j)
            nombre = os.path.basename(f)[7:-5].replace("_", " ").upper()
            ts_raw = content.get('timestamp', 0)
            if float(ts_raw) > latest_raw_ts: latest_raw_ts = float(ts_raw)
            
            data_list.append({
                "REGIÓN": nombre,
                "RIESGO %": float(content.get('score', 0)),
                "DISONANCIA": "⚠️ ALTA" if content.get('disonancia', False) else "✅ BAJA"
            })
    except: continue

# Conversión de Timestamp para humanos
readable_ts = datetime.fromtimestamp(latest_raw_ts).strftime('%d-%m-%Y %H:%M:%S') if latest_raw_ts > 0 else "N/A"

if data_list:
    df = pd.DataFrame(data_list)
    st.markdown(f"<div class='timestamp-box'>📡 ÚLTIMA SEÑAL RECIBIDA: {readable_ts}</div>", unsafe_allow_html=True)
    
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Riesgo Promedio Global", f"{df['RIESGO %'].mean():.1f}%")
    m_col2.metric("Foco Crítico", df.loc[df['RIESGO %'].idxmax()]['REGIÓN'], f"{df['RIESGO %'].max()}%")

    # --- TABLA Y RADAR ---
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("📊 Tabla de Riesgo")
        st.dataframe(df, hide_index=True, use_container_width=True)
    with c2:
        st.subheader("📈 Radar Regional")
        st.bar_chart(data=df, x="REGIÓN", y="RIESGO %", color="#00ff41")

    # --- HISTÓRICO REPARADO (CONVERSIÓN UNIX) ---
    st.divider()
    st.subheader("📉 Análisis de Tendencias Temporales")
    history_path = 'data/history_log.csv'

    if os.path.exists(history_path):
        df_hist = pd.read_csv(history_path)
        
        # CONVERSIÓN CRÍTICA: Convertimos el número Unix en Fecha de Panda
        df_hist['timestamp'] = pd.to_datetime(df_hist['timestamp'], unit='s', errors='coerce')
        df_hist = df_hist.dropna(subset=['timestamp']).sort_values('timestamp')
        
        regiones = sorted(df_hist['region'].unique())
        region_sel = st.selectbox("Seleccione región para histórico:", regiones)
        
        df_plot = df_hist[df_hist['region'] == region_sel]
        
        if not df_plot.empty:
            # Forzamos el gráfico de líneas con el nuevo formato
            st.line_chart(data=df_plot, x='timestamp', y='score', color="#00ff41")
            st.caption(f"Registro: {len(df_plot)} señales procesadas para {region_sel}.")
        else:
            st.info("No hay datos para esta región.")
    else:
        st.warning("Archivo de historial no detectado.")
else:
    st.error("Esperando flujos de datos de la Odroid...")

st.divider()
st.caption("S.I.E.G. V9.5 | M. CASTILLO 2026")
