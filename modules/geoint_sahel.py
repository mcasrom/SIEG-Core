import urllib.request
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def analizar_tension():
    # Fuente: Africanews (RSS de noticias generales, muy estable)
    url = "https://www.africanews.com/feed/"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            puntos = 50
            menciones = 0
            
            # Keywords: Sahel, Golpes, Terrorismo
            criticas = ["coup", "junta", "wagner", "attack", "militants", "ambush", "terror"]
            paises = ["mali", "niger", "burkina faso", "chad", "sudan", "guinea"]
            
            for item in root.findall('.//item'):
                title = item.find('title').text.lower()
                desc = item.find('description').text.lower() if item.find('description') is not None else ""
                txt = title + " " + desc
                
                # Filtro regional
                if any(p in txt for p in paises):
                    menciones += 1
                    if any(w in txt for w in criticas): puntos += 7
                    elif "expelled" in txt or "sanctions" in txt: puntos += 4

            final_score = max(0, min(100, puntos))
            
            resultado = {
                "region": "Sahel/África",
                "score": final_score,
                "menciones": menciones,
                "timestamp": datetime.now().isoformat(),
                "status": "OK"
            }
            
            (DATA_DIR / "geoint_sahel.json").write_text(json.dumps(resultado))
            print(f"[OK] Módulo Sahel actualizado: Score {final_score}")

    except Exception as e:
        print(f"[ERROR] Módulo Sahel: {e}")

if __name__ == "__main__":
    analizar_tension()
