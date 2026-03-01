"""
S.I.E.G. - Geopolitical Intelligence Engine
Versión limpiada: robustez, calidad PEP8, caché optimizado, modularización suave.
"""

import glob
import json
import logging
import os
from datetime import datetime

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# CONFIGURACIÓN CENTRALIZADA
# ---------------------------------------------------------------------------
DATA_DIR = "data"
HISTORY_FILE = os.path.join(DATA_DIR, "history_log.csv")
GEOINT_PATTERN = os.path.join(DATA_DIR, "geoint_*.json")
ACRONIMOS_FILE = os.path.join(DATA_DIR, "acronimos.txt")

ANOMALY_THRESHOLD = 7       # Δ puntos para disparar alerta roja
ANOMALY_WINDOW = 6          # Número de registros a comparar (≈ 3h)

ACTOR_NAME_MAP = {
    "IRAN": "🇮🇷 IRÁN (ACTOR)",
    "M_ORIENTE": "🌍 MEDIO ORIENTE (REGIONAL)",
}

APP_VERSION  = "V11.3"
SCANNER_VERSION = "V9.0"
BUILD_DATE   = "2026"

logging.basicConfig(level=logging.WARNING, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ESTILOS
# ---------------------------------------------------------------------------
TERMINAL_CSS = """
<style>
.stApp { background-color: #0c0e12; color: #00ff41; }
.block-container { max-width: 95% !important; padding-top: 1rem; }
.timestamp-box {
    color: #00ff41; font-family: monospace; font-size: 1.1em;
    border: 1px solid #00ff41; padding: 10px; background: #1a1c23;
    text-align: center; border-radius: 5px; margin-bottom: 20px;
}
.anomaly-box {
    background-color: #550000; border: 2px solid #ff0000;
    color: white; padding: 15px; border-radius: 5px;
    margin-bottom: 20px; font-weight: bold; text-align: center;
    animation: blinker 2.5s linear infinite;
}
@keyframes blinker { 50% { opacity: 0.6; } }
h1, h2, h3 { color: #00ff41 !important; }
.hero-box {
    border: 1px solid #00ff41;
    border-top: 3px solid #00ff41;
    background: linear-gradient(180deg, #0f1a0f 0%, #0c0e12 100%);
    padding: 18px 24px;
    border-radius: 6px;
    margin-bottom: 22px;
    font-family: monospace;
}
.hero-version {
    color: #00ff41;
    font-size: 0.75em;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    opacity: 0.7;
    margin-bottom: 6px;
}
.hero-timestamp {
    color: #00cc33;
    font-size: 1.05em;
    font-weight: bold;
    margin-bottom: 10px;
    letter-spacing: 0.05em;
}
.hero-objectives {
    color: #aaffbb;
    font-size: 0.82em;
    line-height: 1.8;
    border-top: 1px solid #1a3a1a;
    padding-top: 10px;
    margin-top: 6px;
}
.hero-objectives span { color: #00ff41; font-weight: bold; }
</style>
"""

# ---------------------------------------------------------------------------
# FUNCIONES DE CARGA — con caché real y manejo de errores explícito
# ---------------------------------------------------------------------------

def _normalize_region_name(raw: str) -> str:
    """Normaliza nombres de región al formato de display."""
    upper = raw.upper().replace("M_ORIENTE", "MEDIO ORIENTE").replace("IRAN", "IRÁN (ACTOR)")
    return upper


@st.cache_data(ttl=180)  # Caché de 3 minutos — consistente con ventana de anomalías
def load_history() -> pd.DataFrame:
    """Carga y normaliza el historial CSV. Devuelve DataFrame vacío si falla."""
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame(columns=["timestamp", "region", "score"])

    try:
        df = pd.read_csv(
            HISTORY_FILE,
            header=None,
            names=["timestamp", "region", "score"],
        )
        df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])
        df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0.0)
        df["region"] = df["region"].apply(_normalize_region_name)
        df["dt"] = pd.to_datetime(df["timestamp"], unit="s")  # Una sola vez, aquí
        return df
    except Exception as e:
        logger.error("Error cargando historial: %s", e)
        return pd.DataFrame(columns=["timestamp", "region", "score", "dt"])


@st.cache_data(ttl=180)
def load_geoint_actors() -> list[dict]:
    """Carga todos los ficheros geoint_*.json. Omite los corruptos con log."""
    files = sorted(glob.glob(GEOINT_PATTERN))
    actors = []

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = json.load(f)

            raw_name = os.path.basename(filepath)[7:-5].upper()  # strip 'geoint_' y '.json'
            display_name = ACTOR_NAME_MAP.get(raw_name, raw_name.replace("_", " "))

            actors.append({
                "ACTOR / REGIÓN": display_name,
                "RIESGO %": float(content.get("score", 0)),
                "DISONANCIA": "⚠ ALTA" if content.get("disonancia") else "✅ BAJA",
            })
        except (json.JSONDecodeError, OSError, ValueError) as e:
            logger.warning("Fichero omitido %s: %s", filepath, e)

    return actors


@st.cache_data(ttl=600)
def load_acronimos() -> str:
    """Carga el fichero de acrónimos. Devuelve string vacío si no existe."""
    if not os.path.exists(ACRONIMOS_FILE):
        return ""
    try:
        with open(ACRONIMOS_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        logger.warning("No se pudo leer acrónimos: %s", e)
        return ""


# ---------------------------------------------------------------------------
# LÓGICA DE NEGOCIO
# ---------------------------------------------------------------------------

def detect_anomalies(df: pd.DataFrame) -> list[dict]:
    """Detecta actores con incremento de riesgo > ANOMALY_THRESHOLD en la ventana."""
    anomalies = []
    if df.empty:
        return anomalies

    for actor in df["region"].unique():
        series = (
            df[df["region"] == actor]
            .sort_values("timestamp", ascending=False)["score"]
        )
        if len(series) >= ANOMALY_WINDOW:
            delta = float(series.iloc[0]) - float(series.iloc[ANOMALY_WINDOW - 1])
            if delta > ANOMALY_THRESHOLD:
                anomalies.append({
                    "reg": actor.upper().replace("_", " "),
                    "diff": delta,
                })
    return anomalies


# ---------------------------------------------------------------------------
# COMPONENTES UI
# ---------------------------------------------------------------------------

def render_hero(df: pd.DataFrame) -> None:
    """Bloque de identidad: versión, timestamp, objetivos — entre título y alertas."""
    now_str = datetime.now().strftime("%d-%m-%Y %H:%M:%S UTC")
    signal_str = "SIN SEÑAL"
    records = 0
    if not df.empty:
        latest_ts = float(df["timestamp"].max())
        signal_str = datetime.fromtimestamp(latest_ts).strftime("%d-%m-%Y %H:%M:%S")
        records = len(df)

    st.markdown(f"""
    <div class='hero-box'>
        <div class='hero-version'>
            ◈ S.I.E.G. Dashboard {APP_VERSION} &nbsp;|&nbsp;
            Scanner {SCANNER_VERSION} &nbsp;|&nbsp;
            Ciclo: 30 min &nbsp;|&nbsp;
            Nodo: Odroid-C2 / DietPi
        </div>
        <div class='hero-timestamp'>
            📡 &nbsp;ÚLTIMA SEÑAL: {signal_str}
            &nbsp;&nbsp;|&nbsp;&nbsp;
            📊 &nbsp;REGISTROS ACUMULADOS: {records:,}
            &nbsp;&nbsp;|&nbsp;&nbsp;
            🕐 &nbsp;SESIÓN: {now_str}
        </div>
        <div class='hero-objectives'>
            <span>[ OBJETIVO PRIMARIO ]</span>
            &nbsp; Detección temprana de escalada cinética y disonancia narrativa en actores geopolíticos globales.<br>
            <span>[ METODOLOGÍA ]</span>
            &nbsp; OSINT multi-fuente · Análisis léxico ponderado por CF · Scoring gradual 0–100 · Ventana temporal 3h.<br>
            <span>[ COBERTURA ]</span>
            &nbsp; 14 actores / regiones · {len(ACTOR_NAME_MAP) + 12} vectores de señal · Alertas automáticas Δ &gt; 7 pts.<br>
            <span>[ DOCTRINA ]</span>
            &nbsp; Sistema independiente sin fines comerciales · Uso exclusivo de fuentes abiertas (OSINT).
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar() -> None:
    with st.sidebar:
        st.header("📂 DOCUMENTACIÓN TÉCNICA")
        t_met, t_arq, t_acr = st.tabs(["Metodología", "Arquitectura", "Acrónimos"])

        with t_met:
            st.markdown("""
            ### 🔬 OSINT & Disonancia Cognitiva
            El motor analiza la **frecuencia léxica** y la **carga emocional** de señales
            en fuentes abiertas y oficiales.

            * **Cálculo de Riesgo:** Algoritmo ponderado sobre menciones de conflicto,
              movimientos cinéticos y declaraciones de hostilidad.
            * **Anomalía:** Alerta roja cuando un actor supera **Δ > 7 puntos** en
              una ventana de 180 minutos.
            """)

        with t_arq:
            st.markdown("""
            ### 🏗 Infraestructura SIEG-Core
            Implementación sobre nodo físico **Odroid-C2** (ARM) con **DietPi v9.x**.

            * **Persistencia:** CSV local para mitigar desgaste de eMMC.
            * **Sincronización:** Túnel Git automatizado con resolución forzada.
            * **Segregación:** Actores críticos operan con hilos de escaneo independientes.
            """)

        with t_acr:
            acronimos = load_acronimos()
            if acronimos:
                st.text(acronimos)
            else:
                st.caption("Archivo de acrónimos no indexado.")

        st.divider()
        st.markdown("### ✉ CANAL DE CONTACTO")
        st.code("mybloggingnotes@gmail.com", language=None)


def render_anomaly_alerts(anomalies: list[dict]) -> None:
    for a in anomalies:
        st.markdown(
            f"<div class='anomaly-box'>⚠ ALERTA DE HOSTILIDAD: "
            f"{a['reg']} (+{a['diff']:.1f} pts en 3h)</div>",
            unsafe_allow_html=True,
        )


def render_timestamp(df: pd.DataFrame) -> None:
    if df.empty:
        return
    latest_ts = float(df["timestamp"].max())
    readable = datetime.fromtimestamp(latest_ts).strftime("%d-%m-%Y %H:%M:%S")
    st.markdown(
        f"<div class='timestamp-box'>"
        f"📡 ÚLTIMA SEÑAL REGISTRADA: {readable} | 📊 REGISTROS: {len(df)}"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_actors_panel(actors: list[dict]) -> None:
    if not actors:
        return
    df_actual = pd.DataFrame(actors)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📊 Riesgo Actual")
        st.dataframe(df_actual, hide_index=True, use_container_width=True)
    with c2:
        st.subheader("📈 Intensidad")
        st.bar_chart(data=df_actual, x="ACTOR / REGIÓN", y="RIESGO %", color="#00ff41")


def render_history_chart(df: pd.DataFrame) -> None:
    if df.empty:
        return
    st.divider()
    st.subheader("📉 Evolución Histórica (Análisis de Actores)")
    sel = st.selectbox("Inspeccionar historial:", sorted(df["region"].unique()))
    df_plot = df[df["region"] == sel].sort_values("dt")
    st.line_chart(data=df_plot, x="dt", y="score", color="#00ff41", height=400, use_container_width=True)


# ---------------------------------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(page_title="S.I.E.G. Global Radar", page_icon="🛡", layout="wide")
    st.markdown(TERMINAL_CSS, unsafe_allow_html=True)

    # Carga de datos (con caché real — sin cache_data.clear() global)
    df_history = load_history()
    actors = load_geoint_actors()
    anomalies = detect_anomalies(df_history)

    render_sidebar()

    st.title("🛡 S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")
    render_hero(df_history)
    render_anomaly_alerts(anomalies)
    render_actors_panel(actors)
    render_history_chart(df_history)

    st.divider()
    st.caption(f"S.I.E.G. {APP_VERSION} · Scanner {SCANNER_VERSION} · Doctrina de Inteligencia Restaurada · {BUILD_DATE}")


if __name__ == "__main__":
    main()
