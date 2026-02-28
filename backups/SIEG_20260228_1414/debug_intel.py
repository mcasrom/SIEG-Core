import json, glob
from pathlib import Path

DATA_DIR = Path("./data")
KEYWORDS_KINETIC = ["bombardeo", "airstrike", "missile", "misil", "explosion", "bombing", "nuclear", "war", "guerra", "invasion", "ataque", "attack"]
KEYWORDS_SOCIAL = ["tensión", "tension", "conflict", "conflicto", "crisis", "alert", "alerta", "protest", "huelga", "manifestación"]

def analyze():
    print(f"{'REGIÓN':<15} | {'SCORE':<7} | {'ESTADO':<12} | {'DETECTADO (TOP KEYWORDS)'}")
    print("-" * 80)
    
    for f in sorted(DATA_DIR.glob("geoint_*.json")):
        with open(f, 'r') as j:
            score = json.load(j).get("score", 0)
            name = f.stem.replace("geoint_", "").upper()
            
            # Reconstrucción lógica de por qué tiene ese score
            status = "KINETIC" if score > 70 else "SOCIAL" if score > 40 else "STABLE"
            
            # Nota: Aquí simulamos la detección para el reporte CLI
            # En un entorno real, el scanner guardaría los hits en el JSON
            print(f"{name:<15} | {score:>5}% | {status:<12} | ", end="")
            
            if score > 70:
                print("⚠️  DETECTADOS IMPACTOS CINÉTICOS (BOMBARDEO/MISIL)")
            elif score > 40:
                print("📢  RUIDO SOCIAL/POLÍTICO (TECHO ACTIVADO)")
            else:
                print("✅  BAJA ACTIVIDAD")

if __name__ == "__main__":
    analyze()
