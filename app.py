import json, os, time
from flask import Flask, render_template_string, send_file
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def leer_texto(archivo):
    p = Path(archivo)
    return p.read_text(encoding='utf-8') if p.exists() else "Narrativa no disponible."

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <title>S.I.E.G. | Node Alpha</title>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="60">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root { 
            --neon-green: #00ff41; --neon-red: #ff0000; --neon-cyan: #00ffff; --bg-black: #0a0a0a; --card-bg: #111;
            --status-color: {{ 'var(--neon-green)' if node_online else '#ffaa00' }};
        }
        body { background: var(--bg-black); color: var(--neon-green); font-family: 'Courier New', monospace; margin: 0; padding: 20px;
               {% if avg_global > 60 %} box-shadow: inset 0 0 100px rgba(255, 0, 0, 0.2); {% endif %} }
        header { display: flex; justify-content: space-between; border-bottom: 2px solid var(--neon-green); padding-bottom: 10px; margin-bottom: 20px; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab-btn { background: none; border: 1px solid var(--neon-green); color: var(--neon-green); padding: 10px 20px; cursor: pointer; }
        .tab-btn:hover { background: var(--neon-green); color: black; }
        .grid { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 20px; }
        .card { background: var(--card-bg); border: 1px solid #333; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,255,65,0.1); }
        .status-node { color: var(--status-color); font-weight: bold; }
        .alert-kinetic { color: var(--neon-red); animation: blink 1s infinite; }
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.2; } 100% { opacity: 1; } }
        table { width: 100%; border-collapse: collapse; font-size: 0.85em; }
        th, td { padding: 6px; border-bottom: 1px solid #222; text-align: left; }
        .hidden { display: none; }
        .white-text { color: white; white-space: pre-wrap; font-size: 0.9em; }
        .disonancia-text { color: var(--neon-cyan); font-weight: bold; }
    </style>
</head>
<body>

<header>
    <div>
        <h1 style="margin:0;">S.I.E.G. CORE <span style="font-size:0.5em;">v5.7</span></h1>
        <div class="status-node">NODE_STATUS: {{ 'ONLINE' if node_online else 'STALE' }} | AUTH: M. CASTILLO</div>
    </div>
    <div class="timestamp" id="clock">{{ now }}</div>
</header>

<div class="tabs">
    <button class="tab-btn" onclick="showTab('radar')">RADAR_INTEL</button>
    <button class="tab-btn" onclick="showTab('arch')">ARQUITECTURA</button>
    <button class="tab-btn" onclick="showTab('meth')">METODOLOGÍA</button>
    <button class="tab-btn" onclick="showTab('contact')">CONTACTO</button>
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
                <tr><th>REGION</th><th>SCORE</th><th>STATUS</th></tr>
                {% for r in regiones %}
                <tr>
                    <td>{{ r.name }}</td>
                    <td>{{ r.score }}%</td>
                    <td class="{{ 'alert-kinetic' if r.score > 70 and not r.conflict else '' }} {{ 'disonancia-text' if r.conflict else '' }}">
                        {% if r.conflict %}⚠️ DISONANCIA{% elif r.score > 70 %}● WAR_KINETIC{% elif r.score > 40 %}○ TENSION{% else %}◌ STABLE{% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
            <canvas id="lineChart" style="margin-top:15px; max-height: 150px;"></canvas>
        </div>
    </div>
</div>

<div id="arch" class="tab-content hidden"><div class="card"><div class="white-text">{{ txt_arch }}</div></div></div>
<div id="meth" class="tab-content hidden"><div class="card"><div class="white-text">{{ txt_meth }}</div></div></div>
<div id="about" class="tab-content hidden"><div class="card"><div class="white-text">{{ txt_about }}</div></div></div>
<div id="contact" class="tab-content hidden"><div class="card"><h3>ENLACE OPERATIVO</h3><p>Email: <a href="mailto:mybloggingnotes@gmail.com" style="color:var(--neon-green)">mybloggingnotes@gmail.com</a></p></div></div>

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
                label: 'Tensión', 
                data: {{ scores|tojson }}, 
                backgroundColor: 'rgba(0, 255, 65, 0.1)', 
                borderColor: '#00ff41', 
                borderWidth: 2,
                pointBackgroundColor: '#00ff41'
            }] 
        },
        options: {
            scales: { 
                r: { 
                    min: 0, max: 100,
                    beginAtZero: true,
                    angleLines: {color:'#333'}, 
                    grid: {color:'#333'}, 
                    pointLabels: {color:'#00ff41', font: {size: 11}},
                    ticks: { display: false, stepSize: 20 }
                } 
            },
            plugins: { legend: { display: false } }
        }
    });

    const lineCtx = document.getElementById('lineChart');
    new Chart(lineCtx, {
        type: 'line',
        data: { labels: {{ hist.labels|tojson }}, datasets: [{ label: 'Global Avg', data: {{ hist.scores|tojson }}, borderColor: '#ff0000', borderWidth: 1, fill: false, pointRadius: 0 }] },
        options: { scales: { y: { min: 0, max: 100, grid: {color: '#222'} }, x: { grid: {display: false} } }, plugins: {legend: {display: false}} }
    });
</script>
</body>
</html>
"""

@app.route('/')
def index():
    regiones = []
    labels, scores = [], []
    last_mod = 0
    archivos = sorted(DATA_DIR.glob("geoint_*.json"))
    
    for f in archivos:
        m = f.stat().st_mtime
        if m > last_mod: last_mod = m
        try:
            with open(f, 'r') as j:
                content = json.load(j)
                s = content.get("score", 15)
                c = content.get("conflict", False)
                n = f.stem.replace("geoint_", "").upper().replace("_", " ")
                regiones.append({"name": n, "score": s, "conflict": c})
                labels.append(n)
                scores.append(s)
        except: continue
    
    node_online = (time.time() - last_mod) < 1200 if last_mod > 0 else False
    avg_global = sum(scores) / len(scores) if scores else 0
    hist = {"labels": [], "scores": []}
    if (DATA_DIR / "historico.json").exists():
        with open(DATA_DIR / "historico.json", 'r') as f: hist = json.load(f)
    
    return render_template_string(HTML_TEMPLATE, 
        regiones=regiones, labels=labels, scores=scores, hist=hist, 
        now=datetime.now().strftime('%H:%M:%S'), node_online=node_online, avg_global=avg_global,
        txt_arch=leer_texto("arquitectura.md"), txt_meth=leer_texto("metodologia.md"), txt_about=leer_texto("about.md"))

@app.route('/download')
def download():
    path = DATA_DIR / "historico.json"
    return send_file(path, as_attachment=True) if path.exists() else "Error: Log no hallado."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7070)
