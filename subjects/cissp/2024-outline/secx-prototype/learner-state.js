(() => {
'use strict';

const ATLAS_PROGRESS_KEY='cissp_atlas_progress_v1';
const GRAPH_STATE_KEY='cissp_secx_graph_state_v1';
const INTERVALS=[0,1,3,7,14,30,60,120];
const GRADES=['Wrong','Hard','Good','Easy'];

function safeParse(raw,fallback){try{return raw?JSON.parse(raw):fallback}catch{return fallback}}
function dayISO(d=new Date()){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`}
function addDays(n){const d=new Date();d.setHours(12,0,0,0);d.setDate(d.getDate()+n);return dayISO(d)}

let atlasState=safeParse(localStorage.getItem(ATLAS_PROGRESS_KEY),{cards:{},quiz:{attempts:0,correct:0,byDomain:{}}});
if(!atlasState.cards||typeof atlasState.cards!=='object')atlasState.cards={};
if(!atlasState.quiz||typeof atlasState.quiz!=='object')atlasState.quiz={attempts:0,correct:0,byDomain:{}};
let graphState=safeParse(localStorage.getItem(GRAPH_STATE_KEY),{nodes:{},scenarios:{}});
if(!graphState.nodes||typeof graphState.nodes!=='object')graphState.nodes={};
if(!graphState.scenarios||typeof graphState.scenarios!=='object')graphState.scenarios={};
let openNodeId=null;
let scenarioRevealSession=null;

function saveAtlas(){localStorage.setItem(ATLAS_PROGRESS_KEY,JSON.stringify(atlasState))}
function saveGraph(){localStorage.setItem(GRAPH_STATE_KEY,JSON.stringify(graphState))}
function cardState(id){return atlasState.cards[id]||null}
function isDue(id){const s=cardState(id);return !!s&&s.due<=dayISO()}
function isMature(id){const s=cardState(id);return !!s&&(s.stage||0)>=4}
function cardStatus(id){const s=cardState(id);if(!s)return'new';if(isMature(id))return'mature';return isDue(id)?'due':'learning'}
function graphNodeState(id){return graphState.nodes[id]||null}

function gradeCard(id,g){
  if(!Number.isInteger(g)||g<0||g>3)return;
  let s=cardState(id)||{stage:0,reviews:0,lapses:0};
  let stage=s.stage||0;
  if(g===0){stage=0;s.lapses=(s.lapses||0)+1}
  else if(g===1){stage=Math.max(1,stage)}
  else if(g===2){stage=Math.min(stage+1,INTERVALS.length-1)}
  else stage=Math.min(stage+2,INTERVALS.length-1);
  s.stage=stage;
  s.due=addDays(INTERVALS[stage]);
  s.reviews=(s.reviews||0)+1;
  s.last_grade=g;
  s.last_review=dayISO();
  atlasState.cards[id]=s;
  saveAtlas();
  decorateNodes();
  decorateDetail();
  updateProgressScope();
  const status=document.getElementById('status');
  if(status)status.textContent=`Graded ${id}: ${GRADES[g]}. Next review ${s.due}.`;
}

function noteDetail(n){
  if(!n||depth<=0){openNodeId=null;scenarioRevealSession=null;return}
  const now=new Date().toISOString();
  const s=graphState.nodes[n.id]||(graphState.nodes[n.id]={visits:0,maxDepth:0});
  if(openNodeId!==n.id){s.visits=(s.visits||0)+1;s.lastSeen=now;openNodeId=n.id;scenarioRevealSession=null}
  if(depth>(s.maxDepth||0)){s.maxDepth=depth;s.lastSeen=now}
  if(n.kind==='scenario'&&depth>=4&&scenarioRevealSession!==n.id){
    const p=graphState.scenarios[n.id]||(graphState.scenarios[n.id]={reveals:0});
    p.reveals=(p.reveals||0)+1;p.lastReveal=now;scenarioRevealSession=n.id;
  }
  saveGraph();
}

const style=document.createElement('style');
style.textContent=`
.node-progress{display:inline-flex;align-items:center;gap:4px;margin-top:5px;padding:2px 6px;border:1px solid #35526d;border-radius:999px;font-size:9px;color:#c8d9e8;background:#0b1d2d}
.node-progress[data-state="due"]{border-style:dashed}.node-progress[data-state="mature"]{font-weight:700}
.sec-progress{display:grid;gap:8px}.sec-progress-row{display:flex;flex-wrap:wrap;gap:7px;align-items:center}.sec-grade{border:1px solid #456784;border-radius:9px;background:#10263a;color:inherit;padding:7px 9px;cursor:pointer}.sec-grade:hover,.sec-grade:focus-visible{border-color:var(--focus);outline:none}.sec-progress small{color:var(--muted)}
`;
document.head.appendChild(style);
const legend=document.querySelector('.legend');
if(legend&&!legend.querySelector('[data-sec-grade-help]'))legend.insertAdjacentHTML('beforeend','<span data-sec-grade-help><kbd>1–4</kbd> grade card</span>');

function decorateNodes(){
  document.querySelectorAll('.node').forEach(el=>{
    el.querySelector('.node-progress')?.remove();
    const id=el.dataset.id,n=nodes.find(x=>x.id===id);if(!n)return;
    let text='',state='';
    if(n.kind==='card'){state=cardStatus(id);const s=cardState(id);text=s?`${state} · stage ${s.stage||0}`:'new'}
    else if(n.kind==='scenario'){const p=graphState.scenarios[id];if(p?.reveals){state='seen';text=`${p.reveals} answer reveal${p.reveals===1?'':'s'}`}}
    else {const p=graphNodeState(id);if(p?.maxDepth){state='seen';text=`depth ${p.maxDepth}/4`}}
    if(text){const badge=document.createElement('span');badge.className='node-progress';badge.dataset.state=state;badge.textContent=text;el.appendChild(badge)}
  });
}

function decorateDetail(){
  const panel=document.getElementById('detail'),n=current();
  panel?.querySelector('[data-sec-progress]')?.remove();
  if(!panel?.classList.contains('open')||!n||depth<=0){noteDetail(null);return}
  noteDetail(n);
  const section=document.createElement('div');section.className='section sec-progress';section.dataset.secProgress='true';
  if(n.kind==='card'){
    const s=cardState(n.id),status=cardStatus(n.id),due=s?.due||'not scheduled';
    section.innerHTML=`<h3>Atlas spaced review</h3><div class="sec-progress-row"><strong>${esc(status)}</strong><small>${s?`stage ${s.stage||0} · ${s.reviews||0} reviews · due ${esc(due)}`:'No retrieval grade yet.'}</small></div><div class="sec-progress-row">${GRADES.map((label,i)=>`<button class="sec-grade" data-sec-grade="${i}" title="Grade ${i+1}: ${label}">${i+1} · ${label}</button>`).join('')}</div><small>Uses the same progress key and review intervals as CISSP Atlas, so grading here carries into the production study view.</small>`;
    section.querySelectorAll('[data-sec-grade]').forEach(btn=>btn.addEventListener('click',()=>gradeCard(n.id,Number(btn.dataset.secGrade))));
  }else if(n.kind==='scenario'){
    const p=graphState.scenarios[n.id]||{},visits=graphNodeState(n.id)?.visits||0;
    section.innerHTML=`<h3>Practice evidence</h3><div class="sec-progress-row"><strong>${visits} visit${visits===1?'':'s'}</strong><small>${p.reveals||0} answer reveal${p.reveals===1?'':'s'} recorded locally.</small></div><small>An answer reveal is recorded as exposure only; it is not treated as a correct attempt or mastery evidence.</small>`;
  }else{
    const p=graphNodeState(n.id)||{};
    section.innerHTML=`<h3>Graph progress</h3><div class="sec-progress-row"><strong>Depth ${p.maxDepth||depth}/4</strong><small>${p.visits||1} visit${(p.visits||1)===1?'':'s'} · learner state stored separately from curriculum content.</small></div>`;
  }
  panel.appendChild(section);
  decorateNodes();
  updateProgressScope();
}

function updateProgressScope(){
  const scope=document.getElementById('scope');if(!scope)return;
  const current=scope.textContent;
  if(scope.dataset.secRendered!==current)scope.dataset.secBase=current.replace(/ · \d+ due cards$/,'');
  const base=scope.dataset.secBase||current.replace(/ · \d+ due cards$/,'');
  const dueCount=typeof retrievalCards!=='undefined'?retrievalCards.filter(c=>isDue(c.id)).length:0;
  const rendered=`${base} · ${dueCount} due cards`;
  scope.dataset.secRendered=rendered;
  if(current!==rendered)scope.textContent=rendered;
}

const scopeNode=document.getElementById('scope');
if(scopeNode)new MutationObserver(()=>requestAnimationFrame(updateProgressScope)).observe(scopeNode,{childList:true,characterData:true,subtree:true});

const baseRender=render;
window.render=function(focus=false){baseRender(focus);requestAnimationFrame(()=>{decorateNodes();updateProgressScope()})};
const baseShowDetail=showDetail;
window.showDetail=function(force=true){baseShowDetail(force);decorateDetail()};
const baseAscend=ascend;
window.ascend=function(){baseAscend();if(depth===0){openNodeId=null;scenarioRevealSession=null}requestAnimationFrame(()=>{decorateNodes();updateProgressScope()})};

document.addEventListener('keydown',e=>{
  if(!document.getElementById('search')?.hidden)return;
  if(e.target.closest('input,textarea,select,[contenteditable="true"]'))return;
  const n=current();
  if(n?.kind==='card'&&depth>0&&['1','2','3','4'].includes(e.key)){
    e.preventDefault();e.stopImmediatePropagation();gradeCard(n.id,Number(e.key)-1);
  }
},true);

addEventListener('storage',e=>{
  if(e.key===ATLAS_PROGRESS_KEY){atlasState=safeParse(e.newValue,{cards:{},quiz:{attempts:0,correct:0,byDomain:{}}});atlasState.cards=atlasState.cards||{};decorateNodes();decorateDetail();updateProgressScope()}
  if(e.key===GRAPH_STATE_KEY){graphState=safeParse(e.newValue,{nodes:{},scenarios:{}});graphState.nodes=graphState.nodes||{};graphState.scenarios=graphState.scenarios||{};decorateNodes();decorateDetail()}
});

requestAnimationFrame(()=>{decorateNodes();decorateDetail();updateProgressScope()});
})();