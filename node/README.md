# privacy-kit-cl · Node.js

Implementación **Node.js** de `privacy-kit-cl` — misma API y mismos componentes que la versión Python, para cubrir proyectos que corren en Node. Multi-canal: sirve para **cualquier mensajería** (WhatsApp, SMS, Telegram, web chat, email).

## Instalar
```bash
# dentro de tu proyecto Node (sin dependencias externas)
cp -r node/src ./privacy-kit   # o usar como paquete local
```

## Uso
```js
const { PrivacyKit } = require('./privacy-kit');
const pk = PrivacyKit.fromConfig('privacy.config.json'); // o .fromObject({...})

// 1) Antes de mandar texto de un cliente a un LLM (cualquier canal):
const red = pk.redaction.redact(userMessage, subjectId);
pk.transfers.log(subjectId, 'anthropic', 'asistencia_venta', Object.keys(red.found));

// 2) Enviar SOLO red.text al LLM; luego rehidratar la respuesta:
const respuesta = pk.redaction.rehydrate(await llm(red.text), red.tokenMap);
```

Ver [`examples/messaging_integration.js`](examples/messaging_integration.js) para un handler de mensajería multi-canal, y [`examples/smoke_test.js`](examples/smoke_test.js) (`npm test`).

## Componentes
`redaction` · `consent` · `rights` (ARCOP+) · `transfers` · `audit` · `retention` · `notice` · `store` (interfaz de 6 métodos, adaptable a Mongo/Postgres/etc.).

Config declarativa en `src/config.js` (`DEFAULT_CONFIG`). La guía de integración por IA está en la raíz: [`../AGENTS.md`](../AGENTS.md).
