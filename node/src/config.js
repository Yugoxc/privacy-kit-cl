'use strict';
// Configuración declarativa del cumplimiento. Toda la política vive aquí, no en código.
const fs = require('fs');

const DEFAULT_CONFIG = {
  responsable: { nombre: 'NOMBRE EMPRESA', rut: 'XX.XXX.XXX-X', contactoPrivacidad: 'privacidad@empresa.cl' },
  // Categorías de datos personales que trata este sistema.
  dataCategories: {
    identificacion: ['rut', 'nombre'],
    contacto: ['telefono', 'email', 'direccion'],
    ubicacion: ['lat', 'lng', 'comuna'],
    transaccional: ['historial_compra', 'monto', 'deuda'],
    laboral: ['cargo', 'cv', 'pretension_renta'],
    sensible: [],
  },
  // Finalidades y su base de licitud. Son EJEMPLOS multi-rubro: cambia/agrega las tuyas.
  // Bases: consentimiento | contrato | interes_legitimo | ley.
  purposes: {
    asistencia_venta: { legalBasis: 'interes_legitimo' },   // bot/agente de ventas
    soporte: { legalBasis: 'interes_legitimo' },             // atención al cliente / post-venta
    agendamiento: { legalBasis: 'contrato' },                // reserva de horas / citas
    despacho: { legalBasis: 'contrato' },                    // entrega de pedidos
    cobranza: { legalBasis: 'contrato' },                    // gestión de pagos / deuda
    reclutamiento: { legalBasis: 'consentimiento' },         // postulantes / CVs
    verificacion_identidad: { legalBasis: 'ley' },           // KYC / obligación legal
    notificaciones: { legalBasis: 'interes_legitimo' },      // avisos transaccionales
    marketing: { legalBasis: 'consentimiento' },             // comunicaciones comerciales
  },
  // Plazos de retención por categoría (días). 0 = no almacenar.
  retentionDays: { identificacion: 730, contacto: 730, ubicacion: 30, transaccional: 1825, laboral: 365, sensible: 0 },
  // Terceros a los que se transfieren datos.
  thirdParties: {
    anthropic: { pais: 'US', rol: 'encargado', base: 'interes_legitimo' },
    openai: { pais: 'US', rol: 'encargado', base: 'interes_legitimo' },
    pasarela_pago: { pais: 'CL', rol: 'encargado', base: 'contrato' },
  },
  // Panel de administración opcional (módulo admin). Se levanta solo si enabled=true.
  adminUi: { enabled: false, port: 8787, token: '' },
  // Patrones PII para la capa de redacción (strings de RegExp).
  piiPatterns: {
    rut: '\\b\\d{1,2}\\.?\\d{3}\\.?\\d{3}-[\\dkK]\\b',
    email: '\\b[\\w.+-]+@[\\w-]+\\.[\\w.-]+\\b',
    telefono: '(?:\\+?56)?\\s?9\\s?\\d{4}\\s?\\d{4}\\b',
    tarjeta: '\\b(?:\\d[ -]?){13,19}\\b',
  },
};

class PrivacyConfig {
  constructor(raw) { this.raw = raw || { ...DEFAULT_CONFIG }; }

  static load(path) {
    try {
      if (!path || !fs.existsSync(path)) return new PrivacyConfig();
      const data = JSON.parse(fs.readFileSync(path, 'utf-8'));
      return new PrivacyConfig({ ...DEFAULT_CONFIG, ...data });
    } catch { return new PrivacyConfig(); }
  }

  static fromObject(obj) { return new PrivacyConfig({ ...DEFAULT_CONFIG, ...(obj || {}) }); }

  legalBasis(purpose) { return this.raw.purposes?.[purpose]?.legalBasis; }
  retention(category) { return Number(this.raw.retentionDays?.[category] || 0); }
  thirdParty(name) { return this.raw.thirdParties?.[name]; }
  get piiPatterns() { return this.raw.piiPatterns || {}; }
}

module.exports = { PrivacyConfig, DEFAULT_CONFIG };
