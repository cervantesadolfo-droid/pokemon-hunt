
var HUNT = (function(){
  var KEY='pokehunt_v2', N=8;
  function load(){ try{ return JSON.parse(localStorage.getItem(KEY)||'{}'); }catch(e){ return {}; } }
  function save(s){ try{ localStorage.setItem(KEY, JSON.stringify(s)); }catch(e){} }
  function pad(n){ return (n<10?'0':'')+n; }
  function fmt(ms){ ms=Math.max(0,ms|0); var s=Math.floor(ms/1000); var m=Math.floor(s/60); return pad(m)+':'+pad(s%60); }
  function caught(s){ return Object.keys(s.caught||{}).length; }
  function register(name){ var s={name:name, start:Date.now(), caught:{}}; save(s); return s; }
  function catchOne(i){ var s=load(); if(!s.start) return null; s.caught=s.caught||{}; if(!s.caught[i]) s.caught[i]=Date.now();
    if(caught(s)>=N && !s.end) s.end=Math.max.apply(null, Object.keys(s.caught).map(function(k){return s.caught[k];}));
    save(s); return s; }
  function elapsed(s){ return (s.end||Date.now())-s.start; }
  function renderProg(s){ var el=document.getElementById('prog'); if(!el) return; var h='';
    for(var i=1;i<=N;i++) h+='<span class="'+((s.caught||{})[i]?'on':'')+'">'+i+'</span>'; el.innerHTML=h;
    var b=document.getElementById('count'); if(b) b.textContent=caught(s)+' of '+N+' caught'; }
  function tick(s){ var t=document.getElementById('timer'); if(!t) return; function f(){ t.textContent=fmt(elapsed(s)); if(s.end) t.className='timer done'; } f(); if(!s.end) setInterval(f,1000); }
  function entry(s){ return btoa(unescape(encodeURIComponent(JSON.stringify({n:s.name,s:s.start,e:s.end})))); }
  return {load:load,save:save,fmt:fmt,caught:caught,register:register,catchOne:catchOne,elapsed:elapsed,renderProg:renderProg,tick:tick,entry:entry,N:N};
})();
