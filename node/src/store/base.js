'use strict';
// Interfaz de almacenamiento. Implementa esto sobre tu BD (Mongo/Postgres/etc.).
// Solo 6 métodos: el kit no conoce tu infraestructura, solo estos contratos.

class PrivacyStore {
  put(collection, record) { throw new Error('PrivacyStore.put no implementado'); }
  find(collection, query) { throw new Error('PrivacyStore.find no implementado'); }
  delete(collection, query) { throw new Error('PrivacyStore.delete no implementado'); }
  update(collection, query, patch) { throw new Error('PrivacyStore.update no implementado'); }
  appendLog(record) { throw new Error('PrivacyStore.appendLog no implementado'); } // bitácora append-only
  expired(collection, beforeIso) { throw new Error('PrivacyStore.expired no implementado'); }
}

// Implementación de prueba/prototipo. NO usar en producción.
class InMemoryStore extends PrivacyStore {
  constructor() { super(); this._db = {}; this._log = []; }
  _match(r, q) { return Object.entries(q).every(([k, v]) => r[k] === v); }

  put(c, r) { (this._db[c] = this._db[c] || []).push(r); return r.id || String(this._db[c].length); }
  find(c, q) { return (this._db[c] || []).filter((r) => this._match(r, q)); }
  delete(c, q) {
    const rows = this._db[c] || [];
    const keep = rows.filter((r) => !this._match(r, q));
    const n = rows.length - keep.length;
    this._db[c] = keep;
    return n;
  }
  update(c, q, p) { let n = 0; for (const r of this._db[c] || []) if (this._match(r, q)) { Object.assign(r, p); n++; } return n; }
  appendLog(r) { this._log.push(r); }
  expired(c, before) { return (this._db[c] || []).filter((r) => r.expiresAt && r.expiresAt < before); }
}

module.exports = { PrivacyStore, InMemoryStore };
