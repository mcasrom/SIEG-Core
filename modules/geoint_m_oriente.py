import urllib.request
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def analizar_tension():
    # Fuente: Al Jazeera (Muy detallada para Medio Oriente)
    url = "https://www.aljazeera.com/xml/rss/all.xml"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            puntos = 50
            menciones = 0
            
            # Keywords de alta tensión
            criticas = ["missile", "airstrike", "drone", "hezbollah", "houthi", "iran", "gaza", "red sea"]
            
            for item in root.findall('.//item'):
                title = item.find('title').text.lower()
                desc = item.find('description').text.lower() if item.find('description') is not None else ""
                txt = title + " " + desc
                
                # Filtro regional: Israel, Palestina, Líbano, Yemen, Irán, Mar Rojo
                if any(reg in txt for reg in ["israel", "gaza", "lebanon", "yemen", "iran", "red sea", "tehran"]):
                    menciones += 1
                    if any(w in txt for w in criticas): puntos += 6
                    elif "truce" in txt or "aid" in txt: puntos -= 2

            final_score = max(0, min(100, puntos))
            
            resultado = {
                "region": "Medio Oriente",
                "score": final_score,
                "menciones": menciones,
                "timestamp": datetime.now().isoformat(),
                "status": "OK"
            }
            
            (DATA_DIR / "geoint_m_oriente.json").write_text(json.dumps(resultado))
            print(f"[OK] Módulo M.Oriente actualizado: Score {final_score}")

    except Exception as e:
        print(f"[ERROR] Módulo M.Oriente: {e}")

if __name__ == "__main__":
    analizar_tension()
