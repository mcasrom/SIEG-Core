import subprocess
import time
import requests
import os

# CONFIGURACIÓN
PRIMARY_IP = "192.168.1.XX"  # Sustituir por la IP del ODROID 1
PRIMARY_URL = f"http://{PRIMARY_IP}:7070"
CHECK_INTERVAL = 60  # Segundos entre comprobaciones
MAX_FAILURES = 3
SERVER_SCRIPT = "/home/miguelc/intel-center/app.py"

def check_primary():
    try:
        # Intentamos una petición ligera al API
        response = requests.get(f"{PRIMARY_URL}/api/all", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_backup_server():
    print("[ALERT] Nodo Alpha caído. Iniciando servidor en Nodo Beta...")
    # Ejecuta el servidor Flask en segundo plano
    subprocess.Popen(["python3", SERVER_SCRIPT])

def main():
    consecutive_failures = 0
    server_running = False

    print(f"[INFO] Vigilante iniciado. Monitorizando {PRIMARY_IP}...")

    while True:
        if not check_primary():
            consecutive_failures += 1
            print(f"[WARN] Fallo de conexión {consecutive_failures}/{MAX_FAILURES}")
        else:
            if consecutive_failures > 0:
                print("[ OK ] Conexión restaurada con Nodo Alpha.")
            consecutive_failures = 0

        if consecutive_failures >= MAX_FAILURES and not server_running:
            start_backup_server()
            server_running = True
            print("[CRITICAL] Nodo Beta ha tomado el control.")
            break # El secundario ya es el activo

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
