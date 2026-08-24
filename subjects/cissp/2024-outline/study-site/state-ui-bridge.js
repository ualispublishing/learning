(()=>{'use strict';
const KEY='cissp_atlas_progress_v1',DKEY='cissp_atlas_diagnostic_v1';
function read(){try{return JSON.parse(localStorage.getItem(KEY)||'{"cards":{},"quiz":{"attempts":0,"correct":0,"byDomain":{}}}')}catch{return {cards:{},quiz:{attempts:0,correct:0,byDomain:{}}}}}
function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
function localDay(){const d=new Date();return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`}
function refreshProgress(){
  const root=document.querySelector('#progressStats');if(!root)return;
  const st=read(),q=st.quiz||{},hist=q.history||[],acc=q.attempts?Math.round((q.correct||0)/q.attempts*100):null;
  const cards=[...root.querySelectorAll('.stat-card')];
  if(cards[3]){const b=cards[3].querySelector('b');if(b)b.textContent=acc===null?'—':`${acc}%`}
  root.querySelectorAll('.practice-extra-stat').forEach(x=>x.remove());
  const highWrong=hist.filter(x=>!x.ok&&x.confidence==='high').length,calibrated=hist.length,bells=st.bellringers?.attempts||0;
  [['Calibrated attempts',calibrated],['High-confidence misses',highWrong],['Bellringers',bells]].forEach(([label,value])=>{
    const div=document.createElement('div');div.className='stat-card practice-extra-stat';div.innerHTML=`<small>${esc(label)}</small><b>${esc(value)}</b>`;root.appendChild(div);
  });
}
document.querySelectorAll('[data-view="progress"]').forEach(b=>b.addEventListener('click',()=>setTimeout(refreshProgress,0)));
const exportBtn=document.querySelector('#exportBtn');
exportBtn?.addEventListener('click',e=>{
  e.preventDefault();e.stopImmediatePropagation();
  const payload={exported:new Date().toISOString(),app:window.CISSP_META?.meta||{},released_bank:window.CISSP_RELEASED_BANK_MANIFEST||null,state:read()};
  const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}),a=document.createElement('a');
  a.href=URL.createObjectURL(blob);a.download=`cissp-atlas-progress-${localDay()}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);
},{capture:true});
const resetBtn=document.querySelector('#resetBtn');
resetBtn?.addEventListener('click',e=>{
  e.preventDefault();e.stopImmediatePropagation();
  if(confirm('Reset all CISSP Atlas study progress and diagnostic state on this browser?')){
    localStorage.removeItem(KEY);localStorage.removeItem(DKEY);location.reload();
  }
},{capture:true});
})();
