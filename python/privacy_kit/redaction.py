"""Minimización: detecta y anonimiza PII ANTES de enviarla a un LLM o a un tercero.

Es el punto de control más importante para sistemas con IA: evita que datos
personales (RUT, teléfono, tarjeta) viajen en claro a OpenAI/Anthropic.

Estrategia por defecto: pseudonimización reversible por sesión (tokens estables),
para que el LLM pueda razonar sobre "el cliente" sin ver el dato real, y luego
poder rehidratar si el flujo lo necesita (con control de acceso + auditoría).
"""
from __future__ import annotations
import re
import hashlib
from dataclasses import dataclass

from .config import PrivacyConfig


@dataclass
class RedactionResult:
    text: str                 # texto con PII reemplazada por tokens
    token_map: dict[str, str] # token -> valor original (NO enviar al LLM)
    found: dict[str, int]     # tipo_pii -> cantidad encontrada


class Redactor:
    def __init__(self, config: PrivacyConfig):
        self.patterns = {k: re.compile(v) for k, v in config.pii_patterns.items()}

    def _token(self, tipo: str, valor: str, salt: str) -> str:
        h = hashlib.sha256(f"{salt}:{valor}".encode()).hexdigest()[:8]
        return f"[{tipo.upper()}_{h}]"

    def redact(self, text: str, subject_id: str = "anon") -> RedactionResult:
        """Reemplaza PII por tokens estables. Devuelve texto seguro + mapa reversible.

        Enviar SOLO `result.text` al LLM. Guardar `result.token_map` en memoria de
        sesión protegida (nunca en logs ni al tercero).
        """
        if not text:
            return RedactionResult(text="", token_map={}, found={})
        token_map: dict[str, str] = {}
        found: dict[str, int] = {}
        out = text
        for tipo, rx in self.patterns.items():
            def _sub(m):
                val = m.group(0)
                tok = self._token(tipo, val, subject_id)
                token_map[tok] = val
                found[tipo] = found.get(tipo, 0) + 1
                return tok
            out = rx.sub(_sub, out)
        return RedactionResult(text=out, token_map=token_map, found=found)

    def rehydrate(self, text: str, token_map: dict[str, str]) -> str:
        """Reemplaza los tokens por sus valores reales (uso interno controlado)."""
        for tok, val in token_map.items():
            text = text.replace(tok, val)
        return text
