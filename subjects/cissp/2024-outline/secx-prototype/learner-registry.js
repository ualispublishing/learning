var secxObjectives=(window.CISSP_CHUNKS||[]).flatMap(c=>Array.isArray(c.objectives)?c.objectives:[]);
var secxHighCards=(window.CISSP_CHUNKS||[]).flatMap(c=>Array.isArray(c.high)?c.high:[]);
var retrievalCards=[
  ...secxObjectives.map(o=>({
    id:`OBJ-${o.id}`,
    objective:o.id,
    domain:o.domain,
    domain_num:o.domain_num,
    kind:'Objective',
    front:`${o.id} · What is the key CISSP decision rule for ${String(o.label||'').toLowerCase()}?`,
    topic:o.label,
    direct:o.direct,
    trap:o.trap,
    source_ids:o.source_ids||[]
  })),
  ...secxHighCards.map(h=>({...h,kind:h.kind||'High-yield'}))
];
window.SECX_RELEASED_CARDS=retrievalCards;
window.SECX_HIGH_CARDS=secxHighCards;
