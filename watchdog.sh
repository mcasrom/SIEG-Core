#!/bin/bash
# S.I.E.G. Watchdog v1.0 - M. Castillo Edition

echo -e "\e[1;32m[+] Iniciando Monitor de Eventos Críticos...\e[0m"
last_alerts=""

while true; do
    current_alerts=""
    output=""
    
    # Escaneamos los JSON buscando Conflictos o Scores > 70
    for f in data/geoint_*.json; do
        REGION=$(echo $f | cut -d'_' -f2- | cut -d'.' -f1 | tr '[:lower:]' '[:upper:]')
        SCORE=$(grep -o '"score": [0-9]*' $f | cut -d' ' -f2)
        CONFLICT=$(grep -o '"conflict": [a-z]*' $f | cut -d' ' -f2)
        
        if [ "$CONFLICT" == "true" ]; then
            output="${output}\e[1;36m[⚠️ DISONANCIA] $REGION: $SCORE%\e[0m\n"
            current_alerts="${current_alerts}${REGION}_D"
        elif [ $SCORE -gt 70 ]; then
            output="${output}\e[1;31m[🔥 KINETIC]    $REGION: $SCORE%\e[0m\n"
            current_alerts="${current_alerts}${REGION}_K"
        fi
    done

    # Si hay cambios respecto a la última vez, avisamos
    clear
    echo "--- S.I.E.G. WATCHDOG | $(date +%H:%M:%S) ---"
    echo "------------------------------------------"
    if [ -z "$output" ]; then
        echo "ESTADO: Global Estable. Sin anomalías."
    else
        echo -e "$output"
        if [ "$current_alerts" != "$last_alerts" ]; then
            echo -e "\a" # Pitido de sistema (PC Speaker)
            last_alerts=$current_alerts
        fi
    fi
    echo "------------------------------------------"
    echo "Vigilando Irán, Rusia y nodos OSINT..."
    sleep 30
done
