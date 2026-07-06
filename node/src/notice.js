'use strict';
// Transparencia: genera y versiona el aviso de privacidad. `canal` es cualquier
// medio de mensajería (whatsapp, sms, telegram, webchat, email...).
const crypto = require('crypto');

class NoticeBuilder {
  constructor(config) { this.config = config; }

  render(canal = 'mensajeria') {
    const r = this.config.raw.responsable || {};
    const fines = Object.keys(this.config.raw.purposes || {}).join(', ');
    return `🔒 ${r.nombre || 'La empresa'} trata tus datos personales para: ${fines}. ` +
      `Puedes ejercer tus derechos de acceso, rectificación, supresión, oposición y ` +
      `portabilidad escribiendo a ${r.contactoPrivacidad || 'privacidad@empresa.cl'}. ` +
      `Al continuar, aceptas esta política (Ley 21.719).`;
  }

  version() { return 'v' + crypto.createHash('sha256').update(this.render()).digest('hex').slice(0, 6); }
}
module.exports = { NoticeBuilder };
