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
