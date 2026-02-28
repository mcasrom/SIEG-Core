import pathlib

html = ""
html += "<!DOCTYPE html>\n<html lang='es'>\n<head>\n"
html += "<meta charset='UTF-8'>\n"
html += "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
html += "<title>Intel Center</title>\n"
html += "<link href='https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600&display=swap' rel='stylesheet'>\n"
html += "<style>\n"
css = """
:root{--bg:#030810;--bg2:#060f1e;--card:#080f1a;--cy:#00d4ff;--gr:#00ff88;--am:#ffb800;--rd:#ff3c5a;--pu:#8b5cf6;--t1:#e2f0ff;--t2:#7090b0;--t3:#3a5070;--bd:#0d2040}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--t1);font-family:sans-serif;font-size:14px}
body::before{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(0,212,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,255,.04) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:0}
#hdr{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(3,8,16,.95);border-bottom:1px solid var(--bd);height:52px;display:flex;align-items:center;padding:0 16px;gap:16px}
.logo{font-size:18px;font-weight:900;color:var(--cy);letter-spacing:3px;text-shadow:0 0 18px rgba(0,212,255,.5)}
.logo span{color:var(--gr)}
.dot{width:6px;height:6px;border-radius:50%;background:var(--gr);animation:blink 1.5s infinite;box-shadow:0 0 6px var(--gr)}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}
.sysst{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--gr)}
.nav{display:flex;gap:4px;margin-left:12px}
.nb{background:none;border:1px solid transparent;color:var(--t2);font-size:13px;font-weight:600;padding:4px 10px;cursor:pointer;text-transform:uppercase;border-radius:2px;transition:all .2s}
.nb:hover,.nb.act{color:var(--cy);border-color:var(--cy);background:rgba(0,212,255,.07)}
.htime{margin-left:auto;font-size:11px;color:var(--t3)}
#app{padding-top:52px;position:relative;z-index:1}
.view{display:none;padding:14px}
.view.act{display:block}
#loading{position:fixed;inset:0;background:rgba(3,8,16,.92);z-index:200;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px}
#loading.hide{display:none}
.spin{width:40px;height:40px;border:3px solid var(--bd);border-top-color:var(--cy);border-radius:50%;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.ltxt{font-size:12px;color:var(--cy);letter-spacing:2px}
.lsub{font-size:10px;color:var(--t3)}
#errb{display:none;background:rgba(255,60,90,.1);border:1px solid var(--rd);color:var(--rd);font-size:11px;padding:8px 16px;text-align:center}
.dash-grid{display:grid;grid-template-columns:240px 1fr 260px;gap:12px}
@media(max-width:1050px){.dash-grid{grid-template-columns:1fr 260px}}
@media(max-width:720px){.dash-grid{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--bd);border-radius:4px;padding:14px;position:relative;overflow:hidden;transition:border-color .25s}
.card:hover{border-color:rgba(0,212,255,.25)}
.ct{font-size:9px;font-weight:700;color:var(--t2);text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;display:flex;align-items:center;gap:8px}
.ct::after{content:'';flex:1;height:1px;background:var(--bd)}
.ring-wrap{display:flex;flex-direction:column;align-items:center;gap:8px}
.ring{position:relative;width:110px;height:110px}
.ring svg{transform:rotate(-90deg);width:100%;height:100%}
.ring-bg{fill:none;stroke:#0d2040;stroke-width:8}
.ring-fill{fill:none;stroke-width:8;stroke-linecap:round;stroke-dasharray:283;stroke-dashoffset:283;transition:stroke-dashoffset 1.2s ease,stroke .5s}
.ring-val{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:24px;font-weight:900}
.ring-lbl{font-size:10px;letter-spacing:2px;text-transform:uppercase}
.bars{width:100%;display:flex;flex-direction:column;gap:6px;margin-top:8px}
.bar-row{display:flex;align-items:center;gap:8px;font-size:10px}
.bar-lbl{width:55px;color:var(--t2);text-transform:uppercase}
.bar-track{flex:1;height:4px;background:var(--bd);border-radius:2px;overflow:hidden}
.bar-fill{height:100%;border-radius:2px;transition:width 1.2s ease}
.bar-val{width:26px;text-align:right;color:var(--t1)}
.s4{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px}
@media(max-width:720px){.s4{grid-template-columns:repeat(2,1fr)}}
.stat{background:var(--card);border:1px solid var(--bd);border-radius:4px;padding:14px;text-align:center;transition:all .2s}
.stat:hover{border-color:rgba(0,212,255,.25);transform:translateY(-2px)}
.sv{font-size:24px;font-weight:700;line-height:1;margin-bottom:4px}
.sl{font-size:9px;color:var(--t2);text-transform:uppercase;letter-spacing:1.5px}
.sd{font-size:10px;margin-top:3px;color:var(--t3)}
.flist{display:flex;flex-direction:column;gap:5px;max-height:280px;overflow-y:auto}
.fi{padding:7px 9px;border:1px solid var(--bd);border-radius:3px;background:rgba(6,15,30,.6);cursor:pointer;font-size:12px;transition:background .2s}
.fi:hover{background:rgba(0,212,255,.04)}
.fi-id{font-size:10px;color:var(--cy);word-break:break-all}
.fi-txt{color:var(--t2);font-size:11px;word-break:break-word;margin-top:2px}
.fi-src{font-size:9px;color:var(--t3);margin-top:2px}
.badge{font-size:9px;padding:1px 5px;border-radius:2px;text-transform:uppercase;float:right;margin-left:6px}
.bc{background:rgba(255,60,90,.12);color:var(--rd);border:1px solid rgba(255,60,90,.3)}
.bh{background:rgba(255,184,0,.1);color:var(--am);border:1px solid rgba(255,184,0,.25)}
.bm{background:rgba(0,212,255,.1);color:var(--cy);border:1px solid rgba(0,212,255,.25)}
.alist{display:flex;flex-direction:column;gap:6px;max-height:400px;overflow-y:auto}
.ai{padding:8px 10px;border-radius:2px;cursor:pointer;background:rgba(6,15,30,.7);border:1px solid var(--bd);border-left:3px solid;transition:background .2s}
.ai:hover{background:rgba(0,212,255,.04)}
.ai.critical{border-left-color:var(--rd)}
.ai.high{border-left-color:var(--am)}
.ai.medium{border-left-color:var(--cy)}
.ait{font-weight:600;font-size:12px;line-height:1.3;margin-bottom:3px;word-break:break-word}
.aim{font-size:9px;color:var(--t3);display:flex;gap:10px;flex-wrap:wrap}
.ilist{display:flex;flex-direction:column;gap:5px}
.irow{display:flex;justify-content:space-between;align-items:center;padding:5px 8px;border:1px solid var(--bd);border-radius:3px;background:rgba(6,15,30,.5);font-size:10px}
.in{color:var(--t2)}
.iv{padding:1px 5px;border-radius:2px;font-weight:bold}
.ig{color:var(--gr);background:rgba(0,255,136,.08)}
.ia{color:var(--am);background:rgba(255,184,0,.08)}
.ir{color:var(--rd);background:rgba(255,60,90,.08)}
.ic{color:var(--cy);background:rgba(0,212,255,.08)}
.cl{display:flex;flex-direction:column;gap:12px}
.iot{width:100%;border-collapse:collapse;font-size:11px}
.iot th{text-align:left;color:var(--t3);font-size:9px;text-transform:uppercase;padding:6px 8px;border-bottom:1px solid var(--bd)}
.iot td{padding:5px 8px;border-bottom:1px solid rgba(13,32,64,.5);color:var(--t2);word-break:break-all}
.iot tr:hover td{background:rgba(0,212,255,.03);cursor:pointer}
.sh{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.sht{font-size:13px;font-weight:700;letter-spacing:1px}
.bsm{font-size:9px;padding:4px 9px;background:transparent;border:1px solid var(--bd);color:var(--t2);cursor:pointer;border-radius:2px;text-transform:uppercase;transition:all .2s}
.bsm:hover{border-color:var(--cy);color:var(--cy)}
.bpr{background:rgba(0,212,255,.1);border:1px solid var(--cy);color:var(--cy);font-weight:600;font-size:13px;padding:8px 18px;cursor:pointer;border-radius:3px;text-transform:uppercase;transition:all .2s}
.sbox{display:flex;gap:8px;margin-bottom:16px}
.sin{flex:1;background:var(--card);border:1px solid var(--bd);color:var(--t1);font-size:13px;padding:9px 14px;border-radius:3px;outline:none}
.sin:focus{border-color:var(--cy)}
.rc{background:var(--card);border:1px solid var(--bd);border-radius:4px;padding:12px 14px;cursor:pointer;margin-bottom:8px}
.rc:hover{border-color:rgba(0,212,255,.3)}
.rt{font-size:14px;font-weight:600;color:var(--cy);margin-bottom:4px}
.rs{font-size:12px;color:var(--t2);line-height:1.5;margin-bottom:6px}
.rm{font-size:9px;color:var(--t3)}
.mover{position:fixed;inset:0;background:rgba(3,8,16,.88);z-index:500;display:flex;align-items:center;justify-content:center;opacity:0;pointer-events:none;transition:opacity .2s}
.mover.open{opacity:1;pointer-events:all}
.modal{background:var(--bg2);border:1px solid rgba(0,212,255,.3);border-radius:4px;padding:20px;max-width:560px;width:92%;position:relative}
.mcl{position:absolute;top:12px;right:12px;background:none;border:none;color:var(--t2);font-size:18px;cursor:pointer}
.mti{font-size:13px;color:var(--cy);margin-bottom:12px;word-break:break-word;font-weight:700}
.mbo{font-size:12px;color:var(--t2);line-height:1.8}
.mbo p{margin-bottom:6px}
.mbo strong{color:var(--t1)}
.mtags{display:flex;flex-wrap:wrap;gap:4px;margin-top:10px}
.tag{font-size:9px;padding:2px 6px;border-radius:2px;background:rgba(0,212,255,.07);color:var(--cy);border:1px solid rgba(0,212,255,.2)}
#toasts{position:fixed;top:62px;right:14px;z-index:600;display:flex;flex-direction:column;gap:5px;pointer-events:none}
.toast{background:var(--bg2);border-left:3px solid var(--cy);padding:8px 12px;border-radius:3px;font-size:10px;color:var(--t1);max-width:280px}
.toast.warn{border-left-color:var(--am)}
.toast.err{border-left-color:var(--rd)}
.toast.ok{border-left-color:var(--gr)}
.srow{display:flex;justify-content:space-between;padding:5px 8px;background:rgba(6,15,30,.5);border:1px solid var(--bd);border-radius:3px;font-size:10px;margin-bottom:4px}
"""
html += css + "</style>\n</head>\n<body>\n"
html += '<div id="loading"><div class="spin"></div><div class="ltxt">CARGANDO INTELIGENCIA</div><div class="lsub" id="lmsg">Conectando...</div></div>\n'
html += '<header id="hdr"><div class="logo">INTEL<span>CENTER</span></div><div class="sysst"><div class="dot"></div><span id="systxt">INICIALIZANDO</span></div><nav class="nav"><button class="nb act" onclick="sv(\'dashboard\',this)">Dashboard</button><button class="nb" onclick="sv(\'search\',this)">Busqueda</button><button class="nb" onclick="sv(\'iocs\',this)">IOCs</button><button class="nb" onclick="sv(\'status\',this)">Fuentes</button></nav><div class="htime" id="htime"></div></header>\n'
html += '<div id="errb">Backend no disponible - ejecuta python3 app.py</div>\n'
html += '<div id="app">\n'
html += '<div id="view-dashboard" class="view act"><div class="s4" id="s4"></div><div class="dash-grid"><div class="cl"><div class="card"><div class="ct">Nivel de Amenaza</div><div class="ring-wrap"><div class="ring"><svg viewBox="0 0 100 100"><circle class="ring-bg" cx="50" cy="50" r="45"/><circle class="ring-fill" id="rarc" cx="50" cy="50" r="45"/></svg><div class="ring-val" id="rval">--</div></div><div class="ring-lbl" id="rlbl">CARGANDO</div><div class="bars" id="tbars"></div></div></div><div class="card"><div class="ct">Indicadores</div><div class="ilist" id="ilist"></div></div></div><div class="cl"><div class="card"><div class="ct">Alertas <span style="color:var(--rd);font-size:10px" id="acnt"></span></div><div class="alist" id="alist"><div style="color:var(--t3);font-size:11px;padding:20px;text-align:center">Cargando...</div></div></div><div class="card"><div class="ct">CVEs Criticas (NVD)</div><div class="flist" id="cvelist"></div></div></div><div class="cl"><div class="card"><div class="ct">CISA KEV</div><div class="flist" id="kevlist"></div></div><div class="card"><div class="ct">URLhaus</div><div class="flist" id="urllist"></div></div></div></div></div>\n'
html += '<div id="view-search" class="view"><div class="sh"><div class="sht">BUSQUEDA</div></div><div class="sbox"><input type="text" class="sin" id="sin" placeholder="CVE, IP, hash, vendor..."><button class="bpr" onclick="doSearch()">BUSCAR</button></div><div id="sres"></div></div>\n'
html += '<div id="view-iocs" class="view"><div class="sh"><div class="sht">TABLA DE IOCs</div><button class="bsm" onclick="renderIocs()">Actualizar</button></div><div style="overflow-x:auto"><table class="iot"><thead><tr><th style="width:40%">IOC</th><th style="width:15%">Tipo</th><th style="width:20%">Fuente</th><th style="width:10%">Conf%</th><th style="width:15%">Fecha</th></tr></thead><tbody id="iocbody"></tbody></table></div></div>\n'
html += '<div id="view-status" class="view"><div class="sh"><div class="sht">ESTADO DE FUENTES</div><button class="bsm" onclick="loadStatus()">Actualizar</button></div><div id="stgrid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px"></div></div>\n'
html += '</div>\n'
html += '<div class="mover" id="mover"><div class="modal"><button class="mcl" onclick="closeMod()">X</button><div class="mti" id="mti"></div><div class="mbo" id="mbo"></div><div class="mtags" id="mtags"></div></div></div>\n'
html += '<div id="toasts"></div>\n'

js = """
<script>
var API='http://localhost:7070';
var ST={cisa:[],nvd:[],feodo:[],urlhaus:[],malware:[],threatfox:[],alerts:[],stats:{},threat:0};

function e(s){if(s==null)return '';return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}

document.addEventListener('DOMContentLoaded',function(){
  tick(); setInterval(tick,1000);
  load(); setInterval(load,120000);
  document.getElementById('sin').addEventListener('keydown',function(ev){if(ev.key==='Enter')doSearch();});
});

function tick(){
  var n=new Date();
  document.getElementById('htime').textContent=n.toISOString().replace('T',' ').substring(0,19)+' UTC';
}

function load(){
  document.getElementById('lmsg').textContent='Descargando feeds reales...';
  var ctrl=new AbortController();
  var timer=setTimeout(function(){ctrl.abort();},25000);
  fetch(API+'/api/all',{signal:ctrl.signal})
    .then(function(r){clearTimeout(timer);if(!r.ok)throw new Error('HTTP '+r.status);return r.json();})
    .then(function(j){
      if(!j.ok)throw new Error('API error');
      ST=j.data; ST.stats=j.stats; ST.threat=j.threat_level;
      document.getElementById('loading').classList.add('hide');
      document.getElementById('systxt').textContent='EN LINEA - DATOS REALES';
      document.getElementById('errb').style.display='none';
      renderAll();
      toast('Actualizado: '+j.stats.last_update,'ok');
    })
    .catch(function(err){
      clearTimeout(timer);
      document.getElementById('loading').classList.add('hide');
      if(err.name==='AbortError'){
        document.getElementById('systxt').textContent='TIMEOUT';
        toast('Timeout - reintentando en 15s','warn');
        setTimeout(load,15000);
      } else {
        document.getElementById('errb').style.display='block';
        document.getElementById('systxt').textContent='ERROR BACKEND';
        toast('Error de conexion','err');
        setTimeout(load,20000);
      }
    });
}

function renderAll(){rStats();rThreat();rInds();rAlerts();rCVEs();rKEV();rURL();renderIocs();}

function rStats(){
  var s=ST.stats||{};
  var items=[
    {l:'IOCs Totales',v:s.total_iocs||0,c:'var(--cy)'},
    {l:'CVEs Criticas',v:s.total_cves||0,c:'var(--rd)'},
    {l:'Alertas Crit.',v:s.critical_alerts||0,c:'var(--am)'},
    {l:'Fuentes Online',v:s.online_sources||0,c:'var(--gr)'}
  ];
  document.getElementById('s4').innerHTML=items.map(function(i){
    return '<div class="stat"><div class="sv" style="color:'+i.c+'">'+i.v.toLocaleString()+'</div><div class="sl">'+i.l+'</div><div class="sd">TIEMPO REAL</div></div>';
  }).join('');
}

function rThreat(){
  var v=ST.threat||0;
  var arc=document.getElementById('rarc');
  var col=v>=80?'var(--rd)':v>=60?'var(--am)':v>=40?'var(--cy)':'var(--gr)';
  var lbl=v>=80?'CRITICO':v>=60?'ELEVADO':v>=40?'MODERADO':'BAJO';
  arc.style.strokeDashoffset=283*(1-v/100);
  arc.style.stroke=col;
  arc.style.filter='drop-shadow(0 0 8px '+col+')';
  document.getElementById('rval').textContent=v;
  document.getElementById('rval').style.color=col;
  document.getElementById('rlbl').textContent=lbl;
  document.getElementById('rlbl').style.color=col;
  var bars=[
    {l:'CVEs',v:Math.min((ST.nvd||[]).length*5,100),c:'var(--rd)'},
    {l:'C2 IPs',v:Math.min((ST.feodo||[]).length*3,100),c:'var(--am)'},
    {l:'URLs',v:Math.min((ST.urlhaus||[]).length*5,100),c:'var(--cy)'},
    {l:'IOCs',v:Math.min((ST.threatfox||[]).length*4,100),c:'var(--pu)'}
  ];
  document.getElementById('tbars').innerHTML=bars.map(function(b){
    return '<div class="bar-row"><span class="bar-lbl">'+b.l+'</span><div class="bar-track"><div class="bar-fill" style="width:'+b.v+'%;background:'+b.c+'"></div></div><span class="bar-val">'+b.v+'</span></div>';
  }).join('');
}

function rInds(){
  var s=ST.stats||{};
  var items=[
    {n:'CISA KEV',v:(ST.cisa||[]).length+' vulns',c:'ir'},
    {n:'NVD CVEs',v:(ST.nvd||[]).length+' criticas',c:'ir'},
    {n:'Feodo IPs',v:(ST.feodo||[]).length+' IPs',c:'ia'},
    {n:'URLhaus',v:(ST.urlhaus||[]).length+' URLs',c:'ia'},
    {n:'ThreatFox',v:(ST.threatfox||[]).length+' IOCs',c:'ic'},
    {n:'Fuentes',v:(s.online_sources||0)+'/5',c:'ig'}
  ];
  document.getElementById('ilist').innerHTML=items.map(function(i){
    return '<div class="irow"><span class="in">'+i.n+'</span><span class="iv '+i.c+'">'+i.v+'</span></div>';
  }).join('');
}

function rAlerts(){
  var al=ST.alerts||[];
  document.getElementById('acnt').textContent='['+al.length+']';
  if(!al.length){
    document.getElementById('alist').innerHTML='<div style="color:var(--t3);font-size:11px;text-align:center;padding:16px">Sin alertas disponibles</div>';
    return;
  }
  document.getElementById('alist').innerHTML=al.map(function(a){
    var bc=a.severity==='critical'?'bc':a.severity==='high'?'bh':'bm';
    var detail=e(a.detail||'');
    var src=e(a.source||'');
    var dt=e(a.date||'');
    var ttl=e(a.title||'');
    var tags=JSON.stringify(a.tags||[]);
    var id=e(a.id||'');
    return '<div class="ai '+a.severity+'" onclick="openMod(\''+id+'\',\'<p><strong>Fuente:</strong> '+src+'</p><p><strong>Fecha:</strong> '+dt+'</p><p>'+detail+'</p>\','+tags+')"><span class="badge '+bc+'">'+a.severity+'</span><div class="ait">'+ttl+'</div><div class="aim"><span>'+src+'</span><span>'+dt+'</span></div></div>';
  }).join('');
}

function rCVEs(){
  var list=ST.nvd||[];
  document.getElementById('cvelist').innerHTML=list.length?list.map(function(c){
    var bc=c.severity==='critical'?'bc':'bh';
    var score=c.score||'?';
    var id=e(c.id||'');
    var title=e(c.title||'');
    var pub=e(c.published||'');
    var sev=e(c.severity||'');
    var tags=JSON.stringify(['NVD',c.severity,'CVSS '+score]);
    return '<div class="fi" onclick="openMod(\''+id+'\',\'<p><strong>CVSS:</strong> '+score+'</p><p><strong>Severidad:</strong> '+sev+'</p><p><strong>Publicado:</strong> '+pub+'</p><p>'+title+'</p>\','+tags+')"><div style="display:flex;justify-content:space-between"><span class="fi-id">'+id+'</span><span class="badge '+bc+'">CVSS '+score+'</span></div><div class="fi-txt">'+title+'</div><div class="fi-src">'+pub+'</div></div>';
  }).join(''):'<div style="color:var(--t3);font-size:11px;padding:12px;text-align:center">Sin datos NVD</div>';
}

function rKEV(){
  var list=ST.cisa||[];
  document.getElementById('kevlist').innerHTML=list.length?list.map(function(c){
    var id=e(c.id||'');
    var vendor=e(c.vendor||'');
    var prod=e(c.product||'');
    var da=e(c.date_added||'');
    var dd=e(c.due_date||'');
    var action=e(c.action||'');
    var title=e(c.title||'');
    var tags=JSON.stringify(['CISA','KEV',c.vendor||'']);
    return '<div class="fi" onclick="openMod(\''+id+'\',\'<p><strong>Vendor:</strong> '+vendor+'</p><p><strong>Producto:</strong> '+prod+'</p><p><strong>Añadido:</strong> '+da+'</p><p><strong>Limite:</strong> '+dd+'</p><p>'+action+'</p>\','+tags+')"><div style="display:flex;justify-content:space-between"><span class="fi-id">'+id+'</span><span class="badge bc">KEV</span></div><div class="fi-txt">'+vendor+' - '+title+'</div><div class="fi-src">Añadido: '+da+'</div></div>';
  }).join(''):'<div style="color:var(--t3);font-size:11px;padding:12px;text-align:center">Sin datos CISA</div>';
}

function rURL(){
  var list=ST.urlhaus||[];
  document.getElementById('urllist').innerHTML=list.length?list.map(function(u){
    var url=e(u.url||'');
    var threat=e(u.threat||'');
    var country=e(u.country||'');
    var da=e(u.date_added||'');
    var tags=JSON.stringify(['URLhaus',u.threat||'',u.country||'']);
    return '<div class="fi" onclick="openMod(\'URL Maliciosa\',\'<p><strong>URL:</strong> '+url+'</p><p><strong>Threat:</strong> '+threat+'</p><p><strong>Pais:</strong> '+country+'</p><p><strong>Fecha:</strong> '+da+'</p>\','+tags+')"><div style="display:flex;justify-content:space-between"><span class="fi-id">'+url+'</span><span class="badge bh">ONLINE</span></div><div class="fi-txt">'+threat+' - '+country+'</div><div class="fi-src">'+da+'</div></div>';
  }).join(''):'<div style="color:var(--t3);font-size:11px;padding:12px;text-align:center">Sin datos URLhaus</div>';
}

function renderIocs(){
  var iocs=[];
  (ST.feodo||[]).forEach(function(i){iocs.push({ioc:i.ip+(i.port?':'+i.port:''),type:'IP C2',src:'Feodo Tracker',conf:90,date:(i.first_seen||'').substring(0,10)});});
  (ST.urlhaus||[]).forEach(function(i){iocs.push({ioc:i.url,type:'URL',src:'URLhaus',conf:85,date:(i.date_added||'').substring(0,10)});});
  (ST.threatfox||[]).forEach(function(i){iocs.push({ioc:i.ioc,type:i.ioc_type||'IOC',src:'ThreatFox',conf:i.confidence||0,date:(i.first_seen||'').substring(0,10)});});
  var body=document.getElementById('iocbody');
  if(!iocs.length){body.innerHTML='<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--t3)">Sin IOCs</td></tr>';return;}
  body.innerHTML=iocs.map(function(i){
    var cc=i.conf>=80?'var(--rd)':i.conf>=60?'var(--am)':'var(--gr)';
    var ii=e(i.ioc); var it=e(i.type); var is=e(i.src); var id2=e(i.date);
    var tags=JSON.stringify([i.src,i.type]);
    return '<tr onclick="openMod(\''+it+'\',\'<p><strong>IOC:</strong> '+ii+'</p><p><strong>Fuente:</strong> '+is+'</p><p><strong>Confianza:</strong> '+i.conf+'%</p><p><strong>Fecha:</strong> '+id2+'</p>\','+tags+')"><td style="color:var(--cy);font-size:10px">'+ii+'</td><td>'+it+'</td><td>'+is+'</td><td style="text-align:center;color:'+cc+'">'+i.conf+'</td><td>'+id2+'</td></tr>';
  }).join('');
}

function doSearch(){
  var q=document.getElementById('sin').value.trim().toLowerCase();
  var el=document.getElementById('sres');
  if(!q){el.innerHTML='<div style="color:var(--t3);font-size:11px;text-align:center;padding:40px">Ingresa terminos</div>';return;}
  var results=[];
  var all=[].concat(ST.alerts||[],ST.cisa||[],ST.nvd||[],ST.feodo||[],ST.urlhaus||[],ST.threatfox||[]);
  all.forEach(function(item){
    if(JSON.stringify(item).toLowerCase().indexOf(q)>=0){
      var title=item.title||item.id||item.ip||item.url||item.ioc||'Resultado';
      var snip=item.detail||item.action||item.title||item.threat||item.malware||'';
      var meta=item.source||item.src||'Intel';
      results.push({title:String(title),snip:String(snip),meta:String(meta)});
    }
  });
  if(!results.length){el.innerHTML='<div style="color:var(--t3);font-size:11px;text-align:center;padding:40px">Sin resultados para '+e(q)+'</div>';return;}
  el.innerHTML=results.slice(0,40).map(function(r){
    return '<div class="rc"><div class="rt">'+e(r.title)+'</div><div class="rs">'+e(r.snip.substring(0,150))+'</div><div class="rm">'+e(r.meta)+'</div></div>';
  }).join('');
  toast(results.length+' resultados para '+q,'ok');
}

function loadStatus(){
  fetch(API+'/api/status').then(function(r){return r.json();}).then(function(j){
    var names={cisa_kev:'CISA KEV',nvd_cves:'NVD CVEs',feodo_ips:'Feodo Tracker',urlhaus:'URLhaus',malware_bazaar:'MalwareBazaar',threatfox:'ThreatFox'};
    document.getElementById('stgrid').innerHTML=Object.entries(j.feeds).map(function(entry){
      var k=entry[0],v=entry[1];
      var col=v.valid?'color:var(--gr)':v.cached?'color:var(--am)':'color:var(--rd)';
      var txt=v.valid?'VALIDA':v.cached?'EXPIRADA':'SIN CACHE';
      return '<div class="card"><div class="ct">'+(names[k]||k)+'</div><div class="srow"><span style="color:var(--t2)">Estado</span><span style="'+col+'">'+txt+'</span></div>'+(v.cached?'<div class="srow"><span style="color:var(--t2)">Edad</span><span style="color:var(--t3)">'+Math.floor(v.age_sec/60)+'min</span></div>':'')+'</div>';
    }).join('');
  }).catch(function(){toast('Error cargando estado','err');});
}

function sv(name,btn){
  document.querySelectorAll('.view').forEach(function(v){v.classList.remove('act');});
  document.querySelectorAll('.nb').forEach(function(b){b.classList.remove('act');});
  document.getElementById('view-'+name).classList.add('act');
  btn.classList.add('act');
  if(name==='status')loadStatus();
  if(name==='iocs')renderIocs();
}

function openMod(title,body,tags){
  document.getElementById('mti').textContent=title;
  document.getElementById('mbo').innerHTML=body;
  document.getElementById('mtags').innerHTML=(tags||[]).map(function(t){return '<span class="tag">'+e(String(t))+'</span>';}).join('');
  document.getElementById('mover').classList.add('open');
}

function closeMod(){document.getElementById('mover').classList.remove('open');}

document.getElementById('mover').addEventListener('click',function(ev){if(ev.target===document.getElementById('mover'))closeMod();});

function toast(msg,type){
  var el=document.createElement('div');
  el.className='toast '+(type||'');
  el.textContent=msg;
  document.getElementById('toasts').appendChild(el);
  setTimeout(function(){el.remove();},4500);
}
</script>
"""
html += js + "\n</body>\n</html>\n"

out = pathlib.Path("static/index.html")
out.write_text(html, encoding="utf-8")
print("OK - escrito: " + str(len(html)) + " chars, " + str(len(html.splitlines())) + " lineas")

# Verificar que no hay comillas simples sueltas en el JS
import re
lines = html.splitlines()
for i, line in enumerate(lines, 1):
    if i > 200 and "'" in line and "<script>" not in line and "</script>" not in line:
        # Buscar patrones problemáticos: comilla simple dentro de string JS sin escapar
        if re.search(r"innerHTML\s*=\s*.*'[^']*'[^']*'", line):
            print(f"AVISO linea {i}: posible comilla suelta")
            break
print("Verificacion completada")
