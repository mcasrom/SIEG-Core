#!/bin/bash
cd ~/intel-center
git add app.py intel_scanner.py backup_sieg.sh static/ data/historico.json
git commit -m "Auto-sync S.I.E.G. - $(date +'%Y-%m-%d %H:%M')"
git push origin main
