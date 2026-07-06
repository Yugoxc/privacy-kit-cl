'use strict';
// Retención y borrado automático (principio de plazo + derecho al olvido).
class RetentionManager {
  constructor(store, config) { this.store = store; this.config = config; }

  expiresAt(category, createdIso = null) {
    const days = this.config.retention(category);
    if (days <= 0) return null;
    const base = createdIso ? new Date(createdIso) : new Date();
    return new Date(base.getTime() + days * 86400000).toISOString();
  }

  // Borra registros vencidos. Agendar en cron/worker (ej. diario).
  sweep(collections) {
    const now = new Date().toISOString();
    let total = 0;
    for (const col of collections)
      for (const row of this.store.expired(col, now)) total += this.store.delete(col, { id: row.id });
    return total;
  }
}
module.exports = { RetentionManager };
