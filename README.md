# 🛡 S.I.E.G. — Sistema de Inteligencia Estratégica Geopolítica

> **Geopolitical Open Source Intelligence Platform**  
> Autonomous monitoring · 14 global actors · 6 infrastructure axes · Real-time scoring

[![SIEG Core](https://img.shields.io/badge/SIEG_Core-Live-00ff41?style=flat-square)](https://sieg-intelligence-radar.streamlit.app)
[![SIEG Atlas](https://img.shields.io/badge/SIEG_Atlas-Live-00ccff?style=flat-square)](https://sieg-atlas-intelligence.streamlit.app)

---

## 🌐 Dashboards en Vivo / Live Dashboards

| Proyecto | URL | Descripcion |
|----------|-----|-------------|
| **SIEG Core** | [sieg-intelligence-radar.streamlit.app](https://sieg-intelligence-radar.streamlit.app) | 14 actores geopoliticos globales |
| **SIEG Atlas** | [sieg-atlas-intelligence.streamlit.app](https://sieg-atlas-intelligence.streamlit.app) | 6 ejes de infraestructura critica |

---

## 📊 ¿Qué es SIEG? / What is SIEG?

**ES:** SIEG es una plataforma OSINT autonoma que monitoriza la tension geopolitica global mediante analisis de fuentes RSS abiertas. Genera scores de 0-100% por actor o eje tematico, detecta anomalias, disonancia narrativa y activa alertas automaticas.

**EN:** SIEG is an autonomous OSINT platform monitoring global geopolitical tension through open RSS source analysis. It generates 0-100% scores per actor or thematic axis, detects anomalies, narrative dissonance, and triggers automatic alerts.

---

## 🏗 Arquitectura / Architecture

```
Odroid-C2 (ARM · DietPi)
├── SIEG-Core/          ← 14 actores geopoliticos
│   ├── intel_scanner.py   Scanner V9.2
│   ├── app_streamlit.py   Dashboard V12.0
│   ├── mapa_fuentes.txt   ~80 fuentes RSS
│   └── data/
│       ├── geoint_*.json  Estado por actor
│       ├── history_log.csv Historico (90d activos)
│       └── archive/       Historico comprimido
└── SIEG-Atlas/         ← 6 ejes infraestructura
    ├── atlas_scanner.py   Scanner V1.2
    ├── app_atlas.py       Dashboard V1.0
    ├── mapa_atlas.txt     ~30 fuentes RSS
    └── data/live/
        ├── atlas_*.json   Estado por eje
        └── history_atlas.csv
```

---

## ⚡ Ejes Monitorizados / Monitored Axes

### SIEG Core — Actores Geopoliticos
`Iran/M.Oriente` · `Rusia/Ucrania` · `USA` · `China` · `North Korea`  
`Sahel` · `España` · `Latam` · `Mexico` · `Argentina` · `Brasil`  
`Asia-Pacifico` · `Europa Core` · `Australia`

### SIEG Atlas — Infraestructura Critica
`Petroleo & Gas` · `Rutas Maritimas` · `Cables Submarinos`  
`Mar de China` · `Espacio` · `Cibergeopolitica`

---

## 📈 Niveles de Alerta / Alert Levels

| Score | Nivel | Descripcion |
|-------|-------|-------------|
| >= 80% | 🔴 CRITICO | Confrontacion directa / riesgo inmediato |
| 60-79% | 🟠 ALTO | Escalada activa / amenaza sostenida |
| 40-59% | 🟡 MEDIO | Tension elevada sin accion cinetica |
| < 40%  | 🟢 NORMAL | Situacion monitorizada |

---

## 🔌 Calidad de Fuentes / Source Quality

| Indicador | Noticias procesadas | Significado |
|-----------|---------------------|-------------|
| 🟢 VERDE  | >= 80 | Cobertura optima |
| 🔵 AZUL   | >= 60 | Cobertura aceptable |
| 🟡 AMARILLO | >= 40 | Cobertura reducida |
| 🟠 NARANJA | >= 20 | Cobertura critica |
| 🔴 ROJO   | < 20  | Sin cobertura — solo suelo base |

---

## 📁 Documentacion / Documentation

| Documento | Audiencia | Formato |
|-----------|-----------|---------|
| [Guia de Usuario](docs/user_guide.pdf) | Analistas / Publico | PDF bilingue |
| [Referencia Tecnica](docs/technical_reference.md) | Desarrolladores | Markdown |
| [Este README](README.md) | GitHub / Publico | Markdown |

---

## 🖥 Infraestructura / Infrastructure

- **Nodo fisico:** Odroid-C2 · ARM Cortex-A53 · 2GB RAM · DietPi
- **Ciclo SIEG-Core:** cada 30 minutos (cron)
- **Ciclo SIEG-Atlas:** cada 60 minutos (cron)
- **Rotacion datos:** semanal (90 dias activos + archivo historico)
- **Backup:** mensual tar.gz en GitHub rama archive

---

## 👤 Autor / Author

**M. Castillo** — [mybloggingnotes@gmail.com](mailto:mybloggingnotes@gmail.com)  
© 2026 — Open Source Intelligence Research

---

*Ultima actualizacion / Last updated: March 2026*
