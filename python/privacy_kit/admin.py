"""Panel de administración OPCIONAL (Python). Levanta un mini-servidor HTTP (stdlib)
con API REST + UI embebida para gestionar los datos que registra el kit: consentimientos,
transferencias, auditoría, ROPA y el DERECHO AL OLVIDO (borrar todos los datos de un
titular). Superficie sensible: úsalo detrás de auth e interno.
"""
from __future__ import annotations
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

PAGE = r"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
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
   <h2>Buscar titular</h2>
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
async function buscar(){
  const id=$('#sid').value.trim();if(!id){toast('Ingresa un subject_id',false);return;}
  let d;try{d=await api('/api/subject?id='+encodeURIComponent(id));}catch(e){return;}
  $('#res').innerHTML=`
   <div class="card"><h2>Resumen — ${id}</h2>
     <div class="chips">
       <div class="chip"><b>${d.consents.length}</b><span>consentimientos</span></div>
       <div class="chip"><b>${d.transfers.length}</b><span>transferencias</span></div>
       <div class="chip"><b>${d.audit.length}</b><span>eventos auditados</span></div>
     </div>
   </div>
   <div class="card"><h2>Consentimientos</h2>${tbl(d.consents)}</div>
   <div class="card"><h2>Transferencias a terceros</h2>${tbl(d.transfers)}</div>
   <div class="card"><h2>Datos en las fuentes de negocio</h2><pre>${JSON.stringify(d.data,null,2)}</pre></div>
   <div class="card"><h2>Auditoría</h2>${tbl(d.audit)}</div>
   <div class="card danger-zone"><h2 style="color:#ff7b72">⚠️ Derecho al olvido</h2>
     <div class="muted">Elimina TODOS los datos personales de este titular (fuentes + consentimientos + transferencias). La auditoría se conserva como evidencia.</div>
     <div class="row" style="margin-top:10px"><button class="danger" onclick="olvidar('${id}')">🗑️ Eliminar todos los datos de ${id}</button></div>
   </div>`;
}
async function olvidar(id){
  if(!confirm('¿Eliminar TODOS los datos de '+id+'? Esta acción no se puede deshacer.'))return;
  let c;try{c=await api('/api/subject/forget',{method:'POST',body:JSON.stringify({id})});}catch(e){return;}
  toast('Datos eliminados → '+JSON.stringify(c));buscar();
}
async function loadRopa(){let d;try{d=await api('/api/ropa');}catch(e){return;}$('#res').innerHTML='<div class="card"><h2>ROPA — Registro de Actividades de Tratamiento</h2><pre>'+d.ropa.replace(/</g,'&lt;')+'</pre></div>';}
</script></body></html>"""


def serve_admin(pk, enabled: bool | None = None, port: int | None = None,
                token: str | None = None, block: bool = False):
    """Levanta el panel admin. Respeta config['admin_ui'] salvo overrides."""
    cfg = pk.config.raw.get("admin_ui", {})
    enabled = cfg.get("enabled", False) if enabled is None else enabled
    if not enabled:
        print("[privacy-kit] admin UI no habilitada (admin_ui.enabled=False).")
        return None
    port = port or cfg.get("port", 8787)
    tok = token if token is not None else cfg.get("token", "")

    class Handler(BaseHTTPRequestHandler):
        def _json(self, code, obj):
            self.send_response(code); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(json.dumps(obj, default=str).encode())

        def _auth_ok(self):
            return (not tok) or self.headers.get("Authorization", "") == "Bearer " + tok

        def log_message(self, *a):  # silenciar logs
            pass

        def do_GET(self):
            u = urlparse(self.path)
            if u.path in ("/", "/index.html"):
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
                self.wfile.write(PAGE.encode()); return
            if u.path.startswith("/api/"):
                if not self._auth_ok(): return self._json(401, {"error": "no autorizado"})
                if u.path == "/api/health": return self._json(200, {"ok": True})
                if u.path == "/api/ropa": return self._json(200, {"ropa": pk.export_ropa()})
                if u.path == "/api/subject":
                    sid = (parse_qs(u.query).get("id", [""])[0])
                    return self._json(200, pk.subject_report(sid))
                return self._json(404, {"error": "no encontrado"})
            self.send_response(404); self.end_headers()

        def do_POST(self):
            u = urlparse(self.path)
            if not self._auth_ok(): return self._json(401, {"error": "no autorizado"})
            if u.path == "/api/subject/forget":
                length = int(self.headers.get("Content-Length", 0) or 0)
                body = json.loads(self.rfile.read(length) or b"{}")
                return self._json(200, pk.forget(body.get("id", "")))
            return self._json(404, {"error": "no encontrado"})

    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"[privacy-kit] admin UI en http://localhost:{port}")
    if block:
        httpd.serve_forever()
    else:
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd
