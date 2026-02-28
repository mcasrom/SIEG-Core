import urllib.request, json, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def analizar_tension():
    url = "https://feeds.npr.org/1001/rss.xml" # News
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            root = ET.fromstring(response.read())
            puntos, menciones = 50, 0
            keywords = ["protest", "border", "sanctions", "election", "strike", "inflation"]
            for item in root.findall('.//item'):
                txt = (item.find('title').text + " " + item.find('description').text).lower()
                menciones += 1
                if any(w in txt for w in keywords): puntos += 4
            
            final_score = max(0, min(100, puntos))
            resultado = {"region": "USA/Norte", "score": final_score, "menciones": menciones, "timestamp": datetime.now().isoformat()}
            (DATA_DIR / "geoint_usa.json").write_text(json.dumps(resultado))
            print(f"[OK] Módulo USA actualizado: Score {final_score}")
    except Exception as e: print(f"[ERROR] Módulo USA: {e}")

if __name__ == "__main__": analizar_tension()
