"""Genera el Registro de Actividades de Tratamiento (ROPA) desde el config."""
from __future__ import annotations
from .config import PrivacyConfig


def build_ropa(config: PrivacyConfig) -> str:
    r = config.raw
    lines = ["# Registro de Actividades de Tratamiento (ROPA)", ""]
    resp = r.get("responsable", {})
    lines += [f"**Responsable:** {resp.get('nombre')} ({resp.get('rut')})",
              f"**Contacto privacidad:** {resp.get('contacto_privacidad')}", ""]
    lines.append("## Finalidades y base de licitud")
    for p, meta in r.get("purposes", {}).items():
        lines.append(f"- **{p}** — base: {meta.get('legal_basis')}")
    lines.append("\n## Categorías de datos y retención")
    for cat, fields in r.get("data_categories", {}).items():
        dias = r.get("retention_days", {}).get(cat, 0)
        lines.append(f"- **{cat}** ({', '.join(fields) or '—'}) — retención: {dias} días")
    lines.append("\n## Transferencias a terceros")
    for name, meta in r.get("third_parties", {}).items():
        lines.append(f"- **{name}** — país: {meta.get('pais')}, rol: {meta.get('rol')}, base: {meta.get('base')}")
    return "\n".join(lines) + "\n"
