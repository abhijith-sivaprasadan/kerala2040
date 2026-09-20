const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const root = path.join(__dirname,'..');
const code = fs.readFileSync(path.join(root,'docs/assets/app.js'),'utf8');
function context(extra={}) {
  const sandbox = {console, setTimeout, clearTimeout, AbortController,
    document:{querySelector:()=>null}, window:{addEventListener:()=>{}}, ...extra};
  vm.createContext(sandbox); vm.runInContext(code,sandbox); return sandbox;
}
test('missing numeric observations never turn into zeros',()=>{
  const c=context();
  for(const literal of ['null','undefined','""','true','"unknown"']) assert.equal(vm.runInContext(`fmt(${literal})`,c),'—');
  assert.equal(vm.runInContext('fmt(0)',c),'0.0');
});
test('all evidence comes from the deployed snapshot and downloads exist',async()=>{
  const urls=[];
  const c=context({fetch:async url=>{
    urls.push(url); const file=path.join(root,'public',url.replace(/^data\//,''));
    return {ok:true,json:async()=>JSON.parse(fs.readFileSync(file,'utf8'))};
  }});
  await vm.runInContext('loadPlatformData()',c);
  const files=JSON.parse(fs.readFileSync(path.join(root,'public/site-data.json'),'utf8')).metadata.files;
  const requested=['daily_balance','monthly_balance','import_duration','kseb_history','hourly_load_proxy_summary','hourly_load_proxy','energyproject_context'];
  assert.equal(urls.length,1+requested.filter(key=>files[key]).length);
  assert.ok(urls.every(url=>url.startsWith('data/')));
  assert.ok(vm.runInContext('state.daily.records.length',c)>0);
  assert.ok(vm.runInContext('state.ksebHistory.series.installed_capacity.length',c)>0);
  assert.equal(vm.runInContext('state.data.baseline.rows === state.daily.records.length',c),true);
  assert.match(vm.runInContext('state.hourlyProxy.classification',c),/proxy/i);
  assert.match(vm.runInContext('state.hourlyProxy.classification',c),/not_measured|not measured/i);
});

test('hourly reconstruction loads when present without being treated as telemetry',async()=>{
  const c=context({fetch:async url=>{
    const file=path.join(root,'public',url.replace(/^data\//,''));
    let payload=url.endsWith('hourly-load-proxy-summary.json') ? {classification:'proxy_reconstruction_not_measured_telemetry',hours:8760} : JSON.parse(fs.readFileSync(file,'utf8'));
    if(url.endsWith('site-data.json')) payload.metadata.files.hourly_load_proxy_summary='hourly-load-proxy-summary.json';
    return {ok:true,json:async()=>payload};
  }});
  await vm.runInContext('loadPlatformData()',c);
  assert.equal(vm.runInContext('state.hourlyProxy.hours',c),8760);
  assert.equal(vm.runInContext('state.hourlyProxy.classification',c),'proxy_reconstruction_not_measured_telemetry');
});
test('disabled trade survives scenario normalisation',()=>{
  const c=context();
  vm.runInContext(`state.data={scenarios:[{code:'S0',import_option:'disabled'}]}`,c);
  assert.equal(vm.runInContext('scenarios()[0].import_option',c),false);
});
test('failed required dataset rejects instead of mixing evidence snapshots',async()=>{
  const c=context({fetch:async()=>({ok:false,status:404})});
  await assert.rejects(vm.runInContext('loadPlatformData()',c));
});
test('scenario export includes selected stress and stays explicitly unsolved',()=>{
  let payload, clicked=false;
  const c=context({Blob:class {constructor(parts){payload=JSON.parse(parts[0]);}},
    URL:{createObjectURL:()=> 'blob:test',revokeObjectURL:()=>{}},
    document:{querySelector:()=>null,createElement:()=>({click:()=>{clicked=true;}})}});
  vm.runInContext(`state.data={metadata:{git_sha:'evidence-sha'},scenarios:[{code:'S3',name:'Integrated'}],stress_tests:{dry_hydro:{description:'Drought'}}};state.selectedScenario='S3';state.selectedStress.add('dry_hydro');downloadSpecification()`,c);
  assert.ok(clicked);
  assert.equal(payload.classification,'unsolved_scenario_specification');
  assert.equal(payload.hourly_model_calibrated,false);
  assert.equal(payload.stress_tests.dry_hydro.description,'Drought');
  assert.equal(payload.evidence_commit,'evidence-sha');
});

test('audit card rendering escapes source text and never turns a blocked gate green',()=>{
  const c=context();
  vm.runInContext("state.audit={classification:'repository_evidence_audit_not_external_source_validation',"+
    "finding_count:1,open_findings:1,closed_findings:0,source_qa_sha256:'sha',evidence_limit:'committed only',"+
    "findings:[{id:'hydro_<test>',priority:'P0',acquisition:'<img src=x onerror=alert(1)>',"+
    "evidence:'docs/OBSERVED_DAILY_PYPSA.md',verification:{status:'blocked_missing_verified_evidence',"+
    "detail:'No verified cascade',evidence:'docs/OBSERVED_DAILY_PYPSA.md'}}],"+
    "release_gates:{techno_economic_2040:{passed:false,blocking_checks:['hydro_physics'],"+
    "description:'Unavailable'}}}",c);
  const html=vm.runInContext("auditFindingHTML(state.audit.findings[0])",c);
  assert.match(html,/Blocked \/ missing evidence/);
  assert.ok(!html.includes('<img'));
  assert.match(html,/&lt;img/);
  assert.match(html,/Inspect source evidence/);
  assert.equal(vm.runInContext("state.audit.release_gates.techno_economic_2040.passed",c),false);
});

test('workbench card escapes source text and refuses arbitrary links',()=>{
  const c=context();
  const item={
    id:'forest',title:'<img src=x onerror=alert(1)>',
    summary:'<script>alert(1)</script>',phase:'validated_source',
    metric:'0 / 25',unit:'matches',completed:'audited',blocked:'NO legal boundaries',
    action:'request custodial GIS',route:'workbench',
    evidence:[{label:'Injected',href:'javascript:alert(1)'},{label:'Real QA',
      href:'https://github.com/abhijith-sivaprasadan/kerala2040/blob/main/docs/AUDIT_RELEASE_GATES.md'}]
  };
  c.item=item;
  const html=vm.runInContext('researchLedgerCardHTML(item)',c);
  assert.ok(!html.includes('<script>'));
  assert.ok(!html.includes('<img'));
  assert.ok(!html.includes('javascript:'));
  assert.match(html,/&lt;script&gt;/);
  assert.match(html,/0 \/ 25/);
  assert.match(html,/Source coverage verified · model gate open/);
  assert.match(html,/Real QA/);
});
test('workbench stage labels never equate source QA with siting approval',()=>{
  const c=context();
  assert.match(vm.runInContext("researchPhaseLabel('validated_source')",c),/model gate open/);
  assert.match(vm.runInContext("researchPhaseLabel('blocked')",c),/Missing critical evidence/);
  assert.equal(vm.runInContext("researchEvidenceURL('https://not-the-project.example/test')",c),'');
});
