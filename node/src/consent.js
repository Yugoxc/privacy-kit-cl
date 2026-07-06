'use strict';
// Consentimiento / base de licitud, con evidencia verificable.
class ConsentManager {
  constructor(store, config, audit) { this.store = store; this.config = config; this.audit = audit; }

  capture(subjectId, finalidad, canal, avisoVersion, otorgado = true) {
    const base = this.config.legalBasis(finalidad);
    this.store.put('privacy_consent', {
      ts: new Date().toISOString(), subjectId, finalidad, baseLegal: base,
      canal, avisoVersion, otorgado,
    });
    this.audit.record(subjectId, 'consentimiento', canal, finalidad, { otorgado, base });
  }

  hasValidBasis(subjectId, finalidad) {
    const base = this.config.legalBasis(finalidad);
    if (['contrato', 'interes_legitimo', 'ley'].includes(base)) return true;
    return this.store.find('privacy_consent', { subjectId, finalidad }).some((r) => r.otorgado);
  }
}
module.exports = { ConsentManager };
