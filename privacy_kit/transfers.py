"""Registro de transferencias a terceros (LLMs, pasarelas, APIs externas).

La 21.719 exige saber a quién se ceden/comunican datos y con qué base. Mandar el
mensaje de un cliente a Anthropic/OpenAI ES una comunicación a un tercero.
"""
from __future__ import annotations
from datetime import datetime, timezone

from .config import PrivacyConfig
from .store.base import PrivacyStore


class TransferRegistry:
    def __init__(self, store: PrivacyStore, config: PrivacyConfig):
        self.store = store
        self.config = config

    def log(self, subject_id: str, destino: str, finalidad: str,
            categorias: list[str] | None = None) -> None:
        tp = self.config.third_party(destino)
        self.store.put("privacy_transfers", {
            "ts": datetime.now(timezone.utc).isoformat(),
            "subject_id": subject_id,
            "destino": destino,
            "pais": (tp or {}).get("pais", "?"),
            "base_legal": (tp or {}).get("base", "?"),
            "finalidad": finalidad,
            "categorias": categorias or [],
            "tercero_declarado": tp is not None,  # False => transferencia NO registrada en config
        })
