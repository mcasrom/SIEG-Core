import streamlit as st
import json
import glob
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="S.I.E.G. Global Radar", page_icon="🛡", layout="wide")
st.cache_data.clear()

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
        background-color: #440000; border: 2px solid #ff0000;
        color: white; padding: 15px; border-radius: 5px;
        margin-bottom: 20px; font-weight: bold; text-align: center;
        animation: blinker 2s linear infinite;
    }
    @keyframes blinker { 50% { opacity: 0.5; } }
    </style>
    """, unsafe_allow_html=True)

df_h = pd.DataFrame()
if os.path.exists('data/history_log.csv'):
    try:
        df_h = pd.read_csv('data/history_log.csv', header=None, names=['timestamp', 'region', 'score'])
        df_h['timestamp'] = pd.to_numeric(df_h['timestamp'], errors='coerce')
        df_h = df_h.dropna(subset=['timestamp'])
    except: pass

# --- DETECCIÓN DE ANOMALÍAS ---
anomalies = []
if not df_h.empty:
    for region in df_h['region'].unique():
        reg_series = df_h[df_h['region'] == region].sort_values('timestamp', ascending=False)
        if len(reg_series) >= 6:
            diff = float(reg_series.iloc[0]['score']) - float(reg_series.iloc[5]['score'])
            if diff > 7:
                anomalies.append({"reg": region.upper(), "diff": diff})

with st.sidebar:
    st.header("📂 S.I.E.G. V11")
    t_met, t_arq = st.tabs(["Metodología", "Arquitectura"])
    with t_met: st.markdown("### 🔬 OSINT\nAlerta: $\Delta > 7$ en 180 min.")
    with t_arq: st.markdown("### 🏗 Nodo\nOdroid-C2 DietPi Sync.")
    st.divider()
    st.code("mybloggingnotes@gmail.com")

st.title("🛡 S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")

if anomalies:
    for a in anomalies:
        st.markdown(f"<div class='anomaly-box'>⚠️ ALERTA DE HOSTILIDAD: {a['reg']} (+{a['diff']:.1f} puntos)</div>", unsafe_allow_html=True)

if not df_h.empty:
    latest_ts = float(df_h['timestamp'].max())
    readable_ts = datetime.fromtimestamp(latest_ts).strftime('%d-%m-%Y %H:%M:%S')
    st.markdown(f"<div class='timestamp-box'>📡 ÚLTIMA SEÑAL: {readable_ts} | 📊 REGISTROS: {len(df_h)}</div>", unsafe_allow_html=True)

# --- VISUALIZACIÓN ---
files = sorted(glob.glob('data/geoint_*.json'))
data_list = []
for f in files:
    try:
        with open(f, 'r') as j:
            c = json.load(j)
            data_list.append({
                "REGIÓN": os.path.basename(f)[7:-5].replace("_", " ").upper(),
                "RIESGO %": float(c.get('score', 0)),
                "DISONANCIA": "⚠️ ALTA" if c.get('disonancia') else "✅ BAJA"
            })
    except: continue

if data_list:
    df_actual = pd.DataFrame(data_list)
    c_izq, c_der = st.columns(2)
    with c_izq:
        st.subheader("📊 Riesgo Actual")
        st.dataframe(df_actual, hide_index=True, use_container_width=True)
    with c_der:
        st.subheader("📈 Radar Regional")
        st.bar_chart(data=df_actual, x="REGIÓN", y="RIESGO %", color="#00ff41")

if not df_h.empty:
    st.divider()
    st.subheader("📉 Análisis de Tendencias Temporales")
    reg_sel = st.selectbox("Región:", sorted(df_h['region'].unique()))
    df_h['dt'] = pd.to_datetime(df_h['timestamp'], unit='s')
    df_p = df_h[df_h['region'] == reg_sel].sort_values('dt')
    st.line_chart(data=df_p, x='dt', y='score', color="#00ff41", height=400, use_container_width=True)

st.divider()
st.caption("S.I.E.G. V11 | 2026")
