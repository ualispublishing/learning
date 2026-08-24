(()=>{'use strict';
function learnActive(){const el=document.getElementById('learn');return !!el&&!el.classList.contains('hidden')}
function typingTarget(){const el=document.activeElement;if(!el)return false;return el.tagName==='INPUT'||el.tagName==='TEXTAREA'||el.isContentEditable}
function clickReveal(){const b=document.getElementById('revealBtn');if(!b)return false;b.click();return true}
function moveLayer(delta){const buttons=[...document.querySelectorAll('#flashcard .layer-tabs [data-layer]')];if(!buttons.length)return false;let i=buttons.findIndex(b=>b.classList.contains('active'));if(i<0)i=0;const next=i+delta;if(next<0||next>=buttons.length)return false;buttons[next].click();return true}
function rate(n){const buttons=[...document.querySelectorAll('#flashcard .rating [data-grade]')];const b=buttons[n-1];if(!b)return false;b.click();return true}
function handle(e){
  if(!learnActive()||typingTarget()||e.metaKey||e.ctrlKey||e.altKey)return;
  let handled=false;
  if(e.code==='Space'||e.key===' '||e.key==='Spacebar')handled=clickReveal();
  else if(e.key==='ArrowLeft')handled=moveLayer(-1);
  else if(e.key==='ArrowRight')handled=moveLayer(1);
  else if(/^[1-4]$/.test(e.key))handled=rate(Number(e.key));
  if(handled){e.preventDefault();e.stopPropagation();e.stopImmediatePropagation()}
}
// Capture phase intentionally wins over the legacy app-level handler.
document.addEventListener('keydown',handle,true);
// A changed filter should not keep keyboard focus trapped on its select.
document.addEventListener('change',e=>{if(learnActive()&&e.target.matches('#learn select'))e.target.blur()});
})();
