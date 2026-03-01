import streamlit as st
import pandas as pd
import json
import glob
import os
from datetime import datetime

st.set_page_config(page_title="S.I.E.G. V11.7", page_icon="🛡", layout="wide")

# CSS BLINDADO
st.markdown("<style>.stApp {background-color: #0c0e12; color: #00ff41;} .kpi-box {background: #1a1c23; border: 1px solid #00ff41; padding: 15px; border-radius: 5px; text-align: center;}</style>", unsafe_allow_html=True)

# --- CARGA DE DATOS SIN FILTROS NI CACHÉ ---
df = pd.DataFrame()
if os.path.exists('data/history_log.csv'):
    df = pd.read_csv('data/history_log.csv', header=None, names=['ts', 'reg', 'score'])
    df['ts'] = pd.to_numeric(df['ts'], errors='coerce')
    df = df.dropna().sort_values('ts')
    df['reg'] = df['reg'].str.upper().str.replace('M_ORIENTE', 'MEDIO ORIENTE').str.replace('IRAN', 'IRÁN (ACTOR)')

# --- SIDEBAR (TUS TABS ORIGINALES) ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN")
    t1, t2, t3 = st.tabs(["Metodología", "Arquitectura", "Acrónimos"])
    with t1: st.markdown("Análisis OSINT / Riesgo Geopolítico.")
    with t2: st.markdown("Nodo: Odroid-C2 | Cliente: Asus Vivobook")
    with t3: 
        if os.path.exists('data/acronimos.txt'):
            with open('data/acronimos.txt', 'r') as f: st.text(f.read())
    st.divider()
    st.code("mybloggingnotes@gmail.com")

st.title("🛡 S.I.E.G. INTELLIGENCE DASHBOARD")

# --- INDICADORES ---
if not df.empty:
    last_val = df.groupby('reg').last().reset_index().sort_values('score', ascending=False)
    cols = st.columns(3)
    for i in range(min(3, len(last_val))):
        with cols[i]:
            st.markdown(f"<div class='kpi-box'><b>{last_val.iloc[i]['reg']}</b><br><span style='font-size: 2em;'>{last_val.iloc[i]['score']}%</span></div>", unsafe_allow_html=True)

    st.write("")
    st.info(f"📡 ÚLTIMA SEÑAL: {datetime.fromtimestamp(df['ts'].max()).strftime('%H:%M:%S')} | TOTAL REGISTROS: {len(df)}")

    # --- GRÁFICO RECONSTRUIDO (UNA SOLA PIEZA) ---
    st.subheader("📉 LÍNEA TEMPORAL UNIFICADA")
    df['Fecha'] = pd.to_datetime(df['ts'], unit='s')
    # Forzamos pivot para que el gráfico no se rompa
    chart_data = df.pivot_table(index='Fecha', columns='reg', values='score').interpolate()
    st.line_chart(chart_data)

st.divider()
st.caption("S.I.E.G. V11.7 | Emergency Sync Fix")
