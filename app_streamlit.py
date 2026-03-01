import streamlit as st
import json
import glob
import os
import pandas as pd
from datetime import datetime

# 1. Configuración de pantalla
st.set_page_config(page_title="S.I.E.G. Global Radar", page_icon="🛡", layout="wide")

# Limpieza de caché forzada
st.cache_data.clear()

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    h1, h2, h3 { color: #00ff41 !important; border-bottom: 1px solid #224422; }
    [data-testid="stMetricValue"] { color: #00ff41 !important; }
    .timestamp-box { color: #00ff41; font-family: monospace; font-size: 0.9em; border: 1px solid #224422; padding: 8px; width: fit-content; background: #1a1c23; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN")
    t_met, t_arq, t_acr = st.tabs(["Metodología", "Arquitectura", "Acrónimos"])
    with t_met:
        st.markdown("### 🔬 OSINT & Disonancia\nAnálisis de señales geopolíticas en tiempo real.")
    with t_arq:
        st.markdown("### 🏗 Nodo Odroid-C2\nInfraestructura Linux DietPi persistente.")
    with t_acr:
        st.markdown("### 📑 Glosario")
        if os.path.exists('data/acronimos.txt'):
            with open('data/acronimos.txt', 'r') as f: st.text(f.read())

    st.markdown("---")
    st.markdown("### ✉ CONTACTO")
    st.code("mybloggingnotes@gmail.com", language=None)

st.title("🛡 S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")
st.markdown("##### *Análisis de la situación geopolítica global a través de esta interfaz de monitoreo*")

# --- PROCESAMIENTO ---
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

readable_ts = datetime.fromtimestamp(latest_raw_ts).strftime('%d-%m-%Y %H:%M:%S') if latest_raw_ts > 0 else "N/A"

if data_list:
    df = pd.DataFrame(data_list)
    st.markdown(f"<div class='timestamp-box'>📡 ÚLTIMA SEÑAL RECIBIDA: {readable_ts}</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    c1.metric("Riesgo Promedio Global", f"{df['RIESGO %'].mean():.1f}%")
    c2.metric("Foco Crítico", df.loc[df['RIESGO %'].idxmax()]['REGIÓN'], f"{df['RIESGO %'].max()}%")

    st.bar_chart(data=df, x="REGIÓN", y="RIESGO %", color="#00ff41")

    st.divider()
    st.subheader("📉 Análisis de Tendencias Temporales")
    if os.path.exists('data/history_log.csv'):
        df_h = pd.read_csv('data/history_log.csv', header=None, names=['timestamp', 'region', 'score'])
        df_h['timestamp'] = pd.to_datetime(df_h['timestamp'], unit='s', errors='coerce')
        df_h = df_h.dropna(subset=['timestamp']).sort_values('timestamp')
        
        reg_sel = st.selectbox("Seleccione región:", sorted(df_h['region'].unique()))
        df_p = df_h[df_h['region'] == reg_sel]
        st.line_chart(data=df_p, x='timestamp', y='score', color="#00ff41")
        st.caption(f"Registros en base de datos: {len(df_h)}")

st.divider()
st.caption(f"S.I.E.G. V10.3 | 2026")
