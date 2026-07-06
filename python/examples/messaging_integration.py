"""Ejemplo: acoplar privacy-kit a un asistente/bot de MENSAJERÍA en general
(WhatsApp, SMS, Telegram, web chat, email…). El canal es solo un parámetro.

Este es el patrón que una IA replica al integrar el kit en cualquier sistema Python.
"""
from privacy_kit import PrivacyKit

pk = PrivacyKit.from_config("privacy.config.yaml")


def registrar_fuentes_de_datos(db):
    """Conectar las colecciones con PII para los derechos ARCOP."""
    pk.rights.register_source(
        "conversaciones",
        fetch=lambda sid: list(db.find("conversaciones", {"subject_id": sid})),
        delete=lambda sid: db.delete("conversaciones", {"subject_id": sid}),
        rectify=lambda sid, patch: db.update("conversaciones", {"subject_id": sid}, patch),
    )


def manejar_mensaje(subject_id: str, mensaje: str, canal: str, llamar_llm) -> str:
    """Handler genérico de mensaje entrante; sirve para cualquier canal."""
    # Aviso + base de licitud en el primer contacto
    if not pk.consent.has_valid_basis(subject_id, "asistencia_venta"):
        pk.notice.render(canal)  # entregar el aviso por el canal correspondiente
        pk.consent.capture(subject_id, "asistencia_venta", canal, pk.notice.version())

    # Auditoría del tratamiento
    pk.audit.record(subject_id, "procesar_mensaje", f"bot:{canal}", "asistencia_venta")

    # Minimización ANTES de mandar al LLM (lo más importante) + registro de transferencia
    red = pk.redaction.redact(mensaje, subject_id=subject_id)
    pk.transfers.log(subject_id, destino="anthropic", finalidad="asistencia_venta",
                     categorias=list(red.found.keys()))

    respuesta_llm = llamar_llm(red.text)          # el LLM NUNCA ve el RUT/teléfono real
    return pk.redaction.rehydrate(respuesta_llm, red.token_map)  # rehidratar para el cliente


def cliente_pide_sus_datos(subject_id: str) -> str:
    """Intent ARCOP: 'quiero mis datos' / 'bórrenme'."""
    return pk.rights.portability(subject_id)      # o pk.rights.erase(subject_id) para supresión
