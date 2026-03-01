import streamlit as st
import json
import glob
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="S.I.E.G. Global Radar", page_icon="🛡", layout="wide")
st.cache_data.clear()

# CSS PROFESIONAL: Terminal Militar + Alertas
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

# --- CARGA DE DATOS ---
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
                anomalies.append({"reg": region.upper().replace("_", " "), "diff": diff})

# --- SIDEBAR: DOCUMENTACIÓN RESTAURADA ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN S.I.E.G.")
    t_met, t_arq, t_acr = st.tabs(["Metodología", "Arquitectura", "Acrónimos"])
    
    with t_met:
        st.markdown("### 🔬 OSINT & Disonancia\nAnálisis de señales geopolíticas mediante frecuencia léxica y divergencia narrativa. La alerta se dispara con $\Delta > 7$ en una ventana de 3 horas.")
    
    with t_arq:
        st.markdown("### 🏗 Nodo Odroid-C2\nInfraestructura física bajo Linux DietPi. Sincronización Git con protocolo de seguridad `--rebase` para integridad de datos.")
    
    with t_acr:
        if os.path.exists('data/acronimos.txt'):
            with open('data/acronimos.txt', 'r') as f:
                st.text(f.read())
        else:
            st.caption("Archivo acronimos.txt no detectado.")

    st.divider()
    st.markdown("### ✉️ CONTACTO")
    st.code("mybloggingnotes@gmail.com", language=None)

# --- PANEL PRINCIPAL ---
st.title("🛡 S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")

if anomalies:
    for a in anomalies:
        st.markdown(f"<div class='anomaly-box'>⚠️ ALERTA DE HOSTILIDAD: {a['reg']} (+{a['diff']:.1f} puntos detectados)</div>", unsafe_allow_html=True)

if not df_h.empty:
    latest_ts = float(df_h['timestamp'].max())
    readable_ts = datetime.fromtimestamp(latest_ts).strftime('%d-%m-%Y %H:%M:%S')
    st.markdown(f"<div class='timestamp-box'>📡 ÚLTIMA SEÑAL REGISTRADA: {readable_ts} | 📊 TOTAL PUNTOS: {len(df_h)}</div>", unsafe_allow_html=True)

# --- TABLAS Y GRÁFICOS ---
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
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("📊 Riesgo Regional")
        st.dataframe(df_actual, hide_index=True, use_container_width=True)
    with c2:
        st.subheader("📈 Radar de Intensidad")
        st.bar_chart(data=df_actual, x="REGIÓN", y="RIESGO %", color="#00ff41")

if not df_h.empty:
    st.divider()
    st.subheader("📉 Evolución de Tendencias (Histórico Panorámico)")
    reg_sel = st.selectbox("Región a inspeccionar:", sorted(df_h['region'].unique()))
    df_h['dt'] = pd.to_datetime(df_h['timestamp'], unit='s')
    df_p = df_h[df_h['region'] == reg_sel].sort_values('dt')
    st.line_chart(data=df_p, x='dt', y='score', color="#00ff41", height=400, use_container_width=True)

st.divider()
st.caption("S.I.E.G. V11.1 | 2026 | Sistema de Alertas de Hostilidad")
