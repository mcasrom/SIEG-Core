import json, requests, xml.etree.ElementTree as ET, re
from pathlib import Path
from datetime import datetime

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CONFIG_FILE = BASE_DIR / "feeds_config.json"
HISTORICO_FILE = DATA_DIR / "historico.json"

# --- INTELIGENCIA ESTRATÉGICA (SUELOS DE SEGURIDAD) ---
# Estas regiones NUNCA bajarán de este porcentaje por ser zonas de guerra activa.
SUELOS_GUERRA = {
    "rusia": 80,
    "ucrania": 85,
    "iran": 75,
    "m_oriente": 80,
    "m.oriente": 80,
    "israel": 85
}

# Palabras de impacto cinético
KINETIC = ["bombardeo", "misil", "ataque", "explosión", "invasión", "guerra", "airstrike", "missile", "bombing", "artillería"]

def calcular_score_maestro(corpus, region_name, old_score):
    corpus = corpus.lower()
    region_key = region_name.lower().split('_')[0].split('.')[0]
    
    # 1. TEST DE PROXIMIDAD (¿Guerra + Región en la misma frase?)
    es_real_local = False
    for word in KINETIC:
        # Busca la palabra de guerra a menos de 60 caracteres del nombre de la región
        pattern = rf"({region_key}.{{0,60}}{word})|({word}.{{0,60}}{region_key})"
        if re.search(pattern, corpus):
            es_real_local = True
            break

    # 2. CÁLCULO DINÁMICO
    if es_real_local:
        hits = sum(1 for w in KINETIC if w in corpus)
        score = 80 + (hits * 2)
    else:
        # Si hay palabras de guerra pero NO cerca de la región (Eco internacional como España)
        if any(w in corpus for w in KINETIC):
            score = 35 
        else:
            score = 15
        
        # Tensión social/política (Bonus leve)
        if any(w in corpus for w in ["crisis", "tensión", "huelga", "protesta"]):
            score += 10

    # 3. APLICACIÓN DE SUELOS (Evita que Ucrania/Rusia bajen por falta de noticias frescas)
    for key, suelo_minimo in SUELOS_GUERRA.items():
        if key in region_key:
            score = max(score, suelo_minimo)

    # 4. LIMPIEZA DE BASURA ANTERIOR (Si el score nuevo es menor, bajamos un 50% cada vez)
    if score < old_score:
        score = old_score * 0.50 
        
    return max(10, min(100, int(score)))

def scan():
    DATA_DIR.mkdir(exist_ok=True)
    if not CONFIG_FILE.exists(): return
    
    with open(CONFIG_FILE, 'r') as f: config = json.load(f)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Chrome/122.0.0.0'}

    print(f"--- S.I.E.G. SCANNER V8.2 | {datetime.now().strftime('%H:%M:%S')} ---")
    
    scores_lista = []

    for region, urls in config.items():
        corpus = ""
        clean_name = region.lower().replace('/', '_').replace(' ', '_').replace('.', '_')
        filename = f"geoint_{clean_name}.json"
        
        try:
            with open(DATA_DIR / filename, 'r') as f: old = json.load(f)['score']
        except: old = 20

        for url in urls:
            try:
                r = requests.get(url, headers=headers, timeout=8)
                root = ET.fromstring(r.content)
                for item in root.findall('.//item')[:15]:
                    t = item.find('title').text or ""
                    d = item.find('description').text if item.find('description') is not None else ""
                    corpus += f" {t} {d}"
            except: continue
        
        score = calcular_score_maestro(corpus, region, old)
        
        with open(DATA_DIR / filename, 'w') as f: json.dump({"score": score}, f)
        
        scores_lista.append(score)
        icon = "🔥" if score > 70 else "⚖️"
        print(f"[{icon}] {region:15} | Score: {score}%")

    # Guardar histórico para el gráfico de líneas
    if scores_lista:
        promedio = sum(scores_lista) // len(scores_lista)
        ahora = datetime.now().strftime('%H:%M')
        try:
            if HISTORICO_FILE.exists():
                with open(HISTORICO_FILE, 'r') as f: h = json.load(f)
            else: h = {"labels": [], "scores": []}
            h["labels"].append(ahora); h["scores"].append(promedio)
            h["labels"], h["scores"] = h["labels"][-20:], h["scores"][-20:]
            with open(HISTORICO_FILE, 'w') as f: json.dump(h, f)
        except: pass

if __name__ == "__main__":
    scan()
