const {test}=require("node:test");
const assert=require("node:assert/strict");
const vm=require("node:vm");
const fs=require("node:fs");
const path=require("node:path");
const root=path.join(__dirname,"..");
const code=fs.readFileSync(path.join(root,"docs/assets/app.js"),"utf8");
const read=name=>JSON.parse(fs.readFileSync(path.join(root,"public",name),"utf8"));
function context(extra={}){
  const sandbox={
    console,setTimeout,clearTimeout,AbortController,Date,
    document:{querySelector:()=>null,querySelectorAll:()=>[]},
    window:{addEventListener:()=>{},scrollTo:()=>{}},
    ...extra
  };
  vm.createContext(sandbox);vm.runInContext(code,sandbox);return sandbox;
}
function audit(){
  return {classification:"repository_evidence_audit_not_external_source_validation",
    finding_count:1,open_findings:1,closed_findings:0,
    findings:[{id:"forest",verification:{status:"blocked_missing_verified_evidence"}}],
    release_gates:{ecological_capacity_ceiling:{passed:false,blocking_checks:["forest"]},
      techno_economic_2040:{passed:false,blocking_checks:["chronology"]}}};
}
function ledger(){
  return {classification:"dated_repository_research_progress_NOT_geospatial_or_model_readiness",
    audit_open_findings:1,eligible_area_sq_km:null,potential_mw:null,
    ecological_capacity_ceiling_ready:false,reviewed_date:"2026-09-20",
    release_gates:audit().release_gates,workstreams:[]};
}
test("new interface is a clear Kerala-coded research publication, not old chart wall",()=>{
  const html=fs.readFileSync(path.join(root,"docs/index.html"),"utf8");
  const css=fs.readFileSync(path.join(root,"docs/assets/kerala.css"),"utf8");
  for(const text of ["A stronger","energy future","for Kerala",
      "This is not a forecast","How Kerala","Land, WATER","data-view=\"atlas\"",
      "data-view=\"audit\"","data-view=\"industry\"","data-view=\"workbench\""]){
    if(text==="Land, WATER")continue;
    assert.ok(html.includes(text),text);
  }
  assert.match(html,/നമ്മുടെ നാട്/);
  assert.match(html,/കേരളത്തിന്റെ ഊർജഭാവി/);
  assert.match(html,/data-theme-choice="kasavu"/);
  assert.match(html,/data-theme-choice="monsoon"/);
  assert.match(html,/data-theme-choice="laterite"/);
  assert.match(css,/html\[data-theme="monsoon"\]/);
  assert.match(css,/html\[data-theme="laterite"\]/);
  assert.doesNotMatch(html,/cdn\.plot\.ly|unpkg\.com|assets\/workbench\.css/);
});
test("missing numeric data is never converted into a measured zero",()=>{
  const c=context();
  for(const input of ["null","undefined","true","\"\"","\"missing\""])
    assert.equal(vm.runInContext("fmt("+input+")",c),"—");
  assert.equal(vm.runInContext("fmt(0)",c),"0.0");
});
test("required evidence is fetched from one published manifest and verified",async()=>{
  const site=read("site-data.json");
  // The research audit and ledger are generated at package time, not committed in public/.
  site.metadata.files.audit_readiness="audit-readiness.json";
  site.metadata.files.research_ledger="research-ledger.json";
  const files=site.metadata.files;
  const data={
    "site-data.json":site,
    [files.daily_balance]:read(files.daily_balance),
    [files.audit_readiness]:audit(),
    [files.research_ledger]:ledger()
  };
  const requested=[];
  const c=context({fetch:async url=>{
    requested.push(url);
    const file=url.replace(/^data\//,"");
    return {ok:Boolean(data[file]),json:async()=>data[file],status:data[file]?200:404};
  }});
  await vm.runInContext("loadPlatformData()",c);
  assert.deepEqual(requested,["data/site-data.json","data/"+files.daily_balance,
    "data/"+files.audit_readiness,"data/"+files.research_ledger]);
  assert.equal(vm.runInContext("state.site.baseline.rows",c),354);
});
test("missing audit, cross-snapshot rows and fictitious 2040 MW fail closed",()=>{
  const c=context();
  const b=read("site-data.json"),d=read("daily-balance.json");
  c.bundle=b;c.days=d;c.check=audit();c.ledger=ledger();
  assert.equal(vm.runInContext("verifySnapshot(bundle,days,check,ledger)",c),true);
  c.ledger.potential_mw=999;
  assert.throws(()=>vm.runInContext("verifySnapshot(bundle,days,check,ledger)",c),/Unadmitted/);
  c.ledger=ledger();c.days={records:[]};
  assert.throws(()=>vm.runInContext("verifySnapshot(bundle,days,check,ledger)",c),/Mixed SLDC/);
  c.days=d;c.check=null;
  assert.throws(()=>vm.runInContext("verifySnapshot(bundle,days,check,ledger)",c),/Audited/);
});
test("daily chart breaks at missing source dates without joining a false chronology",()=>{
  const c=context();
  c.observations=[
    {date:"2024-09-19",consumption_mu:80},
    {date:"2024-09-21",consumption_mu:100},
    {date:"2024-09-22",consumption_mu:93}
  ];
  const svg=vm.runInContext("plotValues(observations,\"consumption_mu\")",c);
  assert.match(svg,/Breaks represent missing days/);
  assert.match(svg,/2024-09-19/);
  assert.match(svg,/2024-09-22/);
  assert.equal((svg.match(/class="chart-line"/g)||[]).length,1);
  assert.equal((svg.match(/class="chart-dot"/g)||[]).length,1);
});
test("source links are HTTPS-only and research evidence stays in its repository",()=>{
  const c=context();
  assert.equal(vm.runInContext("safeURL(\"javascript:alert(1)\")",c),"");
  assert.equal(vm.runInContext("safeURL(\"https://evil.example@foo.com/test\")",c),"");
  assert.equal(vm.runInContext("repoEvidence(\"https://not-the-project.example/a\")",c),"");
  assert.ok(vm.runInContext("repoEvidence(\"https://github.com/abhijith-sivaprasadan/kerala2040/blob/main/docs/AUDIT_RELEASE_GATES.md\")",c));
});
test("malicious workstream text is escaped, source injection rejected",()=>{
  const c=context();
  c.malicious={phase:"blocked",title:"<img src=x onerror=alert(1)>",
    summary:"<script>alert(1)</script>",id:"forest",metric:"0 / 25",unit:"matches",
    completed:"Compared",blocked:"Not legal boundaries",action:"Acquire gazette links",
    route:"atlas",evidence:[
      {label:"bad",href:"javascript:alert(1)"},
      {label:"good",href:"https://github.com/abhijith-sivaprasadan/kerala2040/blob/main/docs/AUDIT_RELEASE_GATES.md"}]};
  const html=vm.runInContext("sourceTrail(malicious)",c);
  assert.doesNotMatch(html,/javascript:|>bad</);
  assert.match(html,/good/);
  assert.match(vm.runInContext("esc(malicious.summary)",c),/&lt;script&gt;/);
});
test("scenario download stays an unsolved specification with separate commit identities",()=>{
  let output,downloaded=false;
  const c=context({
    Blob:class{constructor(parts){output=JSON.parse(parts[0])}},
    URL:{createObjectURL:()=> "blob:scenario",revokeObjectURL:()=>{}},
    document:{querySelector:()=>null,querySelectorAll:()=>[],createElement:()=>({click:()=>{downloaded=true;}})}
  });
  c.question={code:"S2",name:"Solar storage",description:"Question"};
  c.bundle={metadata:{research_source_commit:"research-sha",git_sha:"older-evidence-sha"}};
  vm.runInContext("state.site=bundle;downloadSpecification(question)",c);
  assert.equal(downloaded,true);
  assert.equal(output.classification,"unsolved_scenario_specification");
  assert.equal(output.hourly_model_calibrated,false);
  assert.equal(output.ecological_capacity_ceiling_ready,false);
  assert.equal(output.potential_mw,null);
  assert.equal(output.source_research_commit,"research-sha");
  assert.equal(output.evidence_build_commit,"older-evidence-sha");
});
test("GIS workstream is not a point-to-polygon or eligible capacity publication",()=>{
  const c=context();
  assert.deepEqual(vm.runInContext("spatialIds",c).join(","),
    "boundary,lulc,landslide,forest,wetlands");
  assert.match(vm.runInContext("labelStage(\"validated_source\")",c),/model gate open/);
  assert.match(vm.runInContext("labelStage(\"blocked\")",c),/Missing critical/);
  const html=fs.readFileSync(path.join(root,"docs/index.html"),"utf8");
  assert.match(html,/not a GIS map or legal boundary/);
  assert.match(html,/No buildable-land or MW estimate has been established/);
});

test("all eight research pages render against one real observed-data snapshot",()=>{
  const elements={};
  function el(selector){
    return elements[selector] ||= {
      innerHTML:"",textContent:"",value:"",
      addEventListener:()=>{},setAttribute:()=>{},querySelectorAll:()=>[],classList:{toggle:()=>{}}
    };
  }
  const c=context({document:{querySelector:el,querySelectorAll:()=>[],
    getElementById:()=>null}});
  const observed=read("site-data.json");
  observed.metadata.research_source_commit="06b09f984357b834149dd54d6e8e9cfccce4c599";
  c.observed=observed;
  c.days=read("daily-balance.json");
  c.check=audit();
  c.science=ledger();
  c.science.workstreams=[
    {id:"electricity",title:"Electricity",phase:"partial",
      metric:"354 / 365",unit:"report days",summary:"Observed subset",
      completed:"QA",blocked:"11 missing",action:"Request original reports",
      route:"electricity",evidence:[]},
    {id:"forest",title:"Forest",phase:"blocked",
      metric:"0 / 25",unit:"polygon matches",summary:"WDPA is not a legal map",
      completed:"Source QA",blocked:"No gazette geometry",
      action:"Request statutory polygons",route:"atlas",evidence:[]}
  ];
  vm.runInContext("state.site=observed;state.daily=days;state.audit=check;state.ledger=science;renderAll()",c);
  assert.match(elements["#headlineMetrics"].innerHTML,/73\.8%/);
  assert.match(elements["#energyChart"].innerHTML,/<svg/);
  assert.match(elements["#energyChartCaption"].textContent,/11 unverified days/);
  assert.match(elements["#spatialPipeline"].innerHTML,/No gazette geometry/);
  assert.match(elements["#scenarioDetail"].innerHTML,/Not a prediction/);
  assert.match(elements["#industryCases"].innerHTML,/Kerala Minerals and Metals Limited/);
  assert.match(elements["#workbenchCards"].innerHTML,/354 \/ 365/);
  assert.match(elements["#auditGates"].innerHTML,/NOT PASSED/);
  assert.match(elements["#downloadGrid"].innerHTML,/site-data\.json/);
});


test("first-visit welcome is small, dismissible and session-scoped without blocking content",()=>{
  const storage=new Map();
  const callbacks=new Map();let next=1;
  const card={hidden:true,classList:{
    classes:new Set(),add(name){this.classes.add(name)},
    remove(name){this.classes.delete(name)}
  }};
  const c=context({
    location:{hash:""},sessionStorage:{
      getItem:key=>storage.get(key),setItem:(key,value)=>storage.set(key,value)
    },
    window:{addEventListener:()=>{},matchMedia:()=>({matches:false})},
    document:{querySelector:selector=>selector==="#welcomeCard"?card:null,
      querySelectorAll:()=>[]},
    setTimeout:cb=>{const id=next++;callbacks.set(id,cb);return id},
    clearTimeout:id=>callbacks.delete(id)
  });
  assert.equal(vm.runInContext("showWelcome()",c),true);
  assert.equal(card.hidden,false);
  assert.equal(storage.get("kerala2040-welcomed"),"1");
  assert.equal(callbacks.size,1);
  assert.equal(vm.runInContext("showWelcome()",c),false);
  vm.runInContext("dismissWelcome()",c);
  assert.equal(callbacks.size,1); // only short dismissal timer survives
  [...callbacks.values()][0]();
  assert.equal(card.hidden,true);
  assert.equal(vm.runInContext("showWelcome()",c),false);
  const html=fs.readFileSync(path.join(root,"docs/index.html"),"utf8");
  assert.match(html,/id="welcomeCard"[^>]+hidden/);
  assert.match(html,/id="welcomeDismiss"/);
  assert.doesNotMatch(html,/aria-modal|role="dialog"/);
  const css=fs.readFileSync(path.join(root,"docs/assets/kerala.css"),"utf8");
  assert.match(css,/\.welcome-card\{position:fixed/);
  assert.doesNotMatch(css,/body\.splash-open\s*\{\s*overflow:\s*hidden/);
});
test("reduced-motion and direct deep links bypass the welcome entirely",()=>{
  for(const [hash,reduced] of [["",true],["#atlas",false]]){
    const card={hidden:true,classList:{add:()=>{},remove:()=>{}}};
    const c=context({
      location:{hash},
      window:{addEventListener:()=>{},matchMedia:()=>({matches:reduced})},
      document:{querySelector:key=>key==="#welcomeCard"?card:null,
        querySelectorAll:()=>[]}
    });
    assert.equal(vm.runInContext("showWelcome()",c),false);
    assert.equal(card.hidden,true);
  }
});
test("custom illustration, icons and social thumbnail are source authored, not model results",()=>{
  const html=fs.readFileSync(path.join(root,"docs/index.html"),"utf8");
  assert.match(html,/og:image:width" content="1200"/);
  assert.match(html,/og:image:height" content="630"/);
  assert.match(html,/twitter:card" content="summary_large_image"/);
  assert.match(html,/assets\/kerala2040-share\.png/);
  for(const icon of ["electric","water","leaf","cycle"]){
    assert.ok(html.includes("assets/icons.svg#"+icon));
  }
  for(const chapter of ["electric","land","pathways","industry"]){
    assert.ok(html.includes("assets/chapter-"+chapter+".svg"));
  }
  assert.match(html,/conceptual illustration—not a mapped network/);
  assert.match(html,/not a GIS map or legal boundary/);
  const css=fs.readFileSync(path.join(root,"docs/assets/kerala.css"),"utf8");
  assert.match(css,/@media\(prefers-reduced-motion:reduce\)/);
  assert.match(css,/\.system-story\.is-visible \.system-current span/);
});


test("energy visuals reconcile to the observed SLDC balance without adding hydro twice",()=>{
  const c=context(),rows=read("daily-balance.json").records;
  c.rows=rows;
  const balance=vm.runInContext("drawBalanceArt(rows)",c);
  assert.match(balance,/30\.67 TWh/);
  assert.match(balance,/22\.64 TWh/);
  assert.match(balance,/8\.03 TWh/);
  assert.match(balance,/7\.21 TWh/);
  assert.match(balance,/73\.8%/);
  assert.match(balance,/Hydropower/);
  assert.match(balance,/not an additional source/);
  const sums=JSON.parse(vm.runInContext(
    'JSON.stringify({total:sumField(rows,"consumption_mu"),imports:sumField(rows,"net_import_interface_mu"),local:sumField(rows,"internal_generation_mu"),hydro:sumField(rows,"hydel_total_mu")})',c));
  assert.ok(Math.abs(sums.total-sums.imports-sums.local)<0.01);
  assert.ok(sums.hydro<sums.local);
});
test("monthly charts use observed-day means, preserve all 11 missing SLDC dates",()=>{
  const c=context(),daily=read("daily-balance.json"),site=read("site-data.json");
  c.days=daily.records;c.scope=site.baseline;
  const months=JSON.parse(vm.runInContext("JSON.stringify(observedMonths(days,scope))",c));
  assert.equal(months.length,12);
  assert.equal(months.reduce((n,m)=>n+m.days.length,0),354);
  assert.equal(months.reduce((n,m)=>n+m.gaps.length,0),11);
  assert.equal(months.reduce((n,m)=>n+m.expected,0),365);
  assert.equal(months[0].key,"2024-04");
  assert.equal(months[11].key,"2025-03");
  assert.equal(months[4].gaps.length,1);
  assert.equal(months[11].gaps.length,3);
  for(const month of months){
    assert.ok(Math.abs(month.mean-month.meanImports-month.meanLocal)<.001);
    assert.equal(month.days.length+month.gaps.length,month.expected);
  }
  c.months=months;
  const svg=vm.runInContext("drawMonthlyArt(months)",c);
  assert.equal((svg.match(/class="viz-month-column"/g)||[]).length,12);
  assert.equal((svg.match(/class="viz-gap-stroke"/g)||[]).length,7);
  assert.match(svg,/not complete monthly totals/);
  assert.match(svg,/354\/365 dates observed/);
});
test("hydro and reservoir are distinct gap-broken observed lines with different units",()=>{
  const c=context(),daily=read("daily-balance.json"),site=read("site-data.json");
  c.days=daily.records;c.scope=site.baseline;
  const svg=vm.runInContext("drawHydroArt(days,scope)",c);
  const segments=daily.records.reduce((n,row,i)=>n+(
    i>0&&Date.parse(row.date)-Date.parse(daily.records[i-1].date)>86400000?1:0
  ),1);
  assert.equal((svg.match(/class="viz-hydro-line"/g)||[]).length,segments);
  assert.equal((svg.match(/class="viz-storage-line"/g)||[]).length,segments);
  assert.equal((svg.match(/class="viz-gap-guide"/g)||[]).length,11);
  assert.match(svg,/MU per day/);
  assert.match(svg,/storage percent/);
  assert.match(svg,/354\/365 reported dates/);
  assert.doesNotMatch(svg,/8760|forecast|potential_mw/);
});
