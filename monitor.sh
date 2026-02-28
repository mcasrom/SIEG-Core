#!/bin/bash
# S.I.E.G. - Monitor de Inteligencia Geopolítica
# Nodo Alpha | Autor: M. Castillo

echo "Iniciando monitorización S.I.E.G. (Refresco: 15 min)..."

while true; do
    echo "--- Actualizando Radar [$(date +'%H:%M:%S')] ---"
    python3 intel_scanner.py
    echo "Escaneo completado. Próxima actualización en 15 minutos."
    sleep 900
done
