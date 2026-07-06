'use strict';
// Ejemplo: acoplar privacy-kit a un asistente/bot de MENSAJERÍA en general
// (WhatsApp, SMS, Telegram, web chat, email…). El canal es solo un parámetro.
// Este es el patrón que una IA replica al integrar el kit en cualquier sistema Node.
const { PrivacyKit } = require('../src');

const pk = PrivacyKit.fromConfig('privacy.config.json');

// Paso 3.4 — conectar las colecciones con PII para los derechos ARCOP.
function registrarFuentes(db) {
  pk.rights.registerSource('conversaciones', {
    fetch: (id) => db.find('conversaciones', { subjectId: id }),
    del: (id) => db.delete('conversaciones', { subjectId: id }),
    rectify: (id, patch) => db.update('conversaciones', { subjectId: id }, patch),
  });
}

// Handler genérico de mensaje entrante, sirve para cualquier canal.
async function manejarMensaje({ subjectId, texto, canal, llamarLLM }) {
  // 3.2 aviso + base de licitud (una vez)
  if (!pk.consent.hasValidBasis(subjectId, 'asistencia_venta')) {
    pk.notice.render(canal); // entregar el aviso por el canal correspondiente
    pk.consent.capture(subjectId, 'asistencia_venta', canal, pk.notice.version());
  }

  // 3.3 auditoría del tratamiento
  pk.audit.record(subjectId, 'procesar_mensaje', `bot:${canal}`, 'asistencia_venta');

  // 3.1 minimización ANTES del LLM  +  3.4 registro de transferencia
  const red = pk.redaction.redact(texto, subjectId);
  pk.transfers.log(subjectId, 'anthropic', 'asistencia_venta', Object.keys(red.found));

  const respuestaLLM = await llamarLLM(red.text);         // el LLM nunca ve PII real
  return pk.redaction.rehydrate(respuestaLLM, red.tokenMap); // rehidratar para el cliente
}

// Intent ARCOP: "quiero mis datos" / "bórrenme"
function clientePideSusDatos(subjectId) {
  return pk.rights.portability(subjectId); // o pk.rights.erase(subjectId)
}

module.exports = { registrarFuentes, manejarMensaje, clientePideSusDatos };
