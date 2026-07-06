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
}

module.exports = { PrivacyKit, PrivacyConfig, PrivacyStore, InMemoryStore };
