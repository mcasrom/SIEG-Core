#!/bin/bash
cd /home/dietpi/SIEG-Core

# 1. Ejecutar el escáner de inteligencia
/usr/bin/python3 intel_scanner.py >> scanner.log 2>&1

# 2. Registrar el punto en el historial (los 337 registros y sumando)
/usr/bin/python3 log_history.py >> history.log 2>&1

# 3. Sincronizar con GitHub (El "bloqueo" de datos que mencionas)
git add data/*.json data/history_log.csv
git commit -m "Auto-update SIEG: $(date)"
git push origin main >> git_sync.log 2>&1
