'use strict';
// Panel de administración OPCIONAL. Levanta un mini-servidor HTTP (sin dependencias)
// con API REST + una UI embebida para gestionar los datos que registra el kit:
// consentimientos, transferencias, auditoría, ROPA, y el DERECHO AL OLVIDO (borrar
// todos los datos de un titular). Superficie sensible: úsalo detrás de auth e interno.
const http = require('http');

function html() {
  return `<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>privacy-kit · Admin</title>
<style>
 :root{--bg:#0d1117;--card:#161b22;--bd:#30363d;--fg:#c9d1d9;--acc:#58a6ff;--g:#3fb950;--r:#ff7b72}
 *{box-sizing:border-box;font-family:'Segoe UI',system-ui,Arial,sans-serif}
 body{margin:0;background:var(--bg);color:var(--fg)}
 header{background:#0f2b46;padding:14px 22px;display:flex;align-items:center;gap:12px;border-bottom:1px solid var(--bd)}
 header h1{font-size:17px;margin:0;color:#fff}.tag{color:#7fc4ff;font-size:12px}
 main{max-width:960px;margin:0 auto;padding:20px}
 .card{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:16px 18px;margin-bottom:16px}
 .row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
 input{background:#0d1117;border:1px solid var(--bd);color:var(--fg);padding:9px 11px;border-radius:7px;font-size:14px}
 input.grow{flex:1;min-width:180px}
 button{background:var(--acc);color:#04121f;border:0;padding:9px 15px;border-radius:7px;font-weight:700;cursor:pointer;font-size:14px}
 button.ghost{background:#21262d;color:var(--fg);border:1px solid var(--bd)}
 button.danger{background:#8b1a1a;color:#fff}
 h2{font-size:14px;color:var(--acc);margin:0 0 8px;text-transform:uppercase;letter-spacing:.5px}
 .chips{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:6px}
 .chip{background:#0d2136;border:1px solid #1f6feb55;border-radius:8px;padding:8px 12px;min-width:120px}
 .chip b{display:block;font-size:22px;color:#fff}.chip span{font-size:11px;color:#8b949e}
 table{width:100%;border-collapse:collapse;font-size:12.5px;margin-top:4px}
 th{text-align:left;color:#8b949e;font-weight:600;padding:6px 8px;border-bottom:1px solid var(--bd)}
 td{padding:6px 8px;border-bottom:1px solid #21262d;vertical-align:top}
 pre{background:#0d1117;border:1px solid var(--bd);border-radius:8px;padding:10px;overflow:auto;font-size:12px;max-height:200px}
 .muted{color:#8b949e;font-size:12px}.mono{font-family:Consolas,monospace}
 .danger-zone{border-color:#8b1a1a55}
 #toast{position:fixed;right:18px;bottom:18px;background:#161b22;border:1px solid var(--bd);border-left:4px solid var(--g);padding:12px 16px;border-radius:8px;display:none;max-width:340px;font-size:13px}
 a{color:var(--acc)}
</style></head><body>
<header><span style="font-size:20px">🛡️</span><h1>privacy-kit</h1><span class="tag">Panel de administración · Ley 21.719</span></header>
<main>
 <div class="card">
   <h2>Acceso</h2>
   <div class="row">
     <input id="tok" class="grow" type="password" placeholder="Token de acceso (admin_ui.token)">
     <button class="ghost" onclick="saveTok()">Guardar token</button>
     <button class="ghost" onclick="loadRopa()">Ver ROPA</button>
   </div>
 </div>

 <div class="card">
   <h2>Buscar por dato (RUT / email / teléfono)</h2>
   <div class="row">
     <input id="q" class="grow mono" placeholder="ej. 11.111.111-1 o cliente@correo.cl">
     <button onclick="buscarDato()">Buscar</button>
   </div>
   <div id="cands" class="muted" style="margin-top:8px">Requiere un resolver registrado (register_resolver) que mapee el dato al subject_id.</div>
 </div>
 <div class="card">
   <h2>Buscar por subject_id</h2>
   <div class="row">
     <input id="sid" class="grow mono" placeholder="subject_id (ej. hash del RUT)">
     <button onclick="buscar()">Buscar</button>
   </div>
   <div class="muted" style="margin-top:6px">Muestra todo lo que el kit tiene de esa persona: consentimientos, transferencias, datos en las fuentes y auditoría.</div>
 </div>

 <div id="res"></div>
</main>
<div id="toast"></div>
<script>
const $=s=>document.querySelector(s);
let TOKEN=localStorage.getItem('pk_tok')||'';
$('#tok').value=TOKEN;
function saveTok(){TOKEN=$('#tok').value.trim();localStorage.setItem('pk_tok',TOKEN);toast('Token guardado');}
function toast(m,ok=true){const t=$('#toast');t.style.borderLeftColor=ok?'#3fb950':'#ff7b72';t.textContent=m;t.style.display='block';setTimeout(()=>t.style.display='none',3500);}
async function api(path,opts={}){opts.headers=Object.assign({'Content-Type':'application/json','Authorization':'Bearer '+TOKEN},opts.headers||{});const r=await fetch(path,opts);if(r.status===401){toast('Token inválido o faltante',false);throw new Error('401');}return r.json();}
function tbl(rows){if(!rows||!rows.length)return '<div class="muted">— sin registros —</div>';const cols=[...new Set(rows.flatMap(r=>Object.keys(r)))];let h='<table><tr>'+cols.map(c=>'<th>'+c+'</th>').join('')+'</tr>';for(const row of rows){h+='<tr>'+cols.map(c=>'<td class="mono">'+fmt(row[c])+'</td>').join('')+'</tr>';}return h+'</table>';}
function fmt(v){if(v==null)return '';if(typeof v==='object')return JSON.stringify(v);return String(v);}
async function buscarDato(){
  const q=$('#q').value.trim();if(!q){toast('Ingresa un dato',false);return;}
  let d;try{d=await api('/api/resolve?q='+encodeURIComponent(q));}catch(e){return;}
  if(!d.supported){$('#cands').innerHTML='<span style="color:#ff7b72">No hay resolver configurado. Registra uno con register_resolver(fn) para buscar por RUT/email/teléfono.</span>';return;}
  if(!d.results.length){$('#cands').textContent='Sin coincidencias.';return;}
  $('#cands').innerHTML='Coincidencias: '+d.results.map(id=>'<button class="ghost" style="margin:3px" onclick="pick(\\''+id+'\\')">'+id+'</button>').join('');
}
function pick(id){$('#sid').value=id;buscar();}
async function buscar(){
  const id=$('#sid').value.trim();if(!id){toast('Ingresa un subject_id',false);return;}
  let d;try{d=await api('/api/subject?id='+encodeURIComponent(id));}catch(e){return;}
  $('#res').innerHTML=\`
   <div class="card"><h2>Resumen — \${id}</h2>
     <div class="chips">
       <div class="chip"><b>\${d.consents.length}</b><span>consentimientos</span></div>
       <div class="chip"><b>\${d.transfers.length}</b><span>transferencias</span></div>
       <div class="chip"><b>\${d.audit.length}</b><span>eventos auditados</span></div>
     </div>
   </div>
   <div class="card"><h2>Consentimientos</h2>\${tbl(d.consents)}</div>
   <div class="card"><h2>Transferencias a terceros</h2>\${tbl(d.transfers)}</div>
   <div class="card"><h2>Datos en las fuentes de negocio</h2><pre>\${JSON.stringify(d.data,null,2)}</pre></div>
   <div class="card"><h2>Auditoría</h2>\${tbl(d.audit)}</div>
   <div class="card danger-zone"><h2 style="color:#ff7b72">⚠️ Derecho al olvido</h2>
     <div class="muted">Elimina TODOS los datos personales de este titular (fuentes + consentimientos + transferencias). La auditoría se conserva como evidencia.</div>
     <div class="row" style="margin-top:10px"><button class="danger" onclick="olvidar('\${id}')">🗑️ Eliminar todos los datos de \${id}</button></div>
   </div>\`;
}
async function olvidar(id){
  if(!confirm('¿Eliminar TODOS los datos de '+id+'? Esta acción no se puede deshacer.'))return;
  let c;try{c=await api('/api/subject/forget',{method:'POST',body:JSON.stringify({id})});}catch(e){return;}
  toast('Datos eliminados → '+JSON.stringify(c));buscar();
}
async function loadRopa(){let d;try{d=await api('/api/ropa');}catch(e){return;}$('#res').innerHTML='<div class="card"><h2>ROPA — Registro de Actividades de Tratamiento</h2><pre>'+d.ropa.replace(/</g,'&lt;')+'</pre></div>';}
</script></body></html>`;
}

function serveAdmin(pk, opts = {}) {
  const cfg = (pk.config.raw && pk.config.raw.adminUi) || {};
  const enabled = opts.enabled !== undefined ? opts.enabled : cfg.enabled;
  if (!enabled) { console.warn('[privacy-kit] admin UI no habilitada (adminUi.enabled=false).'); return null; }
  const port = opts.port || cfg.port || 8787;
  const token = opts.token || cfg.token || '';

  const send = (res, code, obj) => { res.writeHead(code, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(obj)); };
  const authOk = (req) => !token || (req.headers.authorization || '') === 'Bearer ' + token;

  const server = http.createServer(async (req, res) => {
    const u = new URL(req.url, 'http://localhost');
    // UI (sin datos sensibles): libre
    if (req.method === 'GET' && (u.pathname === '/' || u.pathname === '/index.html')) {
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' }); return res.end(html());
    }
    // API: requiere token
    if (u.pathname.startsWith('/api/')) {
      if (!authOk(req)) return send(res, 401, { error: 'no autorizado' });
      try {
        if (req.method === 'GET' && u.pathname === '/api/health') return send(res, 200, { ok: true });
        if (req.method === 'GET' && u.pathname === '/api/ropa') return send(res, 200, { ropa: pk.exportRopa() });
        if (req.method === 'GET' && u.pathname === '/api/resolve') {
          const results = pk.resolve(u.searchParams.get('q') || '');
          return send(res, 200, { supported: results !== null, results: results || [] });
        }
        if (req.method === 'GET' && u.pathname === '/api/subject') {
          const id = u.searchParams.get('id') || '';
          return send(res, 200, pk.subjectReport(id));
        }
        if (req.method === 'POST' && u.pathname === '/api/subject/forget') {
          let body = ''; for await (const c of req) body += c;
          const id = (JSON.parse(body || '{}').id) || '';
          return send(res, 200, pk.forget(id));
        }
        return send(res, 404, { error: 'no encontrado' });
      } catch (e) { return send(res, 500, { error: String(e && e.message || e) }); }
    }
    res.writeHead(404); res.end('not found');
  });
  server.listen(port, () => console.log(`[privacy-kit] admin UI en http://localhost:${port}`));
  return server;
}

module.exports = { serveAdmin };
