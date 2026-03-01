import streamlit as st
import json
import glob
import os
import pandas as pd

# 1. Configuración de pantalla y Estilo Terminal M. Castillo
st.set_page_config(
    page_title="S.I.E.G. Global Radar",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    .stDataFrame { border: 1px solid #00ff41; }
    h1, h2, h3 { color: #00ff41 !important; border-bottom: 1px solid #224422; }
    .stAlert { background-color: #0e1117; color: #ff4b4b; border: 1px solid #ff4b4b; }
    /* Estilo para métricas */
    [data-testid="stMetricValue"] { color: #00ff41 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN")
    st.markdown("""
    ### 🔬 Metodología S.I.E.G.
    - **Nodo:** Odroid-C2 (Analizador)
    - **Motor:** Intel Scanner V9.1
    - **Análisis:** Procesamiento OSINT y detección de disonancia geopolítica.
    ---
    **Analista Jefe:** M. Castillo
    """)

st.title("🛡️ S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")
st.write("🛰️ **Monitoreo Global en Tiempo Real** | Estado: Operativo")

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
    
    # --- SECCIÓN: RESUMEN EJECUTIVO (MÉTRICAS) ---
    top_region = df.loc[df['RIESGO %'].idxmax()]
    avg_risk = df['RIESGO %'].mean()
    high_diso = df[df['DISONANCIA'] == "⚠️ ALTA"].shape[0]

    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Riesgo Promedio Global", f"{avg_risk:.1f}%")
    m_col2.metric("Foco Crítico", top_region['REGIÓN'], f"{top_region['RIESGO %']}%")
    m_col3.metric("Alertas de Disonancia", high_diso)

    # --- DASHBOARD LAYOUT (TABLA Y BARRAS) ---
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("📊 Riesgo Actual")
        st.dataframe(df, hide_index=True)
    with col2:
        st.subheader("📈 Radar Regional")
        st.bar_chart(df, x="REGIÓN", y="RIESGO %", color="#00ff41")

    # --- SECCIÓN: NARRATIVA EXPANDIDA ---
    st.divider()
    st.header("🕵️ Análisis del Analista Jefe")
    
    for index, row in df.iterrows():
        with st.expander(f"Detalles de Inteligencia: {row['REGIÓN']}"):
            riesgo = row['RIESGO %']
            if riesgo > 70:
                st.error(f"**SITUACIÓN CRÍTICA**: Escalada de tensión detectada en {row['REGIÓN']}. Los parámetros indican una probabilidad alta de conflicto o inestabilidad inminente.")
            elif riesgo > 40:
                st.warning(f"**MONITOREO ACTIVO**: {row['REGIÓN']} presenta volatilidad moderada. Se observa ruido en las señales OSINT.")
            else:
                st.success(f"**ESTADO ESTABLE**: {row['REGIÓN']} se mantiene dentro de los márgenes de seguridad operativa.")
            
            if "ALTA" in row['DISONANCIA']:
                st.info("💡 **ALERTA DE DISONANCIA**: Existe una divergencia significativa entre las fuentes oficiales y los reportes de campo. Posible vector de desinformación.")

    # --- SECCIÓN: GRÁFICO HISTÓRICO ---
    st.divider()
    st.subheader("📉 Análisis de Tendencias Temporales")
    history_path = 'data/history_log.csv'

    if os.path.exists(history_path):
        df_hist = pd.read_csv(history_path)
        df_hist['timestamp'] = pd.to_datetime(df_hist['timestamp'], errors='coerce')
        df_hist = df_hist.dropna(subset=['timestamp'])
        
        regiones_disponibles = sorted(df_hist['region'].unique())
        region_sel = st.selectbox("Seleccione región para ver histórico:", regiones_disponibles)
        
        df_plot = df_hist[df_hist['region'] == region_sel].sort_values('timestamp')
        st.line_chart(df_plot, x="timestamp", y="score", color="#00ff41")
    else:
        st.info("🕒 Esperando a que la Odroid genere el archivo 'history_log.csv'...")

else:
    st.warning("No se detectan flujos de datos. Verifique el nodo Odroid.")

st.divider()
st.caption("SISTEMA DE INTELIGENCIA ESTRATÉGICA GLOBAL - V9.1 | M. CASTILLO 2026")
