"""Auditoría — responsabilidad proactiva (art. de responsabilidad de la 21.719).

Bitácora append-only de cada acceso/tratamiento de dato personal. La evidencia es
lo que la Agencia (APDP) exige: "demuestra que cumples", no basta con prometerlo.
"""
from __future__ import annotations
from datetime import datetime, timezone

from .store.base import PrivacyStore


class AuditLog:
    def __init__(self, store: PrivacyStore):
        self.store = store

    def record(self, subject_id: str, accion: str, sistema: str,
               finalidad: str | None = None, detalle: dict | None = None) -> None:
        """Registra un evento de tratamiento. NUNCA incluir PII en claro en `detalle`."""
        self.store.append_log({
            "ts": datetime.now(timezone.utc).isoformat(),
            "subject_id": subject_id,     # idealmente hash del RUT, no el RUT
            "accion": accion,             # ej: "procesar_mensaje", "acceso_arcop", "borrado"
            "sistema": sistema,
            "finalidad": finalidad,
            "detalle": detalle or {},
        })
