#!/bin/bash
# Script de despliegue automático para M. Castillo
cd /home/dietpi/SIEG-Core

# 1. Ejecutar el escaneo de inteligencia
/usr/bin/python3 intel_scanner.py

# 2. Generar la web estática
/usr/bin/python3 generate_static.py

# 3. Subir cambios a GitHub
git add data/*.json index.html
git commit -m "Auto-update: $(date +'%Y-%m-%d %H:%M:%S')"
git push origin main
