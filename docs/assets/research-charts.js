/* Kerala2040 interactive research charts.
 * Data only from the packaged audited historical study or pinned research ledger.
 * SVG is a browser drawing surface, NOT an authored static graph image.
 * Focus/arrow keys, touch/click, pointer inspection, series toggles and source tables.
 */
"use strict";
const researchChartState = new Map();
let researchAtlasLedger = null;
const chartEsc = value => String(value==null?"":value).replace(/[&<>'"]/g,
  char => ({"&":"&amp;","<":"&lt;",">":"&gt;", "'":"&#39;", '"':"&quot;"}[char]));
const chartNumber = (value,unit="",digits=1) => value==null||!Number.isFinite(Number(value)) ?
  "—":Number(value).toLocaleString("en-IN",{maximumFractionDigits:digits})+(unit?" "+unit:"");
const chartPalette = ["#087e65","#bd8236","#8c6bba","#4983ae"];
const yearTitle = x => x.replace("-", "–");
function researchReadout(row,series,source){
  return row.label+" · "+series.map(s=>s.label+": "+chartNumber(row.values[s.key],s.unit,s.decimals??1)).join(" · ")+
    (row.note?" · "+row.note:"")+" · "+source;
}
function researchChartSVG(rows,series,style){
  const wide=style==="horizontal",w=780,h=wide?Math.max(380,rows.length*39+100):375;
  const left=wide?181:62,right=755,top=31,bottom=h-66;
  const active=series.filter(s=>s.visible);
  const ceiling=Math.max(1,...rows.flatMap(row=>active.map(s=>Number(row.values[s.key])||0)));
  const max=ceiling*1.13, grid=[];
  for(let step=0;step<=4;step++){
    const fraction=step/4;
    if(wide){
      const x=left+(right-left)*fraction;
      grid.push('<line x1="'+x+'" y1="'+top+'" x2="'+x+'" y2="'+bottom+'" class="research-gridline"/>'+
        '<text x="'+x+'" y="'+(h-30)+'" text-anchor="middle" class="research-tick">'+
        chartEsc(chartNumber(max*fraction,"",0))+'</text>');
    }else{
      const y=bottom-(bottom-top)*fraction;
      grid.push('<line x1="'+left+'" y1="'+y+'" x2="'+right+'" y2="'+y+'" class="research-gridline"/>'+
        '<text x="'+(left-9)+'" y="'+(y+4)+'" text-anchor="end" class="research-tick">'+
        chartEsc(chartNumber(max*fraction,"",0))+'</text>');
    }
  }
  const shapes=[], labels=[];
  const rowWidth=(right-left)/rows.length, rowHeight=(bottom-top)/rows.length;
  rows.forEach((row,i)=>{
    if(wide){
      const cy=top+(i+.5)*rowHeight;
      labels.push('<text x="'+(left-10)+'" y="'+(cy+5)+'" text-anchor="end" class="research-axis">'+chartEsc(row.label)+'</text>');
      const bh=Math.min(12,rowHeight/Math.max(3,active.length+1));
      active.forEach((s,j)=>{
        const value=row.values[s.key];
        if(value==null||!Number.isFinite(Number(value)))return;
        const y=cy+(j-(active.length-1)/2)*bh*1.16-bh/2;
        const width=(right-left)*Math.max(0,Number(value))/max;
        shapes.push('<rect class="research-point" data-index="'+i+'" data-key="'+chartEsc(s.key)+
          '" x="'+left+'" y="'+y.toFixed(2)+'" width="'+width.toFixed(2)+'" height="'+bh.toFixed(2)+
          '" fill="'+s.color+'" rx="2"><title>'+chartEsc(row.label+": "+s.label+" "+chartNumber(value,s.unit,s.decimals??1))+'</title></rect>');
      });
    }else{
      const cx=left+(i+.5)*rowWidth;
      labels.push('<text x="'+cx.toFixed(2)+'" y="'+(bottom+23)+'" text-anchor="middle" class="research-axis">'+chartEsc(row.label)+'</text>');
      const bw=Math.min(32,rowWidth/Math.max(2,active.length+1));
      active.forEach((s,j)=>{
        const v=row.values[s.key];
        if(v==null||!Number.isFinite(Number(v)))return;
        const hh=Math.max(.6,(bottom-top)*Math.max(0,Number(v))/max);
        const x=cx+(j-(active.length-1)/2)*bw*1.15-bw/2;
        shapes.push('<rect class="research-point" data-index="'+i+'" data-key="'+chartEsc(s.key)+
          '" x="'+x.toFixed(2)+'" y="'+(bottom-hh).toFixed(2)+'" width="'+bw.toFixed(2)+
          '" height="'+hh.toFixed(2)+'" fill="'+s.color+'" rx="2"><title>'+
          chartEsc(row.label+": "+s.label+" "+chartNumber(v,s.unit,s.decimals??1))+'</title></rect>');
      });
    }
  });
  return '<svg viewBox="0 0 '+w+' '+h+'" role="img" tabindex="0" aria-label="Interactive source-data chart; focus and use the arrow keys to inspect each category" xmlns="http://www.w3.org/2000/svg">'+
    '<title>Audited research chart · '+rows.length+' source categories</title>'+
    grid.join("")+shapes.join("")+labels.join("")+'</svg>';
}
function mountResearchChart(id,config){
  const root=document.getElementById(id);
  if(!root)return;
  const rows=config.rows||[];
  if(!rows.length){root.textContent="Verified chart source rows unavailable.";return;}
  const saved=researchChartState.get(id)||{series:new Set(config.series.map(s=>s.key)),index:-1};
  researchChartState.set(id,saved);
  let series=config.series.map((s,i)=>({...s,color:s.color||chartPalette[i%chartPalette.length],
    visible:saved.series.has(s.key)}));
  if(!series.some(s=>s.visible)){saved.series=new Set([config.series[0].key]);series[0].visible=true;}
  root.innerHTML='<div class="research-chart-control" role="group" aria-label="Chart series">'+
    series.map(s=>'<button type="button" data-series="'+chartEsc(s.key)+'" aria-pressed="'+String(s.visible)+
    '" style="--series-colour:'+s.color+'">'+chartEsc(s.label)+'</button>').join("")+'</div>'+
    '<div class="research-chart-canvas">'+researchChartSVG(rows,series,config.style)+'</div>'+
    '<p class="research-chart-readout" aria-live="polite">Select a bar or focus the chart and use ← →. No missing value is replaced with zero.</p>'+
    '<details class="research-chart-data"><summary>View all '+rows.length+' source categories and their coverage</summary>'+
    '<div class="table-scroll"><table><thead><tr><th>Category</th>'+
    config.series.map(s=>'<th>'+chartEsc(s.label)+' ('+chartEsc(s.unit)+')</th>').join("")+
    '<th>Coverage / definition</th></tr></thead><tbody>'+
    rows.map(r=>'<tr><th scope="row">'+chartEsc(r.label)+'</th>'+
      config.series.map(s=>'<td>'+chartEsc(chartNumber(r.values[s.key],"",s.decimals??2))+'</td>').join("")+
      '<td>'+chartEsc(r.note||"—")+'</td></tr>').join("")+
    '</tbody></table></div></details><p class="research-chart-source">'+chartEsc(config.source)+'</p>';
  const svg=root.querySelector("svg"),readout=root.querySelector(".research-chart-readout");
  const update=(index,keyboard=false)=>{
    if(index<0||index>=rows.length)return;
    saved.index=index;
    root.querySelectorAll("[data-index]").forEach(el=>
      el.classList.toggle("is-selected",Number(el.dataset.index)===index));
    readout.setAttribute("aria-live",keyboard?"polite":"off");
    readout.textContent=researchReadout(rows[index],series.filter(s=>s.visible),config.source);
    if(config.onSelect)config.onSelect(rows[index],index);
  };
  root.querySelectorAll("[data-series]").forEach(button=>button.addEventListener("click",()=>{
    const key=button.dataset.series;
    if(saved.series.has(key)&&saved.series.size>1)saved.series.delete(key);
    else saved.series.add(key);
    mountResearchChart(id,config);
  }));
  svg.addEventListener("pointerover",event=>{
    const hit=event.target.closest?.("[data-index]");
    if(hit)update(Number(hit.dataset.index));
  });
  svg.addEventListener("click",event=>{
    const hit=event.target.closest?.("[data-index]");
    if(hit){update(Number(hit.dataset.index),true);svg.focus();}
  });
  svg.addEventListener("keydown",event=>{
    if(!["ArrowRight","ArrowLeft","ArrowDown","ArrowUp","Home","End","Escape"].includes(event.key))return;
    event.preventDefault();
    if(event.key==="Escape"){saved.index=-1;readout.textContent="Selection cleared; focus and use arrow keys.";root.querySelectorAll("[data-index]").forEach(el=>el.classList.remove("is-selected"));return;}
    const next=event.key==="Home"?0:event.key==="End"?rows.length-1:
      event.key==="ArrowLeft"||event.key==="ArrowUp"?
        (saved.index<0?rows.length-1:Math.max(0,saved.index-1)):
        Math.min(rows.length-1,saved.index+1);
    update(next,true);
  });
  if(saved.index>=0&&saved.index<rows.length)update(saved.index);
}
function validateHistorical(study){
  if(study?.classification!=="source_derived_historical_electricity_story_distinct_reporting_boundaries"||
     !study.qa?.no_imputation||study.qa.interval_telemetry_present!==false||
     study.qa.missing_fy2024_25!==11||
     study.paired_fy_2020_21_2025_26?.matched_calendar_month_day_count!==356||
     Object.keys(study.official_economic_review_2025_kerala_consumption_mu||{}).length!==5||
     Object.keys(study.sldc_observed_fy||{}).length!==6||
     !/^[a-f0-9]{64}$/.test(study.source?.sldc_archive_sha256||"")){
    throw new Error("Historical chart data failed evidence-boundary validation");
  }
}
function renderHistoricalResearchCharts(study){
  validateHistorical(study);
  const official=study.official_economic_review_2025_kerala_consumption_mu;
  mountResearchChart("historyOfficial",{
    style:"vertical",source:"Kerala Economic Review 2025 Vol. I p. 569 · official consumer-side scope, FY2020–21–FY2024–25",
    rows:Object.entries(official).map(([fy,mu])=>({label:fy,values:{mu},note:"Official full FY; open access and captive consumption included"})),
    series:[{key:"mu",label:"Official state consumption",unit:"MU",decimals:2}]
  });
  const months=study.paired_months,abbr=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  mountResearchChart("historyMatched",{
    style:"vertical",source:"SLDC audited qualified reports · FY2020–21 vs FY2025–26 · same month/day keys; pandemic comparator",
    rows:abbr.map((name,i)=>{const m=months[String(i+1)];return {label:name,
      values:{old:m?.baseline_mean_mu??null,new:m?.latest_mean_mu??null},
      note:m?m.n+" paired days · "+chartNumber(m.change_pct,"%",2)+" change":"Month not source-qualified"};}),
    series:[{key:"old",label:"2020–21",unit:"MU/day",decimals:2},
      {key:"new",label:"2025–26",unit:"MU/day",decimals:2}]
  });
  mountResearchChart("historyShares",{
    style:"vertical",source:"SLDC qualified FY dates · ratio of summed MU, not mean daily percentage; accounting co-movement ≠ causality",
    rows:Object.entries(study.sldc_observed_fy).map(([fy,r])=>({label:fy,
      values:{imports:r.net_import_energy_share_pct,hydel:r.hydel_energy_share_pct},
      note:r.qualified_days+"/"+r.calendar_days+" qualified days; gaps remain missing"})),
    series:[{key:"imports",label:"Net import share",unit:"%",decimals:2},
      {key:"hydel",label:"Hydel share",unit:"%",decimals:2}]
  });
  mountResearchChart("historyPeaks",{
    style:"vertical",source:"SLDC Statistics evening-peak field on qualified days; not all-hour metered demand",
    rows:Object.entries(study.sldc_observed_fy).map(([fy,r])=>({label:fy,
      values:{p95:r.peak_evening_p95_mw,max:r.peak_evening_max_mw},
      note:r.qualified_days+"/"+r.calendar_days+" qualified energy dates; peak-field count may differ"})),
    series:[{key:"p95",label:"Evening peak P95",unit:"MW",decimals:0},
      {key:"max",label:"Evening peak maximum",unit:"MW",decimals:0}]
  });
}
const atlasChoice={speed:7,slope:5,windDistrict:"Idukki"};
function atlasPicker(target,label,values,current,onchange){
  const root=document.getElementById(target);if(!root)return;
  const bar=document.createElement("div");bar.className="research-chart-pickers";
  const text=document.createElement("label");text.textContent=label+" ";
  const select=document.createElement("select");select.setAttribute("aria-label",label);
  values.forEach(v=>{const opt=document.createElement("option");opt.value=String(v);opt.textContent=String(v);select.appendChild(opt);});
  select.value=String(current);select.addEventListener("change",()=>onchange(select.value));
  text.appendChild(select);bar.appendChild(text);root.prepend(bar);
}
function renderAtlasResearchCharts(ledger){
  researchAtlasLedger=ledger;
  const wind=ledger?.wind_phase1?.normalized;
  const solar=ledger?.solar_phase1?.aggregate;
  if(wind?.districts?.length===14){
    const thresholds=wind.thresholds;
    const speeds=thresholds.minimum_modelled_wind_speed_150m_m_s_inclusive;
    const slopes=thresholds.maximum_DSM_surface_slope_degrees_inclusive;
    const speedIdx=speeds.indexOf(atlasChoice.speed),slopeIdx=slopes.indexOf(atlasChoice.slope);
    const districtList=wind.districts.map(d=>d.district);
    if(!districtList.includes(atlasChoice.windDistrict))atlasChoice.windDistrict=districtList[0];
    const chooseDistrict=row=>{
      if(!row||row.label===atlasChoice.windDistrict)return;
      atlasChoice.windDistrict=row.label;
      const picker=document.getElementById("districtChoice");
      if(picker){picker.value=row.label;picker.dispatchEvent(new Event("change",{bubbles:true}));}
      renderAtlasResearchCharts(ledger);
    };
    mountResearchChart("windDistrictChart",{
      style:"horizontal",source:"NIWE 150 m original NWIC district resource centres × GLO-90 DSM slope; no eligible km² or MW",
      rows:wind.districts.map(d=>({label:d.district,values:{centres:d.counts[speedIdx][slopeIdx]},
        note:d.valid_slope_point_centres+" valid slope centres; "+d.missing_slope_point_centres+" missing; ≥"+atlasChoice.speed+" m/s, ≤"+atlasChoice.slope+"°"})),
      series:[{key:"centres",label:"Modelled source centres",unit:"points",decimals:0}],
      onSelect:chooseDistrict
    });
    atlasPicker("windDistrictChart","Minimum wind speed (m/s)",speeds,atlasChoice.speed,v=>{
      atlasChoice.speed=Number(v);renderAtlasResearchCharts(ledger);
    });
    atlasPicker("windDistrictChart","Maximum DSM slope (°)",slopes,atlasChoice.slope,v=>{
      atlasChoice.slope=Number(v);renderAtlasResearchCharts(ledger);
    });
    const d=wind.districts.find(x=>x.district===atlasChoice.windDistrict);
    mountResearchChart("windSlopeChart",{
      style:"vertical",source:"Wind ≥"+atlasChoice.speed+" m/s · NWIC "+d.district+" valid-slope NIWE points; thresholds illustrative",
      rows:slopes.map((s,i)=>({label:"≤"+s+"°",values:{counts:d.counts[speedIdx][i],
        pct:d.percent_of_district_valid_slope_centres[speedIdx][i]},
        note:d.valid_slope_point_centres+" finite-slope source points as denominator; "+d.missing_slope_point_centres+" missing"})),
      series:[{key:"counts",label:"Source centres",unit:"points",decimals:0}]
    });
    atlasPicker("windSlopeChart","District",districtList,atlasChoice.windDistrict,v=>{
      atlasChoice.windDistrict=v;renderAtlasResearchCharts(ledger);
    });
  }
  if(solar?.districts?.length===14){
    const monthly=solar.statewide.monthly_marginal_pixel_median_PVOUT_kWh_kWp_day;
    mountResearchChart("solarMonthChart",{
      style:"vertical",source:"GSA 2.0 reference-system PVOUT, 1999–2018 long-term; 46,241 native source centres",
      rows:Object.entries(monthly).map(([label,v])=>({label,values:{pvout:v},
        note:"Marginal monthly median; not a paired-pixel seasonal difference"})),
      series:[{key:"pvout",label:"Monthly median PVOUT",unit:"kWh/kWp/day",decimals:3}]
    });
    const selectSolar=row=>{
      const picker=document.getElementById("solarDistrictChoice");
      if(picker&&picker.value!==row.label){
        picker.value=row.label;picker.dispatchEvent(new Event("change",{bubbles:true}));
      }
    };
    mountResearchChart("solarAnnualChart",{
      style:"horizontal",source:"GSA 2.0 1999–2018 PVOUT × original NWIC 14 districts; unweighted source-pixel medians",
      rows:solar.districts.map(d=>({label:d.district,values:{pvout:d.median_annual_PVOUT_kWh_kWp},
        note:d.finite_native_source_pixel_centres+" native source pixels; not built PV generation"})),
      series:[{key:"pvout",label:"Annual median PVOUT",unit:"kWh/kWp/year",decimals:2}],
      onSelect:selectSolar
    });
    mountResearchChart("solarSeasonChart",{
      style:"horizontal",source:"GSA 2.0 NWIC districts · per-pixel February→July relative change before taking district median",
      rows:solar.districts.map(d=>({label:d.district,values:{decline:d.median_pixelwise_Feb_to_Jul_decline_pct},
        note:d.finite_native_source_pixel_centres+" source pixels; median of paired pixel changes"})),
      series:[{key:"decline",label:"Paired Feb→Jul decline",unit:"%",decimals:2}],
      onSelect:selectSolar
    });
  }
}
async function loadHistoricalStudy(filename,ledger){
  renderAtlasResearchCharts(ledger);
  const boxes=["historyOfficial","historyMatched","historyShares","historyPeaks"];
  if(!/^[a-z0-9_-]+\.json$/i.test(filename||"")){
    boxes.forEach(id=>{const el=document.getElementById(id);if(el)el.textContent="No source-verified historical dataset in this release.";});
    return;
  }
  try{
    const study=await getJSON(filename);
    renderHistoricalResearchCharts(study);
  }catch(error){
    console.error("Historical evidence chart loading failed:",error);
    boxes.forEach(id=>{const el=document.getElementById(id);
      if(el)el.textContent="Historical research data failed verification; no charts shown. Read the source audit.";
    });
  }
}


/* KMML's process diagram deliberately contains no invented material/energy widths.
   Datum date and whether a loop was commissioned remain visible on every view. */
const kmmlState={unit:"IBP",filter:"all"};
function validateKMMLCase(data){
  const s=data?.scientific_scope||{};
  if(data?.classification!=="KMML_CHAVARA_SOURCE_BOUNDED_PROCESS_CASE_NOT_MEASURED_2024_25_NOT_RECOVERY_FORECAST"||
    data?.selected_case!=="KMML"||
    data?.units?.length!==9||data?.streams?.length!==10||
    s.measured_mass_energy_water_balance_complete!==false||
    s.measured_recovery_credits_available!==false||
    s.kmml_case_release_gate_passed!==false||
    data.ready_for_numerical_2040_industry_scenario!==false||
    data.published_numeric_recovery_by_Kerala2040!==null||
    data.streams.some(x=>x.annual_tonnes!==null||x.annual_mwh!==null||x.avoided_co2_t!==null)||
    data.dated_evidence?.fy2022_23?.iron_oxide_sponge_iron_trial_mt!==10||
    data.dated_evidence?.fy2022_23?.filter_backwash_m3_per_day_approx!==300||
    JSON.stringify(data.dated_evidence?.fy2022_23?.tio2_fines_overflow_g_per_l)!=="[1,2]"){
    throw new Error("KMML scientific boundary was altered or missing");
  }
  return true;
}
function kmmlGroup(stream){
  if(["pigment_fines","backwash_water"].includes(stream.id))return "trials";
  if(["heat","sponge_mgcl2"].includes(stream.id))return "unquantified";
  return "existing";
}
function kmmlSourceLink(data,id){
  const entry=data.sources[id];
  if(!entry)return "";
  const href=entry.url||"";
  if(!/^https:\/\/www\.kmml\.com\//.test(href))return "";
  return '<a href="'+chartEsc(href)+'" target="_blank" rel="noopener noreferrer">'+
    chartEsc(id==="annual_2022_23"?"KMML Annual Report FY2022–23":id.toUpperCase()+" · official KMML")+' ↗</a>';
}
function renderKMMLCase(data){
  validateKMMLCase(data);
  const status=document.getElementById("kmmlCaseStatus");
  if(status)status.innerHTML=
    '<span><b>9</b> documented process and utility units</span>'+
    '<span><b>10</b> source-qualified residual and loop entries</span>'+
    '<span><b>2022–23</b> dated R&D trial record</span>'+
    '<span><b>Unmeasured</b> annual plant-wide recovery and avoided CO₂</span>';
  const root=document.getElementById("kmmlFlow"),details=document.getElementById("kmmlUnitDetail");
  if(root){
    const orders=[["MS","IBP","U200","U300","U400"],["ARP","TSP","ETP","UTIL"]];
    const printUnit=id=>{
      const u=data.units.find(x=>x.id===id);if(!u)return "";
      const selected=u.id===kmmlState.unit;
      return '<button type="button" data-kmml-unit="'+chartEsc(u.id)+'" aria-pressed="'+selected+
       '" class="kmml-unit kmml-unit-'+chartEsc(u.branch)+'">'+
       '<small>'+chartEsc(u.branch==="pigment"?"PIGMENT · MAIN":
         u.branch==="sponge"?"METAL · SEPARATE":u.branch==="recovery"?"ACID · RETURN":
         u.branch==="environment"?"EFFLUENT / RESIDUE":"UTILITIES")+'</small>'+
       '<strong>'+chartEsc(u.id)+'</strong><span>'+chartEsc(u.name)+'</span></button>';
    };
    root.innerHTML='<div class="kmml-trunk">'+orders[0].map((id,i)=>printUnit(id)+
      (i<orders[0].length-1?'<span aria-hidden="true" class="kmml-arrow">→</span>':"")).join("")+
      '</div><p class="kmml-flow-note">MS → IBP → U200 → U300 → U400 is the pigment chain; select the branches below for the acid return, sponge metal, effluent and cross-cutting utilities.</p>'+
      '<div class="kmml-branches">'+orders[1].map(printUnit).join("")+'</div>';
    root.querySelectorAll("[data-kmml-unit]").forEach(button=>button.addEventListener("click",()=>{
      kmmlState.unit=button.dataset.kmmlUnit;renderKMMLCase(data);
      document.getElementById("kmmlUnitDetail")?.scrollIntoView?.({block:"nearest",behavior:"smooth"});
    }));
  }
  const unit=data.units.find(x=>x.id===kmmlState.unit)||data.units[0];
  if(details)details.innerHTML='<div><small>SELECTED UNIT · '+chartEsc(unit.id)+
    ' · NOT A METERED FLOW</small><h3>'+chartEsc(unit.name)+'</h3>'+
    '<p>'+chartEsc(unit.function)+'</p></div><div><b>Inputs:</b> '+chartEsc(unit.inputs)+
    '</div><div><b>Outputs:</b> '+chartEsc(unit.outputs)+
    '</div><p class="kmml-unit-caveat">Annual output / heat / water: not verified. '+
    kmmlSourceLink(data,unit.origin)+'</p>';
  const fs=document.getElementById("kmmlStreamFilters"),out=document.getElementById("kmmlStreams");
  const filters=[["all","All ten"],["existing","Existing routes / source processes"],
    ["trials","FY2022–23 trials"],["unquantified","Unmeasured opportunities / coproduct"]];
  if(fs){
    fs.innerHTML=filters.map(([id,label])=>'<button type="button" data-kmml-filter="'+id+
      '" aria-pressed="'+String(kmmlState.filter===id)+'">'+chartEsc(label)+'</button>').join("");
    fs.querySelectorAll("[data-kmml-filter]").forEach(button=>button.addEventListener("click",()=>{
      kmmlState.filter=button.dataset.kmmlFilter;renderKMMLCase(data);
    }));
  }
  const selected=data.streams.filter(s=>kmmlState.filter==="all"||kmmlGroup(s)===kmmlState.filter);
  if(out)out.innerHTML=selected.map(s=>{
    const group=kmmlGroup(s),txt=group==="trials"?"DATED TRIAL · FY2022–23":
      group==="unquantified"?"NO RECOVERY CREDIT":"DESCRIBED ROUTE · QUANTITIES UNKNOWN";
    return '<article class="kmml-stream"><div><small>'+chartEsc(s.unit)+' · '+txt+
       '</small><h4>'+chartEsc(s.title)+'</h4><p>'+chartEsc(s.route)+'</p></div>'+
       '<details><summary>What would establish the amount and the benefit?</summary>'+
       '<p>'+chartEsc(s.necessary)+'</p><p>Annual tonnes: — · Annual MWh: — · Avoided CO₂: —</p>'+
       '<div class="source-links">'+s.source_ids.map(id=>kmmlSourceLink(data,id)).join(" ")+'</div></details></article>';
  }).join("");
}
async function loadKMMLCase(filename){
  const root=document.getElementById("kmmlFlow");if(!root)return;
  if(filename!=="kmml-case.json"){root.textContent="No source-verified KMML case in this published research revision.";return;}
  try{renderKMMLCase(await getJSON(filename));}
  catch(err){console.error("KMML case data failed verification:",err);
    root.textContent="KMML case failed provenance/coverage checks; no process claims shown.";
  }
}


/* Historical Kerala total energy and separate provisional half-year fuel sales.
 * Never align publisher FY2019–20 shares with FY2024–25 PPAC consumption.
 */
function validateTotalEnergyAtlas(d){
  if(d?.classification!=="HISTORICAL_KERALA_FINAL_ENERGY_AND_H1_PETROLEUM_SALES_NOT_CURRENT_COMPLETE_ENERGY_BALANCE"||
     d?.emc_final_energy?.observed_years?.length!==6||
     d?.emc_final_energy?.baseline_fy!=="2019-20"||
     d?.emc_final_energy?.baseline_total_mtoe!==10.78||
     d?.emc_final_energy?.rounded_mix_pct?.reduce((v,r)=>v+r.pct,0)!==100||
     d?.emc_final_energy?.mix_reconstruction_allowed!==false||
     d?.emc_final_energy?.internal_discrepancy?.figure_3_fy2015_mtoe!==9.18||
     d?.emc_final_energy?.internal_discrepancy?.section_3_prose_fy2015_mtoe!==9.81||
     d?.ppac_provisional_half_year_2024_25?.no_annualisation!==true||
     d?.ppac_provisional_half_year_2024_25?.publisher_pdf_visual_validation!==false||
     d?.ppac_provisional_half_year_2024_25?.end_date!=="2024-09-30"||
     d?.ppac_provisional_half_year_2024_25?.items?.length!==5||
     Object.values(d?.quantities_deliberately_null||{}).length!==9||
     Object.values(d.quantities_deliberately_null).some(v=>v!==null)){
     throw new Error("Total energy atlas failed fiscal/source/sales boundary admission");
  }
}
function renderTotalEnergyAtlas(d){
  validateTotalEnergyAtlas(d);
  const status=document.getElementById("totalEnergyStatus");
  if(status)status.innerHTML=
    '<span><b>10.78 Mtoe</b> EMC historical FY2019–20 TFEC</span>'+
    '<span><b>64% oil</b> historical publisher-rounded share</span>'+
    '<span><b>19% electricity</b> historical share, NOT electricity generation</span>'+
    '<span><b>FY2024–25: not reconstructed</b> Separate PPAC H1 sales only</span>';
  mountResearchChart("totalEnergyHistoryChart",{
    style:"vertical",source:"EMC Kerala/CII, original Fig. 3 p. 13; publisher contradiction: Fig. 3 FY2015=9.18 Mtoe vs §3 prose p. 19 FY2015=9.81; source values NOT reconciled. Historic fiscal end-year labels.",
    rows:d.emc_final_energy.observed_years.map(r=>({
      label:r.fy,values:{mtoe:r.value_mtoe},note:"EMC Figure 3 FY "+r.fy.slice(-2)+(r.fy==="2014-15"?"; conflicts with §3 prose value 9.81 Mtoe":"; chart rounded to two decimals")
    })),
    series:[{key:"mtoe",label:"Final energy",unit:"Mtoe",decimals:2}]
  });
  mountResearchChart("totalEnergyMixChart",{
    style:"horizontal",source:"EMC Kerala/CII Action Plan, Fig. 4, printed p. 13; published FY2019–20 integer-rounded shares; no measured fuel-by-fuel Mtoe inferred.",
    rows:d.emc_final_energy.rounded_mix_pct.map(r=>({
      label:r.fuel,values:{share:r.pct},
      note:r.pct===0?"Display-rounding 0%, not proof of absence":"Rounded published graphic, not measured exact share"
    })),
    series:[{key:"share",label:"Publisher rounded fuel share",unit:"%",decimals:0}]
  });
  mountResearchChart("totalEnergyPPACChart",{
    style:"horizontal",source:"PPAC Ready Reckoner H1 FY2024–25 Table 6.3(A), indexed PDF text; provisional Apr–Sep sales in Kerala. Original PDF image not yet confirmed; NOT annual or full final-energy balance.",
    rows:d.ppac_provisional_half_year_2024_25.items.map(r=>({
      label:r.product,values:{sales:r.tmt},
      note:"Only April–September 2024; provisional selected-product sales; original PDF image QA pending"
    })),
    series:[{key:"sales",label:"Selected product sales",unit:"thousand tonnes",decimals:2}]
  });
}
async function loadTotalEnergyAtlas(filename){
  const root=document.getElementById("totalEnergyHistoryChart");
  if(!root)return;
  const mounts=["totalEnergyHistoryChart","totalEnergyMixChart","totalEnergyPPACChart"];
  if(filename!=="total-energy-atlas.json"){
    mounts.forEach(id=>{const el=document.getElementById(id);if(el)el.textContent="No source-admitted total-energy dataset in this release.";});
    return;
  }
  try{renderTotalEnergyAtlas(await getJSON(filename));}
  catch(error){
    console.error("Total energy atlas source admission failed:",error);
    mounts.forEach(id=>{const el=document.getElementById(id);if(el)el.textContent="Total energy source QA failed; figures withheld. Read the research chapter.";});
  }
}


/* Full FY PPAC oil-company sales: publisher-indexed historic totals, exact FY2024-25
 * table via independent mirror; no conversion to energy, imports or sector service. */
function validatePPACAnnualSales(d){
  const vals=[6533.5,5461.3,5901.7,6879.1,6891.7,6939.7];
  const rows=d?.annual_kerala_rows;
  if(d?.classification!=="PPAC_KERALA_ANNUAL_OIL_COMPANY_SALES_NOT_FINAL_ENERGY_OR_SECTOR_ALLOCATION"||
     rows?.length!==6||
     rows.some((r,i)=>r.fy!==["2019-20","2020-21","2021-22","2022-23","2023-24","2024-25"][i]||
       r.all_pol_tmt!==vals[i])||
     rows[0].hsd_tmt!==null||
     rows[5].all_pol_tier!=="secondary_transcription_unverified_at_primary"||
     d?.qa?.primary_fy2024_25_pdf_image_verified!==false||
     d?.qa?.all_pol_includes_subcategory_ms_hsd!==true||
     d?.qa?.no_annualisation_of_h1!==true||
     d?.qa?.no_mass_to_energy_without_source_factors!==true||
     d?.qa?.revenue_cost_or_kerala_import_claim_ready!==false||
     Object.values(d?.unsupported_current_results||{}).length!==6||
     Object.values(d.unsupported_current_results).some(x=>x!==null)){
    throw new Error("PPAC annual sales failed vintage, source or final-energy boundary");
  }
}
function renderPPACAnnualSales(d){
  validatePPACAnnualSales(d);
  const rows=d.annual_kerala_rows;
  const source="PPAC Ready Reckoner state sales: official H1 FY2024-25 indexed historical table for FY2019-20–2023-24; FY2024-25 exact original-publication mirror only, original publisher PDF image unverified. Thousands of tonnes SOLD, not final energy.";
  mountResearchChart("totalEnergyAnnualPPACChart",{
    style:"vertical",source,
    rows:rows.map(r=>({label:r.fy,values:{all:r.all_pol_tmt},
      note:r.all_pol_tier==="publisher_indexed_text"?
        "Original PPAC-indexed historical PDF table; no original page-image QA":
        "FY2024–25 SECONDARY REPRODUCTION ONLY · publisher PDF visual comparison pending"})),
    series:[{key:"all",label:"All POL sales",unit:"thousand tonnes",decimals:1}]
  });
  mountResearchChart("totalEnergyPPACProductsChart",{
    style:"vertical",source:source+" Petrol and HSD are components INCLUDED in all-POL. FY2019–20 HSD cell unavailable; do not convert to zero.",
    rows:rows.map(r=>({label:r.fy,values:{petrol:r.ms_tmt,diesel:r.hsd_tmt},
      note:"Petrol "+r.ms_tier+"; diesel "+r.hsd_tier+"; product subset, NOT transport end use"})),
    series:[{key:"petrol",label:"Motor spirit",unit:"thousand tonnes",decimals:1},
      {key:"diesel",label:"High-speed diesel",unit:"thousand tonnes",decimals:1}]
  });
}
async function loadPPACAnnualSales(filename){
  const mounts=["totalEnergyAnnualPPACChart","totalEnergyPPACProductsChart"];
  if(!document.getElementById(mounts[0]))return;
  if(filename!=="ppac-annual-sales.json"){
    mounts.forEach(id=>{const node=document.getElementById(id);
      if(node)node.textContent="Source-audited annual petroleum sales not in this research release.";});
    return;
  }
  try{renderPPACAnnualSales(await getJSON(filename));}
  catch(error){
    console.error("PPAC annual sales source admission failed:",error);
    mounts.forEach(id=>{const node=document.getElementById(id);
      if(node)node.textContent="Annual sales source QA failed; figure withheld.";});
  }
}


/* Current DoECC 2023 inventory belongs on a different emissions accounting
 * perimeter than EMC FY2019–20 final energy and PPAC FY2024–25 sales mass.
 */
function validateEnergyGHGBridge(d){
  const vals=[["transport",13.59,65.87],["residential",3.2,15.48],
    ["industrial",1.89,9.16]];
  if(d?.classification!=="KERALA_GHG_2023_OFFICIAL_SECTOR_EMISSIONS_NOT_FINAL_ENERGY_OR_2024_25"||
    d?.period!=="calendar_2023"||d?.unit!=="MtCO2e"||
    d?.energy_sector_2023_mtco2e!==20.64||
    d?.categories?.length!==3||
    d.categories.some((r,i)=>r.id!==vals[i][0]||r.mtco2e!==vals[i][1]||
      r.share_of_energy_pct!==vals[i][2])||
    d?.historic_source_vintage_conflict?.old_report_energy_mtco2e!==16.96||
    d?.historic_source_vintage_conflict?.current_portal_energy_mtco2e!==17.09||
    d?.historical_seeap_gcv?.values?.length!==7||
    d?.historical_seeap_gcv?.basis?.startsWith("GROSS CALORIFIC VALUE")!==true||
    d?.no_assumed_energy_2024_25_mtoe!==null||
    d?.no_assumed_2024_25_sectoral_emissions_mtco2e!==null||
    d?.no_current_kerala_import_share!==null||
    d?.no_externally_verified_2023_fuel_by_sector_matrix!==null||
    d?.no_raw_seeap_workbook!==true){
    throw new Error("2023 emissions cannot become 2024–25 fuel, energy or CO2 conversion");
  }
}
function renderEnergyGHGBridge(d){
  validateEnergyGHGBridge(d);
  const status=document.getElementById("totalEnergyGHGStatus");
  if(status)status.innerHTML=
    '<span><b>20.64 MtCO₂e</b> official CY2023 modelled energy-sector emissions</span>'+
    '<span><b>~80%</b> of statewide gross GHG excluding LULUCF</span>'+
    '<span><b>Three categories shown</b> not the complete energy-sector category set</span>';
  mountResearchChart("totalEnergyGHGChart",{
    style:"horizontal",
    source:"DoECC Kerala GHG Portal, energy-sector 2023 estimates; calendar year and MtCO2e, NOT final energy, petroleum tonnes, or FY2024–25. Source inventories disagree on 2020: older 16.96 vs portal 17.09 MtCO2e.",
    rows:d.categories.map(r=>({label:r.name,values:{emission:r.mtco2e},
      note:"Official 2023 energy-emissions share "+chartNumber(r.share_of_energy_pct,"%",2)+
        ". "+r.comment})),
    series:[{key:"emission",label:"Emissions (official 2023)",unit:"MtCO₂e",decimals:2}]
  });
}
async function loadEnergyGHGBridge(filename){
  const root=document.getElementById("totalEnergyGHGChart");if(!root)return;
  if(filename!=="energy-ghg-bridge.json"){
    root.textContent="Official 2023 emissions source not packaged in this research release.";return;
  }
  try{renderEnergyGHGBridge(await getJSON(filename));}
  catch(error){console.error("Energy GHG source validation failed:",error);
    root.textContent="2023 energy-emissions source QA failed; figure withheld.";
  }
}


/* WP6 results are recomputed at build time from a plainly synthetic 1R1C
 * model. Never connect a 24-hour demonstration to Kerala capacity or tariffs. */
function validateWP6Pilot(d){
  const keys=["conventional","precooling","chilled_water_storage"];
  if(d?.classification!=="WP6_SYNTHETIC_24H_1R1C_COOLING_COMPARISON_NOT_KERALA_GRID_RESULT"||
     d?.inputs?.classification!=="synthetic_illustrative_1R1C_24_hour_cooling_only_NOT_Kerala_observations"||
     d?.inputs?.hourly_outdoor_C?.length!==24||
     d?.inputs?.peak_window?.start_hour_inclusive!==17||
     d?.inputs?.peak_window?.end_hour_inclusive!==21||
     keys.some(k=>d?.cases?.[k]?.hourly?.length!==24||
       d?.cases?.[k]?.summary?.comfort_violation_hours!==0||
       d?.cases?.[k]?.summary?.end_store_kWh_th!==0||
       d?.cases?.[k]?.summary?.end_room_C!==25.5)||
     d?.sensitivity?.length!==9||
     !d?.science_gates||
     Object.values(d.science_gates).some(v=>v!==false)||
     d.cases.chilled_water_storage.summary.evening_grid_kWh_e>=
       d.cases.conventional.summary.evening_grid_kWh_e||
     d.cases.chilled_water_storage.summary.total_grid_kWh_e<=
       d.cases.conventional.summary.total_grid_kWh_e){
    throw new Error("WP6 cannot publish unbalanced, non-synthetic or Kerala-claimed cooling results");
  }
}
function renderWP6Pilot(d){
  validateWP6Pilot(d);
  const keyLabels={
    conventional:"Conventional AC",
    precooling:"Thermal-mass pre-cooling",
    chilled_water_storage:"Cold-water TES"
  };
  const keys=Object.keys(keyLabels);
  const status=document.getElementById("wp6Status");
  if(status)status.innerHTML=
    '<span><b>24h</b> authored outdoor-temperature profile, not ERA5</span>'+
    '<span><b>24–26°C</b> shared comfort envelope</span>'+
    '<span><b>17–21</b> illustrative evening window</span>'+
    '<span><b>9</b> actual sensitivity reruns</span>';
  const cards=document.getElementById("wp6CaseCards");
  if(cards)cards.innerHTML=keys.map(k=>{
    const s=d.cases[k].summary,base=d.cases.conventional.summary;
    const shift=k==="conventional"?"Reference for both peak metrics":
      "Change from conventional: "+chartNumber(
        s.evening_grid_kWh_e-base.evening_grid_kWh_e,"kWh_e in evening",3);
    return '<article class="wp6-case-card"><small>'+chartEsc(keyLabels[k])+
     ' · SYNTHETIC</small><h3>'+chartEsc(chartNumber(s.total_grid_kWh_e,"kWh_e",3))+
     '</h3><p>Whole-day grid electricity</p><dl><div><dt>Whole-day maximum</dt><dd>'+
     chartEsc(chartNumber(s.whole_day_peak_kW_e,"kW_e",3))+'</dd></div>'+
     '<div><dt>Evening maximum</dt><dd>'+chartEsc(chartNumber(s.evening_peak_kW_e,"kW_e",3))+'</dd></div>'+
     '<div><dt>Evening total</dt><dd>'+chartEsc(chartNumber(s.evening_grid_kWh_e,"kWh_e",3))+'</dd></div>'+
     '<div><dt>Comfort violations</dt><dd>'+s.comfort_violation_hours+
     ' hours</dd></div></dl><p class="wp6-case-note">'+chartEsc(shift)+
     '; pre-cooling early-setpoint shortfall '+chartEsc(
        chartNumber(s.room_cooling_target_shortfall_kWh_th,"kWh_th",3))+
     ' (not occupant comfort loss).</p></article>';
  }).join("");
  const caseRow=(i,field)=>Object.fromEntries(keys.map(k=>[k,d.cases[k].hourly[i][field]]));
  const source="Kerala2040 WP6 authored synthetic 24-hour one-zone physics; NOT measured Kerala hourly load, annual savings, tariffs or a solved 2040 dispatch.";
  mountResearchChart("wp6PowerChart",{
    style:"vertical",source,
    rows:Array.from({length:24},(_,i)=>({
      label:String(i).padStart(2,"0")+":00",
      values:caseRow(i,"grid_kWh_e"),
      note:(i>=17&&i<=21?"Within 17–21 illustrative window. ":"Outside evening window. ")+
        "Grid kWh during ONE hour; direct + charging chiller + discharge pump."
    })),
    series:keys.map(k=>({key:k,label:keyLabels[k],unit:"kWh_e/h",decimals:3}))
  });
  mountResearchChart("wp6RoomChart",{
    style:"vertical",source:source+" All cases share allowed 24–26°C; pre-cooling early target is NOT an occupied discomfort penalty.",
    rows:Array.from({length:24},(_,i)=>({
      label:String(i).padStart(2,"0")+":00",
      values:caseRow(i,"room_C"),
      note:"End-of-hour room temperature; common comfort range 24–26°C."
    })),
    series:keys.map(k=>({key:k,label:keyLabels[k],unit:"°C",decimals:3}))
  });
  mountResearchChart("wp6StoreChart",{
    style:"vertical",source:source+" Only cold-water TES has a storage state; both terminal and initial storage equal zero.",
    rows:Array.from({length:24},(_,i)=>({
      label:String(i).padStart(2,"0")+":00",
      values:{store:d.cases.chilled_water_storage.hourly[i].store_kWh_th},
      note:"End-of-hour cold-energy inventory, includes self-discharge, charge and withdrawal."
    })),
    series:[{key:"store",label:"Thermal stock",unit:"kWh_th",decimals:3}]
  });
  const sensitivity=document.getElementById("wp6Sensitivity");
  if(sensitivity)sensitivity.innerHTML=
    '<div class="table-scroll"><table><thead><tr><th>Cold store (kWh_th)</th>'+
    '<th>Charge COP multiplier</th><th>Grid total (kWh_e)</th>'+
    '<th>Evening peak (kW_e)</th><th>Whole-day peak (kW_e)</th>'+
    '<th>Comfort violations</th></tr></thead><tbody>'+
    d.sensitivity.map(r=>'<tr><td>'+chartEsc(chartNumber(r.storage_kWh_th,"",1))+
       '</td><td>'+chartEsc(chartNumber(r.charging_cop_multiplier,"",2))+
       '</td><td>'+chartEsc(chartNumber(r.total_grid_kWh_e,"",3))+
       '</td><td>'+chartEsc(chartNumber(r.evening_peak_kW_e,"",3))+
       '</td><td>'+chartEsc(chartNumber(r.whole_day_peak_kW_e,"",3))+
       '</td><td>'+r.comfort_violation_hours+'</td></tr>').join("")+
    '</tbody></table></div>';
}
async function loadWP6Pilot(filename){
  const root=document.getElementById("wp6PowerChart");if(!root)return;
  if(filename!=="wp6-cooling-pilot.json"){
    root.textContent="No reproducible WP6 cooling output in this research release.";return;
  }
  try{renderWP6Pilot(await getJSON(filename));}
  catch(err){console.error("WP6 cooling source/physics admission failed",err);
    root.textContent="Cooling experiment failed its scientific checks; results withheld.";
  }
}
