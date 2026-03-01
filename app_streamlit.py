import streamlit as st
import json
import glob
import os
import pandas as pd

# 1. Configuración de pantalla
st.set_page_config(page_title="S.I.E.G. Global Radar", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    h1, h2, h3 { color: #00ff41 !important; border-bottom: 1px solid #224422; }
    [data-testid="stMetricValue"] { color: #00ff41 !important; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.header("📂 DOCUMENTACIÓN")
    st.markdown("### 🔬 Metodología S.I.E.G.\n- **Analista:** M. Castillo\n- **Nodo:** Odroid-C2")

st.title("🛡️ S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")

# --- CARGA DE DATOS ---
files = sorted(glob.glob('data/geoint_*.json'))
data_list = []
for f in files:
    try:
        with open(f, 'r') as j:
            content = json.load(j)
            nombre = os.path.basename(f)[7:-5].replace("_", " ").upper()
            data_list.append({
                "REGIÓN": nombre,
                "RIESGO %": content.get('score', 0),
                "DISONANCIA": "⚠️ ALTA" if content.get('disonancia', False) else "✅ BAJA"
            })
    except: continue

if data_list:
    df = pd.DataFrame(data_list)
    top_region = df.loc[df['RIESGO %'].idxmax()]
    
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Riesgo Promedio", f"{df['RIESGO %'].mean():.1f}%")
    m_col2.metric("Foco Crítico", top_region['REGIÓN'], f"{top_region['RIESGO %']}%")

    st.subheader("📈 Radar Regional Actual")
    st.bar_chart(df, x="REGIÓN", y="RIESGO %", color="#00ff41")

    # --- SECCIÓN CRÍTICA: EL GRÁFICO HISTÓRICO ---
    st.divider()
    st.subheader("📉 Análisis de Tendencias Temporales")
    history_path = 'data/history_log.csv'

    if os.path.exists(history_path):
        df_hist = pd.read_csv(history_path)
        
        # FORZAMOS EL FORMATO DE FECHA
        df_hist['timestamp'] = pd.to_datetime(df_hist['timestamp'], errors='coerce')
        df_hist = df_hist.dropna(subset=['timestamp'])
        
        # Agregamos por si hay duplicados en el mismo minuto
        df_hist = df_hist.sort_values('timestamp')
        
        regiones = sorted(df_hist['region'].unique())
        region_sel = st.selectbox("Seleccione región:", regiones)
        
        # Filtro y preparación para gráfico de líneas
        df_plot = df_hist[df_hist['region'] == region_sel].copy()
        
        if not df_plot.empty:
            # Seteamos el índice para que Streamlit reconozca el eje temporal
            df_plot = df_plot.set_index('timestamp')
            st.line_chart(df_plot['score'], color="#00ff41")
            st.caption(f"Mostrando {len(df_plot)} registros históricos para {region_sel}")
        else:
            st.warning("No hay datos temporales para esta región específica.")
    else:
        st.info("🕒 No se encuentra el archivo history_log.csv")

st.divider()
st.caption("S.I.E.G. V9.1 | M. Castillo 2026")
