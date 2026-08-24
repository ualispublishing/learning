(async()=>{'use strict';
const calibration=window.CISSP_QUESTION_CALIBRATION||{},legacyRationales=window.CISSP_LEGACY_RATIONALES||{};
for(const chunk of (window.CISSP_CHUNKS||[]))for(const q of (chunk.questions||[])){
  const c=calibration[q.id];if(c){q.difficulty_tier=c.tier;q.difficulty_score=c.score}
  const r=legacyRationales[q.id];if(r)q.distractor_rationales=r;
}
// The original card engine keeps an in-memory progress snapshot. v1.3 practice adds
// richer quiz/Bellringer history after that snapshot is created. Preserve those newer
// histories if a later card grade writes the older snapshot back to localStorage.
const PROGRESS_KEY='cissp_atlas_progress_v1',nativeSet=Storage.prototype.setItem;
Storage.prototype.setItem=function(key,value){
  if(this===localStorage&&key===PROGRESS_KEY){
    try{
      const current=JSON.parse(this.getItem(key)||'{}'),incoming=JSON.parse(value||'{}');
      const currentQuizHistory=current.quiz?.history||[],incomingQuizHistory=incoming.quiz?.history||[];
      if(currentQuizHistory.length>incomingQuizHistory.length)incoming.quiz=current.quiz;
      const currentBellHistory=current.bellringers?.history||[],incomingBellHistory=incoming.bellringers?.history||[];
      if(currentBellHistory.length>incomingBellHistory.length)incoming.bellringers=current.bellringers;
      value=JSON.stringify(incoming);
    }catch(e){console.warn('CISSP progress merge fallback',e)}
  }
  return nativeSet.call(this,key,value);
};
try{
  const manifest=await fetch('question-bank/RELEASED_BATCHES.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`release manifest ${r.status}`);return r.json()});
  const files=manifest.released_batches.flatMap(b=>b.files||[]);
  const texts=await Promise.all(files.map(p=>fetch(p,{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`${p} ${r.status}`);return r.text()})));
  const rows=texts.flatMap(t=>t.split(/\r?\n/).filter(Boolean).map(line=>JSON.parse(line)));
  const domainNames=Object.fromEntries((window.CISSP_META?.domains||[]).map(d=>[d.num,d.name]));
  const standard=rows.filter(r=>r.format==='mcq').map(r=>({...r,domain_num:r.domain_primary,domain:domainNames[r.domain_primary]||`Domain ${r.domain_primary}`,objective:r.objectives?.[0]||''}));
  window.CISSP_CHUNKS.push({objectives:[],high:[],questions:standard});
  window.CISSP_BELLRINGERS=rows.filter(r=>r.format==='bellringer');
  window.CISSP_RELEASED_BANK_MANIFEST=manifest;
  window.CISSP_BANK_READY=true;
}catch(err){console.error('CISSP released bank load failed',err);window.CISSP_RELEASE_LOAD_ERROR=String(err);window.CISSP_BELLRINGERS=[];}
await import('./app.js');
await import('./enhancements.js');
await import('./state-ui-bridge.js');
})();
