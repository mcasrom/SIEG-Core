import json, requests, xml.etree.ElementTree as ET, re, time
from pathlib import Path
from datetime import datetime

# Rutas de Sistema
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MAPA_FUENTES = BASE_DIR / "mapa_fuentes.txt"
HISTORICO_FILE = DATA_DIR / "historico.json"

# Configuración de Inteligencia
KINETIC = [
    "bombardeo", "misil", "ataque", "explosión", "invasión", "guerra", 
    "airstrike", "missile", "bombing", "artillería", "frontline", "combat",
    "shelling", "interception", "ballistic", "warship", "encroachment"
]

# Palabras que disparan el score inmediatamente por encima de 85
CRITICAL_ALERTS = ["nuclear", "icbm", "tactical nukes", "mobilization", "martial law"]

SUELOS = {
    "rusia": 80, 
    "ucrania": 85, 
    "iran": 75, 
    "m_oriente": 80, 
    "israel": 85,
    "north_korea": 40  # Suelo preventivo por retórica constante
}

def cargar_mapa_fuentes():
    fuentes = {}
    if not MAPA_FUENTES.exists():
        print(f"[!] ERROR: No se encuentra {MAPA_FUENTES}")
        return {}
    with open(MAPA_FUENTES, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip(): continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3:
                region, url, cf = parts[0], parts[1], float(parts[2])
                if region not in fuentes: fuentes[region] = []
                fuentes[region].append({"url": url, "cf": cf})
    return fuentes

def calcular_triaje(noticias_region, region_name, old_score):
    if not noticias_region: return old_score, False
    
    scores_individuales = []
    region_key = region_name.lower().split('_')[0]
    pesos_confianza = []

    for n in noticias_region:
        corpus = n['text'].lower()
        cf = n['cf']
        
        # 1. Chequeo de Alertas Críticas (Nuclear, ICBM, etc.)
        if any(w in corpus for w in CRITICAL_ALERTS):
            s = 95  # Nivel de alerta máxima inmediata
        else:
            # 2. Lógica de detección cinética por proximidad
            es_real = any(re.search(rf"({region_key}.{{0,60}}{w})|({w}.{{0,60}}{region_key})", corpus) for w in KINETIC)
            # Puntuación base + bonus por repetición de términos
            s = (80 if es_real else 20) + (sum(1 for w in KINETIC if w in corpus) * 2)
        
        scores_individuales.append(s)
        pesos_confianza.append(cf)

    # --- DETECTOR DE MENTIRAS (DISONANCIA) ---
    gap = max(scores_individuales) - min(scores_individuales) if len(scores_individuales) > 1 else 0
    hay_disonancia = gap > 50

    # Promedio Ponderado por Confianza (CF)
    total_weighted = sum(s * cf for s, cf in zip(scores_individuales, pesos_confianza))
    total_cf = sum(pesos_confianza)
    final_score = total_weighted / total_cf if total_cf > 0 else 20

    # Aplicar Suelos de Seguridad
    for key, suelo in SUELOS.items():
        if key in region_key:
            final_score = max(final_score, suelo)

    # Suavizado de caída (Inercia de tensión)
    if final_score < old_score:
        final_score = (old_score * 0.7) + (final_score * 0.3)

    return max(10, min(100, int(final_score))), hay_disonancia

def scan():
    DATA_DIR.mkdir(exist_ok=True)
    fuentes = cargar_mapa_fuentes()
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    print(f"--- S.I.E.G. SCANNER V8.7 | CRITICAL ALERT ENGINE | {datetime.now().strftime('%H:%M:%S')} ---")
    
    global_scores = []

    for region, data_fuentes in fuentes.items():
        noticias_acumuladas = []
        clean_name = region.lower().replace('.', '_')
        file_path = DATA_DIR / f"geoint_{clean_name}.json"
        
        try:
            with open(file_path, 'r') as f: old = json.load(f).get('score', 20)
        except: old = 20

        for f in data_fuentes:
            try:
                r = requests.get(f['url'], headers=headers, timeout=10)
                root = ET.fromstring(r.content)
                for item in root.findall('.//item')[:8]:
                    title = item.find('title').text or ""
                    desc = item.find('description').text if item.find('description') is not None else ""
                    noticias_acumuladas.append({"text": f"{title} {desc}", "cf": f['cf']})
            except Exception: continue
        
        score, conflict = calcular_triaje(noticias_acumuladas, region, old)
        
        with open(file_path, 'w') as f:
            json.dump({"score": score, "conflict": conflict, "timestamp": time.time()}, f)
        
        global_scores.append(score)
        status_icon = "☢️" if score >= 95 else ("⚠️" if conflict else ("🔥" if score > 70 else "⚖️"))
        print(f"[{status_icon}] {region:15} | Score: {score}% | Disonancia: {conflict}")

    if global_scores:
        avg = sum(global_scores) // len(global_scores)
        try:
            h = json.load(open(HISTORICO_FILE)) if HISTORICO_FILE.exists() else {"labels":[], "scores":[]}
            h["labels"].append(datetime.now().strftime('%H:%M'))
            h["scores"].append(avg)
            json.dump({"labels": h["labels"][-30:], "scores": h["scores"][-30:]}, open(HISTORICO_FILE, 'w'))
        except Exception as e:
            print(f"[!] Error guardando histórico: {e}")

if __name__ == "__main__":
    scan()
