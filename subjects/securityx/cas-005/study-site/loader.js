(async()=>{
  try{
    const b64=(window.SX_PAYLOAD_PARTS||[]).join('');
    if(!b64) throw new Error('Study data payload is missing.');
    const bytes=Uint8Array.from(atob(b64),c=>c.charCodeAt(0));
    if(typeof DecompressionStream==='undefined') throw new Error('This browser does not support the built-in gzip decompressor required by this static site. Use a current Chrome, Edge, Firefox, or Safari.');
    const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
    const text=await new Response(stream).text();
    const d=JSON.parse(text);
    window.SX_DECK=d.deck;
    window.SX_QUESTIONS=d.questions;
    window.SX_PBQS=d.pbqs;
    window.SX_BLUEPRINT=d.blueprint;
    window.SX_SOURCES=d.sources;
    const script=document.createElement('script');
    script.src='app.js';
    script.onerror=()=>{throw new Error('Failed to load app.js');};
    document.body.appendChild(script);
  }catch(err){
    console.error(err);
    const el=document.getElementById('stats')||document.body;
    el.innerHTML=`<div class="notice"><strong>Study site failed to load.</strong><br>${String(err.message||err)}</div>`;
  }
})();
