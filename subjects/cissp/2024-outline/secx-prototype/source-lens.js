(() => {
'use strict';

const SOURCE_PAGE_SIZE=16;
let sourceId=null;
let sourceMode='root';
let sourcePage=0;

function sourceRegistry(){return atlasSources&&typeof atlasSources==='object'?atlasSources:{}}
function sourceIds(){return Object.keys(sourceRegistry()).sort((a,b)=>String(sourceTitle(a)).localeCompare(String(sourceTitle(b))))}
function sourceMeta(id){return sourceRegistry()[id]||{title:id,role:'Released Atlas source mapping.',url:''}}
function objectivesForSource(id){return (Array.isArray(releasedObjectives)?releasedObjectives:[]).filter(o=>Array.isArray(o.source_ids)&&o.source_ids.includes(id))}
function reviewCardsForSource(id){const cards=Array.isArray(window.SECX_RELEASED_CARDS)?window.SECX_RELEASED_CARDS:[];return cards.filter(c=>Array.isArray(c.source_ids)&&c.source_ids.includes(id))}
function releasedScenarios(){const state=window.SECX_RELEASED_BANK_STATE||{};return state.ready&&Array.isArray(window.SECX_RELEASED_QUESTIONS)?window.SECX_RELEASED_QUESTIONS:[]}
function scenariosForSource(id){return releasedScenarios().filter(q=>Array.isArray(q.source_ids)&&q.source_ids.includes(id))}
function modeTitle(mode){return mode==='objectives'?'Objectives':mode==='cards'?'Review cards':'Released scenarios'}
function sourceSummary(id){const m=sourceMeta(id),os=objectivesForSource(id),cs=reviewCardsForSource(id),qs=scenariosForSource(id);return`${os.length} objectives · ${cs.length} review cards · ${qs.length} released scenarios${m.role?` · ${m.role}`:''}`}
function sourceDetails(id){const m=sourceMeta(id);return{rule:m.title||id,why:m.role||'This source is explicitly mapped in released Atlas content.',traps:['A shared source is provenance evidence, not proof that two cited concepts have a semantic relationship.','A supporting source may have narrower scope than the CISSP decision rule; preserve Atlas source-role notes.'],sources:[m.url||m.title||id],practice:'Choose Objectives, Review cards, or Released scenarios to inspect only released items that explicitly cite this source.'}}
function objectiveDetails(o,id){return{rule:o.direct||o.summary,why:`Objective ${o.id} explicitly includes ${id} in its released Atlas source_ids mapping.`,traps:[o.trap||'Keep the objective scoped to its stated security decision.','Citation does not mean this source is the sole authority for the objective.'],sources:(o.source_ids||[]).map(sourceTitle),practice:'Use the source mapping for provenance, then return to the objective graph for curriculum relationships.'}}
function cardDetails(c,id){return{rule:c.front,why:`Review card ${c.id} explicitly includes ${id} in its released Atlas source_ids mapping. ${c.direct||''}`.trim(),traps:[c.trap||'Retrieve before reveal and distinguish the nearest confusable concept.','Source co-citation does not create a cross-card semantic edge.'],sources:(c.source_ids||[]).map(sourceTitle),practice:'Retrieve the answer first; use the source list to verify scope and provenance.'}}
function scenarioDetails(q,id){const opts=(q.options||[]).map((x,i)=>`${String.fromCharCode(65+i)}. ${x}`).join(' · ');return{rule:`${q.stem||''}${opts?` Options: ${opts}`:''}`,why:`Released scenario ${q.id} explicitly includes ${id} in its source_ids mapping.`,traps:['Source provenance does not reveal or grade the scenario answer.','Co-citation does not create a cross-scenario semantic edge.'],sources:(q.source_ids||[]).map(sourceTitle),practice:'Open this scenario from its objective/released-scenarios branch to commit an answer before the keyed explanation is revealed.'}}
function addPager(centerId,page,totalPages){if(totalPages<=1)return;if(page>0){nodes.push({id:'source:prev',title:'Previous page',summary:`Page ${page} of ${totalPages}`,kind:'pager',x:.18,y:.88,action:'prev'});links.push([centerId,'source:prev'])}if(page<totalPages-1){nodes.push({id:'source:next',title:'Next page',summary:`Page ${page+2} of ${totalPages}`,kind:'pager',x:.82,y:.88,action:'next'});links.push([centerId,'source:next'])}}

const style=document.createElement('style');
style.textContent=`
.sec-source-button{border:1px solid #456784;border-radius:999px;background:#10283a;color:var(--text);padding:7px 11px;font:inherit;font-size:11px;cursor:pointer;white-space:nowrap}.sec-source-button:hover,.sec-source-button:focus-visible{border-color:var(--focus);outline:none}.node.sources-root{width:190px;min-height:96px}.node.source-node{width:150px;min-height:70px}.node.source-facet{width:170px;min-height:82px}.node.source-scenario{width:132px;min-height:62px;padding:9px 10px}@media(max-width:800px){.top{gap:6px;padding:8px 10px}.brand{font-size:12px}.sec-source-button,.sec-study-button,.sec-due-button{font-size:9px;padding:5px 7px}.node.sources-root,.node.source-node,.node.source-facet{width:118px;min-height:58px}.node.source-scenario{width:104px;min-height:54px}}
`;
document.head.appendChild(style);
const top=document.querySelector('.top'),studyButton=document.getElementById('studyQueueBtn'),dueButton=document.getElementById('dueReviewBtn');
const sourceButton=document.createElement('button');sourceButton.id='sourceLensBtn';sourceButton.className='sec-source-button';sourceButton.type='button';
if(top)top.insertBefore(sourceButton,studyButton||dueButton||document.querySelector('.legend')||null);
function updateSourceButton(){const n=sourceIds().length;sourceButton.textContent=`Sources · ${n}`;sourceButton.setAttribute('aria-label',`Open source provenance lens with ${n} released Atlas sources`)}

window.sourcesLayout=function(returnTo=null,focus=false){
  const ids=sourceIds(),center={id:'sources:root',title:'Source Provenance',summary:`${ids.length} released Atlas sources. Traverse only explicit source_ids mappings.`,kind:'sources-root',x:.5,y:.5,labels:['provenance','explicit mappings'],details:{rule:'Use sources to verify provenance and scope without inventing semantic relationships between co-cited items.',why:'Atlas already records source IDs and source-role notes. This lens exposes those mappings directly.',traps:['Shared citation is not a semantic edge.','A source can support only part of a broader CISSP rule.'],sources:['CISSP Atlas source registry'],practice:'Select a source, then inspect explicitly citing objectives, review cards, or released scenarios.'}};
  nodes=[center];links=[];
  ids.forEach((id,i)=>{const p=radialPosition(i,ids.length,.4,.24),m=sourceMeta(id),os=objectivesForSource(id),cs=reviewCardsForSource(id),qs=scenariosForSource(id);nodes.push({id:`source:${id}`,sourceId:id,title:m.title||id,summary:`${os.length} objectives · ${cs.length} cards · ${qs.length} scenarios`,kind:'source-node',x:p.x,y:p.y,labels:[id,'released source'],details:sourceDetails(id)});links.push([center.id,`source:${id}`])});
  level='sources';sourceId=null;sourceMode='root';sourcePage=0;parentDomain=null;parentObjective=null;active=returnTo&&nodes.some(n=>n.id===returnTo)?returnTo:'sources:root';depth=0;render(focus);updateSourceButton();
};

window.sourceHubLayout=function(id,returnTo=null,focus=false){
  const m=sourceMeta(id),os=objectivesForSource(id),cs=reviewCardsForSource(id),qs=scenariosForSource(id),centerId=`source:${id}`;
  nodes=[{id:centerId,sourceId:id,title:m.title||id,summary:sourceSummary(id),kind:'source-node',x:.5,y:.5,labels:[id,'provenance'],details:sourceDetails(id)}];links=[];
  const facets=[
    {id:`source:${id}:objectives`,mode:'objectives',title:'Objectives',summary:`${os.length} explicit citations`,x:.18,y:.7},
    {id:`source:${id}:cards`,mode:'cards',title:'Review cards',summary:`${cs.length} explicit citations`,x:.5,y:.82},
    {id:`source:${id}:scenarios`,mode:'scenarios',title:'Released scenarios',summary:`${qs.length} explicit citations`,x:.82,y:.7}
  ];
  facets.forEach(f=>{nodes.push({...f,kind:'source-facet',sourceId:id,labels:[id,'source_ids mapping']});links.push([centerId,f.id])});
  level='source-hub';sourceId=id;sourceMode='hub';sourcePage=0;parentDomain=null;parentObjective=null;active=returnTo&&nodes.some(n=>n.id===returnTo)?returnTo:centerId;depth=0;render(focus);
};

window.sourceItemsLayout=function(id,mode,returnTo=null,focus=false,page=null){
  const m=sourceMeta(id),records=mode==='objectives'?objectivesForSource(id):mode==='cards'?reviewCardsForSource(id):scenariosForSource(id),pages=Math.max(1,Math.ceil(records.length/SOURCE_PAGE_SIZE));
  sourceId=id;sourceMode=mode;sourcePage=Math.max(0,Math.min(page??sourcePage,pages-1));
  const slice=records.slice(sourcePage*SOURCE_PAGE_SIZE,(sourcePage+1)*SOURCE_PAGE_SIZE),centerId=`source:list:${id}:${mode}`;
  nodes=[{id:centerId,sourceId:id,title:`${m.title||id} · ${modeTitle(mode)}`,summary:`${records.length} released items explicitly cite ${id}.`,kind:'sources-root',x:.5,y:.5,labels:[id,mode,'explicit source_ids'],details:{rule:'This is a provenance projection over explicit released source_ids.',why:'No lexical or semantic inference is used to populate this list.',traps:['Co-citation does not imply that items depend on, contrast with, or implement one another.'],sources:[m.url||m.title||id],practice:'Inspect an item, then return to the curriculum graph for its actual hierarchy or practice flow.'}}];links=[];
  if(slice.length){
    slice.forEach((item,i)=>{
      const p=radialPosition(i,slice.length,.39,.24);
      if(mode==='objectives'){
        nodes.push({id:`source-item:objective:${item.id}`,itemId:item.id,title:`${item.id} · ${item.label}`,summary:item.summary,kind:'objective',x:p.x,y:p.y,labels:[id,`D${item.domain_num}`,'explicit citation'],details:objectiveDetails(item,id)});links.push([centerId,`source-item:objective:${item.id}`]);
      }else if(mode==='cards'){
        nodes.push({id:`source-item:card:${item.id}`,itemId:item.id,title:`${item.id} · ${item.topic||item.objective}`,summary:item.front,kind:'card',x:p.x,y:p.y,labels:[id,item.objective,'explicit citation'],details:cardDetails(item,id)});links.push([centerId,`source-item:card:${item.id}`]);
      }else{
        const oid=Array.isArray(item.objectives)?item.objectives[0]:(item.objective||'');
        nodes.push({id:`source-item:scenario:${item.id}`,itemId:item.id,title:`${item.id} · ${item.decision_verb||'Scenario'}`,summary:item.stem,kind:'source-scenario',x:p.x,y:p.y,labels:[id,oid||'released scenario','explicit citation'],details:scenarioDetails(item,id)});links.push([centerId,`source-item:scenario:${item.id}`]);
      }
    });
    addPager(centerId,sourcePage,pages);
  }else{
    const empty=`source:empty:${id}:${mode}`;nodes.push({id:empty,title:'No explicit citations',summary:`No released ${modeTitle(mode).toLowerCase()} currently cite ${id}.`,kind:'due-empty',x:.5,y:.24,labels:[id,'provenance'],details:{rule:'No matching explicit source_ids mapping exists in this view.',why:'The source lens fails empty rather than guessing relationships.',traps:['Do not backfill with text similarity or shared terminology.'],sources:[m.url||m.title||id],practice:'Return to the source hub and choose another branch.'}});links.push([centerId,empty]);
  }
  level='source-items';parentDomain=null;parentObjective=null;active=returnTo&&nodes.some(n=>n.id===returnTo)?returnTo:centerId;depth=0;render(focus);
};

sourceButton.addEventListener('click',()=>sourcesLayout(null,true));
const priorCrumb=crumbText;
window.crumbText=function(){if(level==='sources')return'SecX › Sources';if(level==='source-hub')return`SecX › Sources › ${sourceTitle(sourceId)}`;if(level==='source-items')return`SecX › Sources › ${sourceTitle(sourceId)} › ${modeTitle(sourceMode)}`;return priorCrumb()};
const priorDescend=descend;
window.descend=function(){const n=current();if(level==='sources'&&n?.kind==='source-node')return sourceHubLayout(n.sourceId,null,true);if(level==='source-hub'&&n?.kind==='source-facet')return sourceItemsLayout(n.sourceId,n.mode,null,true,0);if(level==='source-items'){if(n?.kind==='pager')return sourceItemsLayout(sourceId,sourceMode,null,true,sourcePage+(n.action==='next'?1:-1));if(n?.kind==='objective'||n?.kind==='card'||n?.kind==='source-scenario'||n?.kind==='due-empty'){depth=Math.max(depth,2);return showDetail()}return}return priorDescend()};
const priorAscend=ascend;
window.ascend=function(){if(depth===0&&level==='source-items')return sourceHubLayout(sourceId,null,true);if(depth===0&&level==='source-hub')return sourcesLayout(`source:${sourceId}`,true);if(depth===0&&level==='sources')return domainLayout('root',true);return priorAscend()};

document.addEventListener('keydown',e=>{if(!document.getElementById('search')?.hidden)return;if(e.target.closest('input,textarea,select,[contenteditable="true"]'))return;if((e.key==='s'||e.key==='S')&&!e.metaKey&&!e.ctrlKey&&!e.altKey){e.preventDefault();e.stopImmediatePropagation();sourcesLayout(null,true)}},true);
addEventListener('secx:released-bank',()=>{if(level==='sources')sourcesLayout(active,false);else if(level==='source-hub')sourceHubLayout(sourceId,active,false);else if(level==='source-items'&&sourceMode==='scenarios')sourceItemsLayout(sourceId,sourceMode,active,false,sourcePage)});
updateSourceButton();
})();