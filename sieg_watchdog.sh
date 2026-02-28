#!/bin/bash
# S.I.E.G. - TACTICAL WATCHDOG v1.0
# Operador: M. Castillo
# Objetivo: Monitorizar umbrales críticos de tensión geopolítica

DATA_DIR="./data"
UMBRAL_CRITICO=85
LOG_FILE="./backups/watchdog.log"

echo "[$(date)] Watchdog iniciado. Monitorizando umbral: $UMBRAL_CRITICO%"

while true; do
    # Buscar todos los archivos JSON de hotspots
    for file in "$DATA_DIR"/geoint_*.json; do
        if [ -f "$file" ]; then
            # Extraer el score usando jq (si no lo tienes: sudo apt install jq)
            # Si no quieres instalar jq, usamos un grep/sed rápido
            SCORE=$(grep -oP '"score":\s*\K[0-9]+' "$file")
            REGION=$(basename "$file" .json | sed 's/geoint_//')

            if [ "$SCORE" -ge "$UMBRAL_CRITICO" ]; then
                MSG="ALERTA CRÍTICA: $REGION ha alcanzado el $SCORE% de tensión."
                
                # 1. Notificación visual (GUI)
                notify-send -u critical "S.I.E.G. ALERTA" "$MSG"
                
                # 2. Alerta sonora (Beep o sonido de sistema)
                # Si tienes 'play' (de sox) o 'paplay' (PulseAudio/Pipewire)
                paplay /usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga 2>/dev/null || echo -e "\a"
                
                # 3. Registro en log
                echo "[$(date)] ALERT: $MSG" >> "$LOG_FILE"
            fi
        fi
    done

    # Intervalo de chequeo: cada 5 minutos
    sleep 300
done
