'use strict';
// Prueba de humo (Node): valida import y flujos básicos. `npm test`.
const { PrivacyKit } = require('../src');

const pk = PrivacyKit.fromConfig('no-existe.json'); // usa DEFAULT_CONFIG

// Redacción antes del LLM (datos ficticios)
const msg = 'Hola, soy Juan, mi RUT es 11.111.111-1 y mi fono +56 9 1234 5678';
const red = pk.redaction.redact(msg, 'cliente1');
if (red.text.includes('11.111.111-1')) throw new Error('el RUT no fue redactado');
if (red.text.includes('1234')) throw new Error('el teléfono no fue redactado');
console.log('texto seguro para el LLM:', red.text);
console.log('PII detectada:', red.found);

// Rehidratar la respuesta del LLM
const primerTok = Object.keys(red.tokenMap)[0];
console.log('respuesta rehidratada:', pk.redaction.rehydrate('Listo ' + primerTok, red.tokenMap));

// Base de licitud + auditoría + transferencia (canal SMS, no WhatsApp)
pk.consent.capture('cliente1', 'asistencia_venta', 'sms', pk.notice.version());
pk.audit.record('cliente1', 'procesar_mensaje', 'demo', 'asistencia_venta');
pk.transfers.log('cliente1', 'anthropic', 'asistencia_venta', Object.keys(red.found));

// ROPA
console.log('\n--- ROPA generado ---');
console.log(pk.exportRopa().slice(0, 300), '...');
console.log('\nOK ✔ smoke test (node) pasó');
