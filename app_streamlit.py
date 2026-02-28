import streamlit as st
import json
import glob
import os
import pandas as pd

# 1. Configuración de página y estilo "Terminal"
st.set_page_config(page_title="S.I.E.G. Global Radar", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    .stDataFrame { border: 1px solid #00ff41; }
    h1, h2, h3 { color: #00ff41 !important; border-bottom: 1px solid #224422; }
    .stAlert { background-color: #0e1117; color: #ff4b4b; border: 1px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (SIDEBAR) PARA METODOLOGÍA ---
with st.sidebar:
    st.header("📂 DOCUMENTACIÓN")
    st.markdown("""
    ### 🔬 Metodología S.I.E.G.
    El motor **Intel Scanner** utiliza una arquitectura de tres capas:
    1. **Recolección:** Scraping de fuentes OSINT y agencias de noticias en tiempo real.
    2. **Análisis:** Procesamiento de lenguaje natural (NLP) para detectar palabras clave de conflicto.
    3. **Puntuación:** Algoritmo ponderado que calcula el **Índice de Riesgo (%)**.

    ### 📟 Hardware
    - **Nodo Central:** Odroid-C2 (ARMv8).
    - **Frecuencia:** Escaneo cada 30 min.
    - **OS:** DietPi (Debian 12).

    ---
    **Author:** M. Castillo
    **Versión:** 8.8
    """)

# --- CUERPO PRINCIPAL ---
st.title("🛡️ S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")
st.write(f"**Estado del Sistema:** Operativo | **Ubicación:** Red Local de M. Castillo")

files = sorted(glob.glob('data/geoint_*.json'))
data_list = []

if not files:
    st.error("⚠️ Error Crítico: No se detectan flujos de datos en el nodo local.")
else:
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
        
        # Dashboard Principal
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("📊 Tabla de Riesgo")
            st.dataframe(df, hide_index=True)

        with col2:
            st.subheader("📈 Radar Geopolítico")
            st.bar_chart(df, x="REGIÓN", y="RIESGO %", color="#00ff41")
            
            # Alerta de Inteligencia
            top_risk = df.loc[df['RIESGO %'].idxmax()]
            st.error(f"⚠️ **PRIORIDAD 1:** {top_risk['REGIÓN']} presenta un nivel crítico del {top_risk['RIESGO %']}%")
    else:
        st.info("Esperando sincronización de datos desde la Odroid...")

st.divider()
st.caption("SISTEMA DE INTELIGENCIA ESTRATÉGICA GLOBAL - 2026")
