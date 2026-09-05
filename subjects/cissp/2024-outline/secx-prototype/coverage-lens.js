(() => {
'use strict';

const COVERAGE_PAGE_SIZE=16;
let coverageMode='root';
let coverageDomain=null;
let coveragePage=0;
let coverageQuestions=[];
let coverageBankReady=false;
let coverageBankError=null;

function qObjectives(q){return Array.isArray(q.objectives)?q.objectives:(q.objective?[q.objective]:[])}
function releasedReviewCards(){return Array.isArray(window.SECX_RELEASED_CARDS)?window.SECX_RELEASED_CARDS:[]}
function supplementalCards(){return Array.isArray(window.SECX_HIGH_CARDS)?window.SECX_HIGH_CARDS:[]}
function objectives(){return Array.isArray(window.secxObjectives)?window.secxObjectives:(typeof secxObjectives!=='undefined'?secxObjectives:releasedObjectives)}
function objectivesInDomain(n){return objectives().filter(o=>o.domain_num===n)}
function scenariosForObjective(id){return coverageQuestions.filter(q=>qObjectives(q).includes(id))}
function supplementalForObjective(id){return supplementalCards().filter(c=>c.objective===id)}
function reviewCardsForObjective(id){return releasedReviewCards().filter(c=>c.objective===id)}
function subtopicsForObjective(id){return Array.isArray(coverage[id])?coverage[id]:[]}
function coveredSubtopicsForObjective(id){
  const labels=subtopicsForObjective(id),qs=scenariosForObjective(id);
  return labels.filter(label=>qs.some(q=>Array.isArray(q.subtopics)&&q.subtopics.includes(label)));
}
function gapRecords(){
  return objectives().flatMap(o=>{
    const covered=new Set(coveredSubtopicsForObjective(o.id));
    return subtopicsForObjective(o.id).map((label,index)=>({objective:o.id,domain_num:o.domain_num,label,index})).filter(x=>!covered.has(x.label));
  });
}
function objectiveMetrics(o){
  const subs=subtopicsForObjective(o.id),covered=coveredSubtopicsForObjective(o.id),qs=scenariosForObjective(o.id);
  return{objective:o.id,domain_num:o.domain_num,subtopics:subs.length,subtopics_with_exact_scenario_tag:covered.length,practice_exposure_gaps:subs.length-covered.length,scenarios:qs.length,supplemental_cards:supplementalForObjective(o.id).length,review_cards:reviewCardsForObjective(o.id).length,sources:(o.source_ids||[]).length};
}
function domainMetrics(d){
  const os=objectivesInDomain(d.num),ms=os.map(objectiveMetrics);
  return{domain_num:d.num,title:d.title||d.name,weight:d.weight,objectives:os.length,subtopics:ms.reduce((n,x)=>n+x.subtopics,0),subtopics_with_exact_scenario_tag:ms.reduce((n,x)=>n+x.subtopics_with_exact_scenario_tag,0),practice_exposure_gaps:ms.reduce((n,x)=>n+x.practice_exposure_gaps,0),scenarios:ms.reduce((n,x)=>n+x.scenarios,0),supplemental_cards:ms.reduce((n,x)=>n+x.supplemental_cards,0),objectives_without_released_scenarios:ms.filter(x=>x.scenarios===0).length};
}
function rebuildSnapshot(){
  const ds=domains.map(domainMetrics),os=objectives().map(objectiveMetrics),gaps=gapRecords();
  window.SECX_COVERAGE_SNAPSHOT={
    bankReady:coverageBankReady,
    bankError:coverageBankError,
    standardQuestions:coverageQuestions.length,
    domains:ds,
    objectives:os,
    gaps:gaps.map(x=>({...x})),
    totals:{
      objectives:os.length,
      subtopics:os.reduce((n,x)=>n+x.subtopics,0),
      subtopics_with_exact_scenario_tag:os.reduce((n,x)=>n+x.subtopics_with_exact_scenario_tag,0),
      practice_exposure_gaps:gaps.length,
      scenarios:coverageQuestions.length,
      supplemental_cards:supplementalCards().length,
      review_cards:releasedReviewCards().length
    }
  };
}
function objectiveDetails(o){
  const m=objectiveMetrics(o),covered=m.subtopics_with_exact_scenario_tag;
  return{
    rule:o.direct||o.summary,
    why:`Explicit Atlas mappings: ${m.subtopics} enriched subtopics, ${m.review_cards} review cards, ${m.supplemental_cards} supplemental reviewed cards, and ${m.scenarios} released scenarios. ${covered}/${m.subtopics} subtopics have at least one exact released scenario tag.`,
    traps:[
      'Practice exposure counts do not measure learner mastery or exam readiness.',
      'A subtopic without an exact scenario tag may still be taught by the objective/card layers; this lens reports mapping exposure only.'
    ],
    sources:(o.source_ids||[]).map(sourceTitle),
    practice:m.scenarios?'Use the Released scenarios branch for application, then return here to inspect remaining exact-tag exposure gaps.':'No released scenario is explicitly mapped to this objective yet; treat this as a practice-exposure gap, not a curriculum omission.'
  };
}
function gapDetails(record){
  const o=objectiveById[record.objective];
  return{
    rule:record.label,
    why:`Released Atlas coverage maps this enriched subtopic to objective ${record.objective}${o?.label?` (${o.label})`:''}, but no manifest-released standard scenario carries this exact subtopic tag under that objective.`,
    traps:[
      'This is an exact-tag practice-exposure gap, not evidence that the subtopic is missing from the curriculum.',
      'This is not learner weakness, mastery, readiness, or a semantic relationship claim; the topic may still be taught or practiced through objective, card, or broader scenario context.'
    ],
    sources:['CISSP Atlas coverage-detail mapping','Manifest-released scenario subtopic tags'],
    practice:'Use the parent objective and its released cards/scenarios for study. This view only identifies the absence of an exact released scenario subtopic tag.'
  };
}
function coverageRadialPosition(i,count,outer,inner){const mobile=window.innerWidth<=800;return radialPosition(i,count,mobile?Math.min(outer,.31):outer,mobile?Math.min(inner,.20):inner)}
function addPager(centerId,page,totalPages){
  if(totalPages<=1)return;
  if(page>0){nodes.push({id:'coverage:prev',title:'Previous page',summary:`Page ${page} of ${totalPages}`,kind:'pager',x:.18,y:.88,action:'prev'});links.push([centerId,'coverage:prev'])}
  if(page<totalPages-1){nodes.push({id:'coverage:next',title:'Next page',summary:`Page ${page+2} of ${totalPages}`,kind:'pager',x:.82,y:.88,action:'next'});links.push([centerId,'coverage:next'])}
}
function addGapPager(centerId,page,totalPages){
  if(totalPages<=1)return;
  if(page>0){nodes.push({id:'coverage:gap:prev',title:'Previous gaps',summary:`Page ${page} of ${totalPages}`,kind:'pager',x:.18,y:.88,action:'prev'});links.push([centerId,'coverage:gap:prev'])}
  if(page<totalPages-1){nodes.push({id:'coverage:gap:next',title:'Next gaps',summary:`Page ${page+2} of ${totalPages}`,kind:'pager',x:.82,y:.88,action:'next'});links.push([centerId,'coverage:gap:next'])}
}

const style=document.createElement('style');
style.textContent=`
.sec-coverage-button{border:1px solid #456784;border-radius:999px;background:#10263a;color:var(--text);padding:7px 11px;font:inherit;font-size:11px;cursor:pointer;white-space:nowrap}.sec-coverage-button:hover,.sec-coverage-button:focus-visible{border-color:var(--focus);outline:none}
.node.coverage-root{width:190px;min-height:96px}.node.coverage-domain{width:154px;min-height:76px}.node.coverage-objective,.node.coverage-gap{width:142px;min-height:68px}
@media(max-width:800px){.top{gap:5px;padding:7px 9px;flex-wrap:wrap;justify-content:flex-start}.top .brand{flex:0 0 100%}.sec-coverage-button,.sec-source-button,.sec-study-button,.sec-due-button{font-size:8px;padding:5px 6px}.node.coverage-root,.node.coverage-domain,.node.coverage-objective,.node.coverage-gap{width:116px;min-height:56px}}
`;
document.head.appendChild(style);
const top=document.querySelector('.top'),sourceButton=document.getElementById('sourceLensBtn'),studyButton=document.getElementById('studyQueueBtn'),dueButton=document.getElementById('dueReviewBtn');
const coverageButton=document.createElement('button');coverageButton.id='coverageLensBtn';coverageButton.className='sec-coverage-button';coverageButton.type='button';
if(top)top.insertBefore(coverageButton,sourceButton||studyButton||dueButton||document.querySelector('.legend')||null);
function updateCoverageButton(){
  coverageButton.textContent=coverageBankReady?`Coverage · ${coverageQuestions.length}`:(coverageBankError?'Coverage · unavailable':'Coverage · loading');
  coverageButton.setAttribute('aria-label',coverageBankReady?`Open explicit coverage lens for ${coverageQuestions.length} released scenarios`:'Open explicit coverage lens');
}

window.coverageLayout=function(returnTo=null,focus=false){
  rebuildSnapshot();
  const snap=window.SECX_COVERAGE_SNAPSHOT,gapCount=snap.totals.practice_exposure_gaps,center={id:'coverage:root',title:'Coverage Map',summary:`${snap.totals.objectives} objectives · ${snap.totals.subtopics} subtopics · ${coverageBankReady?`${snap.totals.scenarios} released scenarios`:'released scenarios loading'} · ${gapCount} exact-tag gaps.`,kind:'coverage-root',x:.5,y:.5,labels:['explicit mappings','practice exposure',`${gapCount} exact-tag gaps`],details:{rule:'Inspect explicit curriculum and practice mappings without converting counts into mastery or semantic-edge claims.',why:'Counts come from released objectives, enriched subtopics, Atlas review cards, and the shared manifest-released scenario registry.',traps:['Coverage counts are corpus properties, not learner-performance scores.','Shared tags or sources do not create cross-domain semantic relationships.'],sources:['CISSP Atlas released data'],practice:`Press Enter to inspect the ${gapCount} enriched subtopics that currently have no exact manifest-released scenario subtopic tag.`}};
  nodes=[center];links=[];
  domains.forEach((d,i)=>{const m=domainMetrics(d),p=coverageRadialPosition(i,domains.length,.4,.24);nodes.push({id:`coverage:d${d.num}`,domainNum:d.num,title:`D${d.num} · ${d.title||d.name}`,summary:`${m.objectives} objectives · ${m.subtopics} subtopics · ${m.scenarios} scenarios`,kind:'coverage-domain',x:p.x,y:p.y,labels:[`${d.weight}% exam weight`,`${m.subtopics_with_exact_scenario_tag}/${m.subtopics} subtopics tagged`,`${m.practice_exposure_gaps} exact-tag gaps`],details:{rule:`Domain ${d.num} explicit coverage summary.`,why:`${m.objectives} objectives, ${m.subtopics} enriched subtopics, ${m.supplemental_cards} supplemental reviewed cards, and ${m.scenarios} released scenarios are explicitly mapped here.`,traps:['Exam weight is blueprint scope, not a learner score.','Scenario count is practice exposure, not proof of completeness.'],sources:['Released Atlas mappings'],practice:'Enter to inspect objective-level counts.'}});links.push([center.id,`coverage:d${d.num}`])});
  level='coverage';coverageMode='root';coverageDomain=null;coveragePage=0;parentDomain=null;parentObjective=null;active=returnTo&&nodes.some(n=>n.id===returnTo)?returnTo:'coverage:root';depth=0;render(focus);updateCoverageButton();
};

window.coverageGapLayout=function(returnTo=null,focus=false,page=null){
  rebuildSnapshot();
  const records=gapRecords(),pages=Math.max(1,Math.ceil(records.length/COVERAGE_PAGE_SIZE));coverageMode='gaps';coverageDomain=null;coveragePage=Math.max(0,Math.min(page??coveragePage,pages-1));
  const slice=records.slice(coveragePage*COVERAGE_PAGE_SIZE,(coveragePage+1)*COVERAGE_PAGE_SIZE),centerId='coverage:gaps';
  nodes=[{id:centerId,title:'Practice Exposure Gaps',summary:`${records.length} enriched subtopics without an exact manifest-released scenario tag`,kind:'coverage-root',x:.5,y:.5,labels:['exact tag comparison','released scenarios only',`page ${coveragePage+1}/${pages}`],details:{rule:'An exposure gap means no manifest-released standard scenario carries the exact enriched subtopic label under its mapped objective.',why:`The released coverage map contains ${window.SECX_COVERAGE_SNAPSHOT.totals.subtopics} enriched subtopics; ${records.length} currently lack an exact released scenario subtopic tag.`,traps:['A gap is not a curriculum omission or factual deficiency.','A gap is not learner weakness, readiness, mastery, or an inferred semantic relationship.'],sources:['CISSP Atlas coverage-detail mapping','Manifest-released scenario subtopic tags'],practice:'Inspect a gap, then use its parent objective, review cards, and broader released scenarios for study.'}}];links=[];
  slice.forEach((record,i)=>{const o=objectiveById[record.objective],p=coverageRadialPosition(i,slice.length,.39,.24),id=`coverage:gap:${record.objective}:${record.index}`;nodes.push({id,itemId:record.objective,domainNum:record.domain_num,title:record.label,summary:`Objective ${record.objective}${o?.label?` · ${o.label}`:''}`,kind:'coverage-gap',x:p.x,y:p.y,labels:[`D${record.domain_num}`,record.objective,'0 exact scenario tags'],details:gapDetails(record)});links.push([centerId,id])});
  addGapPager(centerId,coveragePage,pages);
  level='coverage-gaps';parentDomain=null;parentObjective=null;active=returnTo&&nodes.some(n=>n.id===returnTo)?returnTo:centerId;depth=0;render(focus);
};

window.coverageDomainLayout=function(domainNum,returnTo=null,focus=false,page=null){
  const d=domains.find(x=>x.num===domainNum);if(!d)return coverageLayout(null,focus);
  const records=objectivesInDomain(domainNum),pages=Math.max(1,Math.ceil(records.length/COVERAGE_PAGE_SIZE));coverageDomain=domainNum;coverageMode='domain';coveragePage=Math.max(0,Math.min(page??coveragePage,pages-1));
  const slice=records.slice(coveragePage*COVERAGE_PAGE_SIZE,(coveragePage+1)*COVERAGE_PAGE_SIZE),m=domainMetrics(d),centerId=`coverage:domain:${domainNum}`;
  nodes=[{id:centerId,domainNum,title:`D${domainNum} · ${d.title||d.name}`,summary:`${m.objectives} objectives · ${m.subtopics} subtopics · ${m.scenarios} released scenarios`,kind:'coverage-root',x:.5,y:.5,labels:[`${m.subtopics_with_exact_scenario_tag}/${m.subtopics} exact-tag subtopics`,`${m.practice_exposure_gaps} exact-tag gaps`],details:{rule:'This domain view reports only explicit released mappings.',why:`${m.objectives_without_released_scenarios} objectives currently have zero released scenarios mapped; ${m.practice_exposure_gaps} enriched subtopics lack an exact released scenario tag.`,traps:['Zero mapped scenarios or tags is a practice-exposure gap, not evidence that the objective or subtopic is absent from the curriculum.'],sources:['CISSP Atlas released data'],practice:'Open an objective to inspect its exact counts and sources.'}}];links=[];
  slice.forEach((o,i)=>{const om=objectiveMetrics(o),p=coverageRadialPosition(i,slice.length,.39,.24);nodes.push({id:`coverage:objective:${o.id}`,itemId:o.id,title:`${o.id} · ${o.label}`,summary:`${om.subtopics} subtopics · ${om.scenarios} scenarios · ${om.supplemental_cards} supplemental cards`,kind:'coverage-objective',x:p.x,y:p.y,labels:[`${om.subtopics_with_exact_scenario_tag}/${om.subtopics} subtopics tagged`,`${om.practice_exposure_gaps} exact-tag gaps`,`${om.sources} sources`],details:objectiveDetails(o)});links.push([centerId,`coverage:objective:${o.id}`])});
  addPager(centerId,coveragePage,pages);
  level='coverage-domain';parentDomain=null;parentObjective=null;active=returnTo&&nodes.some(n=>n.id===returnTo)?returnTo:centerId;depth=0;render(focus);
};

coverageButton.addEventListener('click',()=>coverageLayout(null,true));
const priorCrumb=crumbText;
window.crumbText=function(){if(level==='coverage')return'SecX › Coverage';if(level==='coverage-gaps')return'SecX › Coverage › Practice exposure gaps';if(level==='coverage-domain')return`SecX › Coverage › D${coverageDomain}`;return priorCrumb()};
const priorDescend=descend;
window.descend=function(){
  const n=current();
  if(level==='coverage'){
    if(n?.id==='coverage:root')return coverageGapLayout(null,true,0);
    if(n?.kind==='coverage-domain')return coverageDomainLayout(n.domainNum,null,true,0);
    return;
  }
  if(level==='coverage-gaps'){
    if(n?.kind==='pager')return coverageGapLayout(null,true,coveragePage+(n.action==='next'?1:-1));
    if(n?.kind==='coverage-gap'){depth=Math.max(depth,2);return showDetail()}
    return;
  }
  if(level==='coverage-domain'){
    if(n?.kind==='pager')return coverageDomainLayout(coverageDomain,null,true,coveragePage+(n.action==='next'?1:-1));
    if(n?.kind==='coverage-objective'){depth=Math.max(depth,2);return showDetail()}
    return;
  }
  return priorDescend();
};
const priorAscend=ascend;
window.ascend=function(){if(depth===0&&level==='coverage-gaps')return coverageLayout('coverage:root',true);if(depth===0&&level==='coverage-domain')return coverageLayout(`coverage:d${coverageDomain}`,true);if(depth===0&&level==='coverage')return domainLayout('root',true);return priorAscend()};
document.addEventListener('keydown',e=>{if(!document.getElementById('search')?.hidden)return;if(e.target.closest('input,textarea,select,[contenteditable="true"]'))return;if((e.key==='c'||e.key==='C')&&!e.metaKey&&!e.ctrlKey&&!e.altKey){e.preventDefault();e.stopImmediatePropagation();coverageLayout(null,true)}},true);

function syncCoverageBank(){
  const state=window.SECX_RELEASED_BANK_STATE||{};
  if(state.ready&&Array.isArray(window.SECX_RELEASED_QUESTIONS)){
    coverageQuestions=window.SECX_RELEASED_QUESTIONS;
    coverageBankReady=true;
    coverageBankError=null;
  }else{
    coverageQuestions=[];
    coverageBankReady=false;
    coverageBankError=state.error||null;
  }
  rebuildSnapshot();
  updateCoverageButton();
  if(level==='coverage')coverageLayout(active,false);
  else if(level==='coverage-gaps')coverageGapLayout(active,false,coveragePage);
  else if(level==='coverage-domain')coverageDomainLayout(coverageDomain,active,false,coveragePage);
}
addEventListener('secx:released-bank',syncCoverageBank);
syncCoverageBank();
})();
