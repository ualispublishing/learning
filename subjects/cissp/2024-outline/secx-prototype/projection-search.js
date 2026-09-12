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

function relationshipEntries(){
  const records=Array.isArray(window.SECX_RELEASED_RELATIONSHIPS)?window.SECX_RELEASED_RELATIONSHIPS:[];
  return records.map(r=>({
    kind:'relationship-projection',
    title:`${r.id} · ${r.from_id} ${r.type} ${r.to_id}`,
    path:'Reviewed Links',
    text:`reviewed link ${r.id} ${r.from_id} ${r.type} ${r.to_id} ${r.rationale||''}`,
    relationshipId:r.id
  }));
}

function rebuildProjectionSearch(){addProjectionEntries([...sourceEntries(),...coverageEntries(),...relationshipEntries()])}

const input=document.getElementById('searchInput');
const search=document.getElementById('search');
const results=document.getElementById('searchResults');
const searchHead=document.querySelector('.search-head');
const top=document.querySelector('.top');
const coverageButton=document.getElementById('coverageLensBtn');
const sourceButton=document.getElementById('sourceLensBtn');
const studyButton=document.getElementById('studyQueueBtn');
const dueButton=document.getElementById('dueReviewBtn');
let searchOpener=null;

const style=document.createElement('style');
style.textContent=`
.sec-search-button,.sec-search-close{border:1px solid #456784;background:#10263a;color:var(--text);font:inherit;cursor:pointer}.sec-search-button{border-radius:999px;padding:7px 11px;font-size:11px;white-space:nowrap}.sec-search-close{border-radius:10px;padding:7px 10px}.sec-search-button:hover,.sec-search-button:focus-visible,.sec-search-close:hover,.sec-search-close:focus-visible{border-color:var(--focus);outline:none}.search-head{display:flex;gap:8px;align-items:center}.search-input{min-width:0;flex:1}@media(max-width:800px){.sec-search-button,.sec-search-close{font-size:8px;padding:5px 6px}}
`;
document.head.appendChild(style);
const searchButton=document.createElement('button');
searchButton.id='searchPaletteBtn';searchButton.className='sec-search-button';searchButton.type='button';searchButton.textContent='Search';searchButton.setAttribute('aria-label','Open search palette');searchButton.setAttribute('aria-controls','search');
if(top)top.insertBefore(searchButton,coverageButton||sourceButton||studyButton||dueButton||document.querySelector('.legend')||null);
const closeButton=document.createElement('button');
closeButton.id='searchCloseBtn';closeButton.className='sec-search-close';closeButton.type='button';closeButton.textContent='Close';closeButton.setAttribute('aria-label','Close search palette');closeButton.setAttribute('aria-controls','search');
if(searchHead)searchHead.appendChild(closeButton);

function restoreSearchFocus(){
  const opener=searchOpener;
  searchOpener=null;
  if(opener?.isConnected)opener.focus({preventScroll:true});
}
function closeSearchToOpener(){closeSearch();restoreSearchFocus()}
searchButton.addEventListener('click',()=>{searchOpener=searchButton;openSearch();input?.focus({preventScroll:true})});
closeButton.addEventListener('click',closeSearchToOpener);

document.addEventListener('keydown',e=>{
  if(!search?.hidden)return;
  if(e.key!=='/'&&e.code!=='Slash')return;
  if(e.metaKey||e.ctrlKey||e.altKey)return;
  if(e.target.closest('input,textarea,select,[contenteditable="true"]'))return;
  searchOpener=document.activeElement;
},true);

function searchTabStops(){return[input,closeButton].filter(el=>el&&el.isConnected&&!el.disabled&&!el.hidden)}
document.addEventListener('keydown',e=>{
  if(!search||search.hidden)return;
  if(e.key==='Escape'){
    e.preventDefault();
    e.stopImmediatePropagation();
    closeSearchToOpener();
    return;
  }
  if(e.key!=='Tab')return;
  const stops=searchTabStops();
  if(!stops.length)return;
  const currentIndex=stops.indexOf(document.activeElement);
  let nextIndex;
  if(e.shiftKey)nextIndex=currentIndex<=0?stops.length-1:currentIndex-1;
  else nextIndex=currentIndex<0||currentIndex===stops.length-1?0:currentIndex+1;
  e.preventDefault();
  e.stopImmediatePropagation();
  stops[nextIndex].focus({preventScroll:true});
},true);

function syncSearchA11y(){
  if(!input||!search||!results)return;
  const expanded=String(!search.hidden);
  input.setAttribute('role','combobox');
  input.setAttribute('aria-autocomplete','list');
  input.setAttribute('aria-haspopup','listbox');
  input.setAttribute('aria-controls','searchResults');
  input.setAttribute('aria-expanded',expanded);
  searchButton.setAttribute('aria-expanded',expanded);
  const options=[...results.querySelectorAll('.search-result')];
  options.forEach((option,i)=>{option.id=`secx-search-option-${i}`;option.tabIndex=-1});
  const selected=options.find(option=>option.classList.contains('active')||option.getAttribute('aria-selected')==='true');
  if(selected)input.setAttribute('aria-activedescendant',selected.id);
  else input.removeAttribute('aria-activedescendant');
}
if(input){
  input.placeholder='Search curriculum, scenarios, sources, coverage, or reviewed links…';
  input.setAttribute('aria-label','Search curriculum, scenarios, sources, coverage, or reviewed links');
}
if(search&&results){
  new MutationObserver(syncSearchA11y).observe(search,{attributes:true,attributeFilter:['hidden']});
  new MutationObserver(syncSearchA11y).observe(results,{childList:true,subtree:true});
}

const priorNavigate=navigateSearch;
window.navigateSearch=function(item){
  if(!item)return;
  searchOpener=null;
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
  if(item.kind==='relationship-projection'){
    closeSearch();
    return typeof relationshipHubLayout==='function'?relationshipHubLayout(item.relationshipId,null,true):priorNavigate(item);
  }
  return priorNavigate(item);
};

rebuildProjectionSearch();
syncSearchA11y();
addEventListener('secx:released-bank',rebuildProjectionSearch);
addEventListener('secx:relationships-ready',rebuildProjectionSearch);
})();
