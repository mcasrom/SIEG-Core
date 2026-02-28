#!/bin/bash
FECHA=$(date +%Y%m%d_%H%M)
DESTINO="backups/sieg_backup_$FECHA.tar.gz"
mkdir -p backups

echo "[*] Comprimiendo Nodo Alpha..."
tar -czf "$DESTINO" \
    --exclude='backups' \
    --exclude='logs' \
    --exclude='__pycache__' \
    --exclude='*.zip' \
    .

if [ $? -eq 0 ]; then
    echo "[OK] Backup creado: $DESTINO"
    echo "--- Verificando Integridad ---"
    tar -tf "$DESTINO" | grep 'app.py' && echo "[VERIFICADO] app.py presente."
else
    echo "[ERROR] Fallo en el respaldo."
    exit 1
fi
