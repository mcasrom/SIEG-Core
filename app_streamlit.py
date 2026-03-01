import streamlit as st
import json
import glob
import os
import pandas as pd

# 1. Configuración de pantalla
st.set_page_config(page_title="S.I.E.G. Global Radar", page_icon="🛡️", layout="wide")

# Estilo Visual Terminal
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    h1, h2, h3 { color: #00ff41 !important; border-bottom: 1px solid #224422; }
    [data-testid="stMetricValue"] { color: #00ff41 !important; }
    .stDataFrame { border: 1px solid #224422; }
    .timestamp-box { color: #888; font-family: monospace; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL RESTAURADA ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN")
    tab1, tab2, tab3 = st.tabs(["Metodología", "Arquitectura", "Contacto"])
    with tab1:
        st.markdown("### 🔬 Metodología S.I.E.G.\nAnálisis OSINT de disonancia geopolítica mediante procesamiento de señales en tiempo real.")
    with tab2:
        st.markdown("### 🏗️ Arquitectura\n- **Nodo:** Odroid-C2\n- **Motor:** Intel Scanner V9.4\n- **Storage:** GitHub/CSV")
    with tab3:
        st.markdown("### ✉️ Contacto\n**Analista Jefe:** M. Castillo")

st.title("🛡️ S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")

# --- CARGA DE DATOS ---
files = sorted(glob.glob('data/geoint_*.json'))
data_list = []
latest_ts = "N/A"

for f in files:
    try:
        with open(f, 'r') as j:
            content = json.load(j)
            nombre = os.path.basename(f)[7:-5].replace("_", " ").upper()
            ts = content.get('timestamp', 'N/A')
            if ts != 'N/A': latest_ts = ts
            data_list.append({
                "REGIÓN": nombre,
                "RIESGO %": float(content.get('score', 0)),
                "DISONANCIA": "⚠️ ALTA" if content.get('disonancia', False) else "✅ BAJA",
                "ACTUALIZADO": ts
            })
    except: continue

if data_list:
    df = pd.DataFrame(data_list)
    
    # Cabecera con Timestamp General
    st.markdown(f"<p class='timestamp-box'>ÚLTIMA SEÑAL RECIBIDA: {latest_ts}</p>", unsafe_allow_html=True)
    
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Riesgo Promedio Global", f"{df['RIESGO %'].mean():.1f}%")
    m_col2.metric("Foco Crítico", df.loc[df['RIESGO %'].idxmax()]['REGIÓN'], f"{df['RIESGO %'].max()}%")

    # --- TABLA Y RADAR ---
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("📊 Tabla de Riesgo")
        st.dataframe(df[["REGIÓN", "RIESGO %", "DISONANCIA"]], hide_index=True, use_container_width=True)
    with c2:
        st.subheader("📈 Radar Regional")
        st.bar_chart(data=df, x="REGIÓN", y="RIESGO %", color="#00ff41")

    # --- HISTÓRICO REPARADO ---
    st.divider()
    st.subheader("📉 Análisis de Tendencias Temporales")
    history_path = 'data/history_log.csv'

    if os.path.exists(history_path):
        df_hist = pd.read_csv(history_path)
        # Limpieza de fechas forzando formato ISO si es posible
        df_hist['timestamp'] = pd.to_datetime(df_hist['timestamp'], errors='coerce')
        df_hist = df_hist.dropna(subset=['timestamp']).sort_values('timestamp')
        
        regiones = sorted(df_hist['region'].unique())
        region_sel = st.selectbox("Seleccione región para evolución:", regiones)
        
        df_plot = df_hist[df_hist['region'] == region_sel]
        
        if not df_plot.empty:
            # Gráfico con puntos visibles para confirmar datos
            st.line_chart(data=df_plot, x='timestamp', y='score', color="#00ff41")
            st.caption(f"Registro: {len(df_plot)} puntos detectados para {region_sel}.")
        else:
            st.info("No hay datos de serie temporal para esta región.")
    else:
        st.warning("Archivo de historial no detectado.")
else:
    st.error("Nodo Odroid desconectado o archivos de datos no encontrados.")

st.divider()
st.caption("S.I.E.G. V9.4 | M. Castillo 2026")
