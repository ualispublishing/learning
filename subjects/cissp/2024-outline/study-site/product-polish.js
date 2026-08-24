(()=>{'use strict';
const $=s=>document.querySelector(s);
const setText=(s,t)=>{const n=$(s);if(n)n.textContent=t};
const setHTML=(s,t)=>{const n=$(s);if(n)n.innerHTML=t};

// Trim product copy so the interface teaches through use instead of explaining itself.
setText('.brand span','CISSP study system');
setHTML('#today .hero h1','Study what matters.<br><span>Prove you know it.</span>');
setText('#today .hero p','Review, practice, and repair weak areas from one place.');
const coverageBtn=$('#today [data-jump="blueprint"]');if(coverageBtn)coverageBtn.textContent='Coverage map';
setText('#today .section-head h2','Study queue');

setText('#learn .page-title h1','Review');
setText('#learn .page-title p','Recall first. Reveal only what you need.');
setHTML('#learn .shortcut-help','<kbd>Space</kbd><span class="shortcut-label">Reveal</span><kbd>←</kbd><kbd>→</kbd><span class="shortcut-label">Layers</span><kbd>1–4</kbd><span class="shortcut-label">Rate</span>');
setText('#prevBtn','← Previous card');
setText('#nextBtn','Next card →');

setText('#practice .page-title h1','Practice');
setText('#practice .page-title p','Scenario questions with answer rationales.');
setText('#blueprint .page-title h1','Coverage');
setText('#blueprint .page-title p','Track every objective in the current CISSP outline.');
setText('#progress .page-title h1','Progress');
setText('#progress .page-title p','See weak areas and what to study next.');
setText('#sources .page-title h1','Sources');
setText('#sources .page-title p','Scope and reference material.');

const footerVersion=document.querySelector('footer span:last-child');if(footerVersion)footerVersion.textContent='v1.3 · local progress';

function isEditable(){
  const e=document.activeElement;
  return !!e&&(['INPUT','SELECT','TEXTAREA'].includes(e.tagName)||e.isContentEditable);
}
function learnVisible(){const v=$('#learn');return !!v&&!v.classList.contains('hidden')}
function activeLayerButton(){return $('.layer-tabs button.active')}
function moveLayer(delta){
  const current=activeLayerButton();
  if(!current)return false;
  const buttons=[...document.querySelectorAll('.layer-tabs button')];
  const i=buttons.indexOf(current),next=buttons[i+delta];
  if(!next)return false;
  next.click();
  return true;
}
function gradeWithKey(key){
  const i=Number(key)-1;
  const buttons=[...document.querySelectorAll('.rating [data-grade]')];
  if(!buttons[i])return false;
  buttons[i].click();
  return true;
}

// Capture before app.js's older bubble handler so arrows mean layers, not cards.
document.addEventListener('keydown',e=>{
  if(!learnVisible()||isEditable()||e.metaKey||e.ctrlKey||e.altKey)return;
  if(e.key===' '){
    const reveal=$('#revealBtn');
    if(!reveal)return;
    e.preventDefault();e.stopImmediatePropagation();reveal.click();return;
  }
  if(e.key==='ArrowLeft'||e.key==='ArrowRight'){
    e.preventDefault();e.stopImmediatePropagation();
    moveLayer(e.key==='ArrowRight'?1:-1);return;
  }
  if(['1','2','3','4'].includes(e.key)){
    const hasRating=document.querySelector('.rating [data-grade]');
    if(!hasRating)return;
    e.preventDefault();e.stopImmediatePropagation();gradeWithKey(e.key);
  }
},true);

function decorateShortcuts(){
  const reveal=$('#revealBtn');if(reveal){reveal.setAttribute('aria-keyshortcuts','Space');reveal.title='Space';}
  document.querySelectorAll('.rating [data-grade]').forEach((b,i)=>b.setAttribute('aria-keyshortcuts',String(i+1)));
  document.querySelectorAll('.layer-tabs button').forEach(b=>b.setAttribute('aria-keyshortcuts','ArrowLeft ArrowRight'));
}
const learn=$('#learn');if(learn)new MutationObserver(decorateShortcuts).observe(learn,{childList:true,subtree:true});decorateShortcuts();

// Keep dynamic readiness wording compact after the base renderer refreshes it.
function compactReadiness(){const b=$('#readinessCard .ready-copy b');if(b)b.textContent='Mastery'}
const readiness=$('#readinessCard');if(readiness)new MutationObserver(compactReadiness).observe(readiness,{childList:true,subtree:true});compactReadiness();
})();
