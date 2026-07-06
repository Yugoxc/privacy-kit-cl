'use strict';
// Auditoría — responsabilidad proactiva. Bitácora append-only de cada tratamiento.
class AuditLog {
  constructor(store) { this.store = store; }

  // NUNCA incluir PII en claro en `detalle`. `subjectId` debería ser un hash del RUT.
  record(subjectId, accion, sistema, finalidad = null, detalle = null) {
    this.store.appendLog({
      ts: new Date().toISOString(),
      subjectId,
      accion,        // "procesar_mensaje", "acceso_arcop", "borrado"...
      sistema,
      finalidad,
      detalle: detalle || {},
    });
  }
}
module.exports = { AuditLog };
