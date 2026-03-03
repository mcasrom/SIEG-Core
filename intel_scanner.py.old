#!/usr/bin/env python3
"""
S.I.E.G. - Intel Scanner V9.2
Novedades vs V9.1:
  - Autolearning 3 capas: primarias -> fallback -> Google News RSS
  - Indicador de calidad por actor: VERDE/AZUL/AMARILLO/NARANJA/ROJO
  - Umbral minimo: 60 noticias por actor
  - Fuentes aprendidas persistidas en data/sieg_learned_sources.json
  - Calidad guardada en geoint_*.json para visualizacion en dashboard
"""

import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path

import requests
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------------------
# CONFIGURACION
# ---------------------------------------------------------------------------

BASE_DIR       = Path(__file__).resolve().parent
DATA_DIR       = BASE_DIR / "data"
MAPA_FUENTES   = BASE_DIR / "mapa_fuentes.txt"
HISTORICO_FILE = DATA_DIR / "historico.json"
HISTORY_CSV    = DATA_DIR / "history_log.csv"
LEARNED_FILE   = DATA_DIR / "sieg_learned_sources.json"

RSS_ITEMS_POR_FUENTE = 20
TIMEOUT_HTTP         = 10
VERSION              = "V9.2"
MIN_NOTICIAS         = 60     # Umbral minimo aceptable por actor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("SIEG")

# ---------------------------------------------------------------------------
# INDICADOR DE CALIDAD
# ---------------------------------------------------------------------------

def calcular_calidad(n: int, fuentes_activas: int,
                     uso_fallback: bool, uso_web: bool) -> dict:
    if n >= 80:
        nivel, emoji, css = "VERDE",    "🟢", "green"
    elif n >= 60:
        nivel, emoji, css = "AZUL",     "🔵", "blue"
    elif n >= 40:
        nivel, emoji, css = "AMARILLO", "🟡", "yellow"
    elif n >= 20:
        nivel, emoji, css = "NARANJA",  "🟠", "orange"
    else:
        nivel, emoji, css = "ROJO",     "🔴", "red"
    return {
        "nivel": nivel, "emoji": emoji, "css": css,
        "fuentes_activas": fuentes_activas,
        "uso_fallback": uso_fallback, "uso_web": uso_web,
    }

# ---------------------------------------------------------------------------
# BANCO DE FUENTES ALTERNATIVAS (CAPA 2)
# ---------------------------------------------------------------------------

FALLBACK_SOURCES = {
    "Iran_M_Oriente": [
        {"url": "https://www.timesofisrael.com/feed/",              "cf": 0.7},
        {"url": "https://www.middleeasteye.net/rss",                "cf": 0.7},
        {"url": "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml", "cf": 0.9},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml", "cf": 0.9},
        {"url": "https://www.aljazeera.com/xml/rss/all.xml",        "cf": 0.7},
    ],
    "Rusia_Ucrania": [
        {"url": "https://feeds.bbci.co.uk/news/world/europe/rss.xml", "cf": 0.9},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Europe.xml", "cf": 0.9},
        {"url": "https://www.aljazeera.com/xml/rss/all.xml",        "cf": 0.7},
        {"url": "https://foreignpolicy.com/feed/",                  "cf": 0.9},
        {"url": "https://www.defensenews.com/rss/",                 "cf": 0.8},
    ],
    "USA": [
        {"url": "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml", "cf": 0.9},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/US.xml", "cf": 0.9},
        {"url": "https://feeds.skynews.com/feeds/rss/world.xml",    "cf": 0.8},
        {"url": "https://foreignpolicy.com/feed/",                  "cf": 0.9},
    ],
    "China": [
        {"url": "https://feeds.bbci.co.uk/news/world/asia/rss.xml", "cf": 0.9},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/AsiaPacific.xml", "cf": 0.9},
        {"url": "https://thediplomat.com/feed/",                    "cf": 0.8},
        {"url": "https://asia.nikkei.com/rss/feed/nar",             "cf": 0.8},
    ],
    "North_Korea": [
        {"url": "https://feeds.bbci.co.uk/news/world/asia/rss.xml", "cf": 0.9},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/AsiaPacific.xml", "cf": 0.9},
        {"url": "https://thediplomat.com/feed/",                    "cf": 0.8},
        {"url": "https://www.38north.org/feed/",                    "cf": 1.0},
    ],
    "Sahel": [
        {"url": "https://feeds.bbci.co.uk/news/world/africa/rss.xml", "cf": 0.9},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Africa.xml", "cf": 0.9},
        {"url": "https://www.aljazeera.com/xml/rss/all.xml",        "cf": 0.7},
        {"url": "https://www.africanews.com/feed/",                 "cf": 0.7},
    ],
    "Espana": [
        {"url": "https://feeds.bbci.co.uk/news/world/europe/rss.xml", "cf": 0.9},
        {"url": "https://www.elmundo.es/rss/portada.xml",           "cf": 0.8},
        {"url": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml", "cf": 0.8},
        {"url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada", "cf": 0.9},
    ],
    "Latam": [
        {"url": "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml", "cf": 0.9},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Americas.xml", "cf": 0.9},
        {"url": "https://www.aljazeera.com/xml/rss/all.xml",        "cf": 0.7},
    ],
    "Mexico": [
        {"url": "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml", "cf": 0.9},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Americas.xml", "cf": 0.9},
        {"url": "https://www.elsiglodetorreon.com.mx/rss/",         "cf": 0.7},
    ],
    "Argentina": [
        {"url": "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml", "cf": 0.9},
        {"url": "https://www.clarin.com/rss/mundo/",                "cf": 0.8},
        {"url": "https://www.lanacion.com.ar/arcio/rss/",           "cf": 0.8},
    ],
    "Brasil": [
        {"url": "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml", "cf": 0.9},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Americas.xml", "cf": 0.9},
        {"url": "https://www.bbc.com/portuguese/topics/c2lef98lz49t.rss", "cf": 0.9},
    ],
    "Asia_Pacifico": [
        {"url": "https://feeds.bbci.co.uk/news/world/asia/rss.xml", "cf": 0.9},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/AsiaPacific.xml", "cf": 0.9},
        {"url": "https://thediplomat.com/feed/",                    "cf": 0.8},
    ],
    "Europa_Core": [
        {"url": "https://feeds.bbci.co.uk/news/world/europe/rss.xml", "cf": 0.9},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Europe.xml", "cf": 0.9},
        {"url": "https://foreignpolicy.com/feed/",                  "cf": 0.9},
    ],
    "Australia": [
        {"url": "https://feeds.bbci.co.uk/news/world/asia/rss.xml", "cf": 0.9},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/AsiaPacific.xml", "cf": 0.9},
        {"url": "https://www.abc.net.au/news/feed/51120/rss.xml",   "cf": 0.9},
    ],
}

# ---------------------------------------------------------------------------
# GOOGLE NEWS RSS POR REGION (CAPA 3)
# ---------------------------------------------------------------------------

GOOGLE_NEWS_QUERIES = {
    "Iran_M_Oriente": "iran+israel+middle+east+conflict",
    "Rusia_Ucrania":  "russia+ukraine+war+military",
    "USA":            "united+states+military+geopolitics",
    "China":          "china+taiwan+military+south+china+sea",
    "North_Korea":    "north+korea+nuclear+missile+dprk",
    "Sahel":          "sahel+mali+niger+burkina+jihadist",
    "Espana":         "spain+espana+politics+crisis",
    "Latam":          "latin+america+crisis+military",
    "Mexico":         "mexico+security+cartel+military",
    "Argentina":      "argentina+crisis+political",
    "Brasil":         "brazil+crisis+political+military",
    "Asia_Pacifico":  "asia+pacific+military+conflict",
    "Europa_Core":    "europe+nato+military+security",
    "Australia":      "australia+defense+indo+pacific",
}

def build_google_news_url(region: str) -> str:
    query = GOOGLE_NEWS_QUERIES.get(region, region.lower().replace("_", "+"))
    return f"https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"

# ---------------------------------------------------------------------------
# VOCABULARIO (heredado de V9.1)
# ---------------------------------------------------------------------------

KINETIC_ALTO = [
    "bombardeo", "airstrike", "airstrikes", "missile strike", "missile strikes",
    "bombing", "bombed", "invasion", "ballistic", "warship", "frontline",
    "shelling", "artillery fire", "ground offensive", "military offensive",
    "encroachment", "drone strike", "drone attack", "struck", "strikes",
    "air raid", "air campaign", "killed in strike", "targeted strike",
]
KINETIC_MEDIO = [
    "misil", "ataque", "explosion", "combat", "interception",
    "troops deployed", "military buildup", "border clash", "skirmish",
    "armed forces", "ceasefire violation", "escalation", "retaliation",
    "retaliatory", "launched attack", "under attack", "offensive",
]
KINETIC_BAJO = [
    "tension", "warning", "threatens", "sanctions", "provocation",
    "protest", "unrest", "demonstration", "diplomatic crisis",
    "military exercise", "drills", "mobilize",
]
CRITICAL_ALERTS = [
    "nuclear", "icbm", "tactical nuke", "mobilization", "martial law",
    "nuclear warhead", "dirty bomb", "radiological", "chemical weapon",
    "mass casualty", "genocide",
]
DEESCALATION = [
    "ceasefire", "peace talks", "withdrawal", "diplomatic solution",
    "agreement reached", "negotiations", "truce", "summit",
]

REGION_ALIASES = {
    "iran":        ["iran", "iranian", "tehran", "irgc", "hezbollah",
                    "persian", "khamenei", "islamic republic"],
    "israel":      ["israel", "israeli", "idf", "tel aviv", "jerusalem",
                    "netanyahu", "mossad", "iron dome", "gaza", "west bank"],
    "rusia":       ["russia", "russian", "moscow", "kremlin", "putin",
                    "wagner", "rossiya"],
    "ucrania":     ["ukraine", "ukrainian", "kyiv", "kiev", "zelensky",
                    "azov", "dnipro", "kharkiv", "zaporizhzhia"],
    "china":       ["china", "chinese", "beijing", "xi jinping", "pla",
                    "peoples liberation", "ccp", "taiwan strait"],
    "north":       ["north korea", "north korean", "dprk", "kim jong",
                    "pyongyang", "korean peninsula"],
    "usa":         ["united states", "american", "washington", "pentagon",
                    "white house", "congress", "trump", "nato"],
    "sahel":       ["sahel", "mali", "niger", "burkina", "wagner africa",
                    "jihadist", "al-qaeda africa", "isis africa"],
}

SUELOS_BASE = {
    "rusia":   62, "ucrania": 68, "iran":  68,
    "m":       65, "israel":  72, "north": 35,
    "sahel":   32,
}
SUELO_AJUSTE_MAX = 15

# ---------------------------------------------------------------------------
# FUENTES APRENDIDAS
# ---------------------------------------------------------------------------

def cargar_aprendidas() -> dict:
    if not LEARNED_FILE.exists():
        return {}
    try:
        with open(LEARNED_FILE) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}

def guardar_aprendidas(aprendidas: dict) -> None:
    try:
        with open(LEARNED_FILE, "w") as f:
            json.dump(aprendidas, f, indent=2)
    except OSError as e:
        log.warning("No se pudo guardar fuentes aprendidas: %s", e)

# ---------------------------------------------------------------------------
# CARGA DE FUENTES PRIMARIAS
# ---------------------------------------------------------------------------

def cargar_mapa_fuentes() -> dict:
    fuentes = {}
    if not MAPA_FUENTES.exists():
        log.error("No se encuentra %s", MAPA_FUENTES)
        return {}
    with open(MAPA_FUENTES, "r", encoding="utf-8") as f:
        for linea in f:
            if linea.startswith("#") or not linea.strip():
                continue
            parts = [p.strip() for p in linea.split("|")]
            if len(parts) >= 3:
                try:
                    region, url, cf = parts[0], parts[1], float(parts[2])
                    fuentes.setdefault(region, []).append({"url": url, "cf": cf})
                except ValueError:
                    log.warning("Linea mal formada: %s", linea.strip())
    return fuentes

# ---------------------------------------------------------------------------
# FETCH RSS
# ---------------------------------------------------------------------------

def fetch_rss(fuentes_lista: list, region: str, label: str = "P") -> tuple:
    """Retorna (noticias, n_fuentes_activas)."""
    headers  = {"User-Agent": "Mozilla/5.0 (compatible; SIEG-Scanner/9.2)"}
    noticias = []
    activas  = 0
    for fuente in fuentes_lista:
        try:
            r = requests.get(fuente["url"], headers=headers, timeout=TIMEOUT_HTTP)
            r.raise_for_status()
            root  = ET.fromstring(r.content)
            items = root.findall(".//item")[:RSS_ITEMS_POR_FUENTE]
            if items:
                activas += 1
            for item in items:
                title_el = item.find("title")
                desc_el  = item.find("description")
                title    = (title_el.text or "") if title_el is not None else ""
                desc     = (desc_el.text  or "") if desc_el  is not None else ""
                noticias.append({
                    "text": f"{title} {re.sub(r'<[^>]+>', ' ', desc)}",
                    "cf":   fuente["cf"],
                })
        except requests.RequestException as e:
            if label == "P":
                log.warning("%s | Fuente no disponible: %s", region, e)
        except ET.ParseError as e:
            if label == "P":
                log.warning("%s | RSS malformado: %s", region, e)
    return noticias, activas

# ---------------------------------------------------------------------------
# SISTEMA 3 CAPAS
# ---------------------------------------------------------------------------

def fetch_con_autolearning(region: str, fuentes_primarias: list,
                           aprendidas: dict) -> tuple:
    uso_fallback = False
    uso_web      = False

    # Capa 1 — Primarias
    noticias, activas = fetch_rss(fuentes_primarias, region, "P")

    # Capa 2 — Fallback
    if len(noticias) < MIN_NOTICIAS:
        uso_fallback = True
        fb = FALLBACK_SOURCES.get(region, [])
        aprendidas_region = [{"url": u, "cf": 0.7}
                             for u in aprendidas.get(region, [])]
        n2, a2 = fetch_rss(fb + aprendidas_region, region, "FB")
        noticias += n2
        activas  += a2
        if n2:
            log.info("%s | Fallback: +%d noticias | Total: %d",
                     region, len(n2), len(noticias))

    # Capa 3 — Google News
    if len(noticias) < MIN_NOTICIAS:
        uso_web    = True
        google_url = build_google_news_url(region)
        n3, a3 = fetch_rss([{"url": google_url, "cf": 0.6}], region, "WEB")
        noticias += n3
        activas  += a3
        if n3:
            log.info("%s | Google News: +%d noticias | Total: %d",
                     region, len(n3), len(noticias))
            if region not in aprendidas:
                aprendidas[region] = []
            if google_url not in aprendidas[region]:
                aprendidas[region].append(google_url)

    calidad = calcular_calidad(len(noticias), activas, uso_fallback, uso_web)
    return noticias, calidad, aprendidas

# ---------------------------------------------------------------------------
# SCORING
# ---------------------------------------------------------------------------

def _get_aliases(region_key: str) -> list:
    aliases = REGION_ALIASES.get(region_key, [region_key])
    return aliases if region_key in aliases else [region_key] + aliases

def _tokenizar_oraciones(texto: str) -> list:
    return re.split(r"[.!?;|\n]+", texto.lower())

def _score_oracion(oracion: str, region_key: str) -> float:
    for w in CRITICAL_ALERTS:
        if w in oracion:
            return 92.0

    deesc_hits = sum(1 for w in DEESCALATION if w in oracion)
    if deesc_hits >= 2:
        return 15.0

    region_presente = any(a in oracion for a in _get_aliases(region_key))
    hits_alto  = sum(1 for w in KINETIC_ALTO  if w in oracion)
    hits_medio = sum(1 for w in KINETIC_MEDIO if w in oracion)
    hits_bajo  = sum(1 for w in KINETIC_BAJO  if w in oracion)

    if hits_alto + hits_medio + hits_bajo == 0:
        return 18.0

    score = (hits_alto * 22) + (hits_medio * 12) + (hits_bajo * 5)
    if region_presente:
        score *= 1.35
    if deesc_hits == 1:
        score *= 0.80
    return min(90.0, score)

def score_noticia(texto: str, region_key: str, cf: float) -> tuple:
    oraciones = _tokenizar_oraciones(texto)
    scores    = [_score_oracion(o, region_key) for o in oraciones if o.strip()]
    if not scores:
        return 18.0 * cf, cf
    scores.sort(reverse=True)
    return scores[max(0, len(scores) // 4)] * cf, cf

def detectar_disonancia(scores_por_fuente: dict) -> bool:
    est, alt = [], []
    for cf_str, scores in scores_por_fuente.items():
        (est if float(cf_str) >= 0.8 else alt).extend(scores)
    if not est or not alt:
        return False
    return abs(sum(est)/len(est) - sum(alt)/len(alt)) > 35

def calcular_suelo_dinamico(region_key: str, historico: list) -> float:
    base = SUELOS_BASE.get(region_key, 10)
    if len(historico) >= 5:
        media = sum(historico[-10:]) / len(historico[-10:])
        return max(base, min(media * 0.6, base + SUELO_AJUSTE_MAX))
    return base

def calcular_triaje(noticias: list, region: str,
                    old_score: float, historico: list) -> tuple:
    region_key = region.lower().split("_")[0]
    if not noticias:
        return int(old_score), False

    scores_pond, pesos, scores_cf = [], [], {}
    for n in noticias:
        s, cf = score_noticia(n["text"], region_key, n["cf"])
        scores_pond.append(s)
        pesos.append(cf)
        scores_cf.setdefault(str(round(cf, 1)), []).append(s / cf if cf > 0 else 0)

    total_cf    = sum(pesos)
    score_bruto = sum(scores_pond) / total_cf if total_cf > 0 else 18.0
    suelo       = calcular_suelo_dinamico(region_key, historico)
    score_s     = max(score_bruto, suelo)
    score_final = (old_score * 0.65 + score_s * 0.35) if score_s < old_score else score_s

    return max(10, min(100, int(score_final))), detectar_disonancia(scores_cf)

# ---------------------------------------------------------------------------
# HISTORICO
# ---------------------------------------------------------------------------

def cargar_historico_actor(region: str) -> list:
    if not HISTORY_CSV.exists():
        return []
    scores = []
    try:
        with open(HISTORY_CSV) as f:
            for linea in f:
                p = linea.strip().split(",")
                if len(p) == 3 and p[1].strip() == region:
                    try: scores.append(float(p[2]))
                    except ValueError: pass
    except OSError: pass
    return scores[-30:]

def guardar_historico(region: str, score: int, ts: float) -> None:
    try:
        with open(HISTORY_CSV, "a") as f:
            f.write(f"{ts},{region},{score}\n")
    except OSError as e:
        log.warning("No se pudo escribir historico: %s", e)

def actualizar_historico_json(global_scores: list) -> None:
    if not global_scores:
        return
    avg = sum(global_scores) // len(global_scores)
    try:
        h = json.load(open(HISTORICO_FILE)) if HISTORICO_FILE.exists() \
            else {"labels": [], "scores": []}
        h["labels"].append(datetime.now().strftime("%H:%M"))
        h["scores"].append(avg)
        h["labels"] = h["labels"][-30:]
        h["scores"] = h["scores"][-30:]
        json.dump(h, open(HISTORICO_FILE, "w"))
    except (OSError, json.JSONDecodeError) as e:
        log.error("Error historico JSON: %s", e)

# ---------------------------------------------------------------------------
# SCAN PRINCIPAL
# ---------------------------------------------------------------------------

def scan() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    fuentes    = cargar_mapa_fuentes()
    aprendidas = cargar_aprendidas()

    if not fuentes:
        log.error("Sin fuentes configuradas. Abortando.")
        return

    ts = time.time()
    print(f"--- S.I.E.G. SCANNER {VERSION} | {datetime.now().strftime('%H:%M:%S')} ---")
    print(f"    Umbral: {MIN_NOTICIAS} noticias | Capas: P -> FB -> WEB")
    print()

    global_scores = []

    for region, data_fuentes in fuentes.items():
        clean_name = region.lower().replace(".", "_")
        file_path  = DATA_DIR / f"geoint_{clean_name}.json"

        try:
            with open(file_path) as f:
                old_score = float(json.load(f).get("score", 20))
        except (OSError, json.JSONDecodeError, ValueError):
            old_score = 20.0

        historico = cargar_historico_actor(region)

        # Sistema 3 capas
        noticias, calidad, aprendidas = fetch_con_autolearning(
            region, data_fuentes, aprendidas
        )

        score, disonancia = calcular_triaje(noticias, region, old_score, historico)

        try:
            with open(file_path, "w") as f:
                json.dump({
                    "score":               score,
                    "disonancia":          disonancia,
                    "conflict":            disonancia,
                    "timestamp":           ts,
                    "noticias_procesadas": len(noticias),
                    "version":             VERSION,
                    # NUEVO: indicadores de calidad
                    "calidad_nivel":       calidad["nivel"],
                    "calidad_emoji":       calidad["emoji"],
                    "calidad_css":         calidad["css"],
                    "fuentes_activas":     calidad["fuentes_activas"],
                    "uso_fallback":        calidad["uso_fallback"],
                    "uso_web":             calidad["uso_web"],
                }, f, indent=2)
        except OSError as e:
            log.error("%s | No se pudo guardar geoint: %s", region, e)

        guardar_historico(region, score, ts)
        global_scores.append(score)

        # Output con calidad
        icono = ("☢️ " if score >= 92 else
                 "⚠️ " if disonancia   else
                 "🔥 " if score > 70   else "⚖️ ")
        delta     = score - int(old_score)
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        fb_str    = " [FB]"  if calidad["uso_fallback"] else ""
        web_str   = " [WEB]" if calidad["uso_web"]      else ""

        print(f"[{icono}] {region:20} | Score: {score:3}% ({delta_str:>4}) | "
              f"Noticias: {len(noticias):3} | "
              f"Calidad: {calidad['emoji']} {calidad['nivel']}{fb_str}{web_str}")

    guardar_aprendidas(aprendidas)
    actualizar_historico_json(global_scores)
    avg = sum(global_scores) // len(global_scores) if global_scores else 0
    print()
    print(f"--- Scan completado: {len(global_scores)} actores | Avg: {avg}% ---")

if __name__ == "__main__":
    scan()
