'use strict';
// Ejemplo SIN LLM ni chat: un formulario web / CRM que capta datos personales.
// No se usa `redaction` (no hay LLM). El kit se usa para base de licitud
// (consentimiento), retención con borrado automático, auditoría y derechos ARCOP.
// Aplica a formularios, APIs de registro, CRMs, RRHH, etc.
const { PrivacyKit } = require('../src');

const pk = PrivacyKit.fromConfig('privacy.config.json');

function registrarFuentes(db) {
  pk.rights.registerSource('contactos', {
    fetch: (sid) => db.find('contactos', { subjectId: sid }),
    del: (sid) => db.delete('contactos', { subjectId: sid }),
    rectify: (sid, patch) => db.update('contactos', { subjectId: sid }, patch),
  });
}

// Alta de un contacto desde un formulario web (sin IA).
function recibirFormulario(db, subjectId, datos, aceptaMarketing) {
  // El marketing requiere consentimiento EXPLÍCITO (checkbox).
  pk.consent.capture(subjectId, 'marketing', 'webform', pk.notice.version(), aceptaMarketing);

  // Guardar con expiración según la retención de 'contacto'.
  db.put('contactos', {
    subjectId,
    ...datos,
    expiresAt: pk.retention.expiresAt('contacto'),
  });

  // Auditoría (nunca PII en claro en el detalle).
  pk.audit.record(subjectId, 'alta_formulario', 'webform', 'soporte', { marketing: aceptaMarketing });
}

// Cron diario: borra los contactos cuya retención venció.
function barridoRetencion(db) {
  return pk.retention.sweep(['contactos']);
}

// Endpoint ARCOP: /privacidad/{acceso|borrado|rectificacion}
function clienteEjerceDerecho(subjectId, accion, patch = null) {
  if (accion === 'acceso') return pk.rights.access(subjectId);
  if (accion === 'borrado') return pk.rights.erase(subjectId);
  if (accion === 'rectificacion') return pk.rights.rectify(subjectId, patch || {});
  throw new Error('acción ARCOP no soportada');
}

module.exports = { registrarFuentes, recibirFormulario, barridoRetencion, clienteEjerceDerecho };
