/* Kerala2040 — one evidence snapshot, one intelligible research story.
 * The actual numbers, workstreams and gate states come only from packaged QA.
 * The landscape art and Malayalam labels are cultural design, never GIS evidence. */
"use strict";
const RAW = "data/";
const REPO = "https://github.com/abhijith-sivaprasadan/kerala2040";
const $ = (selector,root=document) => root.querySelector(selector);
const $$ = (selector,root=document) => Array.from(root.querySelectorAll(selector));
const esc = value => String(value == null ? "" : value).replace(/[&<>'"]/g,
  char => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[char]));
const num = value => value == null || value === "" || typeof value === "boolean" ? null :
  Number.isFinite(Number(value)) ? Number(value) : null;
const fmt = (value,digits=1) => num(value) == null ? "—" :
  Number(value).toLocaleString("en-IN",{minimumFractionDigits:digits,maximumFractionDigits:digits});
const plain = value => String(value == null ? "" : value).replaceAll("_"," ");
const safeURL = value => {
  const s=String(value||"");
  return /^https:\/\/[a-z0-9.-]+(?::443)?\/[^\s<>"']*$/i.test(s) &&
    !/^https:\/\/[^/]*@/.test(s) ? s : "";
};
const repoEvidence = value => {
  const url=safeURL(value);
  if(url.startsWith(REPO+"/blob/main/") ||
    new RegExp("^"+REPO.replaceAll(".","\\.")+"/actions/runs/[0-9]+$").test(url))return url;
  return "";
};
const repoFile = value => {
  const path=String(value||"");
  return path && !path.includes("..") && /^[a-zA-Z0-9_./-]+$/.test(path) ?
    REPO+"/blob/main/"+path : "";
};
const state={site:null,daily:null,audit:null,ledger:null,route:"overview",month:"all",
  metric:"consumption_mu",scenario:null,theme:"kasavu",district:null,solarDistrict:null};
const gatesRequired=["ecological_capacity_ceiling","techno_economic_2040"];
const routeIds=["overview","electricity","pathways","atlas","industry","workbench","audit","data"];

async function getJSON(filename) {
  if(!/^[a-z0-9_-]+\.json$/i.test(filename))throw new Error("Unsafe bundle filename");
  const response=await fetch(RAW+filename,{cache:"no-store"});
  if(!response.ok)throw new Error("Evidence unavailable: "+filename+" HTTP "+response.status);
  return response.json();
}

function verifySnapshot(site,daily,audit,ledger) {
  if(!site || !site.metadata || !site.metadata.files || !site.baseline)throw new Error("Missing published evidence contract");
  if(!daily || !Array.isArray(daily.records) || site.baseline.rows!==daily.records.length)throw new Error("Mixed SLDC snapshots");
  if(!audit || audit.classification!=="repository_evidence_audit_not_external_source_validation" ||
     audit.finding_count!==audit.findings.length)throw new Error("Audited findings unavailable");
  if(!ledger || ledger.classification!=="dated_repository_research_progress_NOT_geospatial_or_model_readiness" ||
     ledger.audit_open_findings!==audit.open_findings)throw new Error("Mixed research audit");
  if(ledger.eligible_area_sq_km!==null || ledger.potential_mw!==null ||
     ledger.ecological_capacity_ceiling_ready!==false ||
     gatesRequired.some(key=>ledger.release_gates[key]?.passed))throw new Error("Unadmitted scientific result");
  if(site.baseline.hourly_model_calibrated!==false)throw new Error("Unproven hourly calibration");
  return true;
}

async function loadPlatformData(){
  const site=await getJSON("site-data.json");
  const f=site.metadata?.files||{};
  if(!f.daily_balance || !f.audit_readiness || !f.research_ledger)throw new Error("Incomplete published data manifest");
  const [daily,audit,ledger]=await Promise.all([
    getJSON(f.daily_balance),getJSON(f.audit_readiness),getJSON(f.research_ledger)
  ]);
  verifySnapshot(site,daily,audit,ledger);
  state.site=site;state.daily=daily;state.audit=audit;state.ledger=ledger;
  return state;
}
function labelStage(phase){
  return {validated_source:"Source QA verified · model admission separate",
    partial:"Partial evidence",blocked:"Missing critical evidence"}[phase]||"Not verified";
}
function stageClass(phase){return phase==="validated_source"?"verified":phase==="partial"?"partial":"blocked"}
function sourceTrail(item){
  return '<div class="source-links">'+(item.evidence||[]).map(link=>{
    const url=repoEvidence(link.href);
    return url?'<a href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">'+esc(link.label)+' ↗</a>':"";
  }).join("")+"</div>";
}
// The welcome is a small dismissible card, never a modal or an evidence loader.
// It runs at most once per browser session, only on the home route.
let welcomeTimer=null;
let welcomeSeenInMemory=false;
function prefersReducedMotion(){
  return Boolean(window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches);
}
function dismissWelcome(){
  const card=$("#welcomeCard");
  if(welcomeTimer!==null){clearTimeout(welcomeTimer);welcomeTimer=null}
  if(!card || card.hidden)return;
  card.classList.remove("is-open");
  if(prefersReducedMotion()){
    card.hidden=true;
    return;
  }
  card.classList.add("is-leaving");
  welcomeTimer=setTimeout(()=>{
    card.hidden=true;
    card.classList.remove("is-leaving");
    welcomeTimer=null;
  },220);
}
function showWelcome(){
  const card=$("#welcomeCard");
  if(!card || welcomeSeenInMemory || location.hash && location.hash!=="#overview" ||
     prefersReducedMotion())return false;
  try{
    if(sessionStorage.getItem("kerala2040-welcomed")==="1")return false;
    sessionStorage.setItem("kerala2040-welcomed","1");
  }catch{
    // Storage can be disabled: still never replay on later route changes.
  }
  welcomeSeenInMemory=true;
  card.hidden=false;
  card.classList.remove("is-leaving");
  card.classList.add("is-open");
  welcomeTimer=setTimeout(dismissWelcome,2400);
  return true;
}
// All line segments are measured separately: dash animation never crosses missing days.
function animateObservedPaths(root){
  if(!root || prefersReducedMotion() ||
     !document.documentElement?.classList.contains("motion-ready"))return;
  const paths=root.querySelectorAll?.(".chart-line, .viz-hydro-line, .viz-storage-line");
  if(!paths)return;
  paths.forEach((path,index)=>{
    if(typeof path.getTotalLength!=="function")return;
    const length=path.getTotalLength();
    if(!Number.isFinite(length)||length<=0)return;
    path.style.setProperty("--draw-length",(length+2).toFixed(2));
    path.style.setProperty("--draw-delay",Math.min(index,16)*28+"ms");
  });
  root.classList.add("chart-animated");
}
function animateVisibleArtwork(){
  $$(".viz-card.is-visible svg, .viz-electricity-story.is-visible svg, .viz-water-story.is-visible svg").forEach(animateObservedPaths);
  if(state.route==="electricity")animateObservedPaths($("#energyChart svg"));
}
function setupMotion(){
  if(prefersReducedMotion() || !window.IntersectionObserver)return;
  document.documentElement.classList.add("motion-ready");
  const observer=new window.IntersectionObserver(entries=>{
    entries.forEach(entry=>{
      if(entry.isIntersecting){
        entry.target.classList.add("is-visible");
        if(entry.target.matches(".viz-card, .viz-electricity-story, .viz-water-story")){
          entry.target.querySelectorAll("svg").forEach(animateObservedPaths);
        }
        observer.unobserve(entry.target);
      }
    });
  },{threshold:0.14});
  $$(".system-story, .chapter, .viz-card, .viz-electricity-story, .viz-water-story").forEach(element=>observer.observe(element));
}
function go(route){
  const target=routeIds.includes(route)?route:"overview";
  if(location.hash!=="#"+target)history.pushState(null,"","#"+target);
  showView(target);
  const heading=document.querySelector(".view.active h1");
  if(heading){heading.setAttribute("tabindex","-1");heading.focus?.({preventScroll:true});}
}
function showView(route){
  state.route=routeIds.includes(route)?route:"overview";
  if(state.route!=="overview")dismissWelcome();
  $$(".view").forEach(view=>{view.classList.toggle("active",view.dataset.view===state.route);});
  $$("[data-route]").forEach(el=>{
    const active=el.dataset.route===state.route;
    el.classList.toggle("active",active);
    if(el.closest("nav"))el.setAttribute("aria-current",active?"page":"false");
  });
  const menu=$("#mobileNav"),toggle=$("#menuToggle");
  if(menu&&toggle){menu.hidden=true;toggle.setAttribute("aria-expanded","false")}
  window.scrollTo?.({top:0,behavior:"auto"});
  if(state.route==="electricity")window.requestAnimationFrame?.(animateVisibleArtwork);
}
function bindRoutes(root=document){
  $$("[data-route]",root).forEach(button=>{
    if(button.dataset.routeBound)return;
    button.dataset.routeBound="1";
    button.addEventListener("click",event=>{event.preventDefault();go(button.dataset.route)});
  });
}
function chooseTheme(name){
  if(!["kasavu","monsoon","laterite"].includes(name))name="kasavu";
  state.theme=name;
  document.documentElement.dataset.theme=name;
  $$("[data-theme-choice]").forEach(button=>
    button.setAttribute("aria-pressed",String(button.dataset.themeChoice===name)));
  try{localStorage.setItem("kerala2040-theme",name)}catch{}
}
function bindInteractions(){
  bindRoutes();
  $("#welcomeDismiss")?.addEventListener("click",dismissWelcome);
  $$("[data-theme-choice]").forEach(button=>
    button.addEventListener("click",()=>chooseTheme(button.dataset.themeChoice)));
  $("#menuToggle")?.addEventListener("click",()=>{
    const nav=$("#mobileNav"),button=$("#menuToggle");
    nav.hidden=!nav.hidden;
    button.setAttribute("aria-expanded",String(!nav.hidden));
  });
  $("#energyMetric")?.addEventListener("change",e=>{state.metric=e.target.value;renderChart()});
  $("#energyMonth")?.addEventListener("change",e=>{state.month=e.target.value;renderChart()});
  $("#downloadObserved")?.addEventListener("click",downloadObserved);
  $("#scenarioList")?.addEventListener("click",e=>{
    const button=e.target.closest("[data-scenario]");
    if(button){state.scenario=button.dataset.scenario;renderScenario()}
  });
  $("#workbenchSearch")?.addEventListener("input",renderWorkbench);
  $("#workbenchPhase")?.addEventListener("change",renderWorkbench);
  $("#auditSearch")?.addEventListener("input",renderFindings);
  $("#auditPriority")?.addEventListener("change",renderFindings);
  $("#sourceSearch")?.addEventListener("input",renderSources);
  $("#solarDistrictChoice")?.addEventListener("change",event=>{
    state.solarDistrict=event.target.value;renderSolarDistrictDetail();
  });
  $("#districtChoice")?.addEventListener("change",event=>{
    state.district=event.target.value;renderDistrictDetail();
  });
  $("#districtOverview")?.addEventListener("click",event=>{
    const button=event.target.closest?.("[data-district]");
    if(button){state.district=button.dataset.district;renderDistrictDetail();}
  });
  $("#spatialPipeline")?.addEventListener("click",e=>{
    const button=e.target.closest("[data-layer]");
    if(!button)return;
    const id=button.dataset.layer;
    const detail=document.getElementById("layer-"+id);
    if(!detail)return;
    const expanded=button.getAttribute("aria-expanded")==="true";
    button.setAttribute("aria-expanded",String(!expanded));
    detail.hidden=expanded;
  });
  window.addEventListener("popstate",()=>showView(location.hash.slice(1)));
  window.addEventListener("hashchange",()=>showView(location.hash.slice(1)));
}
function statsHTML(items){
  return items.map(([value,label,note])=>'<div class="summary-stat"><strong>'+
    esc(value)+'</strong><span>'+esc(label)+'</span><small>'+esc(note)+'</small></div>').join("");
}

// Kerala2040 editorial charts. All coordinates come from published SLDC daily
// observations. Decorative chapters are separate; no missing day is imputed.
const monthNames=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const sumField=(rows,key)=>rows.reduce((total,row)=>total+Number(row[key]),0);
const drawMU=(mu,places=2)=>fmt(mu/1000,places)+" TWh";
function observedMonths(rows,baseline){
  const start=baseline.expected_start||"2024-04-01";
  const year=Number(start.slice(0,4)),month=Number(start.slice(5,7));
  const missing=baseline.missing_days||[];
  const groups=[];
  for(let i=0;i<12;i++){
    const date=new Date(Date.UTC(year,month-1+i,1));
    const key=date.toISOString().slice(0,7);
    const days=rows.filter(row=>row.date.slice(0,7)===key);
    const gaps=missing.filter(day=>day.slice(0,7)===key);
    const expected=new Date(Date.UTC(date.getUTCFullYear(),date.getUTCMonth()+1,0)).getUTCDate();
    const total=sumField(days,"consumption_mu"),imports=sumField(days,"net_import_interface_mu");
    const local=sumField(days,"internal_generation_mu");
    groups.push({key,label:monthNames[date.getUTCMonth()],days,gaps,expected,
      total,imports,local,mean:days.length?total/days.length:null,
      meanImports:days.length?imports/days.length:null,
      meanLocal:days.length?local/days.length:null});
  }
  return groups;
}
function drawBalanceArt(rows){
  const total=sumField(rows,"consumption_mu"),imports=sumField(rows,"net_import_interface_mu");
  const local=sumField(rows,"internal_generation_mu"),hydro=sumField(rows,"hydel_total_mu");
  if(total<=0 || ![total,imports,local,hydro].every(Number.isFinite))
    return '<p class="viz-unavailable">The observed balance is unavailable. No figure is drawn.</p>';
  const impWidth=Math.min(100,Math.max(0,imports/total*100));
  const localWidth=Math.max(0,100-impWidth);
  const hydroWidth=Math.min(100,Math.max(0,hydro/local*100));
  return '<div class="balance-lead"><span>RECORDED ELECTRICITY CONSUMPTION</span>'+
    '<strong>'+drawMU(total)+'</strong><small>'+rows.length+
    ' observed days · not a complete financial-year total</small></div>'+
    '<div class="balance-track" role="img" aria-label="Of '+drawMU(total)+
    ' recorded consumption, '+drawMU(imports)+' were net imports and '+drawMU(local)+
    ' were generated inside Kerala">'+
      '<span class="balance-import" style="width:'+impWidth.toFixed(3)+'%"></span>'+
      '<span class="balance-local" style="width:'+localWidth.toFixed(3)+'%"></span>'+
    '</div>'+
    '<div class="balance-figures">'+
      '<div><span class="viz-key import"></span><small>NET IMPORTS / INTERSTATE INTERFACES</small>'+
      '<strong>'+fmt(imports/total*100,1)+'%</strong><span>'+drawMU(imports)+'</span></div>'+
      '<div><span class="viz-key local"></span><small>GENERATED INSIDE KERALA</small>'+
      '<strong>'+fmt(local/total*100,1)+'%</strong><span>'+drawMU(local)+'</span></div></div>'+
    '<div class="balance-hydro"><div class="balance-hydro-text"><div><span class="viz-key hydro"></span>'+
      '<strong>Inside the green part: hydropower</strong></div>'+
      '<small>'+drawMU(hydro)+' · '+fmt(hydro/local*100,1)+
      '% of recorded in-state generation, not an additional source of consumption</small></div>'+
      '<div class="hydro-subtrack" role="img" aria-label="Hydro accounts for '+
      fmt(hydro/local*100,1)+' percent of observed in-state generation">'+
      '<span style="width:'+hydroWidth.toFixed(3)+'%"></span></div></div>';
}
function drawMonthlyArt(months){
  const maximum=Math.max(1,...months.map(m=>m.mean||0));
  const yBase=303,scale=204/maximum;
  const grid=[0,.25,.5,.75,1].map(frac=>{
    const y=(yBase-204*frac).toFixed(1);
    return '<line x1="76" y1="'+y+'" x2="1103" y2="'+y+'" class="viz-grid"/>'+
      '<text x="67" y="'+(Number(y)+4)+'" text-anchor="end" class="viz-axis">'+
      esc(fmt(maximum*frac,0))+'</text>';
  }).join("");
  const bars=months.map((m,i)=>{
    const x=93+i*85;
    if(m.mean===null)return '<g><title>'+esc(m.key)+': no observations</title>'+
      '<rect x="'+x+'" y="99" width="44" height="204" class="viz-empty-month"/>'+
      '<text x="'+(x+22)+'" y="321" text-anchor="middle" class="viz-month">'+
        esc(m.label)+'</text></g>';
    const a=Math.max(0,m.meanImports*scale),b=Math.max(0,m.meanLocal*scale);
    const yImp=yBase-a,yLocal=yImp-b;
    return '<g class="viz-month-column" data-month="'+esc(m.key)+'" style="--viz-delay:'+(i*65)+'ms"><title>'+esc(m.key)+': '+m.days.length+
      '/'+m.expected+' reports. Mean observed day '+fmt(m.mean,2)+
      ' MU: net imports '+fmt(m.meanImports,2)+
      ', in-state generation '+fmt(m.meanLocal,2)+
      '. Missing dates: '+(m.gaps.length?m.gaps.join(", "):"none")+'</title>'+
      '<rect x="'+x+'" y="'+yImp.toFixed(2)+'" width="44" height="'+a.toFixed(2)+
      '" class="viz-net-bar"/>'+
      '<rect x="'+x+'" y="'+yLocal.toFixed(2)+'" width="44" height="'+b.toFixed(2)+
      '" class="viz-local-bar"/>'+
      (m.gaps.length?'<path d="M'+x+' 81h44" class="viz-gap-stroke"/>'+
        '<text x="'+(x+22)+'" y="73" text-anchor="middle" class="viz-gap-label">'+
        m.gaps.length+' gap'+(m.gaps.length===1?'':'s')+'</text>':'')+
      '<text x="'+(x+22)+'" y="325" text-anchor="middle" class="viz-month">'+
        esc(m.label)+'</text>'+
      '<text x="'+(x+22)+'" y="346" text-anchor="middle" class="viz-month-count">'+
        m.days.length+'/'+m.expected+'</text></g>';
  }).join("");
  return '<div class="viz-legend"><span><i class="viz-key import"></i>Net imports</span>'+
    '<span><i class="viz-key local"></i>In-state generation</span>'+
    '<span><i class="viz-key gap"></i>Missing original report</span></div>'+
    '<div class="viz-scroll"><svg class="viz-month-svg" viewBox="0 0 1140 376" role="img" tabindex="0" '+
    'aria-label="Monthly mean observed-day electricity consumption, subdivided into net imports and in-state generation. Amber markers show missing reports." '+
    'xmlns="http://www.w3.org/2000/svg"><title>Kerala electricity mix across twelve months</title>'+
    '<desc>Height is mean observed daily consumption in MU/day. These are not complete monthly totals. Gaps are marked, not interpolated.</desc>'+
    '<text x="76" y="23" class="viz-axis">MU/day · observed daily average</text>'+
    grid+bars+'</svg></div><p class="viz-figure-note">SOURCE · SLDC FY2024–25 daily balance'+
    ' · '+months.reduce((n,m)=>n+m.days.length,0)+'/'+
    months.reduce((n,m)=>n+m.expected,0)+' dates observed'+
    ' · gold dash = unresolved daily source report</p><p class="viz-live-readout" aria-live="polite">Focus the chart and use the arrow keys or inspect any month. Missing days stay missing.</p>';
}
function drawMonthlyTable(months){
  const header='<table><thead><tr><th>Month</th><th>Days with reports</th>'+
    '<th>Consumption, mean MU/day</th><th>Net imports, mean MU/day</th>'+
    '<th>In-state, mean MU/day</th><th>Missing original dates</th></tr></thead><tbody>';
  return header+months.map(m=>'<tr><th scope="row">'+esc(m.key)+'</th>'+
    '<td>'+m.days.length+'/'+m.expected+'</td>'+
    '<td>'+fmt(m.mean,2)+'</td><td>'+fmt(m.meanImports,2)+'</td>'+
    '<td>'+fmt(m.meanLocal,2)+'</td>'+
    '<td>'+(m.gaps.length?esc(m.gaps.join(", ")):"None")+'</td></tr>').join("")+
    '</tbody></table>';
}
function drawHydroArt(rows,baseline){
  if(!rows.length)return '<p class="viz-unavailable">No recorded hydro and storage days.</p>';
  const start=Date.parse((baseline.expected_start||rows[0].date)+"T00:00:00Z");
  const end=Date.parse((baseline.expected_end||rows[rows.length-1].date)+"T00:00:00Z");
  const x=date=>74+1002*(Date.parse(date+"T00:00:00Z")-start)/Math.max(86400000,end-start);
  const highest=Math.ceil(Math.max(...rows.map(r=>Number(r.hydel_total_mu)))/5)*5||5;
  const yHydro=v=>274-165*Math.max(0,v)/highest;
  const yWater=v=>520-150*Math.max(0,Math.min(100,v))/100;
  const missing=baseline.missing_days||[];
  const segments=key=>{
    const paths=[];let part=[];
    for(let i=0;i<rows.length;i++){
      if(i && Date.parse(rows[i].date)-Date.parse(rows[i-1].date)>86400000){
        if(part.length)paths.push(part);part=[];
      }
      const y=key==="hydel_total_mu"?yHydro(Number(rows[i][key])):yWater(Number(rows[i][key]));
      part.push((part.length?'L':'M')+x(rows[i].date).toFixed(2)+','+y.toFixed(2));
    }
    if(part.length)paths.push(part);
    return paths.map(d=>'<path d="'+d.join(' ')+'" class="'+
      (key==="hydel_total_mu"?"viz-hydro-line":"viz-storage-line")+'"/>').join("");
  };
  const ticks=[0,.25,.5,.75,1].map(f=>{
    const y1=yHydro(highest*f),y2=yWater(100*f);
    return '<path d="M74 '+y1+'H1076M74 '+y2+'H1076" class="viz-grid"/>'+
      '<text x="65" y="'+(y1+4)+'" text-anchor="end" class="viz-axis">'+fmt(highest*f,0)+'</text>'+
      '<text x="65" y="'+(y2+4)+'" text-anchor="end" class="viz-axis">'+fmt(f*100,0)+'</text>';
  }).join("");
  const months=observedMonths(rows,baseline);
  const labels=months.map(m=>{
    const xx=x(m.key+"-01");
    return '<path d="M'+xx+' 98V525" class="viz-month-guide"/>'+
      '<text x="'+xx+'" y="550" class="viz-axis">'+esc(m.label)+'</text>';
  }).join("");
  const gapLines=missing.map(day=>{
    const xx=x(day).toFixed(2);
    return '<path d="M'+xx+' 96V525" class="viz-gap-guide">'+
      '<title>Missing original daily report: '+esc(day)+'</title></path>';
  }).join("");
  const tooltipDots=rows.map((day,i)=>{
    const xpoint=x(day.date).toFixed(2);
    const yr=yHydro(Number(day.hydel_total_mu)).toFixed(2);
    const ys=yWater(Number(day.storage_pct_energy_weighted)).toFixed(2);
    return '<g class="viz-data-dots"><circle cx="'+xpoint+'" cy="'+yr+
      '" r="2.2" class="viz-hydro-dot"><title>'+esc(day.date)+
      ': '+fmt(day.hydel_total_mu,2)+' MU hydro generation</title></circle>'+
      '<circle cx="'+xpoint+'" cy="'+ys+'" r="2.2" class="viz-storage-dot">'+
      '<title>'+esc(day.date)+': '+fmt(day.storage_pct_energy_weighted,2)+
      '% energy-weighted reservoir storage</title></circle></g>';
  }).join("");
  return '<div class="viz-legend"><span><i class="viz-key hydro"></i>Hydropower output · MU/day</span>'+
    '<span><i class="viz-key storage"></i>Reservoir storage · %</span>'+
    '<span><i class="viz-key gap"></i>Unobserved report date</span></div>'+
    '<div class="viz-scroll"><svg class="viz-hydro-svg" viewBox="0 0 1130 579" role="img" tabindex="0" '+
    'aria-label="Hydropower generation and energy-weighted reservoir storage through FY2024–25. Two independent units, with broken lines at eleven missing original report dates." '+
    'xmlns="http://www.w3.org/2000/svg"><title>Hydro and reservoir storage: the same observed chronology</title>'+
    '<desc>Top line shows daily hydro electricity in MU per day. Lower line shows storage percent. Missing source dates break both lines; storage is not converted to generation.</desc>'+
    '<text x="74" y="46" class="viz-panel-title">01 / ELECTRICITY FROM WATER</text>'+
    '<text x="74" y="70" class="viz-panel-subtitle">Daily hydropower generation · MU/day</text>'+
    '<text x="74" y="337" class="viz-panel-title">02 / WATER HELD IN RESERVOIRS</text>'+
    '<text x="74" y="359" class="viz-panel-subtitle">Energy-weighted reservoir storage · %</text>'+
    ticks+labels+gapLines+segments("hydel_total_mu")+
    segments("storage_pct_energy_weighted")+tooltipDots+
    '<text x="1076" y="576" text-anchor="end" class="viz-axis">FY2024–25 · observed days only</text>'+
    '</svg></div><p class="viz-figure-note">SOURCE · Kerala SLDC daily hydro output and reservoir storage'+
    ' · '+rows.length+'/'+baseline.expected_days+' reported dates'+
    ' · missing reports remain blank</p><p class="viz-live-readout" aria-live="polite">Hover, tap or use the arrow keys to inspect a dated reading. Gaps remain missing.</p>';
}
function drawHydroTable(rows){
  return '<table><thead><tr><th>Date</th><th>Hydro generation (MU/day)</th>'+
    '<th>Reservoir storage (energy-weighted %)</th></tr></thead><tbody>'+
    rows.map(row=>'<tr><th scope="row">'+esc(row.date)+'</th>'+
      '<td>'+fmt(row.hydel_total_mu,4)+'</td>'+
      '<td>'+fmt(row.storage_pct_energy_weighted,3)+'</td></tr>').join("")+
    '</tbody></table>';
}
function drawMonthlyInsight(months){
  const complete=months.filter(m=>m.days.length&&m.total>0);
  if(!complete.length)return "";
  const ranked=complete.map(m=>({key:m.key,share:m.imports/m.total*100}))
    .sort((a,b)=>a.share-b.share);
  const low=ranked[0],high=ranked[ranked.length-1];
  return '<span class="viz-insight-glyph" aria-hidden="true">↝</span>'+
    '<p><strong>The mix moves.</strong> On reported days, the share recorded as net imports '+
    'ranged from <b>'+fmt(low.share,1)+'% in '+esc(low.key)+'</b> to '+
    '<b>'+fmt(high.share,1)+'% in '+esc(high.key)+'</b>. '+
    'These are ratios of reported monthly energy, not twelve independently verified full-month totals.</p>';
}
function drawHydroInsight(rows){
  const readings=rows.filter(row=>Number.isFinite(Number(row.storage_pct_energy_weighted))&&
    Number.isFinite(Number(row.hydel_total_mu)));
  if(!readings.length)return "";
  const low=readings.reduce((a,b)=>Number(b.storage_pct_energy_weighted)<
    Number(a.storage_pct_energy_weighted)?b:a);
  return '<span class="viz-insight-glyph" aria-hidden="true">≈</span>'+
    '<p><strong>Read the two panels together, not as one unit.</strong> The lowest '+
    'recorded energy-weighted storage was <b>'+fmt(low.storage_pct_energy_weighted,1)+
    '% on '+esc(low.date)+'</b>; on that same reported date, hydro output was '+
    '<b>'+fmt(low.hydel_total_mu,2)+' MU</b>. This does not by itself establish '+
    'why generation changed.</p>';
}
function bindMonthlyReadout(box,months){
  const svg=box?.querySelector?.("svg"),readout=box?.querySelector?.(".viz-live-readout");
  if(!svg||!readout||!months.length)return;
  let current=-1;
  function display(i){
    if(i<0||i>=months.length)return;
    current=i;const m=months[i];
    readout.textContent=m.key+" · "+m.days.length+"/"+m.expected+" qualified daily reports"+
      (m.gaps.length?" · absent "+m.gaps.join(", "):" · no missing days")+
      (m.mean==null?" · no reported consumption":
        " · observed-day mean "+fmt(m.mean,2)+" MU/day · imports "+fmt(m.meanImports,2)+
        " MU/day · in-state "+fmt(m.meanLocal,2)+" MU/day");
  }
  svg.addEventListener("pointerover",e=>{
    const group=e.target.closest?.("[data-month]");
    if(group)display(months.findIndex(m=>m.key===group.dataset.month));
  });
  svg.addEventListener("click",e=>{
    const group=e.target.closest?.("[data-month]");
    if(group){display(months.findIndex(m=>m.key===group.dataset.month));svg.focus?.();}
  });
  svg.addEventListener("keydown",e=>{
    if(!["ArrowLeft","ArrowRight","Home","End"].includes(e.key))return;
    e.preventDefault();
    const i=e.key==="Home"?0:e.key==="End"?months.length-1:
      e.key==="ArrowRight"?Math.min(months.length-1,current+1):
        current<0?months.length-1:Math.max(0,current-1);
    display(i);
  });
}
function bindHydroReadout(box,rows,baseline){
  const svg=box?.querySelector?.("svg"),readout=box?.querySelector?.(".viz-live-readout");
  if(!svg||!readout||!rows.length)return;
  let current=-1;
  const start=Date.parse((baseline.expected_start||rows[0].date)+"T00:00:00Z");
  const end=Date.parse((baseline.expected_end||rows[rows.length-1].date)+"T00:00:00Z");
  const byDate=new Map(rows.map((r,i)=>[r.date,i]));
  function displayIndex(i){
    if(i<0||i>=rows.length)return;current=i;
    const r=rows[i];
    readout.textContent=r.date+" · hydel "+fmt(r.hydel_total_mu,2)+
      " MU/day · energy-weighted reservoir storage "+
      fmt(r.storage_pct_energy_weighted,2)+"% · qualified reported day";
  }
  function displayDate(date){
    if(byDate.has(date))displayIndex(byDate.get(date));
    else readout.textContent=date+" · original daily report missing; no hydro or storage value inferred.";
  }
  svg.addEventListener("pointermove",e=>{
    const bounds=svg.getBoundingClientRect?.();
    if(!bounds?.width)return;
    const xp=(e.clientX-bounds.left)*1130/bounds.width;
    if(xp<74||xp>1076)return;
    const pos=Math.max(0,Math.min(1,(xp-74)/1002));
    displayDate(new Date(start+Math.round(pos*(end-start)/86400000)*86400000).toISOString().slice(0,10));
  });
  svg.addEventListener("keydown",e=>{
    if(!["ArrowLeft","ArrowRight","Home","End"].includes(e.key))return;
    e.preventDefault();
    const i=e.key==="Home"?0:e.key==="End"?rows.length-1:
      e.key==="ArrowRight"?Math.min(rows.length-1,current+1):
        current<0?rows.length-1:Math.max(0,current-1);
    displayIndex(i);
  });
}
function renderEditorialHome(){
  if(!state.site||!state.daily)return;
  const months=observedMonths(state.daily.records,state.site.baseline);
  const balance=$("#homeBalanceArt"),year=$("#homeMonthlyArt");
  if(balance)balance.innerHTML=drawBalanceArt(state.daily.records);
  if(year){year.innerHTML=drawMonthlyArt(months);bindMonthlyReadout(year,months);}
  const homeInsight=$("#homeMonthlyInsight");
  if(homeInsight)homeInsight.innerHTML=drawMonthlyInsight(months);
  animateVisibleArtwork();
}
function renderEditorialElectricity(){
  if(!state.site||!state.daily)return;
  const rows=state.daily.records,baseline=state.site.baseline;
  const months=observedMonths(rows,baseline);
  const monthArt=$("#electricMonthlyArt"),monthTable=$("#electricMonthlyTable");
  const hydroArt=$("#hydroSeasonArt"),hydroTable=$("#hydroSeasonTable");
  if(monthArt){monthArt.innerHTML=drawMonthlyArt(months);bindMonthlyReadout(monthArt,months);}
  if(monthTable)monthTable.innerHTML=drawMonthlyTable(months);
  const monthInsight=$("#electricMonthInsight");
  if(monthInsight)monthInsight.innerHTML=drawMonthlyInsight(months);
  if(hydroArt){hydroArt.innerHTML=drawHydroArt(rows,baseline);bindHydroReadout(hydroArt,rows,baseline);}
  if(hydroTable)hydroTable.innerHTML=drawHydroTable(rows);
  const waterInsight=$("#hydroInsight");
  if(waterInsight)waterInsight.innerHTML=drawHydroInsight(rows);
  animateVisibleArtwork();
}

function renderHomepage(){
  const baseline=state.site.baseline;
  const rows=state.ledger.workstreams||[];
  const elements=[
    [fmt(baseline.aggregate_import_share*100,1)+"%","Net imports / consumption",
      "354 observed SLDC days, not a full-year annual share"],
    [fmt(baseline.rows,0)+"/"+fmt(baseline.expected_days,0),"Daily reports preserved",
      "FY2024–25 · "+fmt(baseline.missing_days_count,0)+" dates missing"],
    [fmt(baseline.hydro_generation_twh,2)+" TWh","Observed hydro generation",
      "Available days only; not a firm generation guarantee"],
    [fmt(baseline.missing_days_count,0),"Days still unverified",
      "Original as-issued reports needed; no interpolation"]
  ];
  const metrics=$("#headlineMetrics");
  if(metrics)metrics.innerHTML=elements.map(([value,label,note])=>
    '<div class="number-card"><strong>'+esc(value)+'</strong><span>'+esc(label)+
    '</span><small>'+esc(note)+'</small></div>').join("");
  const coverage=$("#heroCoverage");
  if(coverage)coverage.textContent=baseline.rows+" / "+baseline.expected_days+
    " daily reports · FY2024–25 · no measured full-year hourly series";
  const t=state.site.metadata.generated_at_utc||"";
  const origin=$("#dataOrigin");
  if(origin)origin.textContent="Observed bundle "+(t?t.slice(0,10):"undated")+
    " · Research audit "+(state.ledger.reviewed_date||"undated");
  const latest=$("#latestWindNote");
  const wind=state.ledger.wind_terrain;
  if(latest && wind){
    latest.innerHTML='<span><b>'+fmt(wind.point_centres,0)+'</b><small>NIWE Kerala resource centres</small></span>'+
      '<span><b>'+fmt(wind.speed_m_s.median,2)+' m/s</b><small>Median modelled wind, 150 m</small></span>'+
      '<span><b>'+fmt(wind.slope.finite_point_centres,0)+'</b><small>Valid slope samples · NOT sites</small></span>';
  }
  const target=$("#homeResearchLedger");
  if(target){
    const ids=["electricity","wind","boundary","lris","landslide","forest","wetlands","modelling"];
    target.innerHTML=ids.map(id=>rows.find(item=>item.id===id)).filter(Boolean)
      .map(item=>'<article class="note-row"><span>'+esc(labelStage(item.phase))+
        '</span><h3>'+esc(item.title)+'</h3><p>'+esc(item.summary)+'</p>'+
        '<div class="note-metric">'+esc(item.metric)+'<small>'+esc(item.unit)+
        '</small></div><button type="button" data-route="'+esc(item.route)+
        '">Investigate this question ↗</button></article>').join("");
    bindRoutes(target);
  }
}
function renderProvenance(){
  const s=state.site.metadata,l=state.ledger;
  const source=/^[a-f0-9]{40}$/.test(s.research_source_commit||"") ?
    s.research_source_commit : null;
  const dated=(s.generated_at_utc||"").slice(0,10)||"undated";
  const rev=source?source.slice(0,12):"unrecorded";
  const trail=$("#footerResearchIdentity");
  if(trail)trail.textContent="Research "+rev+" · Observed bundle "+dated+
    " · Audit "+(l.reviewed_date||"undated");
  const box=$("#evidenceSnapshot");
  if(box)box.innerHTML=
    '<span>Research audit reviewed <strong>'+esc(l.reviewed_date||"undated")+'</strong></span>'+
    '<span>Observed bundle published <strong>'+esc(dated)+'</strong></span>'+
    '<span>Research revision <strong>'+esc(rev)+'</strong></span>'+
    '<span>Original evidence build <strong>'+esc((s.git_sha||"unknown").slice(0,12))+'</strong></span>'+
    (source?'<a href="'+REPO+'/tree/'+source+'" target="_blank" rel="noopener noreferrer">Inspect pinned research ↗</a>':"");
}
const metrics={
  consumption_mu:["Consumption","MU/day"],
  net_import_interface_mu:["Net imports","MU/day"],
  internal_generation_mu:["In-state generation","MU/day"],
  hydel_total_mu:["Hydro generation","MU/day"]
};
function selectedDays(){
  return (state.daily?.records||[]).filter(row=>
    state.month==="all"||row.date.slice(0,7)===state.month);
}
function plotValues(rows,key){
  if(!rows.length)return '<div class="chart-empty">No observed rows for this period. No values have been interpolated.</div>';
  const values=rows.map(row=>Number(row[key]));
  if(values.some(v=>!Number.isFinite(v)))return '<div class="chart-empty">Source values unavailable; no chart interpolated.</div>';
  const t0=Date.parse(rows[0].date+"T00:00:00Z");
  const t1=Date.parse(rows[rows.length-1].date+"T00:00:00Z");
  const low=Math.min(...values),high=Math.max(...values);
  const range=Math.max(high-low,1);
  const x=(t)=>60+840*(t-t0)/Math.max(86400000,t1-t0);
  const y=(v)=>245-190*(v-low)/range;
  const segments=[];let segment=[];
  rows.forEach((row,i)=>{
    const t=Date.parse(row.date+"T00:00:00Z");
    if(i&&t-Date.parse(rows[i-1].date+"T00:00:00Z")>86400000){
      if(segment.length)segments.push(segment);segment=[];
    }
    segment.push(x(t).toFixed(2)+","+y(values[i]).toFixed(2));
  });
  if(segment.length)segments.push(segment);
  const grid=[0,.25,.5,.75,1].map(frac=>{
    const yy=245-190*frac;
    return '<line class="chart-grid" x1="60" y1="'+yy+'" x2="900" y2="'+yy+'"/>'+
      '<text class="chart-axis" x="5" y="'+(yy+4)+'">'+esc(fmt(low+range*frac,1))+'</text>';
  }).join("");
  const lines=segments.map(points=>{
    const xy=points.join(" ");
    return points.length===1?'<circle class="chart-dot" cx="'+points[0].split(",")[0]+
      '" cy="'+points[0].split(",")[1]+'" r="4"/>' :
      '<polyline class="chart-line" points="'+xy+'"/>';
  }).join("");
  const title=metrics[key]?.[0]||plain(key);
  const labels='<text class="chart-label" x="60" y="282">'+esc(rows[0].date)+'</text>'+
    '<text class="chart-label" x="900" y="282" text-anchor="end">'+esc(rows[rows.length-1].date)+'</text>';
  return '<svg viewBox="0 0 960 302" role="img" tabindex="0" aria-label="'+esc(title)+
    ', '+rows.length+' observed days. Arrow keys inspect observed dates. Breaks represent missing days." xmlns="http://www.w3.org/2000/svg">'+
    '<title>'+esc(title)+" · "+rows.length+" observed days · gaps not connected</title>"+
    grid+lines+labels+'<line class="chart-crosshair" x1="0" y1="55" x2="0" y2="245"/>'+
    '<circle class="chart-cursor" cx="0" cy="0" r="5"/></svg>'+
    '<div class="chart-readout" aria-live="off">Hover for a dated reading or focus the chart and use arrow keys. Missing days have no invented values.</div>';
}
function bindChartReadout(box,rows,key){
  const svg=box.querySelector?.("svg");
  const text=box.querySelector?.(".chart-readout");
  if(!svg||!text||!rows.length)return;
  const guides=svg.querySelectorAll(".chart-crosshair, .chart-cursor");
  const first=Date.parse(rows[0].date+"T00:00:00Z");
  const last=Date.parse(rows[rows.length-1].date+"T00:00:00Z");
  const span=Math.max(1,Math.round((last-first)/86400000));
  const dayMap=new Map(rows.map((row,index)=>[row.date,index]));
  const values=rows.map(row=>Number(row[key]));
  const low=Math.min(...values),range=Math.max(Math.max(...values)-low,1);
  let current=-1;
  function reset(){
    svg.classList.remove("has-selection");
    text.textContent="Hover for a dated reading or focus the chart and use arrow keys. Missing days have no invented values.";
  }
  function display(date,keyboard=false){
    const index=dayMap.get(date);
    text.setAttribute("aria-live",keyboard?"polite":"off");
    if(index===undefined){
      svg.classList.remove("has-selection");
      text.textContent=date+" · no verified daily report. No value interpolated.";
      return;
    }
    current=index;
    const x=60+840*(Date.parse(date+"T00:00:00Z")-first)/Math.max(86400000,last-first);
    const y=245-190*(values[index]-low)/range;
    guides[0]?.setAttribute("x1",x.toFixed(2));
    guides[0]?.setAttribute("x2",x.toFixed(2));
    guides[1]?.setAttribute("cx",x.toFixed(2));
    guides[1]?.setAttribute("cy",y.toFixed(2));
    svg.classList.add("has-selection");
    text.textContent=date+" · "+metrics[key][0]+": "+fmt(values[index],2)+" MU/day · observed SLDC report.";
  }
  svg.addEventListener("pointermove",event=>{
    const bounds=svg.getBoundingClientRect();
    if(!bounds.width)return;
    const x=(event.clientX-bounds.left)*960/bounds.width;
    if(x<60||x>900){reset();return}
    const ordinal=Math.max(0,Math.min(span,Math.round((x-60)/840*span)));
    display(new Date(first+ordinal*86400000).toISOString().slice(0,10));
  });
  svg.addEventListener("pointerleave",reset);
  svg.addEventListener("keydown",event=>{
    if(!["ArrowLeft","ArrowRight","Home","End","Escape"].includes(event.key))return;
    event.preventDefault();
    if(event.key==="Escape"){reset();return}
    const index=event.key==="Home"?0:event.key==="End"?rows.length-1:
      event.key==="ArrowRight"?Math.min(rows.length-1,current+1):
      current<0?rows.length-1:Math.max(0,current-1);
    display(rows[index].date,true);
  });
}
function renderChart(){
  const key=metrics[state.metric]?state.metric:"consumption_mu";
  const rows=selectedDays();
  const box=$("#energyChart");
  if(box){
    box.innerHTML=plotValues(rows,key);
    bindChartReadout(box,rows,key);
    if(state.route==="electricity")animateObservedPaths(box.querySelector?.("svg"));
  }
  const caption=$("#energyChartCaption");
  const gaps=(state.site.baseline.missing_days||[]).filter(date=>
    state.month==="all"||date.slice(0,7)===state.month);
  if(caption)caption.textContent=metrics[key][0]+" · "+metrics[key][1]+" · "+
    rows.length+" observed days · "+gaps.length+
    " unverified days within period. Breaks mark missing dates. Values are reported daily energy, not hourly MW.";
  const table=$("#energyTable");
  if(table)table.innerHTML='<table><thead><tr><th>Date</th><th>Consumption (MU)</th>'+
    '<th>Net imports (MU)</th><th>Internal generation (MU)</th><th>Hydro (MU)</th></tr></thead><tbody>'+
    rows.map(row=>'<tr><td>'+esc(row.date)+'</td>'+
      ["consumption_mu","net_import_interface_mu","internal_generation_mu","hydel_total_mu"]
        .map(k=>'<td>'+esc(fmt(row[k],4))+'</td>').join("")+'</tr>').join("")+
    '</tbody></table>';
}
function renderElectricity(){
  const b=state.site.baseline;
  $("#electricitySummary").innerHTML=statsHTML([
    [fmt(b.consumption_twh,2)+" TWh","Consumption","Observed days only"],
    [fmt(b.net_import_twh,2)+" TWh","Net imports","Same SLDC accounting scope"],
    [fmt(b.internal_generation_twh,2)+" TWh","In-state generation","Observed days only"],
    [fmt(b.rows,0)+"/"+fmt(b.expected_days,0),"Days with reports","Not a complete FY or hourly chronology"]
  ]);
  const month=$("#energyMonth"),months=[...new Set(state.daily.records.map(row=>row.date.slice(0,7)))];
  if(month)month.innerHTML='<option value="all">All observed dates</option>'+
    months.map(m=>'<option value="'+esc(m)+'">'+esc(m)+'</option>').join("");
  renderChart();
  const item=state.ledger.workstreams.find(x=>x.id==="electricity");
  if(item)$("#electricityResearch").innerHTML='<div class="decision-banner blocked"><strong>'+
    esc(item.title)+" · "+esc(labelStage(item.phase))+'</strong><p><b>Next:</b> '+
    esc(item.action)+'</p>'+sourceTrail(item)+'</div>';
}
function csvValue(v){
  let s=String(v==null?"":v);
  if(/^[=+@\t\r]/.test(s))s="'"+s;
  return '"'+s.replaceAll('"','""')+'"';
}
function downloadObserved(){
  const rows=selectedDays();
  const keys=["date","consumption_mu","net_import_interface_mu","internal_generation_mu","hydel_total_mu"];
  const text=["# Kerala2040 observed FY2024-25 SLDC daily series, selected period: "+state.month,
    "# Missing dates not filled. MU/day, not hourly MW.",
    keys.map(csvValue).join(","),
    ...rows.map(row=>keys.map(k=>csvValue(row[k])).join(","))].join("\r\n");
  const url=URL.createObjectURL(new Blob(["\uFEFF"+text],{type:"text/csv;charset=utf-8"}));
  const a=document.createElement("a");a.href=url;a.download="kerala2040-observed-"+state.month+".csv";
  a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function renderScenario(){
  const all=state.site.scenarios||[];
  if(!all.length){$("#scenarioDetail").textContent="Scenario specifications unavailable.";return}
  const selected=all.find(item=>item.code===state.scenario)||all[0];
  state.scenario=selected.code;
  $("#scenarioList").innerHTML=all.map(item=>
    '<button type="button" data-scenario="'+esc(item.code)+'" class="'+
    (item.code===selected.code?"selected":"")+'" aria-pressed="'+
    (item.code===selected.code)+'"><span>'+esc(item.code)+
    ' / UNSOLVED SPECIFICATION</span>'+esc(item.name)+'</button>').join("");
  $("#scenarioDetail").innerHTML='<span class="section-eyebrow">'+esc(selected.code)+
    ' / RESEARCH DESIGN</span><h3>'+esc(selected.name)+'</h3><p>'+
    esc(selected.description)+'</p><div class="spec-grid">'+
    [['Demand flexibility',selected.demand_flexibility],
      ['Ecological rule',selected.ecology_constraint],
      ['Interstate trade',selected.import_option],
      ['Modelling status',"Not solved / not calibrated"]]
      .map(([k,v])=>'<div><small>'+esc(k)+'</small><strong>'+esc(plain(v))+'</strong></div>').join("")+
    '</div><p><b>Not a prediction or a recommendation.</b> No Kerala2040 2040 capacity, cost or reliability result has been released.</p>'+
    '<button type="button" id="downloadSpecification" class="button button-dark">Download this research question ↓</button>';
  $("#downloadSpecification")?.addEventListener("click",()=>downloadSpecification(selected));
}
function downloadSpecification(s){
  const payload={classification:"unsolved_scenario_specification",hourly_model_calibrated:false,
    ecological_capacity_ceiling_ready:false,eligible_area_sq_km:null,potential_mw:null,
    source_research_commit:state.site.metadata.research_source_commit,
    evidence_build_commit:state.site.metadata.git_sha,
    scenario:s};
  const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:"application/json"}));
  const a=document.createElement("a");a.href=url;a.download="kerala2040-"+s.code+"-research-question.json";
  a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function renderPathways(){
  const g=state.ledger.release_gates.techno_economic_2040;
  $("#pathwayGate").innerHTML='<strong>2040 optimisation: '+(g.passed?"Scoped gate passed":"Not released")+
    '</strong><p>Historical chronology, economics, hydro physics, grid deliverability and ecological limits must be independently validated. None of the scenarios below is a computed Kerala2040 forecast.</p>';
  renderScenario();
  const ref=state.site.references||{};
  $("#referenceStudies").innerHTML=[
    ["cstep_2024","CSTEP 2024 / external benchmark"],
    ["kerala_cn50_2026","CN50 2026 / external benchmark"]
  ].map(([id,label])=>{
    const x=ref[id];if(!x)return "";
    const link=safeURL(x.primary_url);
    return '<article class="reference-card"><span class="section-eyebrow">'+esc(label)+
      '</span><h3>'+esc(x.title)+'</h3><small>'+esc(x.publisher)+'</small>'+
      '<p>'+esc(x.caveat||x.note||"Published external assumptions, not project results.")+'</p>'+
      (link?'<a target="_blank" rel="noopener noreferrer" href="'+esc(link)+'">Read published study ↗</a>':"")+
      '</article>';
  }).join("");
}
function renderSolarDistrictDetail(){
  const solar=state.ledger?.solar_phase1?.aggregate,box=$("#solarDistrictDetail");
  if(!solar || !box)return;
  const row=solar.districts.find(r=>r.district===state.solarDistrict)||solar.districts[0];
  if(!row){box.textContent="Original NWIC district PVOUT not available.";return;}
  state.solarDistrict=row.district;
  const picker=$("#solarDistrictChoice");
  if(picker)picker.value=row.district;
  box.innerHTML='<div class="section-eyebrow">ORIGINAL NWIC DISTRICT / PAIRED PIXELS</div>'+
    '<h3>'+esc(row.district)+'</h3>'+
    '<p>Source-grid 1999–2018 publisher reference-PV-system climatology. '+fmt(row.finite_native_source_pixel_centres,0)+
    ' native 30-arcsecond centres, with all 12 months matched; no land-area or installed-MW inference.</p>'+
    '<div class="wind-normalized-metrics">'+
    '<span><small>Source PVOUT pixels</small><strong>'+fmt(row.finite_native_source_pixel_centres,0)+
    '</strong><em>Original source centres</em></span>'+
    '<span><small>Median annual PVOUT</small><strong>'+fmt(row.median_annual_PVOUT_kWh_kWp,2)+
    '</strong><em>kWh/kWp/year</em></span>'+
    '<span><small>Median paired Feb−Jul</small><strong>'+fmt(row.median_pixelwise_Feb_minus_Jul_kWh_kWp_day,3)+
    '</strong><em>kWh/kWp/day</em></span>'+
    '<span><small>Median paired Feb→Jul decline</small><strong>'+fmt(row.median_pixelwise_Feb_to_Jul_decline_pct,2)+
    '%</strong><em>Pair each pixel before computing the median</em></span></div>'+
    '<p class="caption">This is **not** a model of new rooftop or land installations, modern-module degradation, actual FY2024–25 electricity, legal sites or grid deliverability.</p>';
}
function renderSolarPhase1(){
  const solar=state.ledger?.solar_phase1?.aggregate;
  const summary=$("#solarPhaseSummary"),picker=$("#solarDistrictChoice");
  if(!summary || !picker)return;
  if(!solar){summary.textContent="Source-audited solar phase 1 not available in this evidence snapshot.";return;}
  const a=solar.qa,v=solar.statewide;
  summary.innerHTML='<span><strong>'+fmt(v.source_pixel_centres,0)+'</strong><small>NWIC Kerala PVOUT source centres</small></span>'+
    '<span><strong>'+fmt(v.median_annual_PVOUT_kWh_kWp,2)+'</strong><small>Median annual kWh/kWp, not realized generation</small></span>'+
    '<span><strong>'+fmt(v.median_paired_Feb_to_Jul_drop_pct,2)+'%</strong><small>Paired February→July median decline</small></span>'+
    '<span><strong>'+fmt(a.inside_district_missing_any_of_14_PVOUT_layers,0)+'</strong><small>Missing among 14 within-district source layers</small></span>';
  picker.innerHTML=solar.districts.map(r=>'<option value="'+esc(r.district)+'">'+esc(r.district)+'</option>').join('');
  if(!solar.districts.some(r=>r.district===state.solarDistrict))state.solarDistrict=solar.districts[0]?.district||null;
  renderSolarDistrictDetail();
}
function renderWindTerrain(){
  const root=$("#windTerrainEvidence"),w=state.ledger.wind_terrain;
  if(!root)return;
  if(!w){root.textContent="The executed wind audit is not in this evidence snapshot.";return;}
  const h=w.speed_m_s, t=w.slope, a=w.sensitivity;
  const speedLabels=["<3","3–4","4–5","5–6","6–7","7–8","8–10","≥10"];
  const max=Math.max(...h.bin_counts);
  const histogram=h.bin_counts.map((count,i)=>
    '<div class="wind-bar-row"><span>'+esc(speedLabels[i])+'</span>'+
    '<div class="wind-bar-track"><span style="width:'+
    (100*count/max).toFixed(2)+'%"></span></div><b>'+fmt(count,0)+'</b></div>'
  ).join("");
  const table=a.matching_point_centre_counts_in_row_column_order.map((counts,i)=>
    '<tr><th scope="row">≥'+esc(a.minimum_150m_speed_m_s_inclusive[i])+' m/s</th>'+
    counts.map(count=>'<td>'+fmt(count,0)+'</td>').join("")+'</tr>'
  ).join("");
  root.innerHTML=
    '<div class="wind-stat-grid">'+
    '<div><small>INSIDE THE NWIC KERALA POLYGON</small><strong>'+fmt(w.point_centres,0)+'</strong><span>NIWE 150 m point centres</span></div>'+
    '<div><small>MEDIAN MODELLED WIND SPEED</small><strong>'+fmt(h.median,2)+' <em>m/s</em></strong><span>150 m AGL, long-term resource atlas</span></div>'+
    '<div><small>MEDIAN WIND POWER DENSITY</small><strong>'+fmt(w.wind_power_density_w_m2.median,2)+' <em>W/m²</em></strong><span>Modelled resource, not produced power</span></div>'+
    '<div><small>DSM SLOPE SAMPLES</small><strong>'+fmt(t.finite_point_centres,0)+'</strong><span>'+fmt(t.missing_point_centres,0)+' absent · median '+fmt(t.median_degrees,2)+'°</span></div>'+
    '</div>'+
    '<div class="wind-figures"><figure class="wind-histogram"><figcaption>'+
    '<span class="section-eyebrow">DISTRIBUTION 01 / SOURCE POINTS</span>'+
    '<h3>Modelled wind speed at 150 m</h3><p>Each bar counts NIWE source centres inside the original Kerala polygon, not area or turbine pads.</p></figcaption>'+
    '<div class="wind-bar-list">'+histogram+'</div><small class="wind-axis-caption">Wind-speed class (m/s) · number of point centres</small></figure>'+
    '<figure class="wind-matrix"><figcaption><span class="section-eyebrow">SENSITIVITY 02 / TERRAIN</span>'+
    '<h3>Wind speed × surface slope</h3><p>Hypothetical thresholds only. Rows are minimum wind speed; columns are maximum DSM slope. Cells are point counts with valid sampled slope.</p></figcaption>'+
    '<div class="wind-table-wrap"><table><caption>Point-centre counts by hypothetical wind-speed and GLO-90 DSM slope thresholds; not eligible sites</caption>'+
    '<thead><tr><th scope="col">Wind ≥ / slope ≤</th>'+
    a.maximum_DSM_slope_degrees_inclusive.map(deg=>'<th scope="col">'+esc(deg)+'°</th>').join("")+
    '</tr></thead><tbody>'+table+'</tbody></table></div>'+
    '<p class="wind-table-foot">Slope-available denominator: '+fmt(a.denominator_for_percentages,0)+
    ' centres. No km² or MW inferred.</p></figure></div>'+
    '<p class="caption">Source: NIWE original 150 m national CSV clipped with original NWIC Kerala polygon and joined to verified GLO-90 DSM slope; reviewed '+esc(w.reviewed_date)+'. Raw NIWE geometry and maps are not redistributed here.</p>';
}
function renderDistrictNormalized(){
  const box=$("#districtNormalized");
  const d=state.ledger?.wind_phase1?.normalized;
  if(!box)return;
  if(!d){box.textContent="Normalized descriptive sensitivity is not in this research snapshot.";return;}
  const row=d.districts.find(r=>r.district===state.district);
  if(!row){box.textContent="District not found in normalized NWIC evidence.";return;}
  const source=row.counts[2],share=row.percent_of_district_valid_slope_centres[2],
        reference=row.retention_relative_to_max20_slope_same_min_speed[2];
  box.innerHTML='<div class="section-eyebrow">NORMALIZED RESEARCH RESULT / NO MW</div>'+
    '<h3>'+esc(row.district)+': wind ≥7 m/s across illustrative DSM slope limits</h3>'+
    '<p>Percentage denominator: '+fmt(row.valid_slope_point_centres,0)+
    ' source centres with <em>finite sampled surface slope</em> in this NWIC district. '+
    fmt(row.missing_slope_point_centres,0)+
    ' missing-slope centres are reported but never treated as below the threshold.</p>'+
    '<div class="wind-normalized-metrics">'+source.map((count,i)=>
      '<span><small>DSM slope ≤'+esc(d.thresholds.maximum_DSM_surface_slope_degrees_inclusive[i])+
      '°</small><strong>'+fmt(share[i],2)+'%</strong><em>'+fmt(count,0)+
      ' point centres</em></span>').join('')+'</div>'+
    '<p class="caption">Relative to this district’s ≥7 m/s and ≤20° reference ('+
    fmt(source[3],0)+' centres), its ≤5° subset is '+
    (reference[0]===null?'undefined (empty reference)':fmt(reference[0],2)+'%')+
    '. This reference is <strong>not all windy sites</strong>, nor a land-area denominator. '+
    'Physical, statutory, land-rights, generation and grid filters remain open.</p>';
}
function renderDistrictDetail(){
  const dataset=state.ledger?.nwic_district;
  const metrics=$("#districtMetrics"),thresholds=$("#districtThresholds");
  if(!dataset || !metrics || !thresholds)return;
  const row=dataset.districts.find(x=>x.district===state.district)||dataset.districts[0];
  if(!row)return;
  state.district=row.district;
  const selection=$("#districtChoice");if(selection)selection.value=row.district;
  metrics.innerHTML='<div class="district-selected-label"><span class="section-eyebrow">DISTRICT SELECTED / ജില്ല</span>'+
    '<h3>'+esc(row.district)+'</h3><small>NWIC source-defined district, descriptive point-centre subset</small></div>'+
    '<div class="district-kpi"><strong>'+fmt(row.point_centres,0)+'</strong><span>NIWE point centres</span></div>'+
    '<div class="district-kpi"><strong>'+fmt(row.wind_speed_median_m_s,2)+' <em>m/s</em></strong><span>Median modelled wind at 150 m</span></div>'+
    '<div class="district-kpi"><strong>'+fmt(row.slope_median_degrees,2)+'°</strong><span>Median GLO-90 DSM surface slope</span></div>'+
    '<div class="district-kpi"><strong>'+fmt(row.slope_finite,0)+'</strong><span>Finite slope samples · '+fmt(row.slope_missing,0)+' missing</span></div>';
  const a=dataset.hypothetical_thresholds;
  thresholds.innerHTML='<div class="district-matrix-heading"><h3>Wind × surface slope · '+esc(row.district)+'</h3>'+
    '<p>Numbers are modelled source-point centres. Wind threshold is inclusive; slope is measured on the DSM surface, not turbine-foundation ground. This matrix cannot establish available land or wind-farm MW.</p></div>'+
    '<div class="wind-table-wrap"><table><caption>Hypothetical point-centre counts in '+esc(row.district)+
    ' · speed ≥ and slope ≤; not eligible sites</caption><thead><tr><th scope="col">Wind ≥ / slope ≤</th>'+
    a.max_DSM_surface_slope_degrees_inclusive.map(x=>'<th scope="col">'+esc(x)+'°</th>').join('')+
    '</tr></thead><tbody>'+row.threshold_matrix.map((counts,i)=>
       '<tr><th scope="row">≥'+esc(a.min_modelled_150m_wind_speed_m_s_inclusive[i])+
       ' m/s</th>'+counts.map(n=>'<td>'+fmt(n,0)+'</td>').join('')+'</tr>'
    ).join('')+'</tbody></table></div><p class="caption">Finite slope denominator: '+
    fmt(row.slope_finite,0)+' of '+fmt(row.point_centres,0)+
    ' NIWE centres. Hypothetical thresholds are not adopted engineering criteria.</p>';
  renderDistrictNormalized();
}
function renderDistrictExplorer(){
  const dataset=state.ledger?.nwic_district;
  const summary=$("#districtSourceSummary"),selector=$("#districtChoice"),overview=$("#districtOverview");
  if(!summary || !selector || !overview)return;
  if(!dataset){summary.textContent="NWIC district aggregate is not in this research snapshot.";return;}
  const a=dataset.point_assignment;
  summary.innerHTML='<span><strong>'+fmt(a.uniquely_assigned,0)+'</strong><small>Assigned NWIC source centres</small></span>'+
    '<span><strong>'+fmt(a.unassigned,0)+'</strong><small>Unassigned centres</small></span>'+
    '<span><strong>'+fmt(a.ambiguous,0)+'</strong><small>Multi-district centres</small></span>'+
    '<span><strong>'+fmt(a.slope_missing,0)+'</strong><small>Missing DSM slope samples</small></span>';
  selector.innerHTML=dataset.districts.map(x=>'<option value="'+esc(x.district)+'">'+esc(x.district)+'</option>').join('');
  if(!dataset.districts.some(x=>x.district===state.district)){
    state.district=dataset.districts[0]?.district||null;
  }
  const maxSpeed=12;
  overview.innerHTML='<table><caption>Alphabetical NWIC district comparison · NIWE resource centre counts, not available area or MW</caption>'+
    '<thead><tr><th scope="col">District</th><th scope="col">NIWE centres</th>'+
    '<th scope="col">Median wind at 150 m</th><th scope="col">Median surface slope</th></tr></thead><tbody>'+
    dataset.districts.map(x=>'<tr><th scope="row"><button type="button" data-district="'+esc(x.district)+'">'+
      esc(x.district)+' ↗</button></th><td>'+fmt(x.point_centres,0)+'</td>'+
      '<td><div class="district-speed-track" aria-hidden="true"><span style="width:'+
      Math.min(100,100*x.wind_speed_median_m_s/maxSpeed).toFixed(1)+'%"></span></div>'+
      '<strong>'+fmt(x.wind_speed_median_m_s,2)+' m/s</strong></td><td>'+
      fmt(x.slope_median_degrees,2)+'°</td></tr>'
    ).join('')+'</tbody></table>';
  renderDistrictDetail();
}
function renderLrisEvidence(){
  const box=$("#lrisEvidence"),l=state.ledger.lris;
  if(!box)return;
  if(!l){box.textContent="LRIS investigation not present in this evidence snapshot.";return;}
  const d=state.ledger.district_qa;
  const nwic=state.ledger.nwic_district;
  const districtNote=d?'<div class="decision-banner"><strong>Historic LRIS district-boundary discrepancy: '+
    fmt(d.unassigned_point_centres,0)+' NIWE centres</strong>'+
    '<p>The LRIS polygons covered '+fmt(d.unique_district_point_centres,0)+' of '+
    fmt(d.original_point_centres,0)+' original NWIC-state-clipped resource centres. '+
    (nwic?'The independently supplied original NWIC district dataset now uniquely assigns all '+
      fmt(nwic.point_assignment.uniquely_assigned,0)+
      ' points across 14 districts; zero remain unassigned. This closes the descriptive '+
      'administrative partition, <strong>not land eligibility.</strong>':
      'The LRIS residual remains unresolved until a second district source is checked.')+
    '</p><p class="caption"><a target="_blank" rel="noopener noreferrer" href="'+REPO+
    '/blob/main/docs/NIWE_LRIS_DISTRICT_PARTITION_QA_2026_09_22.md">Read historic LRIS QA ↗</a></p></div>':"";
  box.innerHTML=districtNote+'<p>LRIS advertises land use, roads, slope and waterbodies across <b>'+fmt(l.district_count,0)+
    ' districts</b>. Browser-observed district/block/local-body GeoJSON, level-based category summaries and WMS map images are useful for contextual checks. <strong>They are not the underlying native land-use vector layer.</strong></p>'+
    '<div class="lris-status"><span><b>WFS check</b><small>'+esc(l.wfs_result)+'</small></span>'+
    '<span><b>Original land-use polygons</b><small>Not acquired or independently QA-verified</small></span>'+
    '<span><b>Legal forest / ESZ / paddy</b><small>Notification-linked boundaries still missing</small></span></div>'+
    '<p class="caption">A disabled public WFS does not prove that the data cannot be supplied through another authorised route. See the <a href="'+REPO+
    '/blob/main/data/evidence/gis/lris_public_services_discovery_2026_09_22.json" target="_blank" rel="noopener noreferrer">source-scoped service inventory ↗</a>.</p>';
}
const spatialIds=["wind","boundary","lris","lulc","landslide","forest","wetlands"];
function renderAtlas(){
  const records=spatialIds.map(id=>state.ledger.workstreams.find(x=>x.id===id)).filter(Boolean);
  const box=$("#spatialPipeline");if(!box)return;
  box.innerHTML=records.map((item,i)=>
    '<section><button type="button" class="land-record" data-layer="'+esc(item.id)+
    '" aria-expanded="false" aria-controls="layer-'+esc(item.id)+'">'+
    '<span class="record-index">'+String(i+1).padStart(2,"0")+
    '<span class="record-status">'+esc(labelStage(item.phase))+'</span></span>'+
    '<h3>'+esc(item.title)+'</h3><p><b>'+esc(item.metric)+" "+esc(item.unit)+
    '</b><br>'+esc(item.summary)+'</p><span class="record-arrow" aria-hidden="true">↗</span></button>'+
    '<div class="land-detail" id="layer-'+esc(item.id)+'" hidden>'+
    '<p><b>What has been established:</b> '+esc(item.completed)+'</p>'+
    '<p><b>What has not been established:</b> '+esc(item.blocked)+'</p>'+
    '<p><b>Next verifiable step:</b> '+esc(item.action)+'</p>'+
    sourceTrail(item)+'</div></section>').join("");
}
function renderIndustry(){
  const source=state.site.circular_industry||{},cases=source.cases||{};
  const ids=["kmml","ttpl","fact","kspcb"];
  $("#industryCases").innerHTML=ids.map(id=>{
    const item=cases[id];if(!item)return "";
    const sources=Object.values(item.sources||{}).map(row=>{
      const url=safeURL(row.url);
      return url?'<a href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">'+
        esc(row.note||"Official source")+' ↗</a>':"";
    }).join("");
    return '<article class="industry-card"><span class="section-eyebrow">'+
      esc(id===source.primary_case?"SELECTED CASE / NEEDS MEASURED FLOWS":"DOCUMENTED CONTEXT / RESEARCH CANDIDATE")+
      '</span><h2>'+esc(item.organisation)+'</h2><p>'+
      esc(item.limitation||"Source-recorded operations and proposed projects are distinguished; no new recoverable quantity is inferred.")+
      '</p><h3>Potential research use</h3><p>'+
      esc((item.modelling_use||[]).map(plain).join(" · "))+
      '</p><details><summary>Official evidence trail</summary><div class="source-links">'+
      sources+'</div></details></article>';
  }).join("");
}
function renderWorkbench(){
  const l=state.ledger;
  const all=l.workstreams||[],q=($("#workbenchSearch")?.value||"").toLowerCase().trim();
  const phase=$("#workbenchPhase")?.value||"all";
  const rows=all.filter(item=>(phase==="all"||phase===item.phase) &&
    (!q||[item.id,item.title,item.summary,item.completed,item.blocked,item.action]
      .join(" ").toLowerCase().includes(q)));
  $("#workbenchSummary").innerHTML=statsHTML([
    [String(all.length),"Source-linked workstreams","Not a progress percentage"],
    [String(l.audit_open_findings),"Open acquisition findings","Some have partial or validated source QA"],
    [String(Object.values(l.release_gates).filter(g=>g.passed).length)+
      "/"+Object.keys(l.release_gates).length,"Scoped gates passed","No approved Kerala 2040 optimisation"],
    ["—","Eligible land / MW","No admitted numerical ceiling"]
  ]);
  $("#workbenchCount").textContent=rows.length+" / "+all.length+" research records shown";
  $("#workbenchCards").innerHTML=rows.length?rows.map(item=>
    '<article class="research-item"><div class="research-top"><span class="section-eyebrow">'+
    esc(item.id.toUpperCase())+'</span><span class="status '+stageClass(item.phase)+'">'+
    esc(labelStage(item.phase))+'</span></div><h2>'+esc(item.title)+'</h2><p>'+
    esc(item.summary)+'</p><div class="research-metric">'+esc(item.metric)+' <small>'+
    esc(item.unit)+'</small></div><details><summary>Read the evidence, limitation and next step</summary>'+
    '<p><b>Established:</b> '+esc(item.completed)+'</p><p><b>Unresolved:</b> '+
    esc(item.blocked)+'</p><p><b>Next:</b> '+esc(item.action)+'</p>'+
    sourceTrail(item)+'</details></article>').join("") :
    '<p>No research records match. Clear the filter to view all workstreams.</p>';
}
function renderFindings(){
  const a=state.audit;
  const q=($("#auditSearch")?.value||"").trim().toLowerCase();
  const priority=$("#auditPriority")?.value||"all";
  const found=(a.findings||[]).filter(item=>(priority==="all"||item.priority===priority)&&
    (!q||[item.id,item.acquisition,item.verification?.detail].join(" ").toLowerCase().includes(q)));
  $("#auditCount").textContent=found.length+" / "+a.finding_count+
    " tracked acquisitions · open does not mean no research has been done";
  $("#auditFindings").innerHTML=found.map(item=>{
    const v=item.verification||{},url=repoFile(v.evidence||item.evidence);
    return '<article class="finding"><small>'+esc(item.priority||"SOURCE")+' / '+
      esc(plain(item.id))+'</small><h3>'+esc(plain(item.id))+'</h3><p>'+
      esc(item.acquisition)+'</p><p>'+esc(v.detail||"Evidence remains unverified.")+'</p>'+
      '<span class="status '+(v.status==="verified_in_committed_evidence"?"verified":
      v.status==="partial_or_provisional"?"partial":"blocked")+'">'+esc(plain(v.status||"unverified"))+
      '</span> '+(url?'<a href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">Inspect committed source ↗</a>':"")+
      '</article>';
  }).join("")||'<p>No findings match these filters.</p>';
}
function renderAudit(){
  const a=state.audit;
  $("#auditSummary").innerHTML=statsHTML([
    [String(a.finding_count),"Tracked acquisition questions","As defined in committed audit"],
    [String(a.open_findings),"Open findings","Unresolved, including partial evidence"],
    [String(Object.values(a.release_gates).filter(g=>g.passed).length)+
      "/"+Object.keys(a.release_gates).length,"Scoped gates passed","Not a model completion score"],
    ["0","Published 2040 optimisations","Techno-economic gate not passed"]
  ]);
  $("#auditGates").innerHTML=Object.entries(a.release_gates||{}).map(([key,g])=>
    '<article class="gate"><span class="status '+(g.passed?"verified":"blocked")+'">'+
    (g.passed?"SCOPED PASS":"NOT PASSED")+'</span><div><h3>'+
    esc(plain(key))+'</h3><p>'+esc(g.description||"")+'</p><p>'+
    (g.blocking_checks?.length?"Outstanding: "+esc(g.blocking_checks.join(" · ")):
      "Only this explicitly scoped gate is satisfied.")+'</p></div></article>').join("");
  const p=$("#auditProvenance");
  if(p)p.textContent="Committed repository-evidence audit · archived SLDC source SHA-256 "+
    (a.source_qa_sha256||"unknown")+" · "+(a.evidence_limit||"No external source inference");
  renderFindings();
}
function sourceHome(source){
  for(const field of ["system_statistics_url","tracker","hazard_maps","open_data",
    "economic_review_2025","catalog","endpoint","home","file_api","url","storage_url"]){
    const v=safeURL(source[field]);if(v)return v;
  }
  return "";
}
function renderSources(){
  const s=state.site,files=s.metadata.files||{};
  const q=($("#sourceSearch")?.value||"").trim().toLowerCase();
  const registry=Object.entries(s.sources||{});
  const registered=registry.filter(([id,item])=>
    !q||[id,item.organisation,item.note,item.acquisition].join(" ").toLowerCase().includes(q));
  $("#sourceRegistry").innerHTML=registered.map(([id,item])=>{
    const url=sourceHome(item);
    const status=s.metadata.status[id]||{},label=status.available?
      (status.partial?"Partially acquired":"Available in bundle"):
      status.evidence==="gap"?"Missing verified evidence":"Registered reference, not confirmed acquisition";
    return '<article class="source-entry"><span class="section-eyebrow">'+esc(item.priority||"SOURCE")+
      ' / '+esc(plain(id))+'</span><h3>'+esc(item.organisation||plain(id))+'</h3><p>'+
      esc(item.note||"Source registered, acquisition and usage require verification.")+'</p>'+
      '<small>'+esc(label)+' · '+esc(plain(item.acquisition||"source link"))+'</small>'+
      (url?'<a target="_blank" rel="noopener noreferrer" href="'+esc(url)+'">Open original source ↗</a>':"")+
      '</article>';
  }).join("")||'<p>No sources match that query.</p>';
  const downloads=[["Published evidence manifest","site-data.json"],
    ["Publication metadata","metadata.json"],
    ...Object.entries(files).map(([key,name])=>[plain(key),name])];
  if(s.metadata.files.sldc_station_evidence)downloads.push(["Processed observed-day CSV archive","sldc-processed-evidence.zip"]);
  $("#downloadGrid").innerHTML=downloads.filter(([key,name])=>
    !q||(key+" "+name).toLowerCase().includes(q)).map(([key,name])=>
    '<article class="download-entry"><strong>'+esc(key)+'</strong><small>'+
    esc(name)+'</small><a href="'+RAW+encodeURIComponent(name)+'" download>Download published file ↓</a></article>').join("")||
    '<p>No published downloads match.</p>';
  $("#dataSummary").innerHTML=statsHTML([
    [String(registry.length),"Registered sources","Not all sources acquired or model-ready"],
    [String(downloads.length),"Public downloadable products","Only those allowed by publication policy"],
    [String(s.baseline.rows),"Observed SLDC daily reports","FY2024–25 subset"],
    [String(state.ledger.audit_open_findings),"Open evidence findings","Dated repository audit"]
  ]);
}
function renderAll(){
  renderHomepage();renderEditorialHome();renderProvenance();renderElectricity();renderEditorialElectricity();renderPathways();
  renderWindTerrain();renderDistrictExplorer();renderSolarPhase1();renderLrisEvidence();renderAtlas();renderIndustry();renderWorkbench();renderAudit();renderSources();
  bindRoutes();
}
async function init(){
  bindInteractions();
  showView(location.hash.slice(1)||"overview");
  showWelcome();
  setupMotion();
  try{
    await loadPlatformData();
    renderAll();
    if(typeof loadHistoricalStudy==="function")await loadHistoricalStudy(
      state.site.metadata.files.historical_electricity,state.ledger);
    if(typeof loadKMMLCase==="function")await loadKMMLCase(
      state.site.metadata.files.kmml_case);
    animateVisibleArtwork();
  }catch(err){
    console.error("Kerala2040 evidence load failed:",err);
    const box=$("#headlineMetrics");
    if(box)box.textContent="The verified evidence snapshot could not load. No figures are being shown.";
    const origin=$("#dataOrigin");
    if(origin)origin.textContent="Published data unavailable; inspect the repository instead.";
  }
}
if(typeof window!=="undefined")window.addEventListener("DOMContentLoaded",()=>{
  let theme="kasavu";try{theme=localStorage.getItem("kerala2040-theme")||theme}catch{}
  chooseTheme(theme);init();
});
