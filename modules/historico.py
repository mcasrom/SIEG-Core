import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "history.json"

def persistir_datos():
    # 1. Recolectar lo que hay ahora en los módulos
    snapshot = {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "scores": {}
    }
    
    # Buscamos todos los JSON de geoint en data
    for p in DATA_DIR.glob("geoint_*.json"):
        try:
            data = json.loads(p.read_text())
            snapshot["scores"][data["region"]] = data["score"]
        except:
            continue

    # 2. Cargar histórico existente
    if HISTORY_FILE.exists():
        history = json.loads(HISTORY_FILE.read_text())
    else:
        history = []

    # 3. Añadir snapshot y mantener límite de 90 días
    history.append(snapshot)
    if len(history) > 90:
        history = history[-90:]

    # 4. Guardar de forma atómica
    HISTORY_FILE.write_text(json.dumps(history, indent=2))
    print(f"[OK] Histórico actualizado. Registros guardados: {len(history)}")

if __name__ == "__main__":
    persistir_datos()
