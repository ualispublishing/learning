(()=>{'use strict';
const VERSION='3';
function learnActive(){const el=document.getElementById('learn');return !!el&&!el.classList.contains('hidden')}
function typingTarget(){const el=document.activeElement;if(!el)return false;return el.tagName==='INPUT'||el.tagName==='TEXTAREA'||el.isContentEditable}
function clickReveal(){const b=document.getElementById('revealBtn');if(!b)return false;b.click();return true}
function moveLayer(delta){const buttons=[...document.querySelectorAll('#flashcard .layer-tabs [data-layer]')];if(!buttons.length)return false;let i=buttons.findIndex(b=>b.classList.contains('active'));if(i<0)i=0;const next=i+delta;if(next<0||next>=buttons.length)return false;buttons[next].click();return true}
function rate(n){const b=document.querySelector(`#flashcard .rating [data-grade="${n-1}"]`)||[...document.querySelectorAll('#flashcard .rating [data-grade]')][n-1];if(!b)return false;b.click();return true}
function consume(e){e.preventDefault();e.stopPropagation();e.stopImmediatePropagation()}
function handle(e){
  if(!learnActive()||typingTarget()||e.metaKey||e.ctrlKey||e.altKey)return;
  if(e.code==='Space'||e.key===' '||e.key==='Spacebar'){
    consume(e);clickReveal();return;
  }
  if(e.key==='ArrowLeft'||e.key==='ArrowRight'){
    consume(e);moveLayer(e.key==='ArrowRight'?1:-1);return;
  }
  if(/^[1-4]$/.test(e.key)){
    consume(e);rate(Number(e.key));return;
  }
}
// Window capture runs before the legacy document-level listener. Learn shortcuts are
// always consumed, even before reveal or at layer boundaries, so arrows cannot fall
// through to previous/next-card navigation.
window.addEventListener('keydown',handle,true);
document.addEventListener('change',e=>{if(learnActive()&&e.target.matches('#learn select'))e.target.blur()});
document.documentElement.dataset.learnShortcuts=VERSION;
})();
