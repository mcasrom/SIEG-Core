import urllib.request
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def analizar_tension():
    # Nueva fuente: Al Jazeera Asia - Muy fiable y sin 404 constantes
    url = "https://www.aljazeera.com/xml/rss/all.xml"
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            puntos = 50
            menciones = 0
            
            criticas = ["missile", "taiwan", "south china sea", "nuclear", "kim jong", "military drill", "warships"]
            actores = ["china", "north korea", "japan", "philippines", "seoul", "beijing"]
            
            for item in root.findall('.//item'):
                title = item.find('title').text.lower()
                desc = item.find('description').text.lower() if item.find('description') is not None else ""
                txt = title + " " + desc
                
                # Filtro específico para Asia
                if any(a in txt for a in actores):
                    menciones += 1
                    if any(w in txt for w in criticas):
                        puntos += 7
                    elif "talks" in txt or "agreement" in txt:
                        puntos -= 3

            final_score = max(0, min(100, puntos))
            resultado = {
                "region": "Asia-Pacífico",
                "score": final_score,
                "menciones": menciones,
                "timestamp": datetime.now().isoformat()
            }
            (DATA_DIR / "geoint_asia.json").write_text(json.dumps(resultado))
            print(f"[OK] Módulo Asia actualizado: Score {final_score}")
    except Exception as e:
        print(f"[ERROR] Módulo Asia: {e}")

if __name__ == "__main__":
    analizar_tension()
