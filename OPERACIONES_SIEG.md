# 🛡️ S.I.E.G. - Protocolo de Inteligencia (V8.7)
**Analista:** M. Castillo | **Host:** Asus VivoBook (Linux Native)

## 📋 Comandos Rápidos
- **Actualizar Radar:** `python3 intel_scanner.py`
- **Monitor en Vivo:** `./watchdog.sh`
- **Dashboard Web:** `http://localhost:7070`
- **Auditoría CLI:** `python3 -c "import json, glob, os; ..."` (comando de tabla)

## 🚦 Niveles de Alerta y Acción
| Score | Estado | Acción Recomendada |
|-------|--------|-------------------|
| **0-30%** | ⚖️ Estable | Monitoreo rutinario. |
| **31-60%** | ⚠️ Tensión | Verificar flag de Disonancia. Si es `1`, buscar noticias en `data/`. |
| **61-85%** | 🔥 Conflicto | Alerta táctica. El Watchdog debería estar activo. |
| **86-100%** | ☢️ Crítico | Posible evento nuclear o ICBM. Verificar fuentes OSINT de inmediato. |

## 🔍 Interpretación de la Disonancia (Flag: 1)
- **Score Alto + Disonancia:** "Guerra de Información". Los observadores ven fuego, el Estado lo niega.
- **Score Bajo + Disonancia:** "Operación de Desinformación". Ruido en redes o medios de propaganda sin base real.

## 🛠️ Mantenimiento
Para añadir fuentes, editar **`mapa_fuentes.txt`**. 
Para limpiar datos corruptos: `rm -f data/geoint_*.json`
