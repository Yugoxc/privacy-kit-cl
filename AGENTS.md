# AGENTS.md — Guía de integración para una IA

Este archivo le indica a un agente de IA **cómo acoplar `privacy-kit-cl` a un sistema** (nuevo o existente) para cumplir la Ley 21.719. Seguir los pasos en orden.

## Objetivo
Envolver todos los puntos donde el sistema **recibe, procesa, almacena o transfiere datos personales** con los componentes del kit, sin reescribir la lógica de negocio.

## Paso 0 — Detectar el terreno
1. Identifica el lenguaje/stack y el punto de entrada (API, bot, worker).
2. Localiza dónde entran datos personales: RUT, nombre, teléfono, email, dirección, ubicación, medios de pago, historial.
3. Localiza dónde SALEN a terceros: llamadas a LLMs (OpenAI/Anthropic), pasarelas de pago, APIs externas, logs.

## Paso 1 — Instalar y configurar
1. `pip install -e /ruta/privacy-kit-cl` (o copia `privacy_kit/` al proyecto).
2. Crea `privacy.config.yaml` en la raíz del proyecto a partir de `privacy_kit/config.py::DEFAULT_CONFIG`. Rellena:
   - `data_categories`: qué datos personales trata este sistema.
   - `purposes`: finalidades (ej. "asistencia_venta", "despacho").
   - `retention_days`: plazo por categoría.
   - `third_parties`: terceros a los que se envían datos (nombre, país, base legal).
   - `legal_basis`: base de licitud por finalidad (consentimiento | interés_legítimo | contrato).

## Paso 2 — Implementar el `Store`
Elige el adaptador de almacenamiento: implementa `privacy_kit/store/base.py::PrivacyStore` sobre la BD existente del sistema (Mongo, ClickHouse, Postgres). Solo 6 métodos. Si no hay BD, usa `InMemoryStore` para prototipar.

## Paso 3 — Envolver los 5 puntos de control (en este orden de prioridad)
1. **Minimización antes de LLM/terceros** — CRÍTICO: envuelve TODA llamada a un LLM/API externa con `pk.redaction.redact(texto, subject_id)` para quitar PII. Registra la transferencia con `pk.transfers.log(...)`.
2. **Aviso + base de licitud** — en el primer contacto con el titular, entrega el aviso (`pk.notice.render()`) y registra la base (`pk.consent.capture(...)` si aplica consentimiento).
3. **Auditoría** — en cada acceso a un dato personal, llama `pk.audit.record(...)`.
4. **Derechos ARCOP** — expón los handlers de `pk.rights` (acceso/rectificación/borrado/oposición/portabilidad) como endpoints o intents del bot.
5. **Retención** — agenda `pk.retention.sweep()` (cron/worker) para borrar datos vencidos.

## Paso 4 — Verificar
1. Corre `compliance/checklist_21719.md` y marca cada ítem.
2. Genera/actualiza `compliance/ropa.md` (Registro de Actividades de Tratamiento) con `pk.export_ropa()`.

## Reglas para la IA
- **No inventes** bases legales ni finalidades: si no están en el config, pregúntalas o márcalas `TODO`.
- **Nunca** loguees PII en claro; usa `pk.redaction.redact` también en logs.
- Prioriza el Paso 3.1 (redacción antes de LLM): es el mayor riesgo y el más fácil de omitir.
- Deja los puntos integrados marcados con el comentario `# [privacy-kit]` para trazabilidad.
