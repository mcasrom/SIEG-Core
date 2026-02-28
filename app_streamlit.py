cat << 'EOF' > app_streamlit.py
import streamlit as st
import json
import glob
import os
import pandas as pd

# Configuración visual de M. Castillo
st.set_page_config(page_title="S.I.E.G. Global Radar", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    .stDataFrame { border: 1px solid #00ff41; }
    h1, h2, h3 { color: #00ff41 !important; border-bottom: 1px solid #004411; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")
st.write(f"**Analista:** M. Castillo | **Nodo Principal:** Odroid-C2")

# Cargar datos de la carpeta data/
files = sorted(glob.glob('data/geoint_*.json'))
data_list = []

if not files:
    st.error("No se encontraron archivos JSON en la carpeta 'data/'. Ejecuta primero el scanner.")
else:
    for f in files:
        try:
            with open(f, 'r') as j:
                content = json.load(j)
                # Extraer nombre limpio del archivo
                nombre = os.path.basename(f)[7:-5].replace("_", " ").upper()
                diso_val = content.get('disonancia', content.get('Disonancia', False))
                
                data_list.append({
                    "REGIÓN": nombre,
                    "RIESGO %": content.get('score', 0),
                    "DISONANCIA": "⚠️ ALTA" if diso_val else "✅ BAJA",
                    "ULT. ACTUALIZACIÓN": str(content.get('timestamp', 'N/A'))
                })
        except (json.JSONDecodeError, ValueError):
            # Si el archivo está corrupto o vacío, lo saltamos
            continue

    if data_list:
        df = pd.DataFrame(data_list)

        # Dashboard Layout
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("📊 Tabla de Riesgo")
            st.dataframe(df, hide_index=True)

        with col2:
            st.subheader("📈 Mapa de Calor de Conflictos")
            st.bar_chart(df, x="REGIÓN", y="RIESGO %", color="#00ff41")
            
            # Alerta Crítica
            top_risk = df.loc[df['RIESGO %'].idxmax()]
            st.warning(f"ALERTA MÁXIMA: {top_risk['REGIÓN']} con {top_risk['RIESGO %']}% de riesgo.")
    else:
        st.info("Esperando datos válidos de la Odroid...")

st.divider()
st.caption("SISTEMA DE INTELIGENCIA ESTRATÉGICA GLOBAL - V8.7")
EOF
