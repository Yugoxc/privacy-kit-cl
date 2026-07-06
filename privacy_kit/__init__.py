"""privacy-kit-cl — capa de cumplimiento Ley 21.719 (Chile), acoplable y reutilizable."""
from __future__ import annotations
from dataclasses import dataclass

from .config import PrivacyConfig
from .redaction import Redactor
from .consent import ConsentManager
from .rights import RightsManager
from .audit import AuditLog
from .retention import RetentionManager
from .transfers import TransferRegistry
from .notice import NoticeBuilder
from .store.base import PrivacyStore, InMemoryStore

__version__ = "0.1.0"


@dataclass
class PrivacyKit:
    """Fachada única. Compón todos los componentes sobre un mismo Store + Config."""
    config: PrivacyConfig
    store: PrivacyStore
    redaction: Redactor
    consent: ConsentManager
    rights: RightsManager
    audit: AuditLog
    retention: RetentionManager
    transfers: TransferRegistry
    notice: NoticeBuilder

    @classmethod
    def from_config(cls, path: str, store: PrivacyStore | None = None) -> "PrivacyKit":
        cfg = PrivacyConfig.load(path)
        store = store or InMemoryStore()
        audit = AuditLog(store)
        return cls(
            config=cfg,
            store=store,
            redaction=Redactor(cfg),
            consent=ConsentManager(store, cfg, audit),
            rights=RightsManager(store, cfg, audit),
            audit=audit,
            retention=RetentionManager(store, cfg),
            transfers=TransferRegistry(store, cfg),
            notice=NoticeBuilder(cfg),
        )

    def export_ropa(self) -> str:
        """Genera el Registro de Actividades de Tratamiento (ROPA) a partir del config."""
        from .ropa import build_ropa
        return build_ropa(self.config)
