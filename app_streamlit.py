import streamlit as st
import json
import glob
import os
import pandas as pd
from datetime import datetime

# 1. Configuración de pantalla - M. Castillo
st.set_page_config(page_title="S.I.E.G. Global Radar", page_icon="🛡", layout="wide")
st.cache_data.clear()

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    h1, h2, h3 { color: #00ff41 !important; border-bottom: 1px solid #224422; }
    [data-testid="stMetricValue"] { color: #00ff41 !important; }
    .stDataFrame { border: 1px solid #224422; background-color: #1a1c23; }
    .timestamp-box { 
        color: #00ff41; 
        font-family: monospace; 
        font-size: 1.1em; 
        border: 1px solid #224422; 
        padding: 12px; 
        background: #1a1c23; 
        margin-bottom: 25px; 
        width: 100%; 
        text-align: center; 
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN")
    t_met, t_arq, t_acr = st.tabs(["Metodología", "Arquitectura", "Acrónimos"])
    with t_met: st.markdown("### 🔬 OSINT\nEscaneo de señales y disonancia narrativa.")
    with t_arq: st.markdown("### 🏗 Nodo Odroid-C2\nLinux DietPi | Sincronización Git.")
    with t_acr:
        if os.path.exists('data/acronimos.txt'):
            with open('data/acronimos.txt', 'r') as f: st.text(f.read())
    st.markdown("---")
    st.markdown("### ✉ CONTACTO")
    st.code("mybloggingnotes@gmail.com", language=None)

st.title("🛡 S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")
st.markdown("##### *Análisis de la situación geopolítica global a través de esta interfaz de monitoreo*")

# --- PROCESAMIENTO DE DATOS ---
files = sorted(glob.glob('data/geoint_*.json'))
data_list = []
latest_raw_ts = 0

for f in files:
    try:
        with open(f, 'r') as j:
            content = json.load(j)
            ts_raw = float(content.get('timestamp', 0))
            if ts_raw > latest_raw_ts: latest_raw_ts = ts_raw
            data_list.append({
                "REGIÓN": os.path.basename(f)[7:-5].replace("_", " ").upper(),
                "RIESGO %": float(content.get('score', 0)),
                "DISONANCIA": "⚠️ ALTA" if content.get('disonancia', False) else "✅ BAJA"
            })
    except: continue

if data_list:
    df = pd.DataFrame(data_list)
    num_regs = 0
    if os.path.exists('data/history_log.csv'):
        # Lectura rápida para el contador
        num_regs = len(pd.read_csv('data/history_log.csv', header=None))
    
    readable_ts = datetime.fromtimestamp(latest_raw_ts).strftime('%d-%m-%Y %H:%M:%S')
    st.markdown(f"<div class='timestamp-box'>📡 ÚLTIMA SEÑAL RECIBIDA: {readable_ts} | 📊 REGISTROS EN HISTORIAL: {num_regs}</div>", unsafe_allow_html=True)
    
    m1, m2 = st.columns(2)
    m1.metric("Riesgo Promedio Global", f"{df['RIESGO %'].mean():.1f}%")
    m2.metric("Foco de Tensión Máxima", df.loc[df['RIESGO %'].idxmax()]['REGIÓN'], f"{df['RIESGO %'].max()}%")

    st.divider()
    
    # SECCIÓN 1: TABLA Y BAR_CHART (50/50)
    col_izq, col_der = st.columns([1, 1])
    with col_izq:
        st.subheader("📊 Riesgo Regional Actual")
        st.dataframe(df, hide_index=True, use_container_width=True)
    with col_der:
        st.subheader("📈 Radar Operativo")
        st.bar_chart(data=df, x="REGIÓN", y="RIESGO %", color="#00ff41")

    # SECCIÓN 2: HISTÓRICO (ANCHO TOTAL - SIN COLUMNAS)
    st.divider()
    st.subheader("📉 Análisis de Tendencias Temporales (Full-Width)")
    
    if os.path.exists('data/history_log.csv'):
        # Lectura robusta del histórico
        df_h = pd.read_csv('data/history_log.csv', header=None, names=['timestamp', 'region', 'score'])
        df_h['timestamp'] = pd.to_datetime(df_h['timestamp'], unit='s', errors='coerce')
        df_h = df_h.dropna(subset=['timestamp']).sort_values('timestamp')
        
        reg_sel = st.selectbox("Seleccione región para desglose histórico:", sorted(df_h['region'].unique()))
        df_p = df_h[df_h['region'] == reg_sel]
        
        # El gráfico ahora se expande a todo el ancho de la página (layout="wide")
        st.line_chart(data=df_p, x='timestamp', y='score', color="#00ff41", use_container_width=True)

st.divider()
st.caption("S.I.E.G. V10.6 | 2026")
