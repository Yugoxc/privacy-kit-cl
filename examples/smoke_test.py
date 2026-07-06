"""Prueba de humo: valida que el kit importa y los flujos básicos corren."""
from privacy_kit import PrivacyKit


def main():
    pk = PrivacyKit.from_config("no-existe.yaml")  # usa DEFAULT_CONFIG

    # Redacción antes del LLM (datos ficticios de ejemplo)
    msg = "Hola, soy Juan, mi RUT es 11.111.111-1 y mi fono +56 9 1234 5678"
    red = pk.redaction.redact(msg, subject_id="cliente1")
    assert "11.111.111-1" not in red.text, "el RUT no fue redactado"
    assert "1234" not in red.text, "el teléfono no fue redactado"
    print("texto seguro para el LLM:", red.text)
    print("PII detectada:", red.found)

    # Rehidratar la respuesta del LLM
    resp = pk.redaction.rehydrate("Listo " + list(red.token_map)[0], red.token_map)
    print("respuesta rehidratada:", resp)

    # Base de licitud + auditoría + transferencia
    pk.consent.capture("cliente1", "asistencia_venta", "whatsapp", pk.notice.version())
    pk.audit.record("cliente1", "procesar_mensaje", "demo", "asistencia_venta")
    pk.transfers.log("cliente1", "anthropic", "asistencia_venta", list(red.found))

    # ROPA
    print("\n--- ROPA generado ---")
    print(pk.export_ropa()[:300], "...")
    print("\nOK ✔ smoke test pasó")


if __name__ == "__main__":
    main()
