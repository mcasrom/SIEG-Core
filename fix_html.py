html = open('static/index.html').read()

# Fix 1: comillas en font-family dentro de innerHTML
html = html.replace(
    """'<div style="color:var(--t3);font-family:'Share Tech Mono',monospace;font-size:11px;text-align:center;padding:16px">Sin alertas</div>'""",
    """'<div style="color:var(--t3);font-family:Share Tech Mono,monospace;font-size:11px;text-align:center;padding:16px">Sin alertas</div>'"""
)

# Fix 2: openMod con comillas simples sin escapar
html = html.replace(
    """return '<div class="ai '+a.severity+'" onclick="openMod(''+esc(a.id)+'','""",
    """return '<div class="ai "+a.severity+'" onclick="openMod("+chr(39)+esc(a.id)+chr(39)+",\\'""".replace("chr(39)", "\\'")
)

open('static/index.html', 'w').write(html)
print("Hecho")
