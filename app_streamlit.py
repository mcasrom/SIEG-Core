import streamlit as st
import json
import glob
import os
import pandas as pd
from datetime import datetime

# 1. Configuración de página y limpieza total de memoria
st.set_page_config(page_title="S.I.E.G. Global Radar", page_icon="🛡", layout="wide")

# 2. CSS Blindado (V11.6)
st.markdown("""
    <style>
    .stApp { background-color: #0c0e12; color: #00ff41; }
    .block-container { max-width: 95% !important; padding-top: 1rem; }
    .timestamp-box { 
        color: #00ff41; font-family: monospace; font-size: 1.1em; 
        border: 1px solid #00ff41; padding: 10px; background: #1a1c23; 
        text-align: center; border-radius: 5px; margin-bottom: 20px;
    }
    .kpi-box {
        background: #1a1c23; border: 1px solid #00ff41;
        padding: 15px; border-radius: 5px; text-align: center;
    }
    h1, h2, h3 { color: #00ff41 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. LECTURA FORZADA DEL HISTORIAL (Sin caché)
df_h = pd.DataFrame()
CSV_PATH = 'data/history_log.csv'

if os.path.exists(CSV_PATH):
    try:
        # Leemos forzando tipos para evitar fallos de gráfico
        df_h = pd.read_csv(CSV_PATH, header=None, names=['ts', 'region', 'score'], on_bad_lines='skip')
        df_h['ts'] = pd.to_numeric(df_h['ts'], errors='coerce')
        df_h = df_h.dropna(subset=['ts'])
        # Normalización de nombres para el gráfico
        df_h['region'] = df_h['region'].str.upper().str.replace('M_ORIENTE', 'MEDIO ORIENTE').str.replace('IRAN', 'IRÁN (ACTOR)')
    except Exception as e:
        st.error(f"Error crítico en base de datos: {e}")

# --- SIDEBAR (INALTERABLE) ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN")
    t1, t2, t3 = st.tabs(["Metodología", "Arquitectura", "Acrónimos"])
    with t1: st.markdown("Análisis OSINT y Disonancia Cognitiva.")
    with t2: st.markdown("Nodo Odroid-C2 | DietPi v9.x")
    with t3:
        if os.path.exists('data/acronimos.txt'):
            with open('data/acronimos.txt', 'r') as f: st.text(f.read())
    st.divider()
    st.code("mybloggingnotes@gmail.com")

# --- PANEL PRINCIPAL ---
st.title("🛡 S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")

# CARGA DE ESTADO ACTUAL (JSON)
data_list = []
files = sorted(glob.glob('data/geoint_*.json'))
for f in files:
    try:
        with open(f, 'r') as j:
            c = json.load(j)
            name = os.path.basename(f)[7:-5].upper().replace("_", " ")
            data_list.append({"ACTOR": name, "RIESGO": float(c.get('score', 0)), "DISONANCIA": c.get('disonancia', False)})
    except: continue

# KPI TOP 3
if data_list:
    df_actual = pd.DataFrame(data_list).sort_values("RIESGO", ascending=False)
    cols = st.columns(3)
    for i, (idx, row) in enumerate(df_actual.head(3).iterrows()):
        with cols[i]:
            st.markdown(f"<div class='kpi-box'><small>TOP {i+1}</small><br><b>{row['ACTOR']}</b><br><span style='font-size: 2em;'>{row['RIESGO']}%</span></div>", unsafe_allow_html=True)

# TIMESTAMP Y CONTEO REAL
if not df_h.empty:
    last_ts = df_h['ts'].max()
    readable_ts = datetime.fromtimestamp(last_ts).strftime('%d-%m-%Y %H:%M:%S')
    st.markdown(f"<div class='timestamp-box'>📡 ÚLTIMA SEÑAL: {readable_ts} | 📊 REGISTROS TOTALES: {len(df_h)}</div>", unsafe_allow_html=True)

# GRÁFICO HISTÓRICO (RECONSTRUIDO)
if not df_h.empty:
    st.subheader("📉 Evolución de Tensiones")
    df_h['Fecha'] = pd.to_datetime(df_h['ts'], unit='s')
    # Selector de actor para limpiar el gráfico
    target = st.selectbox("Filtrar Historial:", sorted(df_h['region'].unique()))
    df_plot = df_h[df_h['region'] == target].sort_values('Fecha')
    st.line_chart(data=df_plot, x='Fecha', y='score', color="#00ff41")

# TABLA DE DATOS
if data_list:
    st.subheader("📊 Desglose Regional")
    st.dataframe(pd.DataFrame(data_list), hide_index=True, use_container_width=True)

st.caption("S.I.E.G. V11.6 | Emergency Restore | 2026")
