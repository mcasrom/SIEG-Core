import streamlit as st
import json
import glob
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="S.I.E.G. Global Radar", page_icon="🛡", layout="wide")
st.cache_data.clear()

# CSS TERMINAL INTELIGENCIA
st.markdown("""
    <style>
    .stApp { background-color: #0c0e12; color: #00ff41; }
    .block-container { max-width: 95% !important; padding-top: 1rem; }
    .timestamp-box { 
        color: #00ff41; font-family: monospace; font-size: 1.1em; 
        border: 1px solid #00ff41; padding: 10px; background: #1a1c23; 
        text-align: center; border-radius: 5px; margin-bottom: 20px;
    }
    .anomaly-box {
        background-color: #550000; border: 2px solid #ff0000;
        color: white; padding: 15px; border-radius: 5px;
        margin-bottom: 20px; font-weight: bold; text-align: center;
        animation: blinker 2.5s linear infinite;
    }
    @keyframes blinker { 50% { opacity: 0.6; } }
    h1, h2, h3 { color: #00ff41 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA Y PROCESAMIENTO ---
df_h = pd.DataFrame()
if os.path.exists('data/history_log.csv'):
    try:
        df_h = pd.read_csv('data/history_log.csv', header=None, names=['timestamp', 'region', 'score'])
        df_h['timestamp'] = pd.to_numeric(df_h['timestamp'], errors='coerce')
        df_h = df_h.dropna(subset=['timestamp'])
        # Normalización de nombres de actores
        df_h['region'] = df_h['region'].str.replace('m_oriente', 'MEDIO ORIENTE')
        df_h['region'] = df_h['region'].str.replace('iran', 'IRÁN (ACTOR ESPECÍFICO)')
    except: pass

# --- DETECCIÓN DE ANOMALÍAS ---
anomalies = []
if not df_h.empty:
    for actor in df_h['region'].unique():
        reg_series = df_h[df_h['region'] == actor].sort_values('timestamp', ascending=False)
        if len(reg_series) >= 6:
            diff = float(reg_series.iloc[0]['score']) - float(reg_series.iloc[5]['score'])
            if diff > 7:
                anomalies.append({"reg": actor.upper().replace("_", " "), "diff": diff})

# --- SIDEBAR ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN S.I.E.G.")
    t_met, t_arq, t_acr = st.tabs(["Metodología", "Arquitectura", "Acrónimos"])
    with t_met:
        st.markdown("### 🔬 OSINT & Disonancia\nMonitoreo de actores estatales y regionales. Umbral crítico: $\Delta > 7$ pts / 180 min.")
    with t_arq:
        st.markdown("### 🏗 Nodo Odroid-C2\nActor IRÁN segregado para análisis de alta fidelidad.")
    with t_acr:
        if os.path.exists('data/acronimos.txt'):
            with open('data/acronimos.txt', 'r') as f: st.text(f.read())
    st.divider()
    st.markdown("### ✉️ CONTACTO")
    st.code("mybloggingnotes@gmail.com", language=None)

# --- PANEL PRINCIPAL ---
st.title("🛡 S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")

if anomalies:
    for a in anomalies:
        st.markdown(f"<div class='anomaly-box'>⚠️ ALERTA DE HOSTILIDAD: {a['reg']} (+{a['diff']:.1f} pts)</div>", unsafe_allow_html=True)

if not df_h.empty:
    latest_ts = float(df_h['timestamp'].max())
    readable_ts = datetime.fromtimestamp(latest_ts).strftime('%d-%m-%Y %H:%M:%S')
    st.markdown(f"<div class='timestamp-box'>📡 ÚLTIMA SEÑAL: {readable_ts} | 📊 PUNTOS TOTALES: {len(df_h)}</div>", unsafe_allow_html=True)

# --- MAPEO DE JSON A ACTORES ---
files = sorted(glob.glob('data/geoint_*.json'))
data_list = []
for f in files:
    try:
        with open(f, 'r') as j:
            c = json.load(j)
            nombre = os.path.basename(f)[7:-5].upper()
            if "IRAN" in nombre: nombre = "🇮🇷 IRÁN (ACTOR)"
            elif "M_ORIENTE" in nombre: nombre = "🌍 MEDIO ORIENTE (REGIONAL)"
            else: nombre = nombre.replace("_", " ")
            
            data_list.append({
                "ACTOR / REGIÓN": nombre,
                "RIESGO %": float(c.get('score', 0)),
                "DISONANCIA": "⚠️ ALTA" if c.get('disonancia') else "✅ BAJA"
            })
    except: continue

if data_list:
    df_actual = pd.DataFrame(data_list)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("📊 Riesgo Actual")
        st.dataframe(df_actual, hide_index=True, use_container_width=True)
    with c2:
        st.subheader("📈 Radar de Hostilidad")
        st.bar_chart(data=df_actual, x="ACTOR / REGIÓN", y="RIESGO %", color="#00ff41")

if not df_h.empty:
    st.divider()
    st.subheader("📉 Análisis de Tendencias Temporales")
    actor_sel = st.selectbox("Seleccionar Actor para Inspección:", sorted(df_h['region'].unique()))
    df_h['dt'] = pd.to_datetime(df_h['timestamp'], unit='s')
    df_p = df_h[df_h['region'] == actor_sel].sort_values('dt')
    st.line_chart(data=df_p, x='dt', y='score', color="#00ff41", height=400, use_container_width=True)

st.divider()
st.caption("S.I.E.G. V11.2 | Actor Irán Segregado | 2026")
