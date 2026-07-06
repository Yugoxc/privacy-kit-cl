'use strict';
// Genera el Registro de Actividades de Tratamiento (ROPA) desde el config.
function buildRopa(config) {
  const r = config.raw;
  const lines = ['# Registro de Actividades de Tratamiento (ROPA)', ''];
  const resp = r.responsable || {};
  lines.push(`**Responsable:** ${resp.nombre} (${resp.rut})`,
             `**Contacto privacidad:** ${resp.contactoPrivacidad}`, '');
  lines.push('## Finalidades y base de licitud');
  for (const [p, m] of Object.entries(r.purposes || {})) lines.push(`- **${p}** — base: ${m.legalBasis}`);
  lines.push('', '## Categorías de datos y retención');
  for (const [cat, f] of Object.entries(r.dataCategories || {})) {
    const d = (r.retentionDays || {})[cat] || 0;
    lines.push(`- **${cat}** (${(f || []).join(', ') || '—'}) — retención: ${d} días`);
  }
  lines.push('', '## Transferencias a terceros');
  for (const [n, m] of Object.entries(r.thirdParties || {}))
    lines.push(`- **${n}** — país: ${m.pais}, rol: ${m.rol}, base: ${m.base}`);
  return lines.join('\n') + '\n';
}
module.exports = { buildRopa };
