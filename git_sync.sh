#!/bin/bash
# Script de sincronización SIEG-Core para M. Castillo
CD_PATH="/home/miguelc/intel-center"
cd $CD_PATH

# Añadir cambios de datos y lógica
/usr/bin/git add data/historico.json app.py intel_scanner.py *.org
/usr/bin/git commit -m "Auto-sync S.I.E.G. [$(date +'%Y-%m-%d %H:%M')]"
/usr/bin/git push origin main
