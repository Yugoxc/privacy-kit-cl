'use strict';
// Derechos ARCOP+ (Ley 21.719). Se conectan a endpoints HTTP o intents del bot.
// Registrar las colecciones con PII vía registerSource().
class RightsManager {
  constructor(store, config, audit) {
    this.store = store; this.config = config; this.audit = audit;
    this._sources = {}; // name -> { fetch, del, rectify }
  }

  // del/rectify opcionales. (se usa `del` porque `delete` es palabra reservada)
  registerSource(name, { fetch, del = null, rectify = null }) {
    this._sources[name] = { fetch, del, rectify };
  }

  access(subjectId) {
    this.audit.record(subjectId, 'acceso_arcop', 'rights');
    const out = {};
    for (const [name, s] of Object.entries(this._sources)) out[name] = s.fetch(subjectId);
    return out;
  }

  portability(subjectId) { return JSON.stringify(this.access(subjectId), null, 2); }

  rectify(subjectId, patch) {
    let n = 0;
    for (const s of Object.values(this._sources)) if (s.rectify) n += s.rectify(subjectId, patch);
    this.audit.record(subjectId, 'rectificacion_arcop', 'rights', null, { campos: Object.keys(patch) });
    return n;
  }

  erase(subjectId) {
    let n = 0;
    for (const s of Object.values(this._sources)) if (s.del) n += s.del(subjectId);
    this.audit.record(subjectId, 'supresion_arcop', 'rights', null, { registros: n });
    return n;
  }

  oppose(subjectId, finalidad) {
    this.store.put('privacy_opposition', { subjectId, finalidad });
    this.audit.record(subjectId, 'oposicion_arcop', 'rights', finalidad);
  }
}
module.exports = { RightsManager };
