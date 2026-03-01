#!/usr/bin/env python3
"""
S.I.E.G. - Intel Scanner V9.1
Fixes vs V9.0:
  - Suelos base reajustados: Iran/Israel/M.Oriente suben, refleja conflicto activo
  - REGION_ALIASES: captura menciones indirectas (iranian, idf, irgc, hezbollah...)
  - Kinetic alto ampliado con terminos del conflicto Israel-Iran actual
  - Fuentes Iran_M_Oriente reforzadas con Times of Israel y BBC Middle East
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

RSS_ITEMS_POR_FUENTE = 20
TIMEOUT_HTTP         = 10
VERSION              = "V9.1"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("SIEG")

# ---------------------------------------------------------------------------
# VOCABULARIO DE INTELIGENCIA
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

# ---------------------------------------------------------------------------
# FIX 2: ALIASES DE REGION
# Captura menciones indirectas — "Iranian-backed", "IDF strikes", "IRGC"
# no contienen la palabra "iran" pero son claramente sobre ese actor.
# ---------------------------------------------------------------------------

REGION_ALIASES = {
    "iran":        ["iran", "iranian", "tehran", "irgc", "hezbollah",
                    "persian", "khamenei", "raisi", "islamic republic"],
    "israel":      ["israel", "israeli", "idf", "tel aviv", "jerusalem",
                    "netanyahu", "mossad", "iron dome", "gaza", "west bank"],
    "rusia":       ["russia", "russian", "moscow", "kremlin", "putin",
                    "wagner", "rossiya", "red army"],
    "ucrania":     ["ukraine", "ukrainian", "kyiv", "kiev", "zelensky",
                    "azov", "dnipro", "kharkiv", "zaporizhzhia"],
    "china":       ["china", "chinese", "beijing", "xi jinping", "pla",
                    "peoples liberation", "ccp", "taiwan strait"],
    "north_korea": ["north korea", "north korean", "dprk", "kim jong",
                    "pyongyang", "korean peninsula"],
    "usa":         ["united states", "american", "washington", "pentagon",
                    "white house", "congress", "biden", "trump", "nato"],
    "sahel":       ["sahel", "mali", "niger", "burkina", "wagner africa",
                    "jihadist", "al-qaeda africa", "isis africa"],
}

# ---------------------------------------------------------------------------
# FIX 1: SUELOS BASE REAJUSTADOS
# Iran sube a 68 (conflicto activo con Israel)
# Israel sube a 72 (conflicto activo)
# M_Oriente sube a 65 (teatro regional caliente)
# Rusia baja ligeramente a 62 (frente estabilizado)
# ---------------------------------------------------------------------------

SUELOS_BASE = {
    "rusia":       62,
    "ucrania":     68,
    "iran":        68,   # sube — bombardeos activos Israel-Iran
    "m_oriente":   65,   # sube — teatro regional
    "israel":      72,   # sube — conflicto activo
    "north_korea": 35,
    "sahel":       32,
}

SUELO_AJUSTE_MAX = 15


def calcular_suelo_dinamico(region_key: str, historico_scores: list) -> float:
    """Suelo dinamico = max(base, media_reciente * 0.6)."""
    base = SUELOS_BASE.get(region_key, 10)
    if len(historico_scores) >= 5:
        media_reciente = sum(historico_scores[-10:]) / len(historico_scores[-10:])
        ajuste = min(media_reciente * 0.6, base + SUELO_AJUSTE_MAX)
        return max(base, ajuste)
    return base


# ---------------------------------------------------------------------------
# CARGA DE FUENTES
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
# SCORING POR ORACION CON ALIASES
# ---------------------------------------------------------------------------

def _get_aliases(region_key: str) -> list:
    """Devuelve todos los aliases de una region, incluyendo la clave base."""
    aliases = REGION_ALIASES.get(region_key, [region_key])
    if region_key not in aliases:
        aliases = [region_key] + aliases
    return aliases


def _tokenizar_oraciones(texto: str) -> list:
    return re.split(r"[.!?;|\n]+", texto.lower())


def _score_oracion(oracion: str, region_key: str) -> tuple:
    """
    Calcula score de una oracion.
    FIX: usa aliases para detectar menciones indirectas del actor.
    """
    # Alerta critica
    for w in CRITICAL_ALERTS:
        if w in oracion:
            return 92.0, f"CRITICO:{w}"

    # Desescalada
    deesc_hits = sum(1 for w in DEESCALATION if w in oracion)
    if deesc_hits >= 2:
        return 15.0, "DESESCALADA"

    # FIX: presencia de region via aliases (no solo clave exacta)
    aliases = _get_aliases(region_key)
    region_presente = any(alias in oracion for alias in aliases)

    # Hits cineticos
    hits_alto  = sum(1 for w in KINETIC_ALTO  if w in oracion)
    hits_medio = sum(1 for w in KINETIC_MEDIO if w in oracion)
    hits_bajo  = sum(1 for w in KINETIC_BAJO  if w in oracion)
    total_hits = hits_alto + hits_medio + hits_bajo

    if total_hits == 0:
        return 18.0, "SIN_HITS"

    score_base = (hits_alto * 22) + (hits_medio * 12) + (hits_bajo * 5)

    # Bonus por presencia de region (alias incluidos)
    if region_presente:
        score_base *= 1.35

    # Penalizacion desescalada parcial
    if deesc_hits == 1:
        score_base *= 0.80

    return min(90.0, score_base), f"HITS:A{hits_alto}M{hits_medio}B{hits_bajo}"


def score_noticia(texto: str, region_key: str, cf: float) -> tuple:
    """Score de una noticia = percentil 75 de sus oraciones, ponderado por CF."""
    oraciones = _tokenizar_oraciones(texto)
    scores_oraciones = [_score_oracion(o, region_key)[0] for o in oraciones if o.strip()]

    if not scores_oraciones:
        return 18.0 * cf, cf

    scores_sorted = sorted(scores_oraciones, reverse=True)
    p75_idx = max(0, len(scores_sorted) // 4)
    return scores_sorted[p75_idx] * cf, cf


# ---------------------------------------------------------------------------
# DETECTOR DE DISONANCIA NARRATIVA
# ---------------------------------------------------------------------------

def detectar_disonancia(scores_por_fuente: dict) -> bool:
    """
    Disonancia = divergencia sistematica entre fuentes establishment (CF>=0.8)
    y alternativas (CF<0.8) mayor de 35 puntos.
    """
    establishment, alternativas = [], []
    for cf_str, scores in scores_por_fuente.items():
        (establishment if float(cf_str) >= 0.8 else alternativas).extend(scores)

    if not establishment or not alternativas:
        return False

    return abs(
        sum(establishment) / len(establishment) -
        sum(alternativas)  / len(alternativas)
    ) > 35


# ---------------------------------------------------------------------------
# TRIAJE PRINCIPAL
# ---------------------------------------------------------------------------

def calcular_triaje(noticias: list, region_name: str,
                    old_score: float, historico_scores: list) -> tuple:
    """Calcula (score_final, hay_disonancia) para una region."""
    region_key = region_name.lower().split("_")[0]

    if not noticias:
        log.warning("%s: Sin noticias. Manteniendo score anterior.", region_name)
        return int(old_score), False

    scores_ponderados, pesos_cf = [], []
    scores_por_cf_grupo = {}

    for n in noticias:
        s_pond, cf = score_noticia(n["text"], region_key, n["cf"])
        scores_ponderados.append(s_pond)
        pesos_cf.append(cf)
        cf_key = str(round(n["cf"], 1))
        scores_por_cf_grupo.setdefault(cf_key, []).append(
            s_pond / cf if cf > 0 else 0
        )

    total_cf    = sum(pesos_cf)
    score_bruto = sum(scores_ponderados) / total_cf if total_cf > 0 else 18.0

    suelo          = calcular_suelo_dinamico(region_key, historico_scores)
    score_con_suelo = max(score_bruto, suelo)

    # Inercia de caida — suaviza bajadas bruscas
    if score_con_suelo < old_score:
        score_final = (old_score * 0.65) + (score_con_suelo * 0.35)
    else:
        score_final = score_con_suelo

    hay_disonancia = detectar_disonancia(scores_por_cf_grupo)
    return max(10, min(100, int(score_final))), hay_disonancia


# ---------------------------------------------------------------------------
# HISTORICO
# ---------------------------------------------------------------------------

def cargar_historico_actor(region: str) -> list:
    if not HISTORY_CSV.exists():
        return []
    scores = []
    try:
        with open(HISTORY_CSV, "r") as f:
            for linea in f:
                parts = linea.strip().split(",")
                if len(parts) == 3 and parts[1].strip() == region:
                    try:
                        scores.append(float(parts[2]))
                    except ValueError:
                        continue
    except OSError as e:
        log.warning("No se pudo leer historico CSV: %s", e)
    return scores[-30:]


def guardar_historico(region: str, score: int, timestamp: float) -> None:
    try:
        with open(HISTORY_CSV, "a") as f:
            f.write(f"{timestamp},{region},{score}\n")
    except OSError as e:
        log.warning("No se pudo escribir historico CSV: %s", e)


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
    fuentes = cargar_mapa_fuentes()

    if not fuentes:
        log.error("Sin fuentes configuradas. Abortando.")
        return

    headers = {"User-Agent": "Mozilla/5.0 (compatible; SIEG-Scanner/9.1)"}
    ts      = time.time()

    print(f"--- S.I.E.G. SCANNER {VERSION} | {datetime.now().strftime('%H:%M:%S')} ---")

    global_scores = []

    for region, data_fuentes in fuentes.items():
        clean_name = region.lower().replace(".", "_")
        file_path  = DATA_DIR / f"geoint_{clean_name}.json"

        try:
            with open(file_path, "r") as f:
                old_score = float(json.load(f).get("score", 20))
        except (OSError, json.JSONDecodeError, ValueError):
            old_score = 20.0

        historico          = cargar_historico_actor(region)
        noticias_acumuladas = []

        for fuente in data_fuentes:
            try:
                r = requests.get(fuente["url"], headers=headers, timeout=TIMEOUT_HTTP)
                r.raise_for_status()
                root = ET.fromstring(r.content)
                for item in root.findall(".//item")[:RSS_ITEMS_POR_FUENTE]:
                    title_el = item.find("title")
                    desc_el  = item.find("description")
                    title    = (title_el.text or "") if title_el is not None else ""
                    desc     = (desc_el.text  or "") if desc_el  is not None else ""
                    noticias_acumuladas.append({
                        "text": f"{title} {re.sub(r'<[^>]+>', ' ', desc)}",
                        "cf":   fuente["cf"],
                    })
            except requests.RequestException as e:
                log.warning("%s | Fuente no disponible: %s", region, e)
            except ET.ParseError as e:
                log.warning("%s | RSS malformado: %s", region, e)

        score, disonancia = calcular_triaje(
            noticias_acumuladas, region, old_score, historico
        )

        try:
            with open(file_path, "w") as f:
                json.dump({
                    "score":               score,
                    "disonancia":          disonancia,
                    "conflict":            disonancia,
                    "timestamp":           ts,
                    "noticias_procesadas": len(noticias_acumuladas),
                    "version":             VERSION,
                }, f, indent=2)
        except OSError as e:
            log.error("%s | No se pudo guardar geoint: %s", region, e)

        guardar_historico(region, score, ts)
        global_scores.append(score)

        icono = ("☢️ " if score >= 92 else
                 "⚠️ " if disonancia   else
                 "🔥 " if score > 70   else "⚖️ ")
        delta     = score - int(old_score)
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        print(f"[{icono}] {region:20} | Score: {score:3}% ({delta_str:>4}) | "
              f"Fuentes: {len(noticias_acumuladas):3} | Disonancia: {disonancia}")

    actualizar_historico_json(global_scores)
    avg = sum(global_scores) // len(global_scores) if global_scores else 0
    print(f"--- Scan completado: {len(global_scores)} actores | Avg: {avg}% ---")


if __name__ == "__main__":
    scan()
