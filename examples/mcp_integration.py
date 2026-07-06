"""Ejemplo: acoplar privacy-kit al bot de e-commerce (MCP) que habla con clientes.

Muestra los 5 puntos de control en un flujo real de WhatsApp. Este archivo es el
patrón que una IA replica al integrar el kit en un MCP u otro sistema.
"""
from privacy_kit import PrivacyKit

pk = PrivacyKit.from_config("privacy.config.yaml")


def registrar_fuentes_de_datos(mongo):
    """Paso 3.4 — conectar las colecciones con PII para los derechos ARCOP."""
    pk.rights.register_source(
        "carros",
        fetch=lambda rut: list(mongo.carros.find({"cliente.rut": rut})),
        delete=lambda rut: mongo.carros.delete_many({"cliente.rut": rut}).deleted_count,
        rectify=lambda rut, patch: mongo.carros.update_many(
            {"cliente.rut": rut}, {"$set": patch}).modified_count,
    )


def manejar_mensaje_cliente(rut: str, mensaje: str, llamar_llm) -> str:
    # 3.2 Aviso + base de licitud en el primer contacto
    if not pk.consent.has_valid_basis(rut, "asistencia_venta"):
        # 'asistencia_venta' es interés legítimo => no requiere consentimiento explícito,
        # pero igual entregamos el aviso una vez.
        aviso = pk.notice.render("whatsapp")
        pk.consent.capture(rut, "asistencia_venta", "whatsapp", pk.notice.version())

    # 3.3 Auditoría del tratamiento
    pk.audit.record(rut, "procesar_mensaje", "mcp_ecommerce", "asistencia_venta")

    # 3.1 Minimización ANTES de mandar al LLM (lo más importante)
    red = pk.redaction.redact(mensaje, subject_id=rut)
    pk.transfers.log(rut, destino="anthropic", finalidad="asistencia_venta",
                     categorias=list(red.found.keys()))

    respuesta_llm = llamar_llm(red.text)          # el LLM NUNCA ve el RUT/teléfono real
    return pk.redaction.rehydrate(respuesta_llm, red.token_map)  # rehidratar para el cliente


def cliente_pide_sus_datos(rut: str) -> str:
    """Intent ARCOP: 'quiero mis datos' / 'bórrenme'."""
    return pk.rights.portability(rut)            # o pk.rights.erase(rut) para supresión
