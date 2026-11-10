const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let io=null;

/* ---------- left rail: "On this page" from the section headings of the open tab ---------- */
function rail(k){
  const p=$(`.panel[data-tab="${k}"]`); const secs=[...p.querySelectorAll('section.sec')].filter(s=>s.querySelector('h2'));
  $('#rail').innerHTML=`<p class="lbl">On this page</p>`+secs.map(s=>`<a href="#${s.id}" data-id="${s.id}">${esc(s.querySelector('h2').textContent)}</a>`).join('')+`<a class="totop" href="#top">&uarr; Back to top</a>`;
  $$('#rail a[data-id]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();const t=document.getElementById(a.dataset.id);t&&t.scrollIntoView({behavior:'smooth',block:'start'})}));
  $('#rail .totop').addEventListener('click',e=>{e.preventDefault();window.scrollTo({top:0,behavior:'smooth'})});
  if(io) io.disconnect();
  if('IntersectionObserver' in window){io=new IntersectionObserver(es=>es.forEach(en=>{if(en.isIntersecting)$$('#rail a[data-id]').forEach(a=>a.classList.toggle('cur',a.dataset.id===en.target.id))}),{rootMargin:'-35% 0px -55% 0px'});secs.forEach(s=>io.observe(s))}
}

/* ---------- tabs ---------- */
function showTab(k,keep){
  if(!$(`.panel[data-tab="${k}"]`)) k=$('.panel').dataset.tab;
  $$('.panel').forEach(p=>p.classList.toggle('on',p.dataset.tab===k));
  $$('#tabs .tab').forEach(b=>b.setAttribute('aria-selected',b.dataset.tab===k?'true':'false'));
  const cur=$(`#tabs .tab[data-tab="${k}"]`); if(cur&&cur.scrollIntoView) cur.scrollIntoView({block:'nearest',inline:'nearest'});
  rail(k); if(!keep) window.scrollTo(0,0);
  if(history.replaceState) history.replaceState(null,'','#'+k);
}
/* jump to any element id: a tab key, a section, a slot or a register item */
function goAnchor(id){
  if($(`.panel[data-tab="${id}"]`)){showTab(id);return false}
  const t=document.getElementById(id); if(!t) return false;
  const p=t.closest('.panel'); if(p) showTab(p.dataset.tab,true);
  if(t.tagName==='DETAILS') t.open=true;
  setTimeout(()=>{t.scrollIntoView({behavior:'smooth',block:'start'});t.classList.add('flash');setTimeout(()=>t.classList.remove('flash'),1700)},40);
  return false;
}
function goItem(id){return goAnchor('ri-'+id)}
window.showTab=showTab; window.goAnchor=goAnchor; window.goItem=goItem;
$$('#tabs .tab').forEach(b=>b.addEventListener('click',()=>showTab(b.dataset.tab)));

/* ---------- register: search and facet filters ---------- */
$$('[data-reg]').forEach(root=>{
  const q=root.querySelector('.rg-q'), n=root.querySelector('.rg-n'), rows=[...root.querySelectorAll('.ri')], state={};
  function apply(){
    const term=(q.value||'').trim().toLowerCase(); let shown=0;
    rows.forEach(r=>{
      let ok=Object.entries(state).every(([f,set])=>!set.size||set.has(r.dataset[f]));
      if(ok&&term) ok=r.textContent.toLowerCase().includes(term);
      r.hidden=!ok; if(ok) shown++;
    });
    n.textContent=`${shown} of ${rows.length} shown`;
  }
  root.querySelectorAll('.rg-chip').forEach(c=>c.addEventListener('click',()=>{
    const f=c.dataset.f, v=c.dataset.v; (state[f]=state[f]||new Set());
    if(state[f].has(v)){state[f].delete(v);c.classList.remove('on')}else{state[f].add(v);c.classList.add('on')}
    c.setAttribute('aria-pressed',c.classList.contains('on')?'true':'false'); apply();
  }));
  q.addEventListener('input',apply); apply();
});

/* ---------- ?check lists the placeholders still to fill, by tab and by owner ---------- */
const qs=new URLSearchParams(location.search);
if(qs.has('check')){
  const byTab={}, byOwner={};
  $$('.panel').forEach(p=>p.querySelectorAll('.ph,.skel').forEach(x=>{
    byTab[p.dataset.tab]=(byTab[p.dataset.tab]||0)+1;
    const o=(x.dataset.owner||(x.closest('.slot')||{}).dataset?.owner||'Unassigned'); byOwner[o]=(byOwner[o]||0)+1;
  }));
  const total=Object.values(byTab).reduce((a,b)=>a+b,0); const bar=$('#checkbar'); bar.hidden=false;
  bar.innerHTML=total
    ?`<b>${total} placeholders to fill.</b> By tab: `+Object.entries(byTab).map(([k,v])=>`<button type="button" onclick="showTab('${k}')">${esc($(`#tabs .tab[data-tab="${k}"] .tl`).textContent)} (${v})</button>`).join(' ')
      +`<br><b>By owner:</b> `+Object.entries(byOwner).map(([o,v])=>`${esc(o)} (${v})`).join(' · ')
    :'<b>No placeholders left.</b> The hub is ready to hand over.';
  bar.innerHTML+=' <button type="button" aria-label="Hide this bar" onclick="this.parentNode.hidden=true">Hide</button>';
}
const start=(location.hash||'').slice(1);
if(start && !$(`.panel[data-tab="${start}"]`) && document.getElementById(start)){showTab($('.panel').dataset.tab);goAnchor(start)} else showTab(start||$('.panel').dataset.tab);
