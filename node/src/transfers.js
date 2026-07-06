'use strict';
// Registro de transferencias a terceros (LLMs, pasarelas, APIs externas).
// Enviar el mensaje de un cliente a Anthropic/OpenAI ES una comunicación a un tercero.
class TransferRegistry {
  constructor(store, config) { this.store = store; this.config = config; }

  log(subjectId, destino, finalidad, categorias = []) {
    const tp = this.config.thirdParty(destino);
    this.store.put('privacy_transfers', {
      ts: new Date().toISOString(),
      subjectId,
      destino,
      pais: tp?.pais || '?',
      baseLegal: tp?.base || '?',
      finalidad,
      categorias,
      terceroDeclarado: !!tp, // false => transferencia NO declarada en config
    });
  }
}
module.exports = { TransferRegistry };
