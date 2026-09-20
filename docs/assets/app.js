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
  metric:"consumption_mu",scenario:null,theme:"kasavu"};
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
  return {validated_source:"Source coverage verified · model gate open",
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
function setupMotion(){
  if(prefersReducedMotion() || !window.IntersectionObserver)return;
  document.documentElement.classList.add("motion-ready");
  const observer=new window.IntersectionObserver(entries=>{
    entries.forEach(entry=>{
      if(entry.isIntersecting){
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  },{threshold:0.14});
  $(".system-story, .chapter").forEach(element=>observer.observe(element));
}
function go(route){
  const target=routeIds.includes(route)?route:"overview";
  if(location.hash!=="#"+target)history.pushState(null,"","#"+target);
  showView(target);
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
  window.scrollTo?.({top:0,behavior:"instant"});
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
  $("[data-theme-choice]").forEach(button=>
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
  const target=$("#homeResearchLedger");
  if(target){
    const ids=["electricity","boundary","landslide","forest","wetlands","modelling"];
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
  return '<svg viewBox="0 0 960 302" role="img" aria-label="'+esc(title)+
    ', '+rows.length+' observed days. Breaks represent missing days." xmlns="http://www.w3.org/2000/svg">'+
    '<title>'+esc(title)+" · "+rows.length+" observed days · gaps not connected</title>"+
    grid+lines+labels+'</svg>';
}
function renderChart(){
  const key=metrics[state.metric]?state.metric:"consumption_mu";
  const rows=selectedDays();
  const box=$("#energyChart");if(box)box.innerHTML=plotValues(rows,key);
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
const spatialIds=["boundary","lulc","landslide","forest","wetlands"];
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
  renderHomepage();renderProvenance();renderElectricity();renderPathways();
  renderAtlas();renderIndustry();renderWorkbench();renderAudit();renderSources();
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
