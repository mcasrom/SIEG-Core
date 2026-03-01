#!/bin/bash
cd /home/dietpi/SIEG-Core
/usr/bin/python3 intel_scanner.py
# --- AÑADIMOS ESTO ---
/usr/bin/python3 log_history.py
# ---------------------
git add data/*.json data/history_log.csv
git commit -m "Auto-update SIEG con Historial: $(date)"
git push origin main
