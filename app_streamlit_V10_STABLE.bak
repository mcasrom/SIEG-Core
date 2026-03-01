import streamlit as st
import json
import glob
import os
import pandas as pd
from datetime import datetime

# 1. Configuración de pantalla TOTAL
st.set_page_config(page_title="S.I.E.G. Global Radar", page_icon="🛡", layout="wide")
st.cache_data.clear()

# CSS AGRESIVO para ancho total (Blindado)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    .block-container { max-width: 95% !important; padding-top: 1rem; padding-bottom: 1rem; }
    h1, h2, h3 { color: #00ff41 !important; border-bottom: 1px solid #224422; }
    .timestamp-box { 
        color: #00ff41; font-family: monospace; font-size: 1.2em; 
        border: 2px solid #00ff41; padding: 15px; background: #1a1c23; 
        margin-bottom: 25px; width: 100%; text-align: center; 
    }
    .stTabs [data-baseweb="tab-panel"] { color: #00ff41; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL: DOCUMENTACIÓN AMPLIADA (NO MÁS BREVE MIERDA) ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN TÉCNICA")
    t_met, t_arq, t_acr = st.tabs(["Metodología", "Arquitectura", "Acrónimos"])
    
    with t_met:
        st.markdown("""
        ### 🔬 Ciclo de Inteligencia OSINT
        El motor **S.I.E.G.** opera bajo un modelo de **análisis de fuentes abiertas (Open Source Intelligence)**. 
        * **Ingesta:** Recolección de señales mediante raspado de metadatos geopolíticos y monitorización de flujos de noticias.
        * **Cuantificación:** Las señales se transforman en una escala numérica de **0 a 100** mediante un algoritmo de frecuencia léxica.
        * **Disonancia:** Se calcula la divergencia entre la narrativa oficial y la actividad detectada en el terreno. Una **Disonancia Alta (⚠️)** indica un conflicto potencial inminente o desinformación activa.
        """)

    with t_arq:
        st.markdown("""
        ### 🏗 Infraestructura de Nodo Físico
        A diferencia de sistemas 100% cloud, el núcleo de cálculo reside en un entorno controlado:
        * **Hardware:** Nodo dedicado **Odroid-C2** (Amlogic S905, 2GB RAM).
        * **SO:** Linux (DietPi) optimizado para baja latencia.
        * **Persistencia:** Base de datos relacional ligera y logs históricos en CSV para evitar sobrecarga de E/S en tarjetas eMMC/SD.
        * **Sincronización:** Tubería de despliegue continuo vía **Git** cada 30 minutos, asegurando la integridad de los datos entre el nodo físico y la interfaz web.
        """)
        
    with t_acr:
        st.markdown("### 📑 Glosario Operativo")
        if os.path.exists('data/acronimos.txt'):
            with open('data/acronimos.txt', 'r') as f:
                st.text(f.read())
        else:
            st.info("Archivo acronimos.txt no detectado.")

    st.markdown("---")
    st.markdown("### ✉ CONTACTO")
    st.code("mybloggingnotes@gmail.com", language=None)

st.title("🛡 S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")

# --- CARGA DE DATOS ---
latest_ts = 0
num_regs = 0
df_h = pd.DataFrame()

if os.path.exists('data/history_log.csv'):
    try:
        df_h = pd.read_csv('data/history_log.csv', header=None, names=['timestamp', 'region', 'score'])
        if not df_h.empty:
            df_h['timestamp'] = pd.to_numeric(df_h['timestamp'], errors='coerce')
            df_h = df_h.dropna(subset=['timestamp'])
            latest_ts = float(df_h['timestamp'].max())
            num_regs = len(df_h)
    except: pass

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

# --- RENDERIZADO ---
if latest_ts > 0:
    readable_ts = datetime.fromtimestamp(latest_ts).strftime('%d-%m-%Y %H:%M:%S')
else:
    readable_ts = "SINCRONIZANDO..."

st.markdown(f"<div class='timestamp-box'>📡 ÚLTIMA SEÑAL REGISTRADA: {readable_ts} | 📊 TOTAL PUNTOS: {num_regs}</div>", unsafe_allow_html=True)

if data_list:
    df_actual = pd.DataFrame(data_list)
    c1, c2 = st.columns(2)
    c1.metric("Riesgo Promedio", f"{df_actual['RIESGO %'].mean():.1f}%")
    c2.metric("Estado del Sistema", "OPERATIVO", "SYNC OK")

    st.divider()
    col_izq, col_der = st.columns([1, 1])
    with col_izq:
        st.subheader("📊 Riesgo Actual")
        st.dataframe(df_actual, hide_index=True, use_container_width=True)
    with col_der:
        st.subheader("📈 Radar Regional")
        st.bar_chart(data=df_actual, x="REGIÓN", y="RIESGO %", color="#00ff41")

if not df_h.empty:
    st.divider()
    st.subheader("📉 Análisis de Tendencias Temporales (PANORÁMICO)")
    df_h['dt'] = pd.to_datetime(df_h['timestamp'], unit='s')
    reg_sel = st.selectbox("Filtrar Histórico por Región:", sorted(df_h['region'].unique()))
    df_p = df_h[df_h['region'] == reg_sel].sort_values('dt')
    
    st.line_chart(data=df_p, x='dt', y='score', color="#00ff41", height=400, use_container_width=True)

st.divider()
st.caption("S.I.E.G. V10.9 | 2026")
