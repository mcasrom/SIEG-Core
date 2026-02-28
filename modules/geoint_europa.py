import urllib.request
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def analizar_tension():
    # Cambiamos a DW (Deutsche Welle) - Muy fiable para Europa/Mundo
    url = "https://rss.dw.com/rdf/rss-en-world"
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            puntos = 50
            menciones = 0
            
            # Namespace de RSS (DW usa RDF)
            ns = {'rss': 'http://purl.org/rss/1.0/', 'dc': 'http://purl.org/dc/elements/1.1/'}
            
            # Buscamos en los items (ajustado para formato RDF/RSS estándar)
            for item in root.findall('.//{http://purl.org/rss/1.0/}item'):
                title = item.find('{http://purl.org/rss/1.0/}title').text.lower()
                desc = item.find('{http://purl.org/rss/1.0/}description').text.lower()
                txt = title + " " + desc
                
                if any(reg in txt for reg in ["russia", "ukraine", "nato", "putin", "eu ", "warsaw", "kyiv"]):
                    menciones += 1
                    if any(w in txt for w in ["war", "missile", "strike", "attack", "nuclear", "killed"]):
                        puntos += 8
                    elif any(w in txt for w in ["tension", "sanctions", "threat", "military", "drill"]):
                        puntos += 4

            final_score = max(0, min(100, puntos))
            
            resultado = {
                "region": "Europa/Rusia",
                "score": final_score,
                "menciones": menciones,
                "timestamp": datetime.now().isoformat(),
                "status": "OK"
            }
            
            (DATA_DIR / "geoint_europa.json").write_text(json.dumps(resultado))
            print(f"[OK] Módulo Europa actualizado: Score {final_score} ({menciones} noticias)")

    except Exception as e:
        # Si falla, escribimos un estado de error en el JSON para que el Dashboard avise
        error_res = {"region": "Europa/Rusia", "status": "ERROR", "msg": str(e), "timestamp": datetime.now().isoformat()}
        (DATA_DIR / "geoint_europa.json").write_text(json.dumps(error_res))
        print(f"[ERROR] Módulo Europa: {e}")

if __name__ == "__main__":
    analizar_tension()
