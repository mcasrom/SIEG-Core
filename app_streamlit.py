import streamlit as st
import json
import glob
import os
import pandas as pd
from datetime import datetime

# 1. Configuración de pantalla TOTAL
st.set_page_config(page_title="S.I.E.G. Global Radar", page_icon="🛡", layout="wide")
st.cache_data.clear()

# CSS AGRESIVO para ancho total y visibilidad
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    /* Forzar ancho total real */
    .main .block-container { max-width: 100% !important; padding-left: 2rem; padding-right: 2rem; }
    h1, h2, h3 { color: #00ff41 !important; border-bottom: 1px solid #224422; }
    [data-testid="stMetricValue"] { color: #00ff41 !important; }
    .stDataFrame { border: 1px solid #224422; }
    .timestamp-box { 
        color: #00ff41; font-family: monospace; font-size: 1.2em; 
        border: 2px solid #00ff41; padding: 15px; background: #1a1c23; 
        margin-bottom: 25px; width: 100%; text-align: center; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN")
    t_met, t_arq, t_acr = st.tabs(["Metodología", "Arquitectura", "Acrónimos"])
    with t_met: st.markdown("### 🔬 OSINT\nEscaneo de señales y disonancia.")
    with t_arq: st.markdown("### 🏗 Nodo Odroid-C2\nLinux DietPi | Sincronización Git.")
    with t_acr:
        if os.path.exists('data/acronimos.txt'):
            with open('data/acronimos.txt', 'r') as f: st.text(f.read())
    st.markdown("---")
    st.markdown("### ✉ CONTACTO\nmybloggingnotes@gmail.com")

st.title("🛡 S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")
st.markdown("##### *Análisis de la situación geopolítica global*")

# --- PROCESAMIENTO DE DATOS ---
# 1. Intentar sacar la hora del historial (es más fiable ahora mismo)
latest_ts = 0
num_regs = 0
if os.path.exists('data/history_log.csv'):
    df_h = pd.read_csv('data/history_log.csv', header=None, names=['timestamp', 'region', 'score'])
    latest_ts = df_h['timestamp'].max()
    num_regs = len(df_h)

# 2. Cargar datos actuales de las regiones
files = sorted(glob.glob('data/geoint_*.json'))
data_list = []
for f in files:
    try:
        with open(f, 'r') as j:
            content = json.load(j)
            data_list.append({
                "REGIÓN": os.path.basename(f)[7:-5].replace("_", " ").upper(),
                "RIESGO %": float(content.get('score', 0)),
                "DISONANCIA": "⚠️ ALTA" if content.get('disonancia', False) else "✅ BAJA"
            })
    except: continue

# --- INTERFAZ ---
if not df_h.empty:
    readable_ts = datetime.fromtimestamp(latest_ts).strftime('%d-%m-%Y %H:%M:%S')
    st.markdown(f"<div class='timestamp-box'>📡 ÚLTIMA SEÑAL REGISTRADA: {readable_ts} | 📊 TOTAL PUNTOS: {num_regs}</div>", unsafe_allow_html=True)
    
    m1, m2 = st.columns(2)
    m1.metric("Riesgo Promedio", f"{pd.DataFrame(data_list)['RIESGO %'].mean() if data_list else 0:.1f}%")
    m2.metric("Estado del Sistema", "OPERATIVO", "SYNC OK")

    st.divider()
    col_izq, col_der = st.columns([1, 1])
    with col_izq:
        st.subheader("📊 Riesgo Actual")
        if data_list: st.dataframe(pd.DataFrame(data_list), hide_index=True, use_container_width=True)
    with col_der:
        st.subheader("📈 Radar Regional")
        if data_list: st.bar_chart(data=pd.DataFrame(data_list), x="REGIÓN", y="RIESGO %", color="#00ff41")

    # --- HISTÓRICO REALMENTE ANCHO ---
    st.divider()
    st.subheader("📉 Análisis de Tendencias Temporales (PANORÁMICO)")
    df_h['timestamp'] = pd.to_datetime(df_h['timestamp'], unit='s', errors='coerce')
    df_h = df_h.dropna(subset=['timestamp']).sort_values('timestamp')
    
    reg_sel = st.selectbox("Región:", sorted(df_h['region'].unique()))
    df_p = df_h[df_h['region'] == reg_sel]
    
    # Este gráfico ahora debe estirarse por el CSS inyectado arriba
    st.line_chart(data=df_p, x='timestamp', y='score', color="#00ff41", height=400)

st.divider()
st.caption(f"S.I.E.G. V10.7 | 2026")
