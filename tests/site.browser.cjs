/* Real Chromium smoke test of the packaged, locally served public site.
 * Fails CI for broken startup, routes, missing assets, HTTP errors, downloads,
 * and horizontal overflow. Never hits external source links or creates data. */
"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {chromium}=require("playwright");

const base=process.env.SITE_BASE_URL||"http://127.0.0.1:8765/";
const out=process.env.SITE_SCREENSHOT_DIR||path.join(process.cwd(),"site-browser-artifacts");
fs.mkdirSync(out,{recursive:true});
const results=[];
const origin=new URL(base).origin;
async function run(){
  const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
  const failures=[];
  try{
    const context=await browser.newContext({viewport:{width:1440,height:900},acceptDownloads:true});
    const page=await context.newPage();
    page.on("pageerror",error=>failures.push("JS exception: "+error.message));
    page.on("response",response=>{
      if(response.url().startsWith(origin)&&response.status()>=400)
        failures.push("HTTP "+response.status()+" "+response.url());
    });
    page.on("requestfailed",request=>{
      if(request.url().startsWith(origin))
        failures.push("Asset/request failed: "+request.url()+" "+request.failure()?.errorText);
    });
    await page.goto(base,{waitUntil:"domcontentloaded"});
    try{
      await page.waitForFunction(()=>document.querySelector("#headlineMetrics")
        ?.textContent.includes("73.8%"),null,{timeout:14000});
    }catch(error){
      console.error("STARTUP_DIAGNOSTIC",JSON.stringify({
        failures,
        page:await page.evaluate(()=>({
          title:document.title,
          metrics:document.querySelector("#headlineMetrics")?.textContent,
          origin:document.querySelector("#dataOrigin")?.textContent,
          script:[...document.scripts].map(x=>x.src),
          css:[...document.querySelectorAll('link[rel="stylesheet"]')].map(x=>x.href),
          state:document.readyState,
        })),
      }));
      await page.screenshot({path:path.join(out,"00-startup-failure.png"),fullPage:true});
      throw error;
    }
    await page.locator("#headlineMetrics .number-card").first().waitFor();
    assert.match(await page.title(),/Kerala2040/);
    assert.match(await page.locator("#heroCoverage").innerText(),/354 \/ 365/);
    assert.equal(await page.locator("#welcomeCard").isVisible(),true);
    assert.equal(await page.locator(".view.active").getAttribute("data-view"),"overview");
    assert.equal(await page.locator("body").evaluate(e=>getComputedStyle(e).overflow),"visible");
    await page.locator("#welcomeDismiss").click();
    await page.locator("#welcomeCard").waitFor({state:"hidden",timeout:5000});
    results.push("Desktop: full startup, audited metrics, dismissible welcome and nonblocking page");

    const content=await page.locator("head").evaluate(head=>{
      const attr=(selector,field)=>head.querySelector(selector)?.getAttribute(field);
      return {og:attr('meta[property="og:image"]',"content"),
        twitter:attr('meta[name="twitter:card"]',"content"),
        css:head.querySelector('link[rel="stylesheet"]')?.href,
        app:head.querySelector("script[src]")?.src};
    });
    assert.equal(content.og,"https://kerala2040.github.io/assets/kerala2040-share.png");
    assert.equal(content.twitter,"summary_large_image");
    assert.match(content.css,/kerala\.[a-f0-9]{12}\.css/);
    assert.match(content.app,/app\.[a-f0-9]{12}\.js/);
    for(const asset of ["assets/kerala2040-share.png","assets/kerala2040-touch.png",
      "assets/mark.svg","assets/icons.svg","assets/chapter-electric.svg",
      "assets/chapter-land.svg","assets/chapter-pathways.svg",
      "assets/chapter-industry.svg","manifest.webmanifest",
      "data/site-data.json","data/audit-readiness.json","data/research-ledger.json",
      "data/daily-balance.json"]){
      const response=await page.request.get(new URL(asset,base).href);
      assert.equal(response.status(),200,asset+" must exist");
      if(asset.endsWith(".png")){
        const bytes=await response.body();
        assert.equal(bytes.subarray(0,8).toString("hex"),"89504e470d0a1a0a");
        const expected=asset.includes("share")?[1200,630]:[180,180];
        assert.deepEqual([bytes.readUInt32BE(16),bytes.readUInt32BE(20)],expected);
      }
    }
    results.push("Assets: hashed CSS/JS; source-linked bundles; PNG share 1200×630 and touch 180×180; all four SVG illustrations");

    await page.screenshot({path:path.join(out,"01-desktop-overview.png"),fullPage:true,animations:"disabled"});
    await page.locator('.hero-actions [data-route="electricity"]').click();
    assert.equal(await page.locator(".view.active").getAttribute("data-view"),"electricity");
    assert.equal(await page.locator("#energyChart svg").count(),1);
    assert.match(await page.locator("#energyChartCaption").innerText(),/11 unverified days/);
    await page.locator("#energyMetric").selectOption("net_import_interface_mu");
    assert.match(await page.locator("#energyChartCaption").innerText(),/Net imports/);
    await page.locator("#energyMonth").selectOption("2024-09");
    assert.match(await page.locator("#energyChartCaption").innerText(),/2 unverified days/);
    await page.locator("#energyMonth").selectOption("all");
    const csvPromise=page.waitForEvent("download");
    await page.locator("#downloadObserved").click();
    const csv=await csvPromise;
    assert.match(csv.suggestedFilename(),/kerala2040-observed-all\.csv/);
    await page.locator(".data-details summary").click();
    assert.ok(await page.locator("#energyTable tbody tr").count()>=350);
    results.push("Electricity: navigation, audited chart, series and month filters, missing-day gaps, 354 source records and CSV download");
    await page.screenshot({path:path.join(out,"02-electricity.png"),fullPage:true,animations:"disabled"});

    await page.locator('.main-nav [data-route="pathways"]').click();
    assert.equal(await page.locator("#scenarioList [data-scenario]").count(),5);
    await page.locator("#scenarioList [data-scenario]").nth(1).click();
    assert.match(await page.locator("#scenarioDetail").innerText(),/Not a prediction/);
    const jsonPromise=page.waitForEvent("download");
    await page.locator("#downloadSpecification").click();
    assert.match((await jsonPromise).suggestedFilename(),/research-question\.json$/);
    results.push("Pathways: scenario switching and unsolved-specification download");

    await page.locator('.main-nav [data-route="atlas"]').click();
    assert.equal(await page.locator('#spatialPipeline [data-layer]').count(),5);
    const layer=page.locator('#spatialPipeline [data-layer]').first();
    await layer.click();
    assert.equal(await layer.getAttribute("aria-expanded"),"true");
    const detail=page.locator('#spatialPipeline .land-detail').first();
    assert.equal(await detail.isVisible(),true);
    await layer.click();
    assert.equal(await detail.isVisible(),false);
    assert.match(await page.locator('.view.active').innerText(),/No buildable-land or MW estimate/);
    results.push("Ecology: five source layers, expandable evidence, no invented area/MW");

    await page.locator('.main-nav [data-route="industry"]').click();
    assert.ok(await page.locator("#industryCases .industry-card").count()>=1);
    results.push("Industry: case cards sourced from bundle");

    await page.locator('.main-nav [data-route="workbench"]').click();
    assert.equal(await page.locator("#workbenchCards .research-item").count(),11);
    await page.locator("#workbenchSearch").fill("forest");
    assert.ok(await page.locator("#workbenchCards .research-item").count()>=1);
    await page.locator("#workbenchSearch").fill("");
    const firstDetails=page.locator("#workbenchCards details").first();
    await firstDetails.locator("summary").click();
    assert.equal(await firstDetails.getAttribute("open"),"");
    results.push("Research: 11 records, search, expandable evidence");

    await page.locator('.main-nav [data-route="audit"]').click();
    assert.ok(await page.locator("#auditGates .gate").count()>=2);
    assert.ok(await page.locator("#auditFindings .finding").count()>=1);
    await page.locator("#auditPriority").selectOption("P0");
    assert.match(await page.locator("#auditCount").innerText(),/tracked acquisitions/);
    await page.locator("#auditSearch").fill("forest");
    assert.ok(await page.locator("#auditCount").innerText());
    results.push("Audit: release gates, priority and text filtering");

    await page.locator('.main-nav [data-route="data"]').click();
    assert.ok(await page.locator("#sourceRegistry .source-entry").count()>=8);
    const registryCount=await page.locator("#sourceRegistry .source-entry").count();
    await page.locator("#sourceSearch").fill("SLDC");
    assert.ok((await page.locator("#sourceRegistry .source-entry").count())<registryCount);
    await page.locator("#sourceSearch").fill("");
    assert.ok(await page.locator('#downloadGrid a[href="data/site-data.json"]').count());
    results.push("Sources: registry search and published source downloads");

    await page.goBack({waitUntil:"domcontentloaded"});
    assert.equal(await page.locator(".view.active").getAttribute("data-view"),"audit");
    await page.reload({waitUntil:"domcontentloaded"});
    assert.equal(await page.locator(".view.active").getAttribute("data-view"),"audit");
    assert.equal(await page.locator("#welcomeCard").isVisible(),false);
    results.push("History: back, page refresh and deep link retain the chosen route; welcome does not block");

    for(const theme of ["monsoon","laterite","kasavu"]){
      await page.locator('[data-theme-choice="'+theme+'"]').click();
      assert.equal(await page.locator("html").getAttribute("data-theme"),theme);
      assert.equal(await page.locator('[data-theme-choice="'+theme+'"]').getAttribute("aria-pressed"),"true");
    }
    await page.reload({waitUntil:"domcontentloaded"});
    assert.equal(await page.locator("html").getAttribute("data-theme"),"kasavu");
    results.push("Appearance: all 3 themes, ARIA pressed states, preference persistence");

    const mobile=await browser.newContext({viewport:{width:390,height:844},
      deviceScaleFactor:2,isMobile:true,hasTouch:true,reducedMotion:"reduce"});
    const phone=await mobile.newPage();
    phone.on("pageerror",error=>failures.push("Mobile JS exception: "+error.message));
    await phone.goto(new URL("#overview",base).href,{waitUntil:"domcontentloaded"});
    await phone.waitForFunction(()=>document.querySelector("#headlineMetrics")
      ?.textContent.includes("73.8%"),{timeout:30000});
    assert.equal(await phone.locator("#welcomeCard").isVisible(),false);
    assert.equal(await phone.locator("html").evaluate(el=>el.classList.contains("motion-ready")),false);
    await phone.locator("#menuToggle").click();
    assert.equal(await phone.locator("#mobileNav").isVisible(),true);
    await phone.locator('#mobileNav [data-route="atlas"]').click();
    assert.equal(await phone.locator(".view.active").getAttribute("data-view"),"atlas");
    assert.equal(await phone.locator("#mobileNav").isVisible(),false);
    for(const route of ["overview","electricity","pathways","atlas","industry","workbench","audit","data"]){
      await phone.goto(new URL("#"+route,base).href,{waitUntil:"domcontentloaded"});
      await phone.waitForFunction(route=>document.querySelector(".view.active")?.dataset.view===route,route);
      const dims=await phone.evaluate(()=>({
        doc:document.documentElement.scrollWidth,
        viewport:document.documentElement.clientWidth,
        route:document.querySelector(".view.active")?.dataset.view
      }));
      assert.ok(dims.doc<=dims.viewport+2,route+" horizontal overflow "+
        JSON.stringify(dims));
    }
    await phone.goto(new URL("#overview",base).href,{waitUntil:"domcontentloaded"});
    await phone.screenshot({path:path.join(out,"03-mobile-overview.png"),
      fullPage:true,animations:"disabled"});
    await mobile.close();
    results.push("Mobile 390px: all eight routes, menu open/close, no horizontal overflow, reduced motion and screenshots");
    assert.deepEqual(failures,[]);
    await context.close();
    console.log("BROWSER_SMOKE_OK="+JSON.stringify(results));
    console.log("BROWSER_SCREENSHOTS="+out);
  }finally{
    await browser.close();
  }
}
run().catch(error=>{console.error("BROWSER_SMOKE_FAILED",error.stack||error);process.exitCode=1});
