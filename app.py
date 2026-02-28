import json, os, zipfile, logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from flask import Flask, jsonify, send_from_directory

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

app = Flask(__name__, static_folder='static')

# --- SISTEMA DE LOGS PROFESIONAL ---
handler = RotatingFileHandler(LOG_DIR / 'server.log', maxBytes=1000000, backupCount=5)
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

def cargar_json(f):
    try:
        path = DATA_DIR / f
        if path.exists():
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {"score": 0}
    except Exception as e:
        app.logger.error(f"Error cargando {f}: {e}")
        return {"score": 0}

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/all')
def api_all():
    # Los 12 ejes del radar S.I.E.G.
    puntos = [
        {"l": "España", "f": "geoint_espana.json"},
        {"l": "Ucrania", "f": "geoint_ucrania.json"},
        {"l": "China", "f": "geoint_china.json"},
        {"l": "Europa/Rus", "f": "geoint_europa.json"},
        {"l": "USA/Norte", "f": "geoint_usa.json"},
        {"l": "M.Oriente", "f": "geoint_m_oriente.json"},
        {"l": "Asia-Pac", "f": "geoint_asia.json"},
        {"l": "LATAM", "f": "geoint_latam.json"},
        {"l": "Sahel/Afr", "f": "geoint_sahel.json"},
        {"l": "México", "f": "geoint_mexico.json"},
        {"l": "Argentina", "f": "geoint_argentina.json"},
        {"l": "Brasil", "f": "geoint_brasil.json"}
    ]
    
    radar_scores, radar_labels, alerts = [], [], []

    for p in puntos:
        data = cargar_json(p["f"])
        score = data.get("score", 0)
        radar_scores.append(score)
        radar_labels.append(f"{p['l']} ({score}%)")
        
        # Umbral de alerta calibrado hoy al 80%
        if score > 80:
            alerts.append({
                "id": "HOTSPOT", 
                "title": f"TENSIÓN CRÍTICA: {p['l'].upper()}", 
                "severity": "high"
            })

    # Carga de histórico para gráfico de tendencias
    try:
        with open(DATA_DIR / "historico.json", 'r') as f:
            h = json.load(f)
            stats_semanal = {"labels": h["labels"], "data": h["scores"]}
    except:
        stats_semanal = {"labels": ["Sin Datos"], "data": [0]}

    return jsonify({
        "labels": radar_labels, 
        "radar": radar_scores, 
        "alerts": alerts,
        "stats": stats_semanal
    })

@app.route('/api/download')
def download():
    zip_fn = 'sieg_intel_export.zip'
    zip_path = BASE_DIR / zip_fn
    
    try:
        # Re-creamos el archivo ZIP siempre antes de enviarlo
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Añadir archivos de datos
            for f in DATA_DIR.glob('*.json'):
                zf.write(f, arcname=f"data/{f.name}")
            # Añadir documentación si existe
            if (BASE_DIR / "proyecto.org").exists():
                zf.write(BASE_DIR / "proyecto.org", arcname="proyecto.org")
        
        app.logger.info("Exportación ZIP generada correctamente.")
        return send_from_directory(directory=BASE_DIR, path=zip_fn, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Fallo en descarga: {e}")
        return f"Error en servidor: {e}", 500

if __name__ == '__main__':
    print("--- NODO ALPHA INICIADO EN PUERTO 7070 ---")
    app.run(host='0.0.0.0', port=7070, debug=False)
