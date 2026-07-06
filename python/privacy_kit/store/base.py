"""Interfaz de almacenamiento. Implementa esto sobre tu BD (Mongo/ClickHouse/Postgres).

Solo 6 métodos: el kit no sabe nada de tu infraestructura, solo de estos contratos.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class PrivacyStore(ABC):
    @abstractmethod
    def put(self, collection: str, record: dict[str, Any]) -> str: ...

    @abstractmethod
    def find(self, collection: str, query: dict[str, Any]) -> list[dict[str, Any]]: ...

    @abstractmethod
    def delete(self, collection: str, query: dict[str, Any]) -> int: ...

    @abstractmethod
    def update(self, collection: str, query: dict[str, Any], patch: dict[str, Any]) -> int: ...

    @abstractmethod
    def append_log(self, record: dict[str, Any]) -> None:
        """Bitácora append-only (auditoría). Idealmente inmutable / WORM."""

    @abstractmethod
    def expired(self, collection: str, before_iso: str) -> list[dict[str, Any]]:
        """Registros cuya retención venció (para el barrido de borrado)."""

    def read_log(self, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Opcional (panel admin): leer la bitácora. Default vacío para no romper stores existentes."""
        return []


class InMemoryStore(PrivacyStore):
    """Implementación de prueba/prototipo. NO usar en producción."""
    def __init__(self):
        self._db: dict[str, list[dict]] = {}
        self._log: list[dict] = []

    def put(self, collection, record):
        self._db.setdefault(collection, []).append(record)
        return record.get("id", str(len(self._db[collection])))

    def find(self, collection, query):
        return [r for r in self._db.get(collection, [])
                if all(r.get(k) == v for k, v in query.items())]

    def delete(self, collection, query):
        rows = self._db.get(collection, [])
        keep = [r for r in rows if not all(r.get(k) == v for k, v in query.items())]
        n = len(rows) - len(keep)
        self._db[collection] = keep
        return n

    def update(self, collection, query, patch):
        n = 0
        for r in self._db.get(collection, []):
            if all(r.get(k) == v for k, v in query.items()):
                r.update(patch); n += 1
        return n

    def append_log(self, record):
        self._log.append(record)

    def expired(self, collection, before_iso):
        return [r for r in self._db.get(collection, [])
                if r.get("expires_at") and r["expires_at"] < before_iso]

    def read_log(self, query=None):
        query = query or {}
        return [r for r in self._log if all(r.get(k) == v for k, v in query.items())]
