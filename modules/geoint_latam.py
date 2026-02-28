import urllib.request, json, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def analizar_tension():
    url = "https://feeds.bbci.co.uk/mundo/rss.xml"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            root = ET.fromstring(response.read())
            puntos, menciones = 50, 0
            paises = ["venezuela", "argentina", "méxico", "brasil", "colombia", "ecuador"]
            for item in root.findall('.//item'):
                txt = (item.find('title').text + " " + item.find('description').text).lower()
                if any(p in txt for p in paises):
                    menciones += 1
                    if any(w in txt for w in ["crisis", "protesta", "inflación", "violencia", "elecciones"]): puntos += 5
            
            final_score = max(0, min(100, puntos))
            resultado = {"region": "LATAM", "score": final_score, "menciones": menciones, "timestamp": datetime.now().isoformat()}
            (DATA_DIR / "geoint_latam.json").write_text(json.dumps(resultado))
            print(f"[OK] Módulo LATAM actualizado: Score {final_score}")
    except Exception as e: print(f"[ERROR] Módulo LATAM: {e}")

if __name__ == "__main__": analizar_tension()
