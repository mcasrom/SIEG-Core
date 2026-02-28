import subprocess
import os
import time
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent.parent
MODULES_DIR = BASE_DIR / "modules"

# Lista de sensores en orden de ejecución
SENSORES = [
    "geoint_europa.py",
    "geoint_m_oriente.py",
    "geoint_sahel.py",
    "geoint_asia.py",
    "geoint_usa.py",
    "geoint_latam.py"
]

# El histórico se lanza al final de todos
HISTORICO = "historico.py"

def ejecutar_modulo(script):
    ruta = MODULES_DIR / script
    if not ruta.exists():
        print(f"[ERROR] No existe: {script}")
        return

    print(f"[EXE] Ejecutando {script}...")
    try:
        # Ejecutamos y esperamos a que termine para no saturar el ODROID
        result = subprocess.run(["python3", str(ruta)], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[ OK ] {script} finalizado con éxito.")
        else:
            print(f"[FAIL] {script} falló: {result.stderr}")
    except Exception as e:
        print(f"[EXCP] Error crítico lanzando {script}: {e}")

def main():
    print(f"--- INICIO CICLO INTEL: {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    # 1. Ejecutar cada sensor regional
    for sensor in SENSORES:
        ejecutar_modulo(sensor)
        time.sleep(2) # Pausa de 2 segundos para respiro de CPU del XU4

    # 2. Una vez todos actualizados, actualizar histórico
    ejecutar_modulo(HISTORICO)
    
    print(f"--- FIN DEL CICLO ---")

if __name__ == "__main__":
    main()
