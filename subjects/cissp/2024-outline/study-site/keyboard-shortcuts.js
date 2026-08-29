(()=>{'use strict';
const VERSION='4';
function learnActive(){const el=document.getElementById('learn');return !!el&&!el.classList.contains('hidden')}
function typingTarget(){const el=document.activeElement;if(!el)return false;return el.tagName==='INPUT'||el.tagName==='TEXTAREA'||el.isContentEditable}
function clickReveal(){const b=document.getElementById('revealBtn');if(!b)return false;b.click();return true}
function hideAnswer(){
  if(!document.querySelector('#flashcard .layer-tabs [data-layer]'))return false;
  const prev=document.getElementById('prevBtn'),next=document.getElementById('nextBtn');
  if(!prev||!next)return false;
  // The core app resets reveal state whenever cards change. Round-trip one card so
  // the same card returns to its retrieval gate without reaching into app internals.
  prev.click();next.click();
  return !!document.getElementById('revealBtn');
}
function toggleReveal(){return document.getElementById('revealBtn')?clickReveal():hideAnswer()}
function moveLayer(delta){const buttons=[...document.querySelectorAll('#flashcard .layer-tabs [data-layer]')];if(!buttons.length)return false;let i=buttons.findIndex(b=>b.classList.contains('active'));if(i<0)i=0;const next=i+delta;if(next<0||next>=buttons.length)return false;buttons[next].click();return true}
function moveCard(delta){const b=document.getElementById(delta>0?'nextBtn':'prevBtn');if(!b)return false;b.click();return true}
function rate(n){const b=document.querySelector(`#flashcard .rating [data-grade="${n-1}"]`)||[...document.querySelectorAll('#flashcard .rating [data-grade]')][n-1];if(!b)return false;b.click();return true}
function consume(e){e.preventDefault();e.stopPropagation();e.stopImmediatePropagation()}
function handle(e){
  if(!learnActive()||typingTarget()||e.metaKey||e.ctrlKey||e.altKey)return;
  if(e.code==='Space'||e.key===' '||e.key==='Spacebar'){
    consume(e);toggleReveal();return;
  }
  if(e.key==='ArrowLeft'||e.key==='ArrowRight'){
    consume(e);
    const delta=e.key==='ArrowRight'?1:-1;
    if(document.querySelector('#flashcard .layer-tabs [data-layer]'))moveLayer(delta);
    else moveCard(delta);
    return;
  }
  if(/^[1-4]$/.test(e.key)){
    consume(e);rate(Number(e.key));return;
  }
}
// Window capture runs before the legacy document-level listener. Hidden cards use
// arrows for previous/next navigation; revealed cards use them for learning layers.
window.addEventListener('keydown',handle,true);
document.addEventListener('change',e=>{if(learnActive()&&e.target.matches('#learn select'))e.target.blur()});
document.documentElement.dataset.learnShortcuts=VERSION;
})();
