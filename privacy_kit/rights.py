"""Derechos ARCOP+ del titular (Ley 21.719).

Acceso, Rectificación, Cancelación/supresión, Oposición y Portabilidad. Se exponen
como funciones que el sistema conecta a endpoints HTTP o a intents del bot.
El sistema debe registrar sus colecciones con PII vía `register_source`.
"""
from __future__ import annotations
from typing import Callable

from .config import PrivacyConfig
from .store.base import PrivacyStore
from .audit import AuditLog


class RightsManager:
    def __init__(self, store: PrivacyStore, config: PrivacyConfig, audit: AuditLog):
        self.store = store
        self.config = config
        self.audit = audit
        # fuentes de datos personales del sistema: nombre -> (buscar, borrar, rectificar)
        self._sources: dict[str, dict[str, Callable]] = {}

    def register_source(self, name: str, *, fetch: Callable[[str], list],
                        delete: Callable[[str], int] | None = None,
                        rectify: Callable[[str, dict], int] | None = None) -> None:
        self._sources[name] = {"fetch": fetch, "delete": delete, "rectify": rectify}

    # --- Acceso + Portabilidad ---
    def access(self, subject_id: str) -> dict[str, list]:
        self.audit.record(subject_id, "acceso_arcop", "rights")
        return {name: s["fetch"](subject_id) for name, s in self._sources.items()}

    def portability(self, subject_id: str) -> str:
        import json
        return json.dumps(self.access(subject_id), ensure_ascii=False, default=str, indent=2)

    # --- Rectificación ---
    def rectify(self, subject_id: str, patch: dict) -> int:
        n = 0
        for name, s in self._sources.items():
            if s.get("rectify"):
                n += s["rectify"](subject_id, patch)
        self.audit.record(subject_id, "rectificacion_arcop", "rights", detalle={"campos": list(patch)})
        return n

    # --- Cancelación / supresión (derecho al olvido) ---
    def erase(self, subject_id: str) -> int:
        n = 0
        for name, s in self._sources.items():
            if s.get("delete"):
                n += s["delete"](subject_id)
        self.audit.record(subject_id, "supresion_arcop", "rights", detalle={"registros": n})
        return n

    # --- Oposición ---
    def oppose(self, subject_id: str, finalidad: str) -> None:
        self.store.put("privacy_opposition", {"subject_id": subject_id, "finalidad": finalidad})
        self.audit.record(subject_id, "oposicion_arcop", "rights", finalidad)
