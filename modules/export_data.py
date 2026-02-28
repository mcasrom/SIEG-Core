import tarfile
import os
from datetime import datetime

DATA_DIR = "/home/miguelc/intel-center/data/"
OUTPUT_NAME = f"intel_export_{datetime.now().strftime('%Y%m%d')}.tar.gz"

def export_intel():
    try:
        with tarfile.open(OUTPUT_NAME, "w:gz") as tar:
            tar.add(DATA_DIR, arcname=os.path.basename(DATA_DIR))
        print(f"[OK] Backup de inteligencia generado: {OUTPUT_NAME}")
    except Exception as e:
        print(f"[ERR] Fallo al exportar: {e}")

if __name__ == "__main__":
    export_intel()
