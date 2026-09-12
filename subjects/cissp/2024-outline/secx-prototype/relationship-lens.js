(() => {
'use strict';

let relationshipId=null;

function relationshipRecords(){return Array.isArray(window.SECX_RELEASED_RELATIONSHIPS)?window.SECX_RELEASED_RELATIONSHIPS:[]}
function relationshipById(id){return relationshipRecords().find(r=>r.id===id)||null}
function relationshipIdFromNode(n){if(n?.relationshipId)return n.relationshipId;const id=String(n?.id||''),prefix='relationship:';return id.startsWith(prefix)&&!id.startsWith('relationship:endpoint:')?id.slice(prefix.length):null}
function endpointTargetFromNode(n){if(n?.itemId)return n.itemId;const parts=String(n?.id||'').split(':');if(parts.length!==4||parts[0]!=='relationship'||parts[1]!=='endpoint')return null;const r=relationshipById(parts[2]);return parts[3]==='from'?r?.from_id:parts[3]==='to'?r?.to_id:null}
function endpointObjective(id){return objectiveById[id]||null}
function endpointTitle(id){const o=endpointObjective(id);return o?`${o.id} · ${o.label}`:id}
function relationTitle(r){return`${r.from_id} ${r.type} ${r.to_id}`}
function relationDetails(r){return{
  rule:relationTitle(r),
  why:r.rationale,
  traps:[
    'This edge is learner-facing only because it passed relationship-specific review and the prototype release gate.',
    'Shared wording, co-citation, search similarity, or coverage proximity alone must never create a relationship.'
  ],
  sources:Array.isArray(r.evidence?.references)?r.evidence.references:['SecX released relationship review'],
  practice:'Press Enter to inspect the two stable released endpoints, then open an endpoint to return to its normal Atlas objective context.'
}}
function endpointDetails(id,r,role){const o=endpointObjective(id);return{
  rule:o?.direct||o?.summary||endpointTitle(id),
  why:`This is the ${role} endpoint of ${r.id} (${relationTitle(r)}). The relationship rationale is: ${r.rationale}`,
  traps:[
    'The relationship does not replace the objective hierarchy or broaden either endpoint beyond its released scope.',
    'Navigate into the objective to study its normal subtopics, retrieval cards, and scenarios.'
  ],
  sources:[...(o?.source_ids||[]).map(sourceTitle),...(Array.isArray(r.evidence?.references)?r.evidence.references:[])],
  practice:o?`Press Enter to open objective ${o.id} in its normal domain context.`:'This endpoint is stable but does not currently have an objective-layout route.'
}}
function relationshipRadialPosition(i,count,outer=.37,inner=.23){const mobile=window.innerWidth<=800;return radialPosition(i,count,mobile?Math.min(outer,.29):outer,mobile?Math.min(inner,.20):inner)}
function settleRelationshipFocus(){focusActive();requestAnimationFrame(focusActive)}

const style=document.createElement('style');
style.textContent=`
.sec-relationship-button{border:1px solid #456784;border-radius:999px;background:#122538;color:var(--text);padding:7px 11px;font:inherit;font-size:11px;cursor:pointer;white-space:nowrap}.sec-relationship-button:hover,.sec-relationship-button:focus-visible{border-color:var(--focus);outline:none}.node.relationship-root{width:190px;min-height:96px}.node.relationship-node{width:168px;min-height:76px}.node.relationship-endpoint{width:154px;min-height:72px}@media(max-width:800px){.sec-relationship-button{font-size:8px;padding:5px 6px}.node.relationship-root{width:126px;min-height:62px}.node.relationship-node,.node.relationship-endpoint{width:112px;min-height:56px}}
`;
document.head.appendChild(style);

const top=document.querySelector('.top');
const relationshipButton=document.createElement('button');
relationshipButton.id='relationshipLensBtn';
relationshipButton.className='sec-relationship-button';
relationshipButton.type='button';
if(top)top.insertBefore(relationshipButton,document.getElementById('coverageLensBtn')||document.getElementById('sourceLensBtn')||document.querySelector('.legend')||null);
function updateRelationshipButton(){const n=relationshipRecords().length;relationshipButton.textContent=`Links · ${n}`;relationshipButton.setAttribute('aria-label',`Open ${n} reviewed SecX semantic relationships`)}

window.relationshipsLayout=function(returnTo=null,focus=false){
  const records=relationshipRecords();
  const center={id:'relationships:root',title:'Reviewed Links',summary:`${records.length} relationship-specific, prototype-released semantic links.`,kind:'relationship-root',x:.5,y:.5,labels:['reviewed relationships','released prototype'],details:{rule:'Traverse only semantic relationships that have explicit relationship-level review and prototype release evidence.',why:'The relationship lens consumes the dedicated released relationship runtime artifact. It never loads the reviewer queue or infers edges from similarity, shared sources, or coverage counts.',traps:['These links supplement rather than replace the released Atlas hierarchy.','No relationship should appear here unless it exists in the released relationship artifact.'],sources:['SecX RELEASED_RELATIONSHIPS.json promotion artifact'],practice:'Choose a link to inspect its stable released endpoints and source-backed rationale.'}};
  nodes=[center];links=[];
  records.forEach((r,i)=>{const p=relationshipRadialPosition(i,records.length,.37,.23);nodes.push({id:`relationship:${r.id}`,relationshipId:r.id,title:relationTitle(r),summary:r.rationale,kind:'relationship-node',x:p.x,y:p.y,labels:[r.id,r.type,'reviewed'],details:relationDetails(r)});links.push([center.id,`relationship:${r.id}`])});
  level='relationships';relationshipId=null;parentDomain=null;parentObjective=null;active=returnTo&&nodes.some(n=>n.id===returnTo)?returnTo:'relationships:root';depth=0;render(focus);updateRelationshipButton();
};

window.relationshipHubLayout=function(id,returnTo=null,focus=false){
  const r=relationshipById(id);if(!r)return window.relationshipsLayout(null,focus);
  const centerId=`relationship:${r.id}`;
  nodes=[{id:centerId,relationshipId:r.id,title:relationTitle(r),summary:r.rationale,kind:'relationship-node',x:.5,y:.5,labels:[r.id,r.type,'reviewed'],details:relationDetails(r)}];links=[];
  const endpoints=[{role:'from',id:r.from_id,x:.22,y:.66},{role:'to',id:r.to_id,x:.78,y:.66}];
  endpoints.forEach(e=>{const o=endpointObjective(e.id),nodeId=`relationship:endpoint:${r.id}:${e.role}`;nodes.push({id:nodeId,itemId:e.id,relationshipId:r.id,endpointRole:e.role,title:endpointTitle(e.id),summary:o?.summary||`${e.role} endpoint`,kind:'relationship-endpoint',x:e.x,y:e.y,labels:[e.role,r.type,e.id],details:endpointDetails(e.id,r,e.role)});links.push([centerId,nodeId])});
  level='relationship-hub';relationshipId=r.id;parentDomain=null;parentObjective=null;active=returnTo&&nodes.some(n=>n.id===returnTo)?returnTo:centerId;depth=0;render(focus);
};

relationshipButton.addEventListener('click',()=>{window.relationshipsLayout(null,false);settleRelationshipFocus()});
const priorCrumb=crumbText;
window.crumbText=function(){if(level==='relationships')return'SecX › Reviewed Links';if(level==='relationship-hub')return`SecX › Reviewed Links › ${relationshipId}`;return priorCrumb()};
const priorDescend=descend;
window.descend=function(){
  const n=current();
  if(level==='relationships'&&n?.kind==='relationship-node'){
    const id=relationshipIdFromNode(n);
    if(id){window.relationshipHubLayout(id,null,false);focusActive();return}
  }
  if(level==='relationship-hub'&&n?.kind==='relationship-endpoint'){
    const targetId=endpointTargetFromNode(n),o=endpointObjective(targetId);
    if(o){objectiveLayout(`d${o.domain_num}`,o.id,false);focusActive();return}
    depth=Math.max(depth,2);showDetail();return;
  }
  if(level==='relationship-hub'&&n?.kind==='relationship-node'){depth=Math.max(depth,2);showDetail();return}
  return priorDescend();
};
const priorAscend=ascend;
window.ascend=function(){
  if(depth===0&&level==='relationship-hub'){window.relationshipsLayout(`relationship:${relationshipId}`,false);focusActive();return}
  if(depth===0&&level==='relationships'){domainLayout('root',false);focusActive();return}
  return priorAscend();
};

document.addEventListener('keydown',e=>{if(!document.getElementById('search')?.hidden)return;if(e.target.closest('input,textarea,select,[contenteditable="true"]'))return;if((e.key==='l'||e.key==='L')&&!e.metaKey&&!e.ctrlKey&&!e.altKey){e.preventDefault();e.stopImmediatePropagation();window.relationshipsLayout(null,false);settleRelationshipFocus()}},true);
updateRelationshipButton();
})();
