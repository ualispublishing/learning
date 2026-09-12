(() => {
'use strict';

const ATLAS_PROGRESS_KEY='cissp_atlas_progress_v1';
const GRAPH_STATE_KEY='cissp_secx_graph_state_v1';
const INTERVALS=[0,1,3,7,14,30,60,120];
const GRADES=['Wrong','Hard','Good','Easy'];

function safeParse(raw,fallback){try{return raw?JSON.parse(raw):fallback}catch{return fallback}}
function dayISO(d=new Date()){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`}
function addDays(n){const d=new Date();d.setHours(12,0,0,0);d.setDate(d.getDate()+n);return dayISO(d)}
function normalizeGraph(value){
  if(!value||typeof value!=='object'||Array.isArray(value))value={};
  if(!value.nodes||typeof value.nodes!=='object'||Array.isArray(value.nodes))value.nodes={};
  if(!value.scenarios||typeof value.scenarios!=='object'||Array.isArray(value.scenarios))value.scenarios={};
  return value;
}

let atlasRaw=localStorage.getItem(ATLAS_PROGRESS_KEY)||'';
let atlasState=safeParse(atlasRaw,{cards:{},quiz:{attempts:0,correct:0,byDomain:{}}});
if(!atlasState.cards||typeof atlasState.cards!=='object')atlasState.cards={};
if(!atlasState.quiz||typeof atlasState.quiz!=='object')atlasState.quiz={attempts:0,correct:0,byDomain:{}};
let graphState=normalizeGraph(safeParse(localStorage.getItem(GRAPH_STATE_KEY),{}));
let openNodeId=null;
let scenarioRevealSession=null;

function normalizeAtlas(){
  if(!atlasState||typeof atlasState!=='object')atlasState={};
  if(!atlasState.cards||typeof atlasState.cards!=='object')atlasState.cards={};
  if(!atlasState.quiz||typeof atlasState.quiz!=='object')atlasState.quiz={attempts:0,correct:0,byDomain:{}};
}
function syncAtlas(){
  const raw=localStorage.getItem(ATLAS_PROGRESS_KEY)||'';
  if(raw!==atlasRaw){atlasRaw=raw;atlasState=safeParse(raw,{cards:{},quiz:{attempts:0,correct:0,byDomain:{}}});normalizeAtlas()}
  return atlasState;
}
function saveAtlas(){atlasRaw=JSON.stringify(atlasState);localStorage.setItem(ATLAS_PROGRESS_KEY,atlasRaw)}
function saveGraph(){localStorage.setItem(GRAPH_STATE_KEY,JSON.stringify(graphState))}
function cardState(id){syncAtlas();return atlasState.cards[id]||null}
function isDue(id){const s=cardState(id);return !!s&&s.due<=dayISO()}
function isMature(id){const s=cardState(id);return !!s&&(s.stage||0)>=4}
function cardStatus(id){const s=cardState(id);if(!s)return'new';if(isMature(id))return'mature';return isDue(id)?'due':'learning'}
function graphNodeState(id){return graphState.nodes[id]||null}
function scenarioQuestion(id){return (Array.isArray(window.SECX_RELEASED_QUESTIONS)?window.SECX_RELEASED_QUESTIONS:[]).find(q=>q.id===id)||null}
function scenarioAnswerIndex(q){return Number.isInteger(q?.answer)&&Array.isArray(q.options)&&q.answer>=0&&q.answer<q.options.length?q.answer:null}
function scenarioState(id){
  let p=graphState.scenarios[id];
  if(!p||typeof p!=='object'||Array.isArray(p))p=graphState.scenarios[id]={};
  for(const key of ['reveals','attempts','scored','correct'])if(!Number.isInteger(p[key])||p[key]<0)p[key]=0;
  if(p.correct>p.scored)p.correct=p.scored;
  if(p.scored>p.attempts)p.scored=p.attempts;
  if(p.pendingAttempt&&(!Number.isInteger(p.pendingAttempt.choice)||typeof p.pendingAttempt.committedAt!=='string'))delete p.pendingAttempt;
  return p;
}

const learnerApi=Object.freeze({
  progressKey:ATLAS_PROGRESS_KEY,
  cardState(id){const s=cardState(id);return s?Object.freeze({...s}):null},
  cardStatus,
  isDue,
  isMature,
  todayISO:()=>dayISO(),
  intervalDays:Object.freeze([...INTERVALS])
});
Object.defineProperty(window,'SECX_LEARNER',{value:learnerApi,writable:false,configurable:false,enumerable:true});

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

function commitScenarioAttempt(id,choice){
  const q=scenarioQuestion(id),answer=scenarioAnswerIndex(q);
  if(!q||answer===null||!Number.isInteger(choice)||choice<0||choice>=q.options.length)return false;
  const p=scenarioState(id);
  if(p.pendingAttempt)return false;
  const now=new Date().toISOString();
  p.attempts+=1;
  p.pendingAttempt={choice,committedAt:now};
  p.lastChoice=choice;
  p.lastCommit=now;
  saveGraph();
  const status=document.getElementById('status');
  if(status)status.textContent=`Committed answer ${String.fromCharCode(65+choice)} for ${id}. Reveal depth 4 to score this attempt.`;
  return true;
}

function finalizeScenarioAttempt(id){
  const q=scenarioQuestion(id),answer=scenarioAnswerIndex(q),p=scenarioState(id),pending=p.pendingAttempt;
  if(!pending||answer===null||pending.choice<0||pending.choice>=q.options.length)return null;
  const correct=pending.choice===answer,now=new Date().toISOString();
  p.scored+=1;
  if(correct)p.correct+=1;
  p.lastChoice=pending.choice;
  p.lastOutcome=correct?'correct':'incorrect';
  p.lastScoredAt=now;
  delete p.pendingAttempt;
  saveGraph();
  const status=document.getElementById('status');
  if(status)status.textContent=`Scored committed ${id} attempt: ${correct?'Correct':'Incorrect'}. Scenario evidence remains separate from Atlas progress.`;
  return correct;
}

function noteDetail(n){
  if(!n||depth<=0){openNodeId=null;scenarioRevealSession=null;return}
  const now=new Date().toISOString();
  const s=graphState.nodes[n.id]||(graphState.nodes[n.id]={visits:0,maxDepth:0});
  if(openNodeId!==n.id){s.visits=(s.visits||0)+1;s.lastSeen=now;openNodeId=n.id;scenarioRevealSession=null}
  if(depth>(s.maxDepth||0)){s.maxDepth=depth;s.lastSeen=now}
  if(n.kind==='scenario'&&depth>=4&&scenarioRevealSession!==n.id){
    const p=scenarioState(n.id);
    p.reveals+=1;p.lastReveal=now;scenarioRevealSession=n.id;
    saveGraph();
  }
  if(n.kind==='scenario'&&depth>=4)finalizeScenarioAttempt(n.id);
  saveGraph();
}

const style=document.createElement('style');
style.textContent=`
.node-progress{display:inline-flex;align-items:center;gap:4px;margin-top:5px;padding:2px 6px;border:1px solid #35526d;border-radius:999px;font-size:9px;color:#c8d9e8;background:#0b1d2d}
.node-progress[data-state="due"]{border-style:dashed}.node-progress[data-state="mature"]{font-weight:700}
.sec-progress{display:grid;gap:8px}.sec-progress-row{display:flex;flex-wrap:wrap;gap:7px;align-items:center}.sec-grade,.sec-attempt-commit{border:1px solid #456784;border-radius:9px;background:#10263a;color:inherit;padding:7px 9px;cursor:pointer}.sec-grade:hover,.sec-grade:focus-visible,.sec-attempt-commit:hover,.sec-attempt-commit:focus-visible{border-color:var(--focus);outline:none}.sec-progress small{color:var(--muted)}.sec-attempt{display:grid;gap:7px;padding:9px;border:1px solid #35526d;border-radius:10px;background:#0b1d2d}.sec-attempt-options{display:grid;gap:5px}.sec-attempt-choice{display:flex;gap:7px;align-items:flex-start;cursor:pointer}.sec-attempt-choice input{margin-top:3px}
#detail.open{padding-top:64px}.sec-detail-actions{position:absolute;right:30px;top:28px;z-index:11;display:flex;justify-content:flex-end;gap:7px}.sec-detail-action{border:1px solid #456784;border-radius:10px;background:#10263af2;color:var(--text);padding:7px 10px;font:inherit;font-size:11px;cursor:pointer;box-shadow:0 4px 16px #0006}.sec-detail-action:hover,.sec-detail-action:focus-visible{border-color:var(--focus);outline:none}.sec-detail-actions[hidden]{display:none!important}@media(max-width:800px){#detail.open{padding-top:60px}.sec-detail-actions{right:20px;top:20px;max-width:calc(100% - 40px);gap:5px}.sec-detail-action{font-size:10px;padding:7px 9px}}
`;
document.head.appendChild(style);
const legend=document.querySelector('.legend');
if(legend&&!legend.querySelector('[data-sec-grade-help]'))legend.insertAdjacentHTML('beforeend','<span data-sec-grade-help><kbd>1–4</kbd> grade card</span>');

const main=document.querySelector('main');
const detailActions=document.createElement('div');detailActions.className='sec-detail-actions';detailActions.dataset.secDetailActions='true';detailActions.hidden=true;detailActions.setAttribute('aria-label','Detail actions');
const detailClose=document.createElement('button');detailClose.type='button';detailClose.className='sec-detail-action';detailClose.dataset.secDetailClose='true';detailClose.textContent='Close';detailClose.setAttribute('aria-label','Close detail panel (Escape action)');detailClose.setAttribute('aria-controls','detail');
const detailOpen=document.createElement('button');detailOpen.type='button';detailOpen.className='sec-detail-action';detailOpen.dataset.secDetailOpen='true';detailOpen.textContent='Open';detailOpen.setAttribute('aria-label','Open selected node (Enter action)');
const detailMore=document.createElement('button');detailMore.type='button';detailMore.className='sec-detail-action';detailMore.dataset.secDetailMore='true';
detailActions.append(detailClose,detailOpen,detailMore);if(main)main.appendChild(detailActions);

function updateDetailActions(){
  const panel=document.getElementById('detail'),n=current(),visible=!!(panel?.classList.contains('open')&&n&&depth>0);
  detailActions.hidden=!visible;
  if(!visible)return;
  detailOpen.hidden=n.id==='root';
  const nextDepth=depth%4+1;
  detailMore.textContent=`Depth ${nextDepth}/4`;
  detailMore.setAttribute('aria-label',`Show detail depth ${nextDepth} of 4 (Space action)`);
}
detailClose.addEventListener('click',()=>window.ascend());
detailOpen.addEventListener('click',()=>{const beforeLevel=level,beforeId=current()?.id;window.descend();updateDetailActions();if(level===beforeLevel&&current()?.id===beforeId&&document.querySelector('#detail.open'))detailOpen.focus()});
detailMore.addEventListener('click',()=>{depth=depth%4+1;window.showDetail();updateDetailActions();detailMore.focus()});

function decorateNodes(){
  document.querySelectorAll('.node').forEach(el=>{
    el.querySelector('.node-progress')?.remove();
    const id=el.dataset.id,n=nodes.find(x=>x.id===id);if(!n)return;
    let text='',state='';
    if(n.kind==='card'){state=cardStatus(id);const s=cardState(id);text=s?`${state} · stage ${s.stage||0}`:'new'}
    else if(n.kind==='scenario'){
      const p=graphState.scenarios[id];
      if(p?.attempts){state='attempted';text=`${p.attempts} attempt${p.attempts===1?'':'s'} · ${p.reveals||0} reveal${p.reveals===1?'':'s'}`}
      else if(p?.reveals){state='seen';text=`${p.reveals} answer reveal${p.reveals===1?'':'s'}`}
    }
    else {const p=graphNodeState(id);if(p?.maxDepth){state='seen';text=`depth ${p.maxDepth}/4`}}
    if(text){const badge=document.createElement('span');badge.className='node-progress';badge.dataset.state=state;badge.textContent=text;el.appendChild(badge)}
  });
}

function scenarioAttemptMarkup(n,p,q){
  const answer=scenarioAnswerIndex(q),pending=p.pendingAttempt,attempts=p.attempts||0,scored=p.scored||0,correct=p.correct||0;
  const summary=`${attempts} committed attempt${attempts===1?'':'s'} · ${scored} scored · ${correct} correct`;
  let controls='';
  if(answer!==null&&pending){
    const choice=q.options[pending.choice]||'';
    controls=`<div class="sec-attempt" data-sec-attempt><strong>Committed ${String.fromCharCode(65+pending.choice)}. ${esc(choice)}</strong><small>This choice is locked. Reveal depth 4 to score the committed attempt.</small></div>`;
  }else if(answer!==null&&depth<4&&scenarioRevealSession!==n.id){
    controls=`<div class="sec-attempt" data-sec-attempt><strong>Commit an answer before reveal</strong><div class="sec-attempt-options">${q.options.map((option,i)=>`<label class="sec-attempt-choice"><input type="radio" name="secx-scenario-choice" value="${i}"><span>${String.fromCharCode(65+i)}. ${esc(option)}</span></label>`).join('')}</div><button type="button" class="sec-attempt-commit" data-sec-scenario-commit>Commit answer</button><small>Commitment records the selected option only. Correctness is not recorded until layer 4 is deliberately revealed.</small></div>`;
  }else if(answer!==null){
    controls='<small>The answer has been exposed in this detail session. Close and reopen the scenario before committing another scored attempt.</small>';
  }
  const last=p.lastOutcome?`<small>Last scored attempt: <strong>${p.lastOutcome==='correct'?'Correct':'Incorrect'}</strong>. This result is scenario-attempt evidence only and does not alter Atlas review stage or mastery.</small>`:'';
  return `<div class="sec-progress-row"><strong>${summary}</strong><small>${p.reveals||0} answer reveal${p.reveals===1?'':'s'} recorded separately.</small></div>${last}${controls}`;
}

function decorateDetail(){
  const panel=document.getElementById('detail'),n=current();
  panel?.querySelector('[data-sec-progress]')?.remove();
  updateDetailActions();
  if(!panel?.classList.contains('open')||!n||depth<=0){noteDetail(null);return}
  noteDetail(n);
  const section=document.createElement('div');section.className='section sec-progress';section.dataset.secProgress='true';
  if(n.kind==='card'){
    const s=cardState(n.id),status=cardStatus(n.id),due=s?.due||'not scheduled';
    section.innerHTML=`<h3>Atlas spaced review</h3><div class="sec-progress-row"><strong>${esc(status)}</strong><small>${s?`stage ${s.stage||0} · ${s.reviews||0} reviews · due ${esc(due)}`:'No retrieval grade yet.'}</small></div><div class="sec-progress-row">${GRADES.map((label,i)=>`<button class="sec-grade" data-sec-grade="${i}" title="Grade ${i+1}: ${label}">${i+1} · ${label}</button>`).join('')}</div><small>Uses the same progress key and review intervals as CISSP Atlas, so grading here carries into the production study view.</small>`;
    section.querySelectorAll('[data-sec-grade]').forEach(btn=>btn.addEventListener('click',()=>gradeCard(n.id,Number(btn.dataset.secGrade))));
  }else if(n.kind==='scenario'){
    const p=scenarioState(n.id),visits=graphNodeState(n.id)?.visits||0,q=scenarioQuestion(n.id);
    section.innerHTML=`<h3>Practice evidence</h3><div class="sec-progress-row"><strong>${visits} visit${visits===1?'':'s'}</strong><small>${p.reveals||0} answer reveal${p.reveals===1?'':'s'} recorded locally.</small></div><small>An answer reveal is exposure only unless a choice was explicitly committed first; reveal alone never creates correctness or mastery evidence.</small>${q?scenarioAttemptMarkup(n,p,q):'<small>Released scenario data is unavailable for answer commitment.</small>'}`;
    const commit=section.querySelector('[data-sec-scenario-commit]');
    if(commit)commit.addEventListener('click',()=>{
      const selected=section.querySelector('input[name="secx-scenario-choice"]:checked'),status=document.getElementById('status');
      if(!selected){if(status)status.textContent=`Choose an option before committing ${n.id}.`;return}
      if(commitScenarioAttempt(n.id,Number(selected.value))){decorateDetail();requestAnimationFrame(()=>detailMore.focus())}
    });
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
window.render=function(focus=false){baseRender(focus);requestAnimationFrame(()=>{decorateNodes();updateProgressScope();updateDetailActions()})};
const baseShowDetail=showDetail;
window.showDetail=function(force=true){baseShowDetail(force);decorateDetail()};
const baseAscend=ascend;
window.ascend=function(){baseAscend();if(depth===0){openNodeId=null;scenarioRevealSession=null}updateDetailActions();requestAnimationFrame(()=>{decorateNodes();updateProgressScope();updateDetailActions()})};

document.addEventListener('keydown',e=>{
  if(!document.getElementById('search')?.hidden)return;
  if(e.target.closest('input,textarea,select,[contenteditable="true"]'))return;
  const n=current();
  if(n?.kind==='card'&&depth>0&&['1','2','3','4'].includes(e.key)){
    e.preventDefault();e.stopImmediatePropagation();gradeCard(n.id,Number(e.key)-1);
  }
},true);

addEventListener('storage',e=>{
  if(e.key===ATLAS_PROGRESS_KEY){atlasRaw='__stale__';syncAtlas();decorateNodes();decorateDetail();updateProgressScope()}
  if(e.key===GRAPH_STATE_KEY){graphState=normalizeGraph(safeParse(e.newValue,{}));decorateNodes();decorateDetail()}
});

requestAnimationFrame(()=>{decorateNodes();decorateDetail();updateProgressScope();updateDetailActions()});
})();
