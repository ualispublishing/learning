(() => {
'use strict';

function addProjectionEntries(items){
  const seen=new Set(searchIndex.map(x=>`${x.kind}:${x.title}:${x.path||''}`));
  for(const item of items){
    const key=`${item.kind}:${item.title}:${item.path||''}`;
    if(!seen.has(key)){searchIndex.push(item);seen.add(key)}
  }
}

function sourceEntries(){
  const registry=atlasSources&&typeof atlasSources==='object'?atlasSources:{};
  return Object.entries(registry).map(([id,meta])=>({
    kind:'source-projection',
    title:`${id} · ${meta.title||id}`,
    path:'Source Provenance',
    text:`${id} ${meta.title||''} ${meta.role||''}`,
    sourceId:id
  }));
}

function coverageEntries(){
  const domainEntries=domains.map(d=>({
    kind:'coverage-domain-projection',
    title:`D${d.num} · ${d.title}`,
    path:'Coverage',
    text:`coverage domain ${d.num} ${d.title} ${d.weight}%`,
    domainNum:d.num
  }));
  const objectiveEntries=releasedObjectives.map(o=>({
    kind:'coverage-objective-projection',
    title:`${o.id} · ${o.label}`,
    path:`Coverage › D${o.domain_num}`,
    text:`coverage objective ${o.id} ${o.label} ${o.summary||''}`,
    domainNum:o.domain_num,
    objectiveId:o.id
  }));
  return [...domainEntries,...objectiveEntries];
}

function rebuildProjectionSearch(){addProjectionEntries([...sourceEntries(),...coverageEntries()])}

const priorNavigate=navigateSearch;
window.navigateSearch=function(item){
  if(!item)return;
  if(item.kind==='source-projection'){
    closeSearch();
    return typeof sourceHubLayout==='function'?sourceHubLayout(item.sourceId,null,true):priorNavigate(item);
  }
  if(item.kind==='coverage-domain-projection'){
    closeSearch();
    return typeof coverageDomainLayout==='function'?coverageDomainLayout(item.domainNum,null,true,0):priorNavigate(item);
  }
  if(item.kind==='coverage-objective-projection'){
    closeSearch();
    if(typeof coverageDomainLayout!=='function')return priorNavigate(item);
    coverageDomainLayout(item.domainNum,`coverage:objective:${item.objectiveId}`,true,0);
    const target=[...document.querySelectorAll('.node')].find(x=>x.dataset.id===`coverage:objective:${item.objectiveId}`);
    if(target){active=`coverage:objective:${item.objectiveId}`;render(true)}
    return;
  }
  return priorNavigate(item);
};

const input=document.getElementById('searchInput');
if(input){
  input.placeholder='Search curriculum, scenarios, sources, or coverage…';
  input.setAttribute('aria-label','Search curriculum, scenarios, sources, or coverage');
}

rebuildProjectionSearch();
addEventListener('secx:released-bank',rebuildProjectionSearch);
})();
