# Checklist de cumplimiento — Ley 21.719 (para cada sistema)

Marca cada ítem al integrar el kit. Vigencia plena: **1-dic-2026**.

## Base de licitud y transparencia
- [ ] Cada finalidad tiene base legal declarada (`purposes` en config).
- [ ] Aviso de privacidad entregado en el primer contacto (`notice.render`).
- [ ] Consentimiento registrado cuando la base es "consentimiento" (marketing, etc.).

## Minimización y seguridad (crítico con IA)
- [ ] Toda llamada a LLM/tercero pasa por `redaction.redact` (sin PII en claro).
- [ ] PII cifrada en reposo; `subject_id` en logs es hash, no el RUT.
- [ ] No se registra PII en claro en logs de aplicación.

## Transferencias a terceros
- [ ] Todos los terceros (OpenAI, Anthropic, pasarela) están en `third_parties`.
- [ ] Cada transferencia se registra (`transfers.log`).
- [ ] Existe contrato de encargo (DPA) con cada encargado. (legal)

## Derechos del titular (ARCOP+)
- [ ] Canal para ejercer derechos publicado (correo/bot).
- [ ] Acceso y portabilidad implementados (`rights.access/portability`).
- [ ] Rectificación y supresión implementadas (`rights.rectify/erase`).
- [ ] Oposición implementada (`rights.oppose`).
- [ ] Plazo de respuesta ≤ el legal.

## Retención y responsabilidad
- [ ] Plazos de retención definidos por categoría (`retention_days`).
- [ ] Barrido de borrado agendado (`retention.sweep`).
- [ ] Bitácora de auditoría activa e íntegra (`audit`).
- [ ] ROPA generado y versionado (`export_ropa`).

> ⚠️ No es asesoría legal. Validar con abogado/DPO antes de producción.
