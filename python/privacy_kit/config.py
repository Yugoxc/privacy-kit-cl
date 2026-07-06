"""Configuración declarativa del cumplimiento. Toda la política vive aquí, no en código."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "responsable": {
        "nombre": "NOMBRE EMPRESA",
        "rut": "XX.XXX.XXX-X",
        "contacto_privacidad": "privacidad@empresa.cl",
    },
    # Categorías de datos personales que trata este sistema.
    "data_categories": {
        "identificacion": ["rut", "nombre"],
        "contacto": ["telefono", "email", "direccion"],
        "ubicacion": ["lat", "lng", "comuna"],
        "transaccional": ["historial_compra", "monto", "deuda"],
        "laboral": ["cargo", "cv", "pretension_renta"],
        "sensible": [],  # salud, ideología, etc. — base legal reforzada; evitar si no es imprescindible
    },
    # Finalidades declaradas y su base de licitud. Son EJEMPLOS multi-rubro:
    # cambia/agrega las tuyas. Bases: consentimiento | contrato | interes_legitimo | ley.
    "purposes": {
        "asistencia_venta": {"legal_basis": "interes_legitimo"},   # bot/agente de ventas
        "soporte": {"legal_basis": "interes_legitimo"},            # atención al cliente / post-venta
        "agendamiento": {"legal_basis": "contrato"},               # reserva de horas / citas
        "despacho": {"legal_basis": "contrato"},                   # entrega de pedidos
        "cobranza": {"legal_basis": "contrato"},                   # gestión de pagos / deuda
        "reclutamiento": {"legal_basis": "consentimiento"},        # postulantes / CVs
        "verificacion_identidad": {"legal_basis": "ley"},          # KYC / obligación legal
        "notificaciones": {"legal_basis": "interes_legitimo"},     # avisos transaccionales
        "marketing": {"legal_basis": "consentimiento"},            # comunicaciones comerciales
    },
    # Plazos de retención por categoría (días). 0 = no almacenar.
    "retention_days": {
        "identificacion": 730,
        "contacto": 730,
        "ubicacion": 30,
        "transaccional": 1825,
        "laboral": 365,
        "sensible": 0,
    },
    # Terceros a los que se transfieren datos (clave para el registro de transferencias).
    "third_parties": {
        "anthropic": {"pais": "US", "rol": "encargado", "base": "interes_legitimo"},
        "openai": {"pais": "US", "rol": "encargado", "base": "interes_legitimo"},
        "pasarela_pago": {"pais": "CL", "rol": "encargado", "base": "contrato"},
    },
    # Panel de administración opcional (módulo admin). Se levanta solo si enabled=True.
    "admin_ui": {"enabled": False, "port": 8787, "token": ""},
    # Patrones PII para la capa de redacción (se pueden extender).
    "pii_patterns": {
        "rut": r"\b\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]\b",
        "email": r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b",
        "telefono": r"(?:\+?56)?\s?9\s?\d{4}\s?\d{4}\b",
        "tarjeta": r"\b(?:\d[ -]?){13,19}\b",
    },
}


@dataclass
class PrivacyConfig:
    raw: dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_CONFIG))

    @classmethod
    def load(cls, path: str) -> "PrivacyConfig":
        """Carga YAML/JSON; si no existe, usa DEFAULT_CONFIG (útil para prototipo)."""
        try:
            import os, json
            if not os.path.exists(path):
                return cls()
            text = open(path, encoding="utf-8").read()
            try:
                import yaml  # opcional
                data = yaml.safe_load(text)
            except Exception:
                data = json.loads(text)
            return cls(raw={**DEFAULT_CONFIG, **(data or {})})
        except Exception:
            return cls()

    # Accesores convenientes
    def legal_basis(self, purpose: str) -> str | None:
        return self.raw.get("purposes", {}).get(purpose, {}).get("legal_basis")

    def retention(self, category: str) -> int:
        return int(self.raw.get("retention_days", {}).get(category, 0))

    def third_party(self, name: str) -> dict | None:
        return self.raw.get("third_parties", {}).get(name)

    @property
    def pii_patterns(self) -> dict[str, str]:
        return self.raw.get("pii_patterns", {})
