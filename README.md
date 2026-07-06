# privacy-kit-cl 🛡️

> Cumplimiento de la **Ley 21.719** (protección de datos, Chile) para sistemas con **IA/LLMs** — sin reescribir lo que ya funciona.

![Python](https://img.shields.io/badge/python-3.10+-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![status](https://img.shields.io/badge/status-alpha-orange)

<p align="center">
  <img src="docs/demo.gif" alt="La PII se enmascara antes de llegar al LLM y se rehidrata solo en la respuesta al cliente" width="760">
</p>

<p align="center"><i>La PII (RUT, teléfono) se enmascara <b>antes</b> de tocar el LLM, y se rehidrata solo en la respuesta al cliente.</i></p>

Módulo **independiente y reutilizable** para cumplir la **Ley 21.719** (Protección de Datos Personales de Chile) en cualquier sistema que trate datos personales — especialmente sistemas con **IA/LLMs** que interactúan con clientes por **cualquier canal de mensajería** (WhatsApp, SMS, Telegram, web chat, email…).

**Disponible en Python y Node.js**, con la misma API.

La idea: en vez de reimplementar el cumplimiento en cada proyecto, se **acopla** este kit como una capa transversal. Un desarrollador (o una IA) instala el paquete, lo configura con un archivo declarativo, y envuelve los puntos donde entra/sale/procesa un dato personal.

## Qué resuelve (mapeo a la ley)

| Componente | Artículo/principio 21.719 | Qué hace |
|---|---|---|
| `consent` | Base de licitud, consentimiento | Captura y registra consentimiento con evidencia (quién, cuándo, para qué). |
| `redaction` | Minimización, seguridad | Detecta y **anonimiza PII antes de mandarla a un LLM** o a terceros. |
| `rights` | Derechos ARCOP+ | Handlers de Acceso, Rectificación, Cancelación/supresión, Oposición y Portabilidad. |
| `retention` | Calidad, plazos | Políticas de retención y borrado automático (derecho al olvido). |
| `transfers` | Transferencia a terceros | Registro de a qué terceros (OpenAI, Anthropic, pasarelas…) se envían datos. |
| `audit` | Responsabilidad proactiva | Bitácora inmutable de cada acceso/tratamiento de dato personal. |
| `notice` | Transparencia | Genera el aviso de privacidad y su entrega en el primer contacto. |

## Cómo funciona

<p align="center"><img src="docs/architecture.svg" width="840" alt="Flujo de cumplimiento privacy-kit"></p>

## Principios de diseño

1. **Independiente:** no depende de tu framework. Core sin dependencias externas + una interfaz de almacenamiento (`store`) que adaptas a Mongo, ClickHouse, Postgres, etc.
2. **Declarativo:** todo el comportamiento sale de un archivo de configuración (categorías de datos, finalidades, plazos, terceros). Cambiar la política = cambiar config, no código.
3. **Acoplable por envoltura:** envuelves las llamadas sensibles (`redact(...)`, `transfers.log(...)`, `audit.record(...)`) sin reescribir tu lógica.
4. **AI-friendly:** el archivo [`AGENTS.md`](AGENTS.md) le dice a una IA exactamente cómo integrar el kit en un sistema nuevo o existente.

## Implementaciones

El repo contiene **dos paquetes independientes**, uno por lenguaje, con la misma API. Instala solo el que necesites.

| Lenguaje | Código | Manifiesto | Prueba |
|---|---|---|---|
| **Python** | [`python/privacy_kit/`](python/privacy_kit/) | `pyproject.toml` | `python python/examples/smoke_test.py` |
| **Node.js** | [`node/src/`](node/src/) | `package.json` | `npm test` |

Ambos exponen los mismos componentes (`redaction`, `consent`, `rights`, `transfers`, `audit`, `retention`, `notice`, `store`) y son **agnósticos del canal** de mensajería.

## Instalación

**Python** (pip):
```bash
pip install "git+https://github.com/Yugoxc/privacy-kit-cl.git"
# en local, desde el repo:  pip install .
```

**Node.js** (npm):
```bash
npm install github:Yugoxc/privacy-kit-cl
# en local, desde el repo:  npm install
```

## Uso

**Python**
```python
from privacy_kit import PrivacyKit

pk = PrivacyKit.from_config("privacy.config.yaml")   # sin archivo, usa DEFAULT_CONFIG

# 1) Antes de mandar texto de un cliente a un LLM (cualquier canal):
red = pk.redaction.redact(user_message, subject_id=rut)   # -> RedactionResult(text, token_map, found)
pk.transfers.log(subject_id=rut, destino="anthropic", finalidad="asistencia_venta",
                 categorias=list(red.found.keys()))

# 2) Enviar SOLO red.text al LLM; luego rehidratar la respuesta al cliente:
respuesta = pk.redaction.rehydrate(llm(red.text), red.token_map)

# 3) Auditar el tratamiento:
pk.audit.record(subject_id=rut, accion="procesar_mensaje", sistema="bot:whatsapp")
```

**Node.js**
```js
const { PrivacyKit } = require("privacy-kit-cl");

const pk = PrivacyKit.fromConfig("privacy.config.json"); // o .fromObject({...})

const red = pk.redaction.redact(userMessage, subjectId); // -> { text, tokenMap, found }
pk.transfers.log(subjectId, "anthropic", "asistencia_venta", Object.keys(red.found));

const respuesta = pk.redaction.rehydrate(await llm(red.text), red.tokenMap);
```

Ejemplos completos multi-canal: [`python/examples/messaging_integration.py`](python/examples/messaging_integration.py) · [`node/examples/messaging_integration.js`](node/examples/messaging_integration.js).

## Estado

Scaffold base (esqueleto funcional con interfaces y stubs). Diseñado para crecer proyecto a proyecto. No es asesoría legal — validar con abogado antes de producción.
