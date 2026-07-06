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

__version__ = "0.3.0"


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

    def resolve(self, query: str):
        """Busca subject_id(s) a partir de un dato textual vía el resolver registrado."""
        return self.rights.resolve(query)

    def subject_report(self, subject_id: str) -> dict:
        """Reporte agregado de TODO lo que el kit tiene de un titular (derecho de acceso)."""
        return {
            "subject_id": subject_id,
            "consents": self.store.find("privacy_consent", {"subject_id": subject_id}),
            "transfers": self.store.find("privacy_transfers", {"subject_id": subject_id}),
            "opposition": self.store.find("privacy_opposition", {"subject_id": subject_id}),
            "audit": self.store.read_log({"subject_id": subject_id}),
            "data": self.rights.access(subject_id),  # datos en las fuentes registradas
        }

    def forget(self, subject_id: str) -> dict:
        """Derecho al olvido: borra TODOS los datos personales del titular (fuentes +
        colecciones internas). Conserva la auditoría como evidencia y registra la supresión."""
        counts = {
            "fuentes": self.rights.erase(subject_id),
            "consentimientos": self.store.delete("privacy_consent", {"subject_id": subject_id}),
            "transferencias": self.store.delete("privacy_transfers", {"subject_id": subject_id}),
            "oposiciones": self.store.delete("privacy_opposition", {"subject_id": subject_id}),
        }
        self.audit.record(subject_id, "olvido_total", "admin", detalle=counts)
        return counts

    def serve_admin(self, **opts):
        """Levanta el panel de administración opcional (requiere admin_ui.enabled)."""
        from .admin import serve_admin
        return serve_admin(self, **opts)
