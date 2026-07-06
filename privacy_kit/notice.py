"""Transparencia: genera y versiona el aviso de privacidad (para el primer contacto)."""
from __future__ import annotations
import hashlib

from .config import PrivacyConfig


class NoticeBuilder:
    def __init__(self, config: PrivacyConfig):
        self.config = config

    def render(self, canal: str = "whatsapp") -> str:
        r = self.config.raw.get("responsable", {})
        finalidades = ", ".join(self.config.raw.get("purposes", {}).keys())
        return (
            f"🔒 {r.get('nombre','La empresa')} trata tus datos personales para: {finalidades}. "
            f"Puedes ejercer tus derechos de acceso, rectificación, supresión, oposición y "
            f"portabilidad escribiendo a {r.get('contacto_privacidad','privacidad@empresa.cl')}. "
            f"Al continuar, aceptas esta política (Ley 21.719)."
        )

    def version(self) -> str:
        return "v" + hashlib.sha256(self.render().encode()).hexdigest()[:6]
