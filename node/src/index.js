'use strict';
// privacy-kit-cl (Node) — capa de cumplimiento Ley 21.719, acoplable y reutilizable.
const { PrivacyConfig } = require('./config');
const { Redactor } = require('./redaction');
const { ConsentManager } = require('./consent');
const { RightsManager } = require('./rights');
const { AuditLog } = require('./audit');
const { RetentionManager } = require('./retention');
const { TransferRegistry } = require('./transfers');
const { NoticeBuilder } = require('./notice');
const { PrivacyStore, InMemoryStore } = require('./store/base');
const { buildRopa } = require('./ropa');

class PrivacyKit {
  constructor(config, store) {
    this.config = config;
    this.store = store || new InMemoryStore();
    this.audit = new AuditLog(this.store);
    this.redaction = new Redactor(config);
    this.consent = new ConsentManager(this.store, config, this.audit);
    this.rights = new RightsManager(this.store, config, this.audit);
    this.retention = new RetentionManager(this.store, config);
    this.transfers = new TransferRegistry(this.store, config);
    this.notice = new NoticeBuilder(config);
  }

  static fromConfig(path, store) { return new PrivacyKit(PrivacyConfig.load(path), store); }
  static fromObject(obj, store) { return new PrivacyKit(PrivacyConfig.fromObject(obj), store); }

  exportRopa() { return buildRopa(this.config); }

  /** Reporte agregado de TODO lo que el kit tiene de un titular (para atender "acceso"). */
  subjectReport(subjectId) {
    return {
      subject_id: subjectId,
      consents: this.store.find('privacy_consent', { subjectId }),
      transfers: this.store.find('privacy_transfers', { subjectId }),
      opposition: this.store.find('privacy_opposition', { subjectId }),
      audit: this.store.readLog({ subjectId }),
      data: this.rights.access(subjectId), // datos en las fuentes registradas
    };
  }

  /**
   * Derecho al olvido: borra TODOS los datos personales asociados a un titular
   * (fuentes registradas + colecciones internas del kit). NO borra la bitácora de
   * auditoría (se conserva como evidencia) y registra la propia supresión.
   */
  forget(subjectId) {
    const counts = {
      fuentes: this.rights.erase(subjectId), // colecciones de negocio registradas
      consentimientos: this.store.delete('privacy_consent', { subjectId }),
      transferencias: this.store.delete('privacy_transfers', { subjectId }),
      oposiciones: this.store.delete('privacy_opposition', { subjectId }),
    };
    this.audit.record(subjectId, 'olvido_total', 'admin', null, counts);
    return counts;
  }

  /** Levanta el panel de administración (opcional). Requiere admin_ui.enabled en config. */
  serveAdmin(opts = {}) {
    const { serveAdmin } = require('./admin');
    return serveAdmin(this, opts);
  }
}

module.exports = { PrivacyKit, PrivacyConfig, PrivacyStore, InMemoryStore };
