(() => {
'use strict';

const STUDY_PAGE_SIZE=16;
let studyMode='root';
let studyPage=0;

function progressState(id){
  try{return JSON.parse(localStorage.getItem('cissp_atlas_progress_v1')||'{}').cards?.[id]||null}catch{return null}
}
function todayISO(){const d=new Date();return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`}
function statusOf(id){const s=progressState(id);if(!s)return'new';if((s.stage||0)>=4)return'mature';return s.due<=todayISO()?'due':'learning'}
function allReviewCards(){return Array.isArray(window.SECX_RELEASED_CARDS)?window.SECX_RELEASED_CARDS:[]}
function objectiveCards(oid){return allReviewCards().filter(c=>c.objective===oid)}
function objectiveScore(oid){const cards=objectiveCards(oid);if(!cards.length)return 0;return cards.reduce((sum,c)=>sum+Math.min(4,progressState(c.id)?.stage||0),0)/(cards.length*4)}
function weakestDomain(){
  const list=Array.isArray(window.secxObjectives)?window.secxObjectives:(typeof secxObjectives!=='undefined'?secxObjectives:[]);
  const byDomain=new Map();
  for(const o of list){if(!byDomain.has(o.domain_num))byDomain.set(o.domain_num,[]);byDomain.get(o.domain_num).push(o.id)}
  return domains.map(d=>{const ids=byDomain.get(d.num)||[];const score=ids.length?ids.reduce((sum,id)=>sum+objectiveScore(id),0)/ids.length:0;return{...d,score}}).sort((a,b)=>a.score-b.score||b.weight-a.weight||a.num-b.num)[0]||domains[0];
}
function cardsForMode(mode){
  const cards=allReviewCards(),today=todayISO();
  if(mode==='due')return cards.filter(c=>{const s=progressState(c.id);return !!s&&s.due<=today}).sort((a,b)=>(progressState(a.id)?.due||'').localeCompare(progressState(b.id)?.due||'')||String(a.id).localeCompare(String(b.id)));
  if(mode==='new')return cards.filter(c=>!progressState(c.id)).sort((a,b)=>(a.domain_num||0)-(b.domain_num||0)||String(a.objective).localeCompare(String(b.objective))||String(a.id).localeCompare(String(b.id)));
  if(mode==='learning')return cards.filter(c=>statusOf(c.id)==='learning').sort((a,b)=>(progressState(a.id)?.stage||0)-(progressState(b.id)?.stage||0)||String(a.id).localeCompare(String(b.id)));
  if(mode==='mature')return cards.filter(c=>statusOf(c.id)==='mature').sort((a,b)=>(progressState(a.id)?.last_review||'').localeCompare(progressState(b.id)?.last_review||'')||String(a.id).localeCompare(String(b.id)));
  if(mode==='weak'){
    const weak=weakestDomain();
    return cards.filter(c=>c.domain_num===weak.num).sort((a,b)=>(progressState(a.id)?.stage||0)-(progressState(b.id)?.stage||0)||String(a.objective).localeCompare(String(b.objective))||String(a.id).localeCompare(String(b.id)));
  }
  return [];
}
function continuePlan(){
  const due=cardsForMode('due');
  if(due.length)return{mode:'due',label:'Due',card:due[0]};
  const learning=cardsForMode('learning');
  if(learning.length)return{mode:'learning',label:'Learning',card:learning[0]};
  const weak=weakestDomain(),fresh=cardsForMode('new'),weakNew=fresh.filter(c=>c.domain_num===weak.num);
  if(weakNew.length)return{mode:'new',label:`New D${weak.num}`,card:weakNew[0]};
  if(fresh.length)return{mode:'new',label:'New',card:fresh[0]};
  return{mode:'root',label:'Study',card:null};
}
function pageForCard(mode,id){const records=cardsForMode(mode),index=records.findIndex(c=>c.id===id);return index<0?0:Math.floor(index/STUDY_PAGE_SIZE)}
function modeTitle(mode){return({due:'Due reviews',new:'New cards',learning:'Learning cards',mature:'Mature cards',weak:'Lowest review-score domain'})[mode]||'Study queue'}
function cardDetails(c){return{rule:c.front,why:c.direct||'Retrieve the answer before revealing this layer.',traps:[c.trap||'Distinguish the nearest confusable concept.'],sources:(c.source_ids||[]).map(sourceTitle),practice:'Retrieve first, then grade the first retrieval using the Atlas schedule.'}}
function addPager(centerId,page,totalPages){
  if(totalPages<=1)return;
  if(page>0){nodes.push({id:'study:prev',title:'Previous page',summary:`Page ${page} of ${totalPages}`,kind:'pager',x:.18,y:.88,action:'prev'});links.push([centerId,'study:prev'])}
  if(page<totalPages-1){nodes.push({id:'study:next',title:'Next page',summary:`Page ${page+2} of ${totalPages}`,kind:'pager',x:.82,y:.88,action:'next'});links.push([centerId,'study:next'])}
}

const style=document.createElement('style');
style.textContent=`
.sec-study-button{border:1px solid #456784;border-radius:999px;background:#0d2235;color:var(--text);padding:7px 11px;font:inherit;font-size:11px;cursor:pointer;white-space:nowrap}.sec-study-button:hover,.sec-study-button:focus-visible{border-color:var(--focus);outline:none}.node.study-root{width:190px;min-height:96px}.node.study-facet{width:164px;min-height:78px}@media(max-width:800px){.sec-study-button{font-size:10px;padding:6px 9px}.node.study-root,.node.study-facet{width:126px;min-height:62px}}
`;
document.head.appendChild(style);
const top=document.querySelector('.top'),dueButton=document.getElementById('dueReviewBtn');
const continueButton=document.createElement('button');continueButton.id='continueStudyBtn';continueButton.className='sec-study-button';continueButton.type='button';
const studyButton=document.createElement('button');studyButton.id='studyQueueBtn';studyButton.className='sec-study-button';studyButton.type='button';
if(top){top.insertBefore(continueButton,dueButton||document.querySelector('.legend')||null);top.insertBefore(studyButton,dueButton||document.querySelector('.legend')||null)}

function counts(){const cards=allReviewCards();return{due:cardsForMode('due').length,new:cards.filter(c=>!progressState(c.id)).length,learning:cards.filter(c=>statusOf(c.id)==='learning').length,mature:cards.filter(c=>statusOf(c.id)==='mature').length}}
function updateStudyButton(){const c=counts();studyButton.textContent=`Study · ${c.due} due`;studyButton.setAttribute('aria-label',`Open study queue: ${c.due} due, ${c.new} new, ${c.learning} learning, ${c.mature} mature cards`)}
function updateContinueButton(){const plan=continuePlan();continueButton.textContent=`Continue · ${plan.label}`;continueButton.setAttribute('aria-label',plan.mode==='root'?'Open Study Queue; no due, learning, or new review cards remain':`Continue with ${plan.label.toLowerCase()} review work`)}
function refreshStudyControls(){updateStudyButton();updateContinueButton()}

window.studyQueueLayout=function(focus=false){
  const c=counts(),weak=weakestDomain();
  const center={id:'study:queue',title:'Study Queue',summary:'Choose work from Atlas review state without changing curriculum relationships.',kind:'study-root',x:.5,y:.5,labels:['learner state','Atlas schedule'],details:{rule:'Prefer due retrieval before new material; use review-stage signals as scheduling guidance, not proof of knowledge.',why:'This lens reuses Atlas card grades and keeps learner state separate from curriculum content.',traps:['A low review-stage score is not the same as an exam-readiness diagnosis.','Scenario answer exposure is not counted as retrieval mastery.'],sources:['CISSP Atlas learner progress'],practice:'Choose a queue, retrieve before reveal, then grade the first retrieval.'}};
  nodes=[center];links=[];
  const facets=[
    {id:'study:due',mode:'due',title:'Due reviews',summary:`${c.due} scheduled now`,x:.5,y:.17},
    {id:'study:new',mode:'new',title:'New cards',summary:`${c.new} ungraded`,x:.18,y:.43},
    {id:'study:learning',mode:'learning',title:'Learning',summary:`${c.learning} scheduled before maturity`,x:.28,y:.78},
    {id:'study:mature',mode:'mature',title:'Mature',summary:`${c.mature} stage 4+`,x:.72,y:.78},
    {id:'study:weak',mode:'weak',title:'Lowest review score',summary:`D${weak.num} · ${Math.round((weak.score||0)*100)}% review-stage score`,x:.82,y:.43}
  ];
  for(const f of facets){nodes.push({...f,kind:'study-facet',labels:[f.mode==='weak'?`D${weak.num}`:'Atlas card state','study lens']});links.push([center.id,f.id])}
  level='study-queue';parentDomain=null;parentObjective=null;studyMode='root';studyPage=0;active='study:queue';depth=0;render(focus);refreshStudyControls();
};

window.studyCardLayout=function(mode,returnTo=null,focus=false,page=null){
  const records=cardsForMode(mode),pages=Math.max(1,Math.ceil(records.length/STUDY_PAGE_SIZE));
  studyMode=mode;studyPage=Math.max(0,Math.min(page??studyPage,pages-1));
  const slice=records.slice(studyPage*STUDY_PAGE_SIZE,(studyPage+1)*STUDY_PAGE_SIZE),weak=weakestDomain();
  const centerId=`study:list:${mode}`,center={id:centerId,title:modeTitle(mode),summary:mode==='weak'?`${records.length} review cards in D${weak.num} (${weak.title}); ${Math.round((weak.score||0)*100)}% Atlas review-stage score.`:`${records.length} Atlas review cards in this queue.`,kind:'study-root',x:.5,y:.5,labels:[mode==='weak'?`D${weak.num}`:mode,'Atlas review state'],details:{rule:mode==='weak'?'This domain has the lowest current Atlas review-stage score; use it as a review-priority signal only.':'This queue is derived from existing Atlas review state.',why:'No curriculum relationship or mastery claim is created by this lens.',traps:['Scheduling and stage signals support study prioritization; they do not guarantee exam readiness.'],sources:['CISSP Atlas learner progress'],practice:'Retrieve before reveal and grade the first retrieval.'}};
  nodes=[center];links=[];
  if(slice.length){for(const [i,c] of slice.entries()){const pos=radialPosition(i,slice.length,.39,.24),s=progressState(c.id),st=statusOf(c.id);nodes.push({id:c.id,title:`${c.id} · ${c.topic}`,summary:c.front,kind:'card',x:pos.x,y:pos.y,labels:[c.objective,st,s?.due?`due ${s.due}`:'not yet graded'],details:cardDetails(c)});links.push([centerId,c.id])}addPager(centerId,studyPage,pages)}
  else {nodes.push({id:`study:empty:${mode}`,title:'Queue empty',summary:`No Atlas review cards currently match ${modeTitle(mode).toLowerCase()}.`,kind:'due-empty',x:.5,y:.24,labels:['learner state'],details:{rule:'There is no work in this queue right now.',why:'The queue is calculated from current Atlas learner state.',traps:['Do not manufacture state changes just to populate a queue.'],sources:['CISSP Atlas learner progress'],practice:'Choose another queue or return to the curriculum graph.'}});links.push([centerId,`study:empty:${mode}`])}
  level='study-cards';parentDomain=null;parentObjective=null;active=returnTo&&nodes.some(n=>n.id===returnTo)?returnTo:centerId;depth=0;render(focus);refreshStudyControls();
};

function runContinue(){const plan=continuePlan();if(plan.mode==='root')return studyQueueLayout(true);return studyCardLayout(plan.mode,plan.card?.id||null,true,pageForCard(plan.mode,plan.card?.id))}
continueButton.addEventListener('click',runContinue);
studyButton.addEventListener('click',()=>studyQueueLayout(true));
const priorCrumb=crumbText;
window.crumbText=function(){if(level==='study-queue')return'SecX › Study queue';if(level==='study-cards')return`SecX › Study queue › ${modeTitle(studyMode)}`;return priorCrumb()};
const priorDescend=descend;
window.descend=function(){
  const n=current();
  if(level==='study-queue'&&n?.kind==='study-facet')return studyCardLayout(n.mode,null,true,0);
  if(level==='study-cards'){
    if(n?.kind==='pager')return studyCardLayout(studyMode,null,true,studyPage+(n.action==='next'?1:-1));
    if(n?.kind==='card'||n?.kind==='due-empty'){depth=Math.max(depth,2);return showDetail()}
    return;
  }
  return priorDescend();
};
const priorAscend=ascend;
window.ascend=function(){if(depth===0&&level==='study-cards')return studyQueueLayout(true);if(depth===0&&level==='study-queue')return domainLayout('root',true);return priorAscend()};

document.addEventListener('keydown',e=>{
  if(!document.getElementById('search')?.hidden)return;
  if(e.target.closest('input,textarea,select,[contenteditable="true"]'))return;
  if((e.key==='q'||e.key==='Q')&&!e.metaKey&&!e.ctrlKey&&!e.altKey){e.preventDefault();e.stopImmediatePropagation();studyQueueLayout(true)}
},true);

document.addEventListener('click',e=>{if(!e.target.closest?.('[data-sec-grade]'))return;setTimeout(()=>{refreshStudyControls();if(level==='study-cards'){const id=current()?.id,keep=id&&cardsForMode(studyMode).some(c=>c.id===id)?id:null;studyCardLayout(studyMode,keep,true,studyPage)}},0)});
addEventListener('storage',e=>{if(e.key==='cissp_atlas_progress_v1')refreshStudyControls()});
refreshStudyControls();
})();
