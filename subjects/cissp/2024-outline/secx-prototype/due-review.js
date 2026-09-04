(() => {
'use strict';

const DUE_PAGE_SIZE=16;
let duePage=0;

function progressState(id){
  try{return JSON.parse(localStorage.getItem('cissp_atlas_progress_v1')||'{}').cards?.[id]||null}catch{return null}
}
function todayISO(){const d=new Date();return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`}
function dueCards(){
  const today=todayISO();
  return (typeof retrievalCards!=='undefined'?retrievalCards:[])
    .filter(c=>{const s=progressState(c.id);return !!s&&s.due<=today})
    .sort((a,b)=>(progressState(a.id)?.due||'').localeCompare(progressState(b.id)?.due||'')||String(a.id).localeCompare(String(b.id)));
}
function cardDetails(c){return{rule:c.front,why:c.direct||'Retrieve the answer before revealing this layer.',traps:[c.trap||'Distinguish the nearest confusable concept.'],sources:(c.source_ids||[]).map(sourceTitle),practice:'Explain the answer without notes, then state one limitation, tradeoff, or confusable alternative.'}}

const style=document.createElement('style');
style.textContent=`
.sec-due-button{border:1px solid #456784;border-radius:999px;background:#10263a;color:var(--text);padding:7px 11px;font:inherit;font-size:11px;cursor:pointer;white-space:nowrap}.sec-due-button:hover,.sec-due-button:focus-visible{border-color:var(--focus);outline:none}.node.due-root{width:184px;min-height:94px}.node.due-empty{width:176px;min-height:70px}@media(max-width:800px){.sec-due-button{font-size:10px;padding:6px 9px}.node.due-root,.node.due-empty{width:128px}}
`;
document.head.appendChild(style);
const top=document.querySelector('.top'),legend=document.querySelector('.legend');
const dueButton=document.createElement('button');
dueButton.id='dueReviewBtn';dueButton.className='sec-due-button';dueButton.type='button';
if(top)top.insertBefore(dueButton,legend||null);

function updateDueButton(){const count=dueCards().length;dueButton.textContent=`Review due · ${count}`;dueButton.setAttribute('aria-label',`Review ${count} due retrieval cards`)}
function addDuePager(centerId,page,totalPages){
  if(totalPages<=1)return;
  if(page>0){nodes.push({id:'due:prev',title:'Previous page',summary:`Page ${page} of ${totalPages}`,kind:'pager',x:.18,y:.88,action:'prev'});links.push([centerId,'due:prev'])}
  if(page<totalPages-1){nodes.push({id:'due:next',title:'Next page',summary:`Page ${page+2} of ${totalPages}`,kind:'pager',x:.82,y:.88,action:'next'});links.push([centerId,'due:next'])}
}
window.dueReviewLayout=function(returnTo=null,focus=false,page=null){
  const records=dueCards(),pages=Math.max(1,Math.ceil(records.length/DUE_PAGE_SIZE));
  duePage=Math.max(0,Math.min(page??duePage,pages-1));
  const slice=records.slice(duePage*DUE_PAGE_SIZE,(duePage+1)*DUE_PAGE_SIZE);
  const center={id:'due:reviews',title:'Due Reviews',summary:records.length?`${records.length} released retrieval cards due under the Atlas schedule.`:'No released retrieval cards are currently due.',kind:'due-root',x:.5,y:.5,labels:['Atlas schedule',`${records.length} due`],details:{rule:'Review due retrieval cards before adding new material.',why:'This branch is derived only from the existing Atlas spaced-review state for released retrieval-card IDs.',traps:['A due state is a scheduling signal, not proof that a card is weak or that its objective is unmastered.'],sources:['CISSP Atlas learner progress'],practice:records.length?'Retrieve the answer before revealing it, then grade the first retrieval.':'Return after a card reaches its scheduled review date.'}};
  nodes=[center];links=[];
  if(slice.length){
    slice.forEach((c,i)=>{const pos=radialPosition(i,slice.length,.39,.24),s=progressState(c.id);nodes.push({id:c.id,title:`${c.id} · ${c.topic}`,summary:c.front,kind:'card',x:pos.x,y:pos.y,labels:[c.objective,`due ${s?.due||todayISO()}`,'released card'],details:cardDetails(c)});links.push([center.id,c.id])});
    addDuePager(center.id,duePage,pages);
  }else{
    nodes.push({id:'due:empty',title:'Nothing due',summary:'The released retrieval-card queue has no scheduled reviews due today.',kind:'due-empty',x:.5,y:.23,labels:['Atlas schedule'],details:{rule:'No scheduled retrieval review is currently due.',why:'Due status comes from Atlas card grades and review intervals, not page views.',traps:['Do not manufacture due work by changing curriculum state.'],sources:['CISSP Atlas learner progress'],practice:'Continue through the curriculum or return when a scheduled review becomes due.'}});links.push([center.id,'due:empty']);
  }
  level='due-reviews';parentDomain=null;parentObjective=null;active=returnTo&&nodes.some(n=>n.id===returnTo)?returnTo:'due:reviews';depth=0;render(focus);updateDueButton();
};

dueButton.addEventListener('click',()=>dueReviewLayout(null,true,0));

const graphCrumbText=crumbText;
window.crumbText=function(){if(level==='due-reviews')return'SecX › Due reviews';return graphCrumbText()};
const graphDescend=descend;
window.descend=function(){
  const n=current();
  if(level==='due-reviews'){
    if(n?.kind==='pager'){return dueReviewLayout(null,true,duePage+(n.action==='next'?1:-1))}
    if(n?.kind==='card'||n?.kind==='due-empty'){depth=Math.max(depth,2);return showDetail()}
    return;
  }
  return graphDescend();
};
const graphAscend=ascend;
window.ascend=function(){
  if(depth===0&&level==='due-reviews')return domainLayout('root',true);
  return graphAscend();
};

document.addEventListener('keydown',e=>{
  if(!document.getElementById('search')?.hidden)return;
  if(e.target.closest('input,textarea,select,[contenteditable="true"]'))return;
  if(e.key==='Escape'&&level==='due-reviews'&&depth===0){
    e.preventDefault();e.stopImmediatePropagation();domainLayout('root',true);return;
  }
  if((e.key==='r'||e.key==='R')&&!e.metaKey&&!e.ctrlKey&&!e.altKey){e.preventDefault();e.stopImmediatePropagation();dueReviewLayout(null,true,0)}
},true);

document.addEventListener('click',e=>{
  const grade=e.target.closest?.('[data-sec-grade]');if(!grade)return;
  const inDue=level==='due-reviews',id=inDue?current()?.id:null;
  setTimeout(()=>{
    updateDueButton();
    if(inDue){const keep=id&&dueCards().some(c=>c.id===id)?id:null;dueReviewLayout(keep,true,duePage)}
  },0);
});

addEventListener('storage',e=>{if(e.key==='cissp_atlas_progress_v1')updateDueButton()});
updateDueButton();
})();
