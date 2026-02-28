import streamlit as st
import json
import glob
import os
import pandas as pd

# 1. Configuración de pantalla y Estilo Terminal M. Castillo
st.set_page_config(page_title="S.I.E.G. Global Radar", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    .stDataFrame { border: 1px solid #00ff41; }
    h1, h2, h3 { color: #00ff41 !important; border-bottom: 1px solid #224422; }
    .stAlert { background-color: #0e1117; color: #ff4b4b; border: 1px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN")
    st.markdown("""
    ### 🔬 Metodología S.I.E.G.
    - **Nodo:** Odroid-C2 (Analizador)
    - **Motor:** Intel Scanner V8.9
    - **Análisis:** Procesamiento OSINT y detección de disonancia geopolítica.
    ---
    **Analista:** M. Castillo
    """)

st.title("🛡️ S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")

# --- CARGA DE DATOS ACTUALES ---
files = sorted(glob.glob('data/geoint_*.json'))
data_list = []

for f in files:
    try:
        with open(f, 'r') as j:
            content = json.load(j)
            nombre = os.path.basename(f)[7:-5].replace("_", " ").upper()
            diso_val = content.get('disonancia', content.get('Disonancia', False))
            data_list.append({
                "REGIÓN": nombre,
                "RIESGO %": content.get('score', 0),
                "DISONANCIA": "⚠️ ALTA" if diso_val else "✅ BAJA",
                "ULT. ACTUALIZACIÓN": str(content.get('timestamp', 'N/A'))
            })
    except (json.JSONDecodeError, ValueError):
        continue

if data_list:
    df = pd.DataFrame(data_list)
    
    # Dashboard Layout (Tabla y Barras)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("📊 Riesgo Actual")
        st.dataframe(df, hide_index=True)
    with col2:
        st.subheader("📈 Radar Regional")
        st.bar_chart(df, x="REGIÓN", y="RIESGO %", color="#00ff41")

    # --- NUEVA SECCIÓN: GRÁFICO HISTÓRICO ---
    st.divider()
    st.subheader("📉 Análisis de Tendencias Temporales")
    history_path = 'data/history_log.csv'

    if os.path.exists(history_path):
        df_hist = pd.read_csv(history_path)
        df_hist['timestamp'] = pd.to_datetime(df_hist['timestamp'])
        
        # Selector de región para no saturar el gráfico
        regiones_disponibles = sorted(df_hist['region'].unique())
        region_sel = st.selectbox("Seleccione región para ver histórico:", regiones_disponibles)
        
        # Filtrar y mostrar gráfico de líneas
        df_plot = df_hist[df_hist['region'] == region_sel].sort_values('timestamp')
        st.line_chart(df_plot, x="timestamp", y="score", color="#00ff41")
    else:
        st.info("🕒 Esperando a que la Odroid genere el archivo 'history_log.csv'...")

else:
    st.warning("No se detectan flujos de datos. Verifique el nodo Odroid.")

st.divider()
st.caption("SISTEMA DE INTELIGENCIA ESTRATÉGICA GLOBAL - V8.9 | 2026")
