/* Browser-level contract for the actual, built Kerala2040 publication.
   Run: node tests/site.browser.cjs _site
   Requires the optional CI-only Playwright package and Chromium. */
"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const http=require("node:http");
const os=require("node:os");
const path=require("node:path");
const {chromium}=require("playwright");
const root=path.resolve(process.argv[2]||"_site");
const mime={".html":"text/html; charset=utf-8",".js":"application/javascript; charset=utf-8",
  ".css":"text/css; charset=utf-8",".svg":"image/svg+xml",".png":"image/png",
  ".json":"application/json",".webmanifest":"application/manifest+json",
  ".zip":"application/zip",".txt":"text/plain; charset=utf-8"};
const artifactDir=path.join(os.tmpdir(),"kerala2040-browser-qa");
fs.mkdirSync(artifactDir,{recursive:true});
function check(condition,message){assert.ok(condition,message)}
function server(){
  return http.createServer((req,res)=>{
    try{
      const u=new URL(req.url,"http://localhost"),decoded=decodeURIComponent(u.pathname);
      const target=path.resolve(root,"."+ (decoded==="/"?"/index.html":decoded));
      if(target!==root && !target.startsWith(root+path.sep)){
        res.writeHead(403);res.end("Forbidden");return;
      }
      if(!fs.statSync(target).isFile())throw Error("not file");
      const bytes=fs.readFileSync(target);
      res.writeHead(200,{"Content-Type":mime[path.extname(target)]||"application/octet-stream",
        "Content-Length":bytes.length,"Cache-Control":"no-store",
        "X-Content-Type-Options":"nosniff"});
      if(req.method!=="HEAD")res.end(bytes);else res.end();
    }catch{
      res.writeHead(404,{"Content-Type":"text/plain"});res.end("Not found");
    }
  });
}
async function visible(locator,why){
  await locator.waitFor({state:"visible",timeout:20000});
  check(await locator.isVisible(),why);
}
async function main(){
  check(fs.existsSync(path.join(root,"index.html")),"Packaged site missing; build first");
  const httpd=server();await new Promise(resolve=>httpd.listen(0,"127.0.0.1",resolve));
  const address=httpd.address(),base="http://127.0.0.1:"+address.port+"/";
  let browser;
  try{
    browser=await chromium.launch({headless:true});
    const ctx=await browser.newContext({viewport:{width:1440,height:900},
      acceptDownloads:true,serviceWorkers:"block"});
    const page=await ctx.newPage();
    page.setDefaultTimeout(20000);
    const errors=[],failed=[];
    page.on("pageerror",e=>errors.push(String(e)));
    page.on("response",response=>{
      if(response.url().startsWith(base)&&response.status()>=400)
        failed.push(response.status()+" "+response.url());
    });
    await page.goto(base,{waitUntil:"domcontentloaded"});
    try{await page.locator("#headlineMetrics .number-card").first().waitFor({timeout:10000})}
    catch(e){
      const report={errors,failed,url:page.url(),title:await page.title(),
        ready:await page.evaluate(()=>document.readyState),
        metrics:await page.locator("#headlineMetrics").innerText().catch(()=>"(not found)"),
        scripts:await page.locator("script[src]").evaluateAll(es=>es.map(e=>e.src))};
      console.error("PAGE_BOOT_DIAGNOSTIC",JSON.stringify(report));
      await page.screenshot({path:path.join(artifactDir,"failed-boot.png"),fullPage:true});
      throw e;
    }
    check(await page.locator("#headlineMetrics .number-card").count()===4,
      "All four observed-electricity metrics must render");
    const metrics=await page.locator("#headlineMetrics").innerText();
    check(metrics.includes("354")&&metrics.includes("11"),"Do not fabricate missing dates");
    check(await page.locator(".system-node").count()===4,"Four connected-system chapters");
    check(await page.locator("html").evaluate(e=>e.classList.contains("motion-ready")),
      "Animations never activated in ordinary browser preferences");
    const sunAnimation=await page.locator(".scene-sun").evaluate(e=>getComputedStyle(e).animationName);
    check(sunAnimation.includes("monsoon-glow"),"Hero animation is not running: "+sunAnimation);
    await page.locator(".system-story").scrollIntoViewIfNeeded();
    await page.waitForFunction(()=>document.querySelector(".system-story")?.classList.contains("is-visible"));
    const currentAnimation=await page.locator(".system-current span").first().evaluate(e=>getComputedStyle(e).animationName);
    check(currentAnimation.includes("current-flow"),"Illustrated energy current is not animated: "+currentAnimation);
    console.log("PASS ANIMATION: hero sun, observer reveal and system current");
    await visible(page.locator("#homeBalanceArt .balance-track"),"Observed energy balance visual");
    check((await page.locator("#homeBalanceArt").innerText()).includes("22.64 TWh"),
      "Visual observed net-import total missing");
    check((await page.locator("#homeBalanceArt").innerText()).includes("7.21 TWh"),
      "Hydropower must be nested, not double-counted");
    check(await page.locator("#homeMonthlyArt .viz-month-column").count()===12,
      "Homepage monthly comparison must contain twelve observed-period columns");
    check(await page.locator("#homeMonthlyArt .viz-gap-stroke").count()===7,
      "Seven months with unverified daily reports must visibly flag gaps");
    check((await page.locator("#homeMonthlyInsight").innerText()).includes("The mix moves"),
      "Monthly figure is missing its source-derived explanation");
    await page.locator("#homeMonthlyArt").scrollIntoViewIfNeeded();
    await page.waitForFunction(()=>
      document.querySelector("#homeMonthlyArt")?.closest(".viz-card")?.classList.contains("is-visible"));
    const monthMotion=await page.locator("#homeMonthlyArt .viz-net-bar").first()
      .evaluate(el=>getComputedStyle(el).animationName);
    check(monthMotion.includes("rise-observed"),"Observed month bars do not rise: "+monthMotion);
    const hydroSplit=await page.locator("#homeBalanceArt .hydro-subtrack>span")
      .evaluate(el=>getComputedStyle(el).animationName);
    // The balance figure may still be above the active observer threshold.
    check(hydroSplit.includes("grow-share")||hydroSplit==="none",
      "Unexpected hydro subset animation: "+hydroSplit);
    for(const css of [".scene-wave",".scene-vallam",".scene-palm"]){
      const name=await page.locator(css).evaluate(el=>getComputedStyle(el).animationName);
      check(name!=="none","Kerala landscape has no motion: "+css);
    }
    console.log("PASS MOTION: month bars, landscape water, vallam and coconut palms");
    console.log("PASS EDITORIAL HOME: balance totals, hydro subset, twelve month columns and gaps");
    await visible(page.locator("#welcomeCard"),"First-visit welcome");
    check(await page.locator("#main").isVisible(),"Splash cannot block content");
    await page.locator("#welcomeDismiss").click();
    await page.locator("#welcomeCard").waitFor({state:"hidden"});
    await page.screenshot({path:path.join(artifactDir,"homepage-desktop.png"),fullPage:true});
    console.log("PASS home: 4 metrics, 354/365, 11 gaps; welcome dismisses; editorial system visible");

    const expected=process.env.KERALA_RESEARCH_SHA;
    const snapshot=await (await page.request.get(base+"data/site-data.json")).json();
    if(expected)check(snapshot.metadata.research_source_commit===expected,
      "Web content is not pinned to expected research commit");
    check(snapshot.baseline.rows===354&&snapshot.baseline.missing_days_count===11,
      "Observed-day safety contract changed");

    async function route(name){
      await page.locator('.main-nav button[data-route="'+name+'"]').click();
      await visible(page.locator('.view.active[data-view="'+name+'"]'),"Route "+name);
      check(new URL(page.url()).hash==="#"+name,"Incorrect hash route "+name);
    }
    await route("electricity");
    await page.locator("#historyOfficial .research-point").first().waitFor();
    check(await page.locator("#historyOfficial .research-point").count()===5,
      "Official five-year history must render from its own validated data");
    check(await page.locator("#historyMatched .research-point").count()===24,
      "Matched month/day series must contain 12 comparable observations for each FY");
    check(await page.locator("#historyShares .research-point").count()===12,
      "Two distinct net-import/hydel energy-share series must render for six FYs");
    check(await page.locator("#historyPeaks .research-point").count()===12,
      "Peak P95/maximum data must be distinct for six FYs");
    await page.locator("#historyOfficial svg").focus();
    await page.locator("#historyOfficial svg").press("Home");
    check((await page.locator("#historyOfficial .research-chart-readout").innerText()).includes("2020-21"),
      "Historical keyboard readout must name its selected source year");
    await page.locator('#historyShares button[data-series="imports"]').click();
    check(await page.locator("#historyShares .research-point").count()===6,
      "Toggling source series must redraw the plot and preserve source-year counts");
    check((await page.locator("#historyShares .research-chart-source").innerText()).includes("accounting"),
      "Chart must retain energy-boundary caveat after filtering");
    check((await page.locator("#historicalEvidenceTitle").innerText()).includes("electricity story"),
      "Historical chapter absent");
    await page.locator("#electricMonthlyArt svg").focus();
    await page.locator("#electricMonthlyArt svg").press("Home");
    check((await page.locator("#electricMonthlyArt .viz-live-readout").innerText()).includes("2024-04"),
      "Original FY2024–25 monthly graph must support dated keyboard inspection");
    await page.locator("#hydroSeasonArt svg").focus();
    await page.locator("#hydroSeasonArt svg").press("Home");
    check((await page.locator("#hydroSeasonArt .viz-live-readout").innerText()).includes("2024-04"),
      "Original hydro and storage graph must support dated keyboard inspection");
    check(await page.locator("#electricMonthlyArt .viz-month-column").count()===12,
      "Detailed month comparison is incomplete");
    check(await page.locator("#electricMonthlyTable tbody tr").count()===12,
      "Exact monthly figures missing from the data table");
    check(await page.locator("#hydroSeasonArt .viz-gap-guide").count()===11,
      "Hydro and storage chronology must mark all eleven missing dates");
    check(await page.locator("#hydroSeasonArt .viz-hydro-line").count()>1,
      "Hydro line wrongly connects missing dates");
    check(await page.locator("#hydroSeasonArt .viz-storage-line").count()>1,
      "Storage line wrongly connects missing dates");
    check(await page.locator("#hydroSeasonTable tbody tr").count()===354,
      "Exact hydro and reservoir readings not exposed");
    check((await page.locator("#electricMonthInsight").innerText()).includes("net imports"),
      "Electricity month chart must explain the changing mix");
    check((await page.locator("#hydroInsight").innerText()).includes("same reported date"),
      "Hydro chart must contextualize units and the observed low storage date");
    await page.locator("#hydroSeasonArt").scrollIntoViewIfNeeded();
    await page.waitForFunction(()=>
      document.querySelector("#hydroSeasonArt")?.closest(".viz-water-story")?.classList.contains("is-visible"));
    await page.waitForFunction(()=>
      document.querySelector("#hydroSeasonArt .viz-hydro-svg")?.classList.contains("chart-animated"));
    const hydroPaths=await page.locator("#hydroSeasonArt .viz-hydro-line").evaluateAll(elements=>
      elements.map(el=>({length:Number(el.style.getPropertyValue("--draw-length")),
        name:getComputedStyle(el).animationName})));
    check(hydroPaths.length>1&&hydroPaths.every(path=>
      path.length>0&&path.name.includes("trace-observed")),
      "Each observed hydro segment must draw independently of eleven source gaps");
    const storagePaths=await page.locator("#hydroSeasonArt .viz-storage-line").evaluateAll(elements=>
      elements.map(el=>({length:Number(el.style.getPropertyValue("--draw-length")),
        name:getComputedStyle(el).animationName})));
    check(storagePaths.length>1&&storagePaths.every(path=>
      path.length>0&&path.name.includes("trace-observed")),
      "Reservoir chronology must animate only its actual observed segments");
    console.log("PASS EDITORIAL ELECTRICITY: twelve months, observed-day table and two gapped water series");
    await visible(page.locator("#energyChart svg"),"Daily observed electricity chart");
    await page.waitForFunction(()=>
      document.querySelector("#energyChart svg")?.classList.contains("chart-animated"));
    const dateSvg=page.locator("#energyChart svg");
    const trendMotion=await page.locator("#energyChart .chart-line").first()
      .evaluate(el=>getComputedStyle(el).animationName);
    check(trendMotion.includes("trace-observed"),"Daily trend path does not draw: "+trendMotion);
    await dateSvg.focus();await dateSvg.press("Home");
    check((await page.locator(".chart-readout").innerText()).includes("observed SLDC report"),
      "Keyboard readout must identify the source-backed day");
    await dateSvg.press("End");
    check((await page.locator(".chart-readout").innerText()).includes("2025-03"),
      "Keyboard End must inspect the last available observed date");
    console.log("PASS DAILY MOTION: SVG trace and dated keyboard inspection");
    check((await page.locator("#energyChartCaption").innerText()).includes("11 unverified"),
      "Chart obscures gaps");
    await page.locator("#energyMetric").selectOption("net_import_interface_mu");
    check((await page.locator("#energyChart .chart-line").first()
      .evaluate(el=>getComputedStyle(el).animationName)).includes("trace-observed"),
      "Metric changes should reanimate the newly rendered observed line");
    await visible(page.locator("#energyChart svg"),"Filtered energy series");
    const months=await page.locator("#energyMonth option").count();
    check(months>=12,"Historical month filter missing");
    await page.locator("#energyMonth").selectOption({index:1});
    await page.locator("#energyChart svg").focus();
    await page.locator("#energyChart svg").press("Home");
    check((await page.locator(".chart-readout").innerText()).includes("2024-04"),
      "Month selection must update the keyboard chart reading");
    const csvPromise=page.waitForEvent("download");
    await page.locator("#downloadObserved").click();
    const csv=await csvPromise;
    check(csv.suggestedFilename().endsWith(".csv"),"CSV download not triggered");
    console.log("PASS electricity: chart, gaps, metric and month filters, CSV download");

    await route("pathways");
    check(await page.locator("#scenarioList button").count()>=4,
      "Scenario choices missing");
    await page.locator("#scenarioList button").nth(1).click();
    check((await page.locator("#scenarioDetail").innerText()).includes("Not a prediction"),
      "Unsolved scenario must be labelled");
    const scenarioPromise=page.waitForEvent("download");
    await page.locator("#downloadSpecification").click();
    check((await scenarioPromise).suggestedFilename().endsWith(".json"),
      "Scenario download missing");
    console.log("PASS pathways: options and explicitly unsolved specification download");

    await route("atlas");
    await page.locator("#windDistrictChart .research-point").first().waitFor();
    check(await page.locator("#windDistrictChart .research-point").count()===14,
      "Wind district chart must display all fourteen NWIC districts");
    check(await page.locator("#windSlopeChart .research-point").count()===4,
      "Interactive wind slope sensitivity must contain four original thresholds");
    check(await page.locator("#solarMonthChart .research-point").count()===12,
      "Solar source-grid climatology must contain twelve months");
    check(await page.locator("#solarAnnualChart .research-point").count()===14 &&
      await page.locator("#solarSeasonChart .research-point").count()===14,
      "Both district solar source charts must render fourteen values");
    await page.locator('#windDistrictChart .research-chart-pickers select').first().selectOption("8");
    check((await page.locator("#windDistrictChart .research-chart-data").textContent()).includes("≥8 m/s"),
      "Wind speed threshold selector must update its reported source-defined denominator");
    check(await page.locator("#spatialPipeline [data-layer]").count()===7,
      "All seven spatial evidence layers must load");
    const forest=page.locator('#spatialPipeline [data-layer="forest"]');
    await forest.click();
    check(await forest.getAttribute("aria-expanded")==="true","Forest layer did not expand");
    await visible(page.locator("#layer-forest"),"Forest verification detail");
    check((await page.locator("#layer-forest").innerText()).includes("Next verifiable step"),
      "Spatial layer has no follow-up");
    check((await page.locator("#windTerrainEvidence").innerText()).includes("2,00,692"),
      "Executed NIWE resource analysis missing on published atlas");
    check((await page.locator("#windTerrainEvidence").innerText()).includes("8,637"),
      "Wind × DSM sensitivity matrix missing");
    check((await page.locator("#lrisEvidence").innerText()).includes("Service WFS is disabled"),
      "LRIS limitation absent from site");
    check((await page.locator("#districtSourceSummary").innerText()).includes("2,00,692"),
      "Complete NWIC point partition missing on site");
    check((await page.locator("#districtSourceSummary").innerText()).includes("Unassigned centres"),
      "District QA coverage lacks unassigned population label");
    check(await page.locator("#districtChoice option").count()===14,
      "Exactly fourteen original NWIC districts must be selectable");
    await page.locator("#districtChoice").selectOption("Palakkad");
    check((await page.locator("#districtMetrics").innerText()).includes("6.41"),
      "Palakkad modelled source wind median absent");
    check((await page.locator("#districtThresholds").innerText()).includes("6,330"),
      "Palakkad actual source-point sensitivity count absent");
    check((await page.locator("#lrisEvidence").innerText()).includes(
      "zero remain unassigned"),"Historic LRIS gap must be labelled resolved by NWIC");
    check((await page.locator("#districtNormalized").innerText()).includes("27.50%"),
      "Palakkad denominator-normalized wind/terrain share absent");
    check((await page.locator("#districtNormalized").innerText()).includes("23,020") ||
      (await page.locator("#districtNormalized").innerText()).includes("23,020".replace(",","")),
      "Palakkad finite DSM denominator missing");
    await page.locator("#districtChoice").selectOption("Idukki");
    check((await page.locator("#districtNormalized").innerText()).includes("8.08%"),
      "Idukki normalized source-point fraction absent");
    for(const file of ["wind-district-normalized-20260923.svg",
                       "wind-terrain-sensitivity-20260923.svg"]){
      const response=await page.request.get(base+"assets/"+file);
      check(response.status()===200,"Source-safe vector figure missing: "+file);
      check((await response.text()).includes("<svg"),"Figure is not SVG: "+file);
    }
    check((await page.locator("#solarPhaseSummary").innerText()).includes("46,241"),
      "Solar source-pixel exact district partition absent");
    check((await page.locator("#solarPhaseSummary").innerText()).includes("43.60%"),
      "Paired February to July source solar result missing");
    check(await page.locator("#solarDistrictChoice option").count()===14,
      "All fourteen NWIC solar districts must be selectable");
    await page.locator("#solarDistrictChoice").selectOption("Wayanad");
    check((await page.locator("#solarDistrictDetail").innerText()).includes("49.22%"),
      "Paired Wayanad source-pixel seasonality absent");
    await page.locator("#solarDistrictChoice").selectOption("Thiruvananthapuram");
    check((await page.locator("#solarDistrictDetail").innerText()).includes("32.23%"),
      "Paired Thiruvananthapuram source-pixel seasonality absent");
    for(const file of ["solar-phase1-monthly-20260923.svg",
                       "solar-phase1-district-annual-20260923.svg",
                       "solar-phase1-district-seasonality-20260923.svg"]){
      const response=await page.request.get(base+"assets/"+file);
      check(response.status()===200,"Published solar poster vector missing: "+file);
      check((await response.text()).includes("<svg"),"Solar poster file not SVG: "+file);
    }
    console.log("PASS atlas: full native 14-district solar × wind descriptive results, paired seasonality and poster SVGs");

    await route("industry");
    check(await page.locator(".industry-card").count()>=3,"Industry evidence absent");
    await route("workbench");
    check(await page.locator(".research-item").count()===14,
      "All fourteen research streams must render");
    await page.locator("#workbenchSearch").fill("forest");
    check(await page.locator(".research-item").count()>=1,
      "Research filtering not functional");
    await page.locator("#workbenchSearch").fill("");
    await route("audit");
    check(await page.locator(".gate").count()>=2,"Scientific release gates missing");
    check((await page.locator("#auditGates").innerText()).includes("NOT PASSED"),
      "Unresolved gates must be explicit");
    await route("data");
    const downloads=page.locator("#downloadGrid a[href]");
    check(await downloads.count()>=15,"Published evidence library incomplete");
    for(const href of await downloads.evaluateAll(els=>els.map(el=>el.getAttribute("href")))){
      const response=await page.request.get(new URL(href,base).href);
      check(response.status()===200,"Broken published download "+href+" / "+response.status());
    }
    console.log("PASS industry, eleven workstreams, filters, audit and all published downloads");

    for(const theme of ["monsoon","laterite","kasavu"]){
      await page.locator('[data-theme-choice="'+theme+'"]').click();
      check(await page.locator("html").getAttribute("data-theme")===theme,
        "Theme selection broken: "+theme);
      check(await page.locator('[data-theme-choice="'+theme+'"]').getAttribute("aria-pressed")==="true",
        "Selected theme not accessible");
    }
    await route("overview");
    check(await page.locator('.topic-trail a[data-route]').count()===8,
      "Every page must show eight direct, linked topic routes");
    await page.locator('.topic-trail a[data-route="industry"]').click();
    await visible(page.locator('.view.active[data-view="industry"]'),
      "Persistent topic ribbon must navigate to Industry");
    await page.locator('.topic-trail a[data-route="overview"]').click();
    await page.reload({waitUntil:"domcontentloaded"});
    await page.locator("#headlineMetrics .number-card").first().waitFor();
    check(await page.locator("html").getAttribute("data-theme")==="kasavu",
      "Theme not persisted");
    console.log("PASS all three themes and session preference");

    const share=await page.request.get(base+"assets/kerala2040-share.png");
    check(share.status()===200,"Public social image is missing");
    const image=await share.body();
    check(image.subarray(0,8).equals(Buffer.from("89504e470d0a1a0a","hex")),
      "Social card must be PNG, not SVG");
    check(image.readUInt32BE(16)===1200&&image.readUInt32BE(20)===630,
      "Incorrect social thumbnail dimensions");
    check((await page.locator('meta[property="og:image"]').getAttribute("content"))
      ==="https://kerala2040.github.io/assets/kerala2040-share.png",
      "Open Graph source not published");
    console.log("PASS social PNG, metadata, favicon bundle and source SHA");

    const deep=await browser.newContext({reducedMotion:"reduce",viewport:{width:390,height:844},
      acceptDownloads:true});
    const mobile=await deep.newPage();
    const mobileErrors=[];
    mobile.on("pageerror",e=>mobileErrors.push(String(e)));
    await mobile.goto(base+"#atlas",{waitUntil:"domcontentloaded"});
    await mobile.locator("#spatialPipeline [data-layer]").first().waitFor();
    check(!await mobile.locator("#welcomeCard").isVisible(),
      "Direct links/reduced motion must not show splash");
    const overflow=await mobile.evaluate(()=>
      document.documentElement.scrollWidth-document.documentElement.clientWidth);
    check(overflow<=2,"Mobile page overflows horizontally by "+overflow+"px");
    await mobile.locator("#menuToggle").click();
    await visible(mobile.locator("#mobileNav"),"Mobile menu");
    await mobile.locator('#mobileNav button[data-route="industry"]').click();
    await visible(mobile.locator('.view.active[data-view="industry"]'),"Mobile navigation");
    check(!await mobile.locator("#mobileNav").isVisible(),"Mobile menu must close after navigation");
    await mobile.locator("#menuToggle").click();
    await mobile.locator('#mobileNav button[data-route="electricity"]').click();
    await mobile.locator("#energyChart svg").waitFor({state:"visible"});
    check(!await mobile.locator("html").evaluate(el=>el.classList.contains("motion-ready")),
      "Reduced-motion setting must not activate editorial animations");
    check((await mobile.locator("#energyChart .chart-line").first()
      .evaluate(el=>getComputedStyle(el).animationName))==="none",
      "Reduced-motion users must get complete static observed lines");
    await mobile.screenshot({path:path.join(artifactDir,"mobile-industry.png"),fullPage:true});
    check(mobileErrors.length===0,"Mobile JS errors: "+mobileErrors.join(" | "));
    check(errors.length===0,"Desktop JS errors: "+errors.join(" | "));
    check(failed.length===0,"Missing first-party assets: "+failed.join(" | "));
    console.log("PASS mobile, reduced motion, deep link, no overflow, no console/page failures");
    console.log("BROWSER_SMOKE_PASS="+JSON.stringify({
      routes:8,researchStreams:13,spatialLayers:7,downloadLinks:await downloads.count(),
      screenshotDirectory:artifactDir,sourceCommit:expected||"local-branch-build"}));
    await deep.close();await ctx.close();
  }finally{
    if(browser)await browser.close();
    await new Promise(resolve=>httpd.close(resolve));
  }
}
main().catch(e=>{console.error("BROWSER_SMOKE_FAIL",e?.stack||e);process.exitCode=1});
