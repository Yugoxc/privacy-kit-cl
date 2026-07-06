"""Ejemplo SIN LLM ni chat: un formulario web / CRM que capta datos personales.

Aquí NO se usa `redaction` (no hay LLM). El kit se usa para lo demás:
base de licitud (consentimiento), retención con borrado automático, auditoría y
derechos ARCOP. Aplica a formularios, APIs de registro, CRMs, RRHH, etc.
"""
from privacy_kit import PrivacyKit

pk = PrivacyKit.from_config("privacy.config.yaml")


def registrar_fuentes(db):
    """Conectar la colección con PII para los derechos ARCOP."""
    pk.rights.register_source(
        "contactos",
        fetch=lambda sid: list(db.find("contactos", {"subject_id": sid})),
        delete=lambda sid: db.delete("contactos", {"subject_id": sid}),
        rectify=lambda sid, patch: db.update("contactos", {"subject_id": sid}, patch),
    )


def recibir_formulario(db, subject_id: str, datos: dict, acepta_marketing: bool):
    """Alta de un contacto desde un formulario web (sin IA)."""
    # Base de licitud: el marketing requiere consentimiento EXPLÍCITO (checkbox).
    pk.consent.capture(subject_id, "marketing", "webform", pk.notice.version(),
                       otorgado=acepta_marketing)

    # Guardar con fecha de expiración según la retención de 'contacto'.
    db.put("contactos", {
        "subject_id": subject_id,
        **datos,
        "expires_at": pk.retention.expires_at("contacto"),
    })

    # Auditoría (nunca PII en claro en el detalle).
    pk.audit.record(subject_id, "alta_formulario", "webform", "soporte",
                    {"marketing": acepta_marketing})


def barrido_retencion(db):
    """Cron diario: borra los contactos cuya retención venció."""
    return pk.retention.sweep(["contactos"])


def cliente_ejerce_derecho(subject_id: str, accion: str, patch: dict | None = None):
    """Endpoint ARCOP: /privacidad/{acceso|borrado|rectificacion}."""
    if accion == "acceso":
        return pk.rights.access(subject_id)          # o portability() para exportar
    if accion == "borrado":
        return pk.rights.erase(subject_id)
    if accion == "rectificacion":
        return pk.rights.rectify(subject_id, patch or {})
    raise ValueError("acción ARCOP no soportada")
