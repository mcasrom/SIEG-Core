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
    .stDataFrame { border: 1px solid #224422; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.header("📂 DOCUMENTACIÓN")
    st.markdown("### 🔬 Metodología S.I.E.G.\n- **Analista:** M. Castillo\n- **Nodo:** Odroid-C2")

st.title("🛡️ S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")

# --- CARGA DE DATOS ACTUALES ---
files = sorted(glob.glob('data/geoint_*.json'))
data_list = []
for f in files:
    try:
        with open(f, 'r') as j:
            content = json.load(j)
            nombre = os.path.basename(f)[7:-5].replace("_", " ").upper()
            data_list.append({
                "REGIÓN": nombre,
                "RIESGO %": float(content.get('score', 0)),
                "DISONANCIA": "⚠️ ALTA" if content.get('disonancia', False) else "✅ BAJA"
            })
    except: continue

if data_list:
    df = pd.DataFrame(data_list)
    
    # Métricas Superiores
    top_region = df.loc[df['RIESGO %'].idxmax()]
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Riesgo Promedio Global", f"{df['RIESGO %'].mean():.1f}%")
    m_col2.metric("Foco Crítico", top_region['REGIÓN'], f"{top_region['RIESGO %']}%")

    # --- TABLA Y RADAR (BAR CHART) ---
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.subheader("📊 Tabla de Riesgo")
        st.dataframe(df, hide_index=True, use_container_width=True)
    
    with col_right:
        st.subheader("📈 Radar Regional")
        # Forzamos a Streamlit a entender qué columnas usar
        st.bar_chart(data=df, x="REGIÓN", y="RIESGO %", color="#00ff41")

    # --- HISTÓRICO (LINE CHART) ---
    st.divider()
    st.subheader("📉 Análisis de Tendencias Temporales")
    history_path = 'data/history_log.csv'

    if os.path.exists(history_path):
        df_hist = pd.read_csv(history_path)
        # Limpieza profunda de fechas
        df_hist['timestamp'] = pd.to_datetime(df_hist['timestamp'], errors='coerce')
        df_hist = df_hist.dropna(subset=['timestamp'])
        
        regiones = sorted(df_hist['region'].unique())
        region_sel = st.selectbox("Seleccione región para ver evolución:", regiones)
        
        # Filtramos y preparamos datos para el gráfico de líneas
        df_plot = df_hist[df_hist['region'] == region_sel].sort_values('timestamp')
        
        if not df_plot.empty:
            # IMPORTANTE: El gráfico de líneas necesita el tiempo como índice para mostrarse bien
            df_plot_final = df_plot.rename(columns={'timestamp': 'Fecha', 'score': 'Nivel de Riesgo'})
            st.line_chart(data=df_plot_final, x='Fecha', y='Nivel de Riesgo', color="#00ff41")
            st.caption(f"Historial de {region_sel}: {len(df_plot)} registros procesados.")
        else:
            st.info("No hay datos históricos suficientes para esta región.")
    else:
        st.warning("Archivo de historial no detectado.")
else:
    st.error("Error crítico: No se han podido cargar los archivos JSON de data/.")

st.divider()
st.caption("S.I.E.G. V9.3 | M. Castillo 2026")
