import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. Configuración radical: No hay caché, no hay memoria
st.set_page_config(page_title="S.I.E.G. BRUTE FORCE", layout="wide")

# 2. CSS para que al menos no te queme los ojos
st.markdown("<style>.stApp {background-color: #0c0e12; color: #00ff41;} h1 {color: #00ff41;}</style>", unsafe_allow_html=True)

st.title("🛡 S.I.E.G. - MODO DATOS PUROS")

# 3. LECTURA CRUDA (Sin decoradores, sin caché, directo al disco)
if os.path.exists('data/history_log.csv'):
    # Leemos el CSV ignorando cualquier error de formato
    df = pd.read_csv('data/history_log.csv', header=None, names=['ts', 'reg', 'score'], on_bad_lines='skip')
    
    # Limpieza rápida de tipos
    df['ts'] = pd.to_numeric(df['ts'], errors='coerce')
    df['score'] = pd.to_numeric(df['score'], errors='coerce')
    df = df.dropna()
    
    # MOSTRAR EL DATO REAL QUE HAY EN EL DISCO
    total_lineas = len(df)
    ultima_señal = datetime.fromtimestamp(df['ts'].max()).strftime('%d-%m-%Y %H:%M:%S')
    
    # Esto es lo que NO puede fallar:
    st.metric(label="📊 REGISTROS EN DISCO", value=total_lineas)
    st.metric(label="📡 HORA DEL ÚLTIMO DATO", value=ultima_señal)
    
    st.divider()
    
    # 4. TABLA DE ÚLTIMOS MOVIMIENTOS (Los 15 más recientes)
    st.subheader("Últimas 15 señales captadas por la Odroid")
    df_recent = df.sort_values('ts', ascending=False).head(15)
    st.table(df_recent)

else:
    st.error("NO SE ENCUENTRA EL ARCHIVO DE DATOS")

st.caption("S.I.E.G. V11.10 | MODO FUERZA BRUTA | SIN CACHÉ")
