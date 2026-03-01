import streamlit as st
import pandas as pd
import json
import glob
import os
from datetime import datetime

st.set_page_config(page_title="S.I.E.G. SAFE MODE", layout="wide")

# CSS MÍNIMO PARA ESTABILIDAD
st.markdown("""<style>
    .stApp {background-color: #0c0e12; color: #00ff41;}
    .kpi {background: #1a1c23; border: 1px solid #00ff41; padding: 20px; border-radius: 10px; text-align: center;}
    h1, h2, h3 {color: #00ff41 !important;}
</style>""", unsafe_allow_html=True)

# --- CARGA DE DATOS (MODO SEGURO) ---
df_h = pd.DataFrame()
if os.path.exists('data/history_log.csv'):
    try:
        df_h = pd.read_csv('data/history_log.csv', header=None, names=['ts', 'reg', 'score'], on_bad_lines='skip')
        df_h['score'] = pd.to_numeric(df_h['score'], errors='coerce')
        df_h['ts'] = pd.to_numeric(df_h['ts'], errors='coerce')
        df_h = df_h.dropna().sort_values('ts')
    except: st.warning("Error leyendo histórico.")

# --- SIDEBAR (TABS RECUPERADOS) ---
with st.sidebar:
    st.title("🛡 S.I.E.G.")
    t1, t2, t3 = st.tabs(["Metodología", "Arquitectura", "Acrónimos"])
    with t1: st.write("Análisis OSINT / Disonancia.")
    with t2: st.write("Odroid-C2 -> Asus -> Cloud")
    with t3:
        if os.path.exists('data/acronimos.txt'):
            with open('data/acronimos.txt', 'r') as f: st.text(f.read())
    st.divider()
    st.code("mybloggingnotes@gmail.com")

st.title("S.I.E.G. INTELLIGENCE DASHBOARD")

# --- BLOQUE DE KPIs ---
data_list = []
for f in glob.glob('data/geoint_*.json'):
    try:
        with open(f, 'r') as j:
            c = json.load(j)
            name = os.path.basename(f)[7:-5].upper()
            data_list.append({"Actor": name, "Riesgo": float(c.get('score', 0))})
    except: continue

if data_list:
    df_act = pd.DataFrame(data_list).sort_values("Riesgo", ascending=False)
    cols = st.columns(3)
    for i in range(min(3, len(df_act))):
        with cols[i]:
            st.markdown(f"<div class='kpi'><b>{df_act.iloc[i]['Actor']}</b><br><h1>{df_act.iloc[i]['Riesgo']}%</h1></div>", unsafe_allow_html=True)

# --- INFO Y GRÁFICO ---
if not df_h.empty:
    st.success(f"Dato sincronizado: {len(df_h)} registros | Último: {datetime.fromtimestamp(df_h['ts'].max())}")
    st.subheader("Evolución Temporal")
    # Gráfico simple sin manipulaciones complejas
    sel = st.selectbox("Región", df_h['reg'].unique())
    st.line_chart(df_h[df_h['reg'] == sel].set_index('ts')['score'])
    
    st.subheader("Tabla Maestra")
    st.dataframe(df_act, use_container_width=True)

st.caption("S.I.E.G. V11.9 | SAFE MODE RESTORED")
