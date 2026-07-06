'use strict';
// Minimización: detecta y anonimiza PII ANTES de enviarla a un LLM o a un tercero.
// Es el control más importante en sistemas con IA. Pseudonimización reversible por
// sesión: el LLM razona sobre "el cliente" sin ver el dato real; se rehidrata luego.
const crypto = require('crypto');

class Redactor {
  constructor(config) {
    this.patterns = {};
    for (const [tipo, rx] of Object.entries(config.piiPatterns || {})) {
      this.patterns[tipo] = new RegExp(rx, 'g');
    }
  }

  _token(tipo, valor, salt) {
    const h = crypto.createHash('sha256').update(`${salt}:${valor}`).digest('hex').slice(0, 8);
    return `[${tipo.toUpperCase()}_${h}]`;
  }

  /**
   * Reemplaza PII por tokens estables. Enviar SOLO `result.text` al LLM.
   * Guardar `result.tokenMap` en memoria de sesión protegida (nunca en logs ni al tercero).
   * @returns {{text:string, tokenMap:Object, found:Object}}
   */
  redact(text, subjectId = 'anon') {
    if (!text) return { text: '', tokenMap: {}, found: {} };
    const tokenMap = {};
    const found = {};
    let out = text;
    for (const [tipo, rx] of Object.entries(this.patterns)) {
      out = out.replace(rx, (m) => {
        const tok = this._token(tipo, m, subjectId);
        tokenMap[tok] = m;
        found[tipo] = (found[tipo] || 0) + 1;
        return tok;
      });
    }
    return { text: out, tokenMap, found };
  }

  /** Reemplaza los tokens por sus valores reales (uso interno controlado). */
  rehydrate(text, tokenMap) {
    for (const [tok, val] of Object.entries(tokenMap)) {
      text = text.split(tok).join(val);
    }
    return text;
  }
}

module.exports = { Redactor };
