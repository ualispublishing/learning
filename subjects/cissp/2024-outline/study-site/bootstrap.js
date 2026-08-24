(async()=>{'use strict';
const root=document.documentElement;
root.dataset.cisspReady='loading';
root.dataset.cisspBank='loading';
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

function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot',"'":'&#039;'}[c]))}
function surfaceStartupIssue(message,{fatal=false}={}){
  root.dataset.cisspReady=fatal?'failed':'degraded';
  const main=document.querySelector('#main');
  if(!main)return;
  const existing=document.querySelector('#startupIssue');
  const box=existing||document.createElement('div');
  box.id='startupIssue';
  box.className='notice';
  box.setAttribute('role','alert');
  box.innerHTML=`<b>${fatal?'CISSP Atlas could not finish starting.':'CISSP Atlas recovered from a startup issue.'}</b> ${esc(message||'Unknown startup error')}${fatal?' <button class="btn small" type="button" onclick="location.reload()">Reload</button>':''}`;
  if(!existing)main.prepend(box);
}

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
  root.dataset.cisspBank='ready';
}catch(err){
  console.error('CISSP released bank load failed',err);
  window.CISSP_RELEASE_LOAD_ERROR=String(err);
  window.CISSP_BELLRINGERS=[];
  root.dataset.cisspBank='degraded';
}

try{
  await import('./app.js');
  root.dataset.cisspCore='ready';
}catch(err){
  console.error('CISSP core app load failed',err);
  root.dataset.cisspCore='failed';
  surfaceStartupIssue(err,{fatal:true});
  return;
}

let optionalFailures=0;
for(const modulePath of ['./enhancements.js','./state-ui-bridge.js','./product-polish.js?v=5']){
  try{
    await import(modulePath);
  }catch(err){
    optionalFailures++;
    console.error(`CISSP optional module failed: ${modulePath}`,err);
    surfaceStartupIssue(`${modulePath}: ${err?.message||err}`);
  }
}
if(!optionalFailures)root.dataset.cisspReady='true';
})();
