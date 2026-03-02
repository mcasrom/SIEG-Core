"""
S.I.E.G. - Geopolitical Intelligence Engine
Dashboard V12.0 — Visualizacion avanzada, heatmap, gauges, tabs por actor,
filtros de riesgo, indicadores de tendencia, mapa mundial.
"""

import glob
import json
import logging
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# CONFIGURACION
# ---------------------------------------------------------------------------
DATA_DIR        = "data"
HISTORY_FILE    = os.path.join(DATA_DIR, "history_log.csv")
GEOINT_PATTERN  = os.path.join(DATA_DIR, "geoint_*.json")
ACRONIMOS_FILE  = os.path.join(DATA_DIR, "acronimos.txt")

ANOMALY_THRESHOLD = 7
ANOMALY_WINDOW    = 6

APP_VERSION     = "V12.0"
SCANNER_VERSION = "V9.0"
BUILD_DATE      = "2026"

# JSONs obsoletos a ignorar (versiones antiguas del scanner)
OBSOLETE_ACTORS = {"asia", "europa", "m_oriente"}

# Mapeo nombre interno -> display
DISPLAY_MAP = {
    "IRAN_M_ORIENTE": "🇮🇷 Iran / M.Oriente",
    "RUSIA_UCRANIA":  "🇷🇺 Rusia / Ucrania",
    "NORTH_KOREA":    "🇰🇵 Corea del Norte",
    "ASIA_PACIFICO":  "🌏 Asia Pacifico",
    "EUROPA_CORE":    "🇪🇺 Europa Core",
    "USA":            "🇺🇸 USA",
    "CHINA":          "🇨🇳 China",
    "ESPANA":         "🇪🇸 Espana",
    "LATAM":          "🌎 Latam",
    "MEXICO":         "🇲🇽 Mexico",
    "ARGENTINA":      "🇦🇷 Argentina",
    "BRASIL":         "🇧🇷 Brasil",
    "SAHEL":          "🌍 Sahel",
    "AUSTRALIA":      "🇦🇺 Australia",
}

# Coordenadas para mapa mundial (lat, lon)
COORDS = {
    "IRAN_M_ORIENTE": (32.0,  53.0),
    "RUSIA_UCRANIA":  (55.0,  37.0),
    "NORTH_KOREA":    (40.0, 127.0),
    "ASIA_PACIFICO":  (35.0, 105.0),
    "EUROPA_CORE":    (50.0,  10.0),
    "USA":            (38.0, -97.0),
    "CHINA":          (35.0, 105.0),
    "ESPANA":         (40.0,  -3.0),
    "LATAM":          (-15.0,-60.0),
    "MEXICO":         (23.0, -102.0),
    "ARGENTINA":      (-34.0,-64.0),
    "BRASIL":         (-10.0,-55.0),
    "SAHEL":          (15.0,  10.0),
    "AUSTRALIA":      (-25.0,133.0),
}

logging.basicConfig(level=logging.WARNING, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
TERMINAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

.stApp { background-color: #0c0e12; color: #00ff41; }
.block-container { max-width: 98% !important; padding-top: 0.5rem; }

h1, h2, h3 { color: #00ff41 !important; font-family: 'Share Tech Mono', monospace; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background-color: #0f1a0f; border-bottom: 1px solid #00ff41; }
.stTabs [data-baseweb="tab"] { color: #00aa22; font-family: monospace; }
.stTabs [aria-selected="true"] { color: #00ff41 !important; border-bottom: 2px solid #00ff41 !important; }

/* Anomaly */
.anomaly-box {
    background-color: #550000; border: 2px solid #ff0000;
    color: white; padding: 12px 20px; border-radius: 5px;
    margin-bottom: 8px; font-weight: bold; text-align: center;
    font-family: monospace; letter-spacing: 0.05em;
    animation: blinker 2.5s linear infinite;
}
@keyframes blinker { 50% { opacity: 0.6; } }

/* Hero */
.hero-box {
    border: 1px solid #00ff41; border-top: 3px solid #00ff41;
    background: linear-gradient(180deg, #0f1a0f 0%, #0c0e12 100%);
    padding: 16px 22px; border-radius: 6px; margin-bottom: 18px;
    font-family: 'Share Tech Mono', monospace;
}
.hero-version { color: #00ff41; font-size: 0.72em; letter-spacing: 0.15em; opacity: 0.7; margin-bottom: 5px; }
.hero-timestamp { color: #00cc33; font-size: 1.0em; font-weight: bold; margin-bottom: 8px; }
.hero-objectives { color: #aaffbb; font-size: 0.80em; line-height: 1.8;
    border-top: 1px solid #1a3a1a; padding-top: 8px; margin-top: 4px; }
.hero-objectives span { color: #00ff41; font-weight: bold; }

/* Gauge cards */
.gauge-card {
    background: #0f1a0f; border: 1px solid #1a3a1a; border-radius: 6px;
    padding: 10px; margin-bottom: 8px; text-align: center; font-family: monospace;
}
.gauge-label { font-size: 0.75em; color: #aaffbb; letter-spacing: 0.1em; margin-bottom: 4px; }
.gauge-score { font-size: 1.6em; font-weight: bold; }
.gauge-delta { font-size: 0.8em; margin-top: 2px; }
.score-critical { color: #ff2222; }
.score-high     { color: #ff8800; }
.score-medium   { color: #ffdd00; }
.score-low      { color: #00ff41; }

/* Filter pills */
.filter-active { background: #00ff41; color: #000; padding: 2px 10px; border-radius: 12px; font-size: 0.8em; }

/* Dataframe override */
.stDataFrame { border: 1px solid #1a3a1a !important; }

/* Quality badge */
.quality-badge {
    display: inline-block; font-family: monospace;
    font-size: 0.70em; padding: 2px 8px; border-radius: 10px;
    margin-top: 3px; letter-spacing: 0.08em; font-weight: bold;
}
.quality-green  { background: #0a2a0a; color: #00ff41; border: 1px solid #00ff41; }
.quality-blue   { background: #0a1a2a; color: #00ccff; border: 1px solid #00ccff; }
.quality-yellow { background: #2a2a00; color: #ffdd00; border: 1px solid #ffdd00; }
.quality-orange { background: #2a1500; color: #ff8800; border: 1px solid #ff8800; }
.quality-red    { background: #2a0000; color: #ff2222; border: 1px solid #ff2222; }

/* Footer */
.sieg-footer {
    border-top: 1px solid #1a3a1a; margin-top: 30px;
    padding: 16px 0 8px 0; text-align: center;
    font-family: monospace; font-size: 0.78em; color: #558855;
    line-height: 2.2;
}
.sieg-footer a { color: #00ff41; text-decoration: none; }
.sieg-footer a:hover { text-decoration: underline; }
</style>
"""

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def score_color(score: float) -> str:
    if score >= 80: return "score-critical"
    if score >= 60: return "score-high"
    if score >= 40: return "score-medium"
    return "score-low"

def score_label(score: float) -> str:
    if score >= 80: return "CRITICO"
    if score >= 60: return "ALTO"
    if score >= 40: return "MEDIO"
    return "BAJO"

def trend_arrow(delta: float) -> str:
    if delta > 5:  return f"🔺 +{delta:.0f}"
    if delta < -5: return f"🔻 {delta:.0f}"
    if delta > 0:  return f"↑ +{delta:.0f}"
    if delta < 0:  return f"↓ {delta:.0f}"
    return "→ 0"

def normalize_timestamp(val) -> float:
    """Convierte timestamps ISO o unix float a unix float."""
    try:
        f = float(val)
        # Si es menor que 1e10 podria ser unix seconds normal
        return f
    except (ValueError, TypeError):
        pass
    try:
        return datetime.fromisoformat(str(val)).timestamp()
    except Exception:
        return float("nan")

# ---------------------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------------------

@st.cache_data(ttl=180)
def load_history() -> pd.DataFrame:
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame(columns=["timestamp", "region", "score", "dt"])
    try:
        df = pd.read_csv(HISTORY_FILE, header=None, names=["timestamp", "region", "score"])
        # Normalizar timestamps mixtos (ISO + unix float)
        df["timestamp"] = df["timestamp"].apply(normalize_timestamp)
        df = df.dropna(subset=["timestamp"])
        df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0.0)
        df["region"] = df["region"].str.upper().str.strip()
        # Filtrar actores obsoletos
        df = df[~df["region"].isin({o.upper() for o in OBSOLETE_ACTORS})]
        df["dt"] = pd.to_datetime(df["timestamp"], unit="s")
        return df.sort_values("dt")
    except Exception as e:
        logger.error("Error cargando historial: %s", e)
        return pd.DataFrame(columns=["timestamp", "region", "score", "dt"])


@st.cache_data(ttl=180)
def load_geoint_actors() -> list:
    files = sorted(glob.glob(GEOINT_PATTERN))
    actors = []
    for filepath in files:
        raw_name = os.path.basename(filepath)[7:-5].upper()
        if raw_name.lower() in OBSOLETE_ACTORS:
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = json.load(f)
            actors.append({
                "key":             raw_name,
                "display":         DISPLAY_MAP.get(raw_name, raw_name.replace("_", " ")),
                "score":           float(content.get("score", 0)),
                "disonancia":      bool(content.get("disonancia", False)),
                "noticias":        int(content.get("noticias_procesadas", 0)),
                "timestamp":       float(content.get("timestamp", 0)),
                "version":         content.get("version", "?"),
                "calidad_nivel":   content.get("calidad_nivel", "ROJO"),
                "calidad_emoji":   content.get("calidad_emoji", "🔴"),
                "calidad_css":     content.get("calidad_css", "red"),
                "fuentes_activas": int(content.get("fuentes_activas", 0)),
                "uso_fallback":    bool(content.get("uso_fallback", False)),
                "uso_web":         bool(content.get("uso_web", False)),
            })
        except (json.JSONDecodeError, OSError, ValueError) as e:
            logger.warning("Fichero omitido %s: %s", filepath, e)

    # Ordenar por score descendente
    return sorted(actors, key=lambda x: x["score"], reverse=True)


@st.cache_data(ttl=600)
def load_acronimos() -> str:
    if not os.path.exists(ACRONIMOS_FILE):
        return ""
    try:
        with open(ACRONIMOS_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


# ---------------------------------------------------------------------------
# LOGICA DE NEGOCIO
# ---------------------------------------------------------------------------

def detect_anomalies(df: pd.DataFrame) -> list:
    anomalies = []
    if df.empty:
        return anomalies
    for actor in df["region"].unique():
        series = df[df["region"] == actor].sort_values("timestamp", ascending=False)["score"]
        if len(series) >= ANOMALY_WINDOW:
            delta = float(series.iloc[0]) - float(series.iloc[ANOMALY_WINDOW - 1])
            if delta > ANOMALY_THRESHOLD:
                anomalies.append({"reg": actor.replace("_", " "), "diff": delta})
    return anomalies


def compute_trends(df: pd.DataFrame, actors: list) -> dict:
    """Calcula delta vs penultimo ciclo para cada actor."""
    trends = {}
    for a in actors:
        key = a["key"]
        series = df[df["region"] == key].sort_values("timestamp", ascending=False)["score"]
        if len(series) >= 2:
            trends[key] = float(series.iloc[0]) - float(series.iloc[1])
        else:
            trends[key] = 0.0
    return trends


# ---------------------------------------------------------------------------
# COMPONENTES UI
# ---------------------------------------------------------------------------

def render_hero(df: pd.DataFrame, n_actors: int) -> None:
    now_str    = datetime.now().strftime("%d-%m-%Y %H:%M:%S UTC")
    signal_str = "SIN SENAL"
    records    = 0
    if not df.empty:
        signal_str = datetime.fromtimestamp(float(df["timestamp"].max())).strftime("%d-%m-%Y %H:%M:%S")
        records    = len(df)

    st.markdown(f"""
    <div class='hero-box'>
        <div class='hero-version'>
            S.I.E.G. Dashboard {APP_VERSION} &nbsp;|&nbsp; Scanner {SCANNER_VERSION}
            &nbsp;|&nbsp; Ciclo: 30 min &nbsp;|&nbsp; Nodo: Odroid-C2 / DietPi
        </div>
        <div class='hero-timestamp'>
            📡 ULTIMA SENAL: {signal_str} &nbsp;|&nbsp;
            📊 REGISTROS: {records:,} &nbsp;|&nbsp;
            🕐 SESION: {now_str}
        </div>
        <div class='hero-objectives'>
            <span>[ OBJETIVO ]</span> Deteccion temprana de escalada cinetica y disonancia narrativa en actores geopoliticos.<br>
            <span>[ METODOLOGIA ]</span> OSINT multi-fuente · Scoring gradual 0-100 · Ponderacion CF · Ventana 3h.<br>
            <span>[ COBERTURA ]</span> {n_actors} actores / regiones · Alertas automaticas Delta &gt; {ANOMALY_THRESHOLD} pts.<br>
            <span>[ DOCTRINA ]</span> Sistema independiente · Uso exclusivo de fuentes abiertas (OSINT).
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_anomaly_alerts(anomalies: list) -> None:
    for a in anomalies:
        st.markdown(
            f"<div class='anomaly-box'>⚠ ALERTA DE HOSTILIDAD: "
            f"{a['reg']} (+{a['diff']:.1f} pts en 3h)</div>",
            unsafe_allow_html=True,
        )


def render_sidebar(actors: list, df: pd.DataFrame) -> None:
    with st.sidebar:
        st.header("📂 S.I.E.G. CONTROL")

        # Mini-resumen de estado
        if actors:
            n_critical = sum(1 for a in actors if a["score"] >= 80)
            n_high     = sum(1 for a in actors if 60 <= a["score"] < 80)
            st.markdown(f"""
            **Estado global:**
            🔴 Criticos: `{n_critical}` &nbsp;|&nbsp; 🟠 Altos: `{n_high}`
            """)
            st.divider()

        t_met, t_arq, t_acr = st.tabs(["Metodologia", "Arquitectura", "Acronimos"])

        with t_met:
            st.markdown("""
            **OSINT & Disonancia Cognitiva**

            El motor analiza frecuencia lexica y carga emocional en fuentes abiertas.

            - **Scoring:** Algoritmo ponderado por CF (Coeficiente de Fiabilidad)
            - **Anomalia:** Alerta cuando Delta > 7 pts en ventana de 3h
            - **Disonancia:** Divergencia sistematica entre fuentes establishment vs alternativas > 35 pts
            """)
        with t_arq:
            st.markdown("""
            **Infraestructura SIEG-Core**

            Nodo fisico **Odroid-C2** (ARM) · **DietPi v9.x**

            - Persistencia: CSV local (proteccion eMMC)
            - Sync: Git automatizado cada 30 min
            - Scanner: V9.2 autolearning 3 capas
            - Calidad: VERDE/AZUL/AMARILLO/NARANJA/ROJO
            """)
        with t_acr:
            acronimos = load_acronimos()
            st.text(acronimos) if acronimos else st.caption("Acronimos no indexados.")

        st.divider()
        st.markdown("**✉ Contacto**")
        st.code("mybloggingnotes@gmail.com", language=None)


def render_gauge_grid(actors: list, trends: dict, risk_filter: str) -> None:
    """Cuadricula de gauges por actor con score, nivel y tendencia."""
    filtered = actors
    if risk_filter != "TODOS":
        filtered = [a for a in actors if score_label(a["score"]) == risk_filter]

    if not filtered:
        st.info("No hay actores en este nivel de riesgo.")
        return

    cols_per_row = 4
    for i in range(0, len(filtered), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, actor in enumerate(filtered[i:i+cols_per_row]):
            with cols[j]:
                delta   = trends.get(actor["key"], 0.0)
                css_cls = score_color(actor["score"])
                nivel   = score_label(actor["score"])
                disstr  = "⚠ DISON" if actor["disonancia"] else ""
                arrow   = trend_arrow(delta)

                # Gauge plotly mini
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=actor["score"],
                    gauge={
                        "axis": {"range": [0, 100], "tickcolor": "#00ff41",
                                 "tickfont": {"color": "#00ff41", "size": 8}},
                        "bar":  {"color": "#ff2222" if actor["score"] >= 80
                                          else "#ff8800" if actor["score"] >= 60
                                          else "#ffdd00" if actor["score"] >= 40
                                          else "#00ff41"},
                        "bgcolor": "#0f1a0f",
                        "bordercolor": "#1a3a1a",
                        "steps": [
                            {"range": [0,  40], "color": "#0a140a"},
                            {"range": [40, 60], "color": "#1a1a00"},
                            {"range": [60, 80], "color": "#1a0d00"},
                            {"range": [80,100], "color": "#1a0000"},
                        ],
                    },
                    number={"font": {"color": "#00ff41", "size": 28}, "suffix": "%"},
                    title={"text": actor["display"], "font": {"color": "#aaffbb", "size": 11}},
                ))
                fig.update_layout(
                    height=180, margin=dict(t=40, b=10, l=10, r=10),
                    paper_bgcolor="#0c0e12", font_color="#00ff41",
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                st.markdown(
                    f"<div style='text-align:center;font-family:monospace;font-size:0.75em;color:#aaffbb'>"
                    f"{arrow} &nbsp; <b>{nivel}</b> &nbsp; {disstr}"
                    f"</div>"
                    f"<div style='text-align:center;margin-top:3px'>"
                    f"<span class='quality-badge quality-{actor.get('calidad_css','red')}'>"
                    f"{actor.get('calidad_emoji','🔴')} {actor.get('calidad_nivel','ROJO')}"
                    f"{'  FB' if actor.get('uso_fallback') else ''}"
                    f"{'  WEB' if actor.get('uso_web') else ''}"
                    f"</span></div>",
                    unsafe_allow_html=True,
                )


def render_world_map(actors: list) -> None:
    """Mapa mundial con intensidad de riesgo por region."""
    rows = []
    for a in actors:
        coords = COORDS.get(a["key"])
        if coords:
            rows.append({
                "lat":     coords[0],
                "lon":     coords[1],
                "score":   a["score"],
                "display": a["display"],
                "nivel":   score_label(a["score"]),
                "size":    max(a["score"] * 0.8, 10),
            })
    if not rows:
        st.warning("Sin datos de coordenadas.")
        return

    df_map = pd.DataFrame(rows)
    fig = px.scatter_geo(
        df_map,
        lat="lat", lon="lon",
        size="size",
        color="score",
        color_continuous_scale=[
            [0.0,  "#00ff41"],
            [0.4,  "#ffdd00"],
            [0.6,  "#ff8800"],
            [1.0,  "#ff0000"],
        ],
        range_color=[0, 100],
        hover_name="display",
        hover_data={"score": True, "nivel": True, "lat": False, "lon": False, "size": False},
        projection="natural earth",
    )
    fig.update_layout(
        paper_bgcolor="#0c0e12",
        geo=dict(
            bgcolor="#0c0e12",
            landcolor="#0f1a0f",
            oceancolor="#050810",
            showocean=True,
            showland=True,
            showcountries=True,
            countrycolor="#1a3a1a",
            coastlinecolor="#1a3a1a",
            framecolor="#00ff41",
        ),
        coloraxis_colorbar=dict(
            tickfont={"color": "#00ff41"},
            title=dict(text="Score", font={"color": "#00ff41"}),
        ),
        margin=dict(t=10, b=10, l=0, r=0),
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_heatmap(df: pd.DataFrame) -> None:
    """Heatmap actores x tiempo con intensidad de riesgo."""
    if df.empty:
        st.info("Sin datos historicos para heatmap.")
        return

    # Pivotar: filas = actores, columnas = ventanas temporales (hora)
    df_h = df.copy()
    df_h["hora"] = df_h["dt"].dt.strftime("%m-%d %H:%M")
    pivot = df_h.pivot_table(index="region", columns="hora", values="score", aggfunc="mean")
    pivot = pivot.fillna(0)

    # Limitar a ultimas 48 columnas para legibilidad
    pivot = pivot[pivot.columns[-48:]]

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=[DISPLAY_MAP.get(r, r.replace("_", " ")) for r in pivot.index],
        colorscale=[
            [0.0,  "#0a140a"],
            [0.4,  "#1a4a00"],
            [0.6,  "#884400"],
            [0.8,  "#aa2200"],
            [1.0,  "#ff0000"],
        ],
        zmin=0, zmax=100,
        hoverongaps=False,
        hovertemplate="<b>%{y}</b><br>%{x}<br>Score: %{z:.0f}%<extra></extra>",
        colorbar=dict(
            tickfont={"color": "#00ff41"},
            title=dict(text="Score", font={"color": "#00ff41"}),
        ),
    ))
    fig.update_layout(
        paper_bgcolor="#0c0e12",
        plot_bgcolor="#0c0e12",
        font_color="#00ff41",
        xaxis=dict(tickangle=45, tickfont={"size": 8, "color": "#aaffbb"},
                   gridcolor="#1a3a1a"),
        yaxis=dict(tickfont={"size": 10, "color": "#aaffbb"},
                   gridcolor="#1a3a1a"),
        margin=dict(t=10, b=80, l=10, r=10),
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_comparative_chart(df: pd.DataFrame) -> None:
    """Grafico comparativo multi-actor en el mismo eje temporal."""
    if df.empty:
        return
    regions = sorted(df["region"].unique())
    selected = st.multiselect(
        "Seleccionar actores a comparar:",
        options=regions,
        default=regions[:4],
        format_func=lambda r: DISPLAY_MAP.get(r, r.replace("_", " ")),
    )
    if not selected:
        return

    fig = go.Figure()
    palette = ["#00ff41","#ff8800","#ff2222","#00ccff","#ffdd00",
               "#ff44aa","#44ffff","#aa44ff","#ffffff","#aaffbb"]

    for idx, region in enumerate(selected):
        df_r = df[df["region"] == region].sort_values("dt")
        fig.add_trace(go.Scatter(
            x=df_r["dt"],
            y=df_r["score"],
            mode="lines+markers",
            name=DISPLAY_MAP.get(region, region.replace("_", " ")),
            line=dict(color=palette[idx % len(palette)], width=2),
            marker=dict(size=4),
            hovertemplate="%{fullData.name}<br>%{x}<br>Score: %{y}%<extra></extra>",
        ))

    # Lineas de umbral
    for level, color, label in [(80,"#ff2222","CRITICO"), (60,"#ff8800","ALTO"), (40,"#ffdd00","MEDIO")]:
        fig.add_hline(y=level, line_dash="dot", line_color=color,
                      annotation_text=label, annotation_font_color=color,
                      annotation_font_size=9)

    fig.update_layout(
        paper_bgcolor="#0c0e12", plot_bgcolor="#0c0e12",
        font_color="#00ff41",
        xaxis=dict(gridcolor="#1a3a1a", tickfont={"color":"#aaffbb"}),
        yaxis=dict(range=[0,105], gridcolor="#1a3a1a", tickfont={"color":"#aaffbb"}),
        legend=dict(bgcolor="#0f1a0f", bordercolor="#1a3a1a",
                    font={"color":"#aaffbb","size":10}),
        margin=dict(t=20, b=20, l=10, r=10),
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_actor_detail_tab(actor: dict, df: pd.DataFrame, trends: dict) -> None:
    """Tab de detalle individual por actor."""
    key   = actor["key"]
    delta = trends.get(key, 0.0)
    css   = score_color(actor["score"])
    nivel = score_label(actor["score"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score actual", f"{actor['score']}%", f"{delta:+.1f} vs ciclo anterior")
    c2.metric("Nivel", nivel)
    c3.metric("Fuentes procesadas", actor["noticias"])
    c4.metric("Disonancia", "⚠ ALTA" if actor["disonancia"] else "✅ BAJA")

    # Historico del actor
    df_a = df[df["region"] == key].sort_values("dt")
    if not df_a.empty:
        fig = go.Figure(go.Scatter(
            x=df_a["dt"], y=df_a["score"],
            mode="lines+markers",
            fill="tozeroy",
            fillcolor="rgba(0,255,65,0.07)",
            line=dict(color="#00ff41", width=2),
            marker=dict(size=4, color="#00ff41"),
            hovertemplate="%{x}<br>Score: %{y}%<extra></extra>",
        ))
        fig.add_hline(y=80, line_dash="dot", line_color="#ff2222", annotation_text="CRITICO")
        fig.add_hline(y=60, line_dash="dot", line_color="#ff8800", annotation_text="ALTO")
        fig.update_layout(
            paper_bgcolor="#0c0e12", plot_bgcolor="#0c0e12",
            font_color="#00ff41",
            xaxis=dict(gridcolor="#1a3a1a", tickfont={"color":"#aaffbb"}),
            yaxis=dict(range=[0,105], gridcolor="#1a3a1a", tickfont={"color":"#aaffbb"}),
            margin=dict(t=20, b=20, l=10, r=10),
            height=280,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Stats basicas
        st.caption(
            f"Min: {df_a['score'].min():.0f}% · "
            f"Max: {df_a['score'].max():.0f}% · "
            f"Media: {df_a['score'].mean():.1f}% · "
            f"Registros: {len(df_a)}"
        )
    else:
        st.info("Sin datos historicos para este actor.")


def render_summary_table(actors: list, trends: dict) -> None:
    """Tabla resumen ordenada por score con tendencia."""
    rows = []
    for a in actors:
        delta = trends.get(a["key"], 0.0)
        rows.append({
            "Actor / Region":  a["display"],
            "Score %":         int(a["score"]),
            "Nivel":           score_label(a["score"]),
            "Tendencia":       trend_arrow(delta),
            "Disonancia":      "⚠ ALTA" if a["disonancia"] else "✅ BAJA",
            "Fuentes":         a["noticias"],
        })
    df_t = pd.DataFrame(rows)
    st.dataframe(
        df_t,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Score %": st.column_config.ProgressColumn(
                "Score %", min_value=0, max_value=100, format="%d%%"
            ),
        },
    )


# ---------------------------------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="S.I.E.G. Global Radar",
        page_icon="🛡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(TERMINAL_CSS, unsafe_allow_html=True)

    # Carga de datos
    df_history = load_history()
    actors     = load_geoint_actors()
    anomalies  = detect_anomalies(df_history)
    trends     = compute_trends(df_history, actors)

    render_sidebar(actors, df_history)

    # Cabecera
    st.title("🛡 S.I.E.G. - GEOPOLITICAL INTELLIGENCE ENGINE")
    render_hero(df_history, len(actors))
    render_anomaly_alerts(anomalies)

    # --- TABS PRINCIPALES ---
    tab_overview, tab_map, tab_heatmap, tab_comparative, tab_actors = st.tabs([
        "📊 Overview",
        "🌍 Mapa Mundial",
        "🔥 Heatmap",
        "📈 Comparativa",
        "🔍 Por Actor",
    ])

    with tab_overview:
        st.subheader("Estado Actual — Todos los Actores")

        # Filtro de riesgo
        risk_filter = st.radio(
            "Filtrar por nivel:",
            ["TODOS", "CRITICO", "ALTO", "MEDIO", "BAJO"],
            horizontal=True,
        )
        st.divider()

        render_gauge_grid(actors, trends, risk_filter)
        st.divider()
        render_summary_table(actors, trends)

    with tab_map:
        st.subheader("Mapa de Intensidad Global")
        st.caption("Tamano del circulo proporcional al score. Color: verde=bajo → rojo=critico.")
        render_world_map(actors)

    with tab_heatmap:
        st.subheader("Heatmap de Tension — Actores x Tiempo (ultimas 48 lecturas)")
        render_heatmap(df_history)

    with tab_comparative:
        st.subheader("Evolucion Comparativa Multi-Actor")
        render_comparative_chart(df_history)

    with tab_actors:
        st.subheader("Detalle por Actor")
        if actors:
            actor_names = [a["display"] for a in actors]
            sel_display = st.selectbox("Seleccionar actor:", actor_names)
            sel_actor   = next(a for a in actors if a["display"] == sel_display)
            render_actor_detail_tab(sel_actor, df_history, trends)
        else:
            st.info("Sin datos de actores disponibles.")

    st.markdown(f"""
    <div class='sieg-footer'>
        \U0001f6e1 S.I.E.G. Intelligence Radar {APP_VERSION} &nbsp;&middot;&nbsp;
        Scanner {SCANNER_VERSION} &nbsp;&middot;&nbsp;
        Geopolitical Open Source Intelligence<br>
        &copy; {BUILD_DATE} <b>M. Castillo</b> &nbsp;&middot;&nbsp;
        <a href='mailto:mybloggingnotes@gmail.com'>mybloggingnotes@gmail.com</a>
        &nbsp;&middot;&nbsp; Nodo: Odroid-C2 / DietPi
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
