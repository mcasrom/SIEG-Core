import streamlit as st
import json
import glob
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="S.I.E.G. Global Radar", page_icon="🛡", layout="wide")
st.cache_data.clear()

# CSS TERMINAL DE INTELIGENCIA
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

# --- PROCESAMIENTO DE HISTORIAL ---
df_h = pd.DataFrame()
if os.path.exists('data/history_log.csv'):
    try:
        df_h = pd.read_csv('data/history_log.csv', header=None, names=['timestamp', 'region', 'score'])
        df_h['timestamp'] = pd.to_numeric(df_h['timestamp'], errors='coerce')
        df_h = df_h.dropna(subset=['timestamp'])
        df_h['region'] = df_h['region'].str.replace('m_oriente', 'MEDIO ORIENTE').str.replace('iran', 'IRÁN (ACTOR)')
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

# --- SIDEBAR: DOCTRINA EXPANDIDA ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN TÉCNICA")
    t_met, t_arq, t_acr = st.tabs(["Metodología", "Arquitectura", "Acrónimos"])
    
    with t_met:
        st.markdown("""
        ### 🔬 OSINT & Disonancia Cognitiva
        El motor analiza la **frecuencia léxica** y la **carga emocional** de señales en fuentes abiertas y oficiales. 
        
        * **Cálculo de Riesgo:** Algoritmo ponderado sobre menciones de conflicto, movimientos cinéticos y declaraciones de hostilidad.
        * **Anomalía:** El sistema dispara alerta roja cuando un actor sufre un incremento de riesgo **$\Delta > 7$ puntos** en una ventana temporal de 180 minutos (3 horas).
        """)
    
    with t_arq:
        st.markdown("""
        ### 🏗 Infraestructura SIEG-Core
        Implementación sobre nodo físico **Odroid-C2** (Arquitectura ARM) operando con **DietPi v9.x**.
        
        * **Persistencia:** Almacenamiento local en CSV para mitigar el desgaste de la eMMC.
        * **Sincronización:** Túnel Git automatizado con protocolo de resolución forzada para garantizar la disponibilidad del dato en Streamlit Cloud 24/7.
        * **Segregación:** Actores críticos (como Irán) operan con hilos de escaneo independientes.
        """)
    
    with t_acr:
        if os.path.exists('data/acronimos.txt'):
            with open('data/acronimos.txt', 'r') as f: st.text(f.read())
        else: st.caption("Archivo de acrónimos no indexado.")

    st.divider()
    st.markdown("### ✉️ CANAL DE CONTACTO")
    st.code("mybloggingnotes@gmail.com", language=None)

# --- PANEL PRINCIPAL ---
st.title("🛡 S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")

if anomalies:
    for a in anomalies:
        st.markdown(f"<div class='anomaly-box'>⚠️ ALERTA DE HOSTILIDAD: {a['reg']} (+{a['diff']:.1f} pts en 3h)</div>", unsafe_allow_html=True)

if not df_h.empty:
    latest_ts = float(df_h['timestamp'].max())
    readable_ts = datetime.fromtimestamp(latest_ts).strftime('%d-%m-%Y %H:%M:%S')
    st.markdown(f"<div class='timestamp-box'>📡 ÚLTIMA SEÑAL REGISTRADA: {readable_ts} | 📊 REGISTROS: {len(df_h)}</div>", unsafe_allow_html=True)

# --- CARGA DE ACTORES (JSON) ---
files = sorted(glob.glob('data/geoint_*.json'))
data_list = []
for f in files:
    try:
        with open(f, 'r') as j:
            c = json.load(j)
            name = os.path.basename(f)[7:-5].upper()
            if "IRAN" in name: name = "🇮🇷 IRÁN (ACTOR)"
            elif "M_ORIENTE" in name: name = "🌍 MEDIO ORIENTE (REGIONAL)"
            else: name = name.replace("_", " ")
            
            data_list.append({
                "ACTOR / REGIÓN": name,
                "RIESGO %": float(c.get('score', 0)),
                "DISONANCIA": "⚠️ ALTA" if c.get('disonancia') else "✅ BAJA"
            })
    except: continue

if data_list:
    df_actual = pd.DataFrame(data_list)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📊 Riesgo Actual")
        st.dataframe(df_actual, hide_index=True, use_container_width=True)
    with c2:
        st.subheader("📈 Intensidad")
        st.bar_chart(data=df_actual, x="ACTOR / REGIÓN", y="RIESGO %", color="#00ff41")

if not df_h.empty:
    st.divider()
    st.subheader("📉 Evolución Histórica (Análisis de Actores)")
    sel = st.selectbox("Inspeccionar historial:", sorted(df_h['region'].unique()))
    df_h['dt'] = pd.to_datetime(df_h['timestamp'], unit='s')
    df_p = df_h[df_h['region'] == sel].sort_values('dt')
    st.line_chart(data=df_p, x='dt', y='score', color="#00ff41", height=400, use_container_width=True)

st.divider()
st.caption("S.I.E.G. V11.3 | Doctrina de Inteligencia Restaurada | 2026")
