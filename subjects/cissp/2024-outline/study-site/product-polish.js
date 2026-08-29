(()=>{'use strict';
const $=s=>document.querySelector(s);
const setText=(s,t)=>{const n=$(s);if(n)n.textContent=t};
const setHTML=(s,t)=>{const n=$(s);if(n)n.innerHTML=t};

// Final workflow overrides load after the compact product skin so the study path
// remains visible without reintroducing the older visual clutter.
if(!document.querySelector('link[data-workflow-clarity]')){
  const link=document.createElement('link');
  link.rel='stylesheet';
  link.href='workflow-clarity.css?v=1';
  link.dataset.workflowClarity='1';
  document.head.appendChild(link);
}

// Trim product copy so the interface teaches through use instead of explaining itself.
setText('.brand span','CISSP study system');
setHTML('#today .hero h1','Study what matters.<br><span>Prove you know it.</span>');
setText('#today .hero p','Review, practice, and repair weak areas from one place.');
const coverageBtn=$('#today [data-jump="blueprint"]');if(coverageBtn)coverageBtn.textContent='Coverage map';
setText('#today .section-head h2','Study queue');

setText('#learn .page-title h1','Review');
setText('#learn .page-title p','Recall first. Reveal only what you need.');
setHTML('#learn .shortcut-help','<kbd>Space</kbd><span class="shortcut-label">Reveal / hide</span><kbd>←</kbd><kbd>→</kbd><span class="shortcut-label">Cards hidden · Layers shown</span><kbd>1–4</kbd><span class="shortcut-label">Rate</span>');
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

const footerVersion=document.querySelector('footer span:last-child');if(footerVersion)footerVersion.textContent='v1.24 · local progress';

// Accessibility metadata only. Keyboard behavior lives exclusively in keyboard-shortcuts.js.
function decorateShortcuts(){
  const reveal=$('#revealBtn');if(reveal){reveal.setAttribute('aria-keyshortcuts','Space');reveal.title='Space';}
  document.querySelectorAll('.rating [data-grade]').forEach((b,i)=>b.setAttribute('aria-keyshortcuts',String(i+1)));
  document.querySelectorAll('.layer-tabs button').forEach(b=>b.setAttribute('aria-keyshortcuts','ArrowLeft ArrowRight'));
}
const learn=$('#learn');if(learn)new MutationObserver(decorateShortcuts).observe(learn,{childList:true,subtree:true});decorateShortcuts();

// Keep dynamic readiness wording compact after the base renderer refreshes it.
// Guard the write so the observer cannot trigger itself indefinitely.
function compactReadiness(){
  const b=$('#readinessCard .ready-copy b');
  if(b&&b.textContent!=='Mastery')b.textContent='Mastery';
}
const readiness=$('#readinessCard');if(readiness)new MutationObserver(compactReadiness).observe(readiness,{childList:true,subtree:true});compactReadiness();
})();
