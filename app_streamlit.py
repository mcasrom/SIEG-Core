import streamlit as st
import pandas as pd
import json
import glob
import os
from datetime import datetime

# 1. Configuración de página
st.set_page_config(page_title="S.I.E.G. V11.8", page_icon="🛡", layout="wide")

# 2. CSS Blindado (V11.3/4 Style)
st.markdown("""
    <style>
    .stApp { background-color: #0c0e12; color: #00ff41; }
    .kpi-box { background: #1a1c23; border: 1px solid #00ff41; padding: 15px; border-radius: 5px; text-align: center; margin-bottom: 10px; }
    .timestamp-box { color: #00ff41; font-family: monospace; border: 1px solid #00ff41; padding: 10px; background: #1a1c23; text-align: center; margin-bottom: 20px; }
    h1, h2, h3 { color: #00ff41 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. LECTURA DE DATOS (A PRUEBA DE ERRORES)
df_h = pd.DataFrame()
if os.path.exists('data/history_log.csv'):
    try:
        df_h = pd.read_csv('data/history_log.csv', header=None, names=['ts', 'reg', 'score'], on_bad_lines='skip')
        df_h['ts'] = pd.to_numeric(df_h['ts'], errors='coerce')
        # FORZAMOS score a ser flotante, si hay basura será NaN y lo borramos
        df_h['score'] = pd.to_numeric(df_h['score'], errors='coerce')
        df_h = df_h.dropna(subset=['ts', 'score'])
        df_h['reg'] = df_h['reg'].str.upper().str.replace('M_ORIENTE', 'MEDIO ORIENTE').str.replace('IRAN', 'IRÁN (ACTOR)')
    except: pass

# --- SIDEBAR: REINSTALACIÓN DE TABS (BLINDADOS) ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN")
    t_met, t_arq, t_acr = st.tabs(["Metodología", "Arquitectura", "Acrónimos"])
    with t_met:
        st.markdown("### 🔬 OSINT & Disonancia\nAnálisis de frecuencia léxica y carga emocional en señales abiertas.")
    with t_arq:
        st.markdown("### 🏗 Infraestructura\nNodo Odroid-C2 (ARM) | DietPi v9.x | Sincronización Git forzada.")
    with t_acr:
        if os.path.exists('data/acronimos.txt'):
            with open('data/acronimos.txt', 'r') as f: st.text(f.read())
        else: st.caption("No se detecta data/acronimos.txt")
    st.divider()
    st.code("mybloggingnotes@gmail.com")

# --- PANEL PRINCIPAL ---
st.title("🛡 S.I.E.G. INTELLIGENCE ENGINE")

# Carga de archivos JSON actuales
data_list = []
files = sorted(glob.glob('data/geoint_*.json'))
for f in files:
    try:
        with open(f, 'r') as j:
            c = json.load(j)
            name = os.path.basename(f)[7:-5].upper().replace("_", " ")
            data_list.append({"ACTOR": name, "RIESGO": float(c.get('score', 0)), "DISONANCIA": c.get('disonancia', False)})
    except: continue

# KPIs - TOP 3
if data_list:
    df_actual = pd.DataFrame(data_list).sort_values("RIESGO", ascending=False)
    cols = st.columns(3)
    for i, (idx, row) in enumerate(df_actual.head(3).iterrows()):
        with cols[i]:
            st.markdown(f"<div class='kpi-box'><small>TOP {i+1}</small><br><b>{row['ACTOR']}</b><br><span style='font-size: 2.2em;'>{row['RIESGO']}%</span></div>", unsafe_allow_html=True)

# TIMESTAMP Y CONTEO
if not df_h.empty:
    last_ts = df_h['ts'].max()
    readable_ts = datetime.fromtimestamp(last_ts).strftime('%d-%m-%Y %H:%M:%S')
    st.markdown(f"<div class='timestamp-box'>📡 ÚLTIMA SEÑAL: {readable_ts} | 📊 REGISTROS: {len(df_h)}</div>", unsafe_allow_html=True)

# GRÁFICO SEGURO (SIN PIVOT_TABLE)
if not df_h.empty:
    st.subheader("📈 Evolución Histórica")
    df_h['Fecha'] = pd.to_datetime(df_h['ts'], unit='s')
    actor_sel = st.selectbox("Seleccionar Actor para análisis:", sorted(df_h['reg'].unique()))
    df_p = df_h[df_h['reg'] == actor_sel].sort_values('Fecha')
    st.line_chart(data=df_p, x='Fecha', y='score', color="#00ff41")

# TABLA FINAL
if data_list:
    st.subheader("📊 Datos de Campo")
    st.dataframe(pd.DataFrame(data_list), hide_index=True, use_container_width=True)

st.caption("S.I.E.G. V11.8 | Emergency Restoration | 2026")
