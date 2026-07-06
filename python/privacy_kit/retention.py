"""Retención y borrado automático. Cumple el principio de plazo y el derecho al olvido."""
from __future__ import annotations
from datetime import datetime, timezone, timedelta

from .config import PrivacyConfig
from .store.base import PrivacyStore


class RetentionManager:
    def __init__(self, store: PrivacyStore, config: PrivacyConfig):
        self.store = store
        self.config = config

    def expires_at(self, category: str, created_iso: str | None = None) -> str | None:
        days = self.config.retention(category)
        if days <= 0:
            return None
        base = datetime.fromisoformat(created_iso) if created_iso else datetime.now(timezone.utc)
        return (base + timedelta(days=days)).isoformat()

    def sweep(self, collections: list[str]) -> int:
        """Borra registros vencidos. Agendar en cron/worker (ej. diario)."""
        now = datetime.now(timezone.utc).isoformat()
        total = 0
        for col in collections:
            for row in self.store.expired(col, now):
                total += self.store.delete(col, {"id": row.get("id")})
        return total
