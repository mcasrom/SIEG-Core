import json, os, time
from flask import Flask, render_template_string, send_file
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <title>S.I.E.G. | Node Alpha</title>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="60">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root { --neon-green: #00ff41; --neon-red: #ff0000; --bg-black: #0a0a0a; --card-bg: #111; }
        body { background: var(--bg-black); color: var(--neon-green); font-family: 'Courier New', monospace; margin: 0; padding: 20px; }
        header { display: flex; justify-content: space-between; border-bottom: 2px solid var(--neon-green); padding-bottom: 10px; margin-bottom: 20px; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab-btn { background: none; border: 1px solid var(--neon-green); color: var(--neon-green); padding: 10px 20px; cursor: pointer; }
        .tab-btn:hover { background: var(--neon-green); color: black; }
        .grid { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 20px; }
        .card { background: var(--card-bg); border: 1px solid #333; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,255,65,0.1); }
        .status-node { color: var(--neon-green); font-weight: bold; }
        .alert-kinetic { color: var(--neon-red); animation: blink 1s infinite; }
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.2; } 100% { opacity: 1; } }
        table { width: 100%; border-collapse: collapse; font-size: 0.9em; }
        th, td { padding: 8px; border-bottom: 1px solid #222; text-align: left; }
        .hidden { display: none; }
        .timestamp { font-size: 1.2em; border: 1px solid var(--neon-green); padding: 5px 15px; }
    </style>
</head>
<body>

<header>
    <div>
        <h1 style="margin:0;">S.I.E.G. CORE <span style="font-size:0.5em;">v5.2</span></h1>
        <div class="status-node">NODE_STATUS: ONLINE | AUTH: M. CASTILLO</div>
    </div>
    <div class="timestamp" id="clock">{{ now }}</div>
</header>

<div class="tabs">
    <button class="tab-btn" onclick="showTab('radar')">RADAR_INTEL</button>
    <button class="tab-btn" onclick="showTab('arch')">ARQUITECTURA</button>
    <button class="tab-btn" onclick="showTab('meth')">METODOLOGÍA</button>
    <button class="tab-btn" onclick="showTab('about')">ABOUT</button>
    <a href="/download" class="tab-btn" style="text-decoration:none;">EXPORT_LOGS</a>
</div>

<div id="radar" class="tab-content">
    <div class="grid">
        <div class="card">
            <h3>GLOBAL_THREAT_RADAR</h3>
            <canvas id="radarChart"></canvas>
        </div>
        <div class="card">
            <h3>KINETIC_STATUS_REPORT</h3>
            <table>
                <tr><th>REGION</th><th>LEVEL</th><th>STATUS</th></tr>
                {% for r in regiones %}
                <tr>
                    <td>{{ r.name }}</td>
                    <td>{{ r.score }}%</td>
                    <td class="{{ 'alert-kinetic' if r.score > 70 else '' }}">
                        {{ "● WAR_KINETIC" if r.score > 70 else "○ SOCIAL_TENSION" if r.score > 40 else "◌ STABLE" }}
                    </td>
                </tr>
                {% endfor %}
            </table>
            <br>
            <h3>AVG_TENSION_HISTORY</h3>
            <canvas id="lineChart"></canvas>
        </div>
    </div>
</div>

<div id="arch" class="tab-content hidden">
    <div class="card">
        <h3>SISTEMA MODULAR S.I.E.G.</h3>
        <p>1. <b>feeds_config.json</b>: Capa de datos y URLs de inteligencia.</p>
        <p>2. <b>intel_scanner.py</b>: Motor de triaje y procesamiento cinético.</p>
        <p>3. <b>app.py</b>: Nodo de visualización y API Flask.</p>
        <p>4. <b>Historico.json</b>: Base de datos cronológica.</p>
    </div>
</div>

<div id="meth" class="tab-content hidden">
    <div class="card">
        <h3>ALGORITMO DE TRIAJE CINÉTICO</h3>
        <p>El sistema separa el "Ruido Social" de la "Acción Cinética":</p>
        <ul>
            <li><b>Techo Social (40%)</b>: Regiones sin palabras clave de combate (ej. España).</li>
            <li><b>Trigger Cinético (70%+)</b>: Activado por impactos, misiles o invasiones (ej. Irán).</li>
            <li><b>Triangulación</b>: Mínimo 3 fuentes por región para validar la alerta.</li>
        </ul>
    </div>
</div>

<div id="about" class="tab-content hidden">
    <div class="card">
        <h3>SIEG - SYSTEM INTELLIGENCE EARLY GATE</h3>
        <p>Desarrollado para el análisis de código abierto (OSINT).</p>
        <p>Autor: M. Castillo | Entorno: GNU/Linux 26-Year Veteran Build.</p>
    </div>
</div>

<script>
    function showTab(id) {
        document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
        document.getElementById(id).classList.remove('hidden');
    }

    const radarCtx = document.getElementById('radarChart');
    new Chart(radarCtx, {
        type: 'radar',
        data: {
            labels: {{ labels|tojson }},
            datasets: [{
                label: 'Tensión Real',
                data: {{ scores|tojson }},
                backgroundColor: 'rgba(0, 255, 65, 0.1)',
                borderColor: '#00ff41',
                borderWidth: 2
            }]
        },
        options: {
            scales: { r: { angleLines: {color:'#333'}, grid: {color:'#333'}, pointLabels:{color:'#00ff41'}, suggestMin:0, suggestMax:100 } }
        }
    });

    const lineCtx = document.getElementById('lineChart');
    new Chart(lineCtx, {
        type: 'line',
        data: {
            labels: {{ hist.labels|tojson }},
            datasets: [{ label: 'Global Avg', data: {{ hist.scores|tojson }}, borderColor: '#ff0000', borderWidth: 1, fill: false }]
        }
    });
</script>
</body>
</html>
"""

@app.route('/')
def index():
    regiones = []
    labels, scores = [], []
    for f in sorted(DATA_DIR.glob("geoint_*.json")):
        with open(f, 'r') as j:
            s = json.load(j).get("score", 0)
            n = f.stem.replace("geoint_", "").upper()
            regiones.append({"name": n, "score": s})
            labels.append(n); scores.append(s)
    
    hist = {"labels": [], "scores": []}
    if (DATA_DIR / "historico.json").exists():
        with open(DATA_DIR / "historico.json", 'r') as f: hist = json.load(f)
    
    return render_template_string(HTML_TEMPLATE, regiones=regiones, labels=labels, scores=scores, hist=hist, now=datetime.now().strftime('%H:%M:%S'))

@app.route('/download')
def download():
    path = DATA_DIR / "historico.json"
    return send_file(path, as_attachment=True) if path.exists() else "No log file found."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7070)
