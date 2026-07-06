"""Consentimiento / base de licitud. Captura evidencia de la base con que se tratan datos."""
from __future__ import annotations
from datetime import datetime, timezone

from .config import PrivacyConfig
from .store.base import PrivacyStore
from .audit import AuditLog


class ConsentManager:
    def __init__(self, store: PrivacyStore, config: PrivacyConfig, audit: AuditLog):
        self.store = store
        self.config = config
        self.audit = audit

    def capture(self, subject_id: str, finalidad: str, canal: str,
                texto_aviso_version: str, otorgado: bool = True) -> None:
        """Registra el consentimiento (o su rechazo) con evidencia verificable."""
        base = self.config.legal_basis(finalidad)
        self.store.put("privacy_consent", {
            "ts": datetime.now(timezone.utc).isoformat(),
            "subject_id": subject_id,
            "finalidad": finalidad,
            "base_legal": base,
            "canal": canal,               # whatsapp, web, sms...
            "aviso_version": texto_aviso_version,
            "otorgado": otorgado,
        })
        self.audit.record(subject_id, "consentimiento", canal, finalidad,
                          {"otorgado": otorgado, "base": base})

    def has_valid_basis(self, subject_id: str, finalidad: str) -> bool:
        base = self.config.legal_basis(finalidad)
        if base in ("contrato", "interes_legitimo", "ley"):
            return True  # no requiere consentimiento explícito
        rows = self.store.find("privacy_consent",
                               {"subject_id": subject_id, "finalidad": finalidad})
        return any(r.get("otorgado") for r in rows)
