/* Browser-level contract for the actual, built Kerala2040 publication.
   Run: node tests/site.browser.cjs _site
   Requires the optional CI-only Playwright package and Chromium. */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const http = require("node:http");
const os = require("node:os");
const path = require("node:path");
const { chromium } = require("playwright");
const root = path.resolve(process.argv[2] || "_site");
const mime = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".json": "application/json",
  ".webmanifest": "application/manifest+json",
  ".zip": "application/zip",
  ".txt": "text/plain; charset=utf-8",
};
const artifactDir = path.join(os.tmpdir(), "kerala2040-browser-qa");
fs.mkdirSync(artifactDir, { recursive: true });
function check(condition, message) {
  assert.ok(condition, message);
}
function server() {
  return http.createServer((req, res) => {
    try {
      const u = new URL(req.url, "http://localhost"),
        decoded = decodeURIComponent(u.pathname);
      const target = path.resolve(
        root,
        "." + (decoded === "/" ? "/index.html" : decoded),
      );
      if (target !== root && !target.startsWith(root + path.sep)) {
        res.writeHead(403);
        res.end("Forbidden");
        return;
      }
      if (!fs.statSync(target).isFile()) throw Error("not file");
      const bytes = fs.readFileSync(target);
      res.writeHead(200, {
        "Content-Type":
          mime[path.extname(target)] || "application/octet-stream",
        "Content-Length": bytes.length,
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
      });
      if (req.method !== "HEAD") res.end(bytes);
      else res.end();
    } catch {
      res.writeHead(404, { "Content-Type": "text/plain" });
      res.end("Not found");
    }
  });
}
async function visible(locator, why) {
  await locator.waitFor({ state: "visible", timeout: 20000 });
  check(await locator.isVisible(), why);
}
async function main() {
  const httpd = server();
  await new Promise((resolve) => httpd.listen(0, "127.0.0.1", resolve));
  const base = "http://127.0.0.1:" + httpd.address().port + "/";
  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({
      viewport: { width: 1440, height: 900 },
    });
    const errors = [],
      failed = [];
    page.on("pageerror", (e) => errors.push(String(e)));
    page.on("response", (r) => {
      if (r.url().startsWith(base) && r.status() >= 400) failed.push(r.url());
    });
    await page.goto(base);
    await page.waitForFunction(() =>
      document.querySelector("#sourceCount").textContent.includes("datasets"),
    );
    check(!(await page.locator("#loadError").isVisible()), "No data error");
    await page.locator('[data-connection="leaf"]').click();
    check(
      (await page.locator("#connectionLink").getAttribute("href")) === "#atlas",
      "Concept connection leads to evidence",
    );
    await page.locator("#hydroTransfer").selectOption("60pct");
    check(
      (await page.locator("#hydroStats").innerText()).includes("5,454.820 GWh"),
      "Latest hydro evidence and units",
    );
    await page.locator("#hydroTransfer").selectOption("full");
    check(
      (await page.locator("#hydroStats").innerText()).includes("0.160 GWh"),
      "Full transfer hydro result",
    );
    check(
      (await page.locator(".chart canvas").count()) > 0,
      "Live evidence charts",
    );
    check(
      (await page.locator(".journey-card img").count()) === 4,
      "Original chapter artwork",
    );
    await page.locator("#heroMonth").fill("11");
    check(
      (await page.locator("#heroMonthLabel").innerText()).includes("March"),
      "Month slider updates",
    );
    await page
      .getByRole("button", { name: "Import share", exact: true })
      .click();
    check(
      (await page.locator("#balanceDesc").innerText()).includes("Net imported"),
      "Balance toggle",
    );
    await page.locator("#monthlyChart canvas").press("End");
    check(
      (await page.locator("#monthlyChart .chart-readout").innerText()).includes(
        "2025-03",
      ),
      "Keyboard chart reading",
    );
    await page
      .locator("summary")
      .filter({ hasText: "Daily demand, imports" })
      .click();
    await page
      .locator("#dailyMetric")
      .selectOption("storage_pct_energy_weighted");
    await page.locator("#dailySeason").selectOption("monsoon");
    await page
      .locator("summary")
      .filter({ hasText: "Wind, terrain and threshold" })
      .click();
    await page.locator("#district").selectOption("Palakkad");
    await page.locator("#windThreshold").selectOption("3");
    check(
      (await page.locator("#districtTitle").innerText()) === "Palakkad",
      "District selection",
    );
    check(
      (await page.locator("#thresholdGrid button").count()) === 16,
      "Complete sensitivity grid",
    );
    await page.locator("#pilot").selectOption("bess");
    check(
      (await page.locator("#pilotStats").innerText()).includes("+1.21 kWh"),
      "Storage loss accounting",
    );
    await page.locator("#pilot").selectOption("industry");
    check(
      (await page.locator("#pilotStats").innerText()).includes("11.40 kW"),
      "Industry actual model summary",
    );
    await page.locator("#pilot").selectOption("psp");
    await page.locator("summary").filter({hasText: "Assumptions, exact hourly results and limitations"}).click();
    check(
      (await page.locator("#pilotScope").innerText()).includes(
        "not a Kerala project",
      ),
      "PSP scope",
    );
    await page.locator("#pilot").selectOption("cooling");
    check(
      (await page.locator("#pilotStats").innerText()).includes("+0.70 kWh"),
      "Cooling electricity penalty",
    );
    await page.locator("#pilot").selectOption("integrated");
    check(
      (await page.locator("#pilotStats").innerText()).includes("24.53 kW"),
      "Integrated site peak",
    );
    await page
      .getByRole("button", { name: "Transfer & shortage", exact: true })
      .click();
    check(
      (await page.locator("#modelResults").innerText()).includes("6.600 TWh"),
      "Model units",
    );
    await page
      .getByRole("button", { name: "Price & local supply", exact: true })
      .click();
    await page.locator("#envelope").selectOption("reference");
    check(
      (await page.locator("#modelInsight").innerText()).includes("119.34"),
      "Reference envelope result",
    );
    await page.locator("#sourceSearch").fill("import-economics");
    check(
      (await page.locator("#sourceList .source-row").count()) === 1,
      "Library search",
    );
    await page.locator("#sourceSearch").fill("no-such-source");
    check(
      (await page.locator("#sourceCount").innerText()).startsWith("0 datasets"),
      "Empty search",
    );
    await page.locator("#sourceSearch").fill("");
    await page.locator("#moreSources").click();
    for (const href of await page
      .locator("a[download]")
      .evaluateAll((es) => es.map((e) => e.href)))
      check((await page.request.get(href)).ok(), "Download exists: " + href);
    await page.goto(base + "#workbench");
    check(
      (await page.locator("#workbench").getAttribute("open")) !== null,
      "Legacy deep link opens its section",
    );
    for (const width of [320, 390, 768, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(base + "#overview");
      check(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
        "No horizontal overflow at " + width,
      );
      if (width < 850) {
        await page.locator("#menu").click();
        check(
          await page.locator("#navigation").isVisible(),
          "Mobile navigation opens",
        );
        await page.locator('#navigation a[href="#pathways"]').click();
        check(
          (await page.locator("#menu").getAttribute("aria-expanded")) ===
            "false",
          "Mobile menu closes",
        );
      }
      await page.screenshot({
        path: path.join(artifactDir, "v2-" + width + ".png"),
      });
    }
    await page.locator('[data-theme-choice="monsoon"]').click();
    check(
      (await page.locator("html").getAttribute("data-theme")) === "monsoon",
      "Dark theme",
    );
    await page.screenshot({ path: path.join(artifactDir, "v2-monsoon.png") });
    await page.locator('[data-theme-choice="laterite"]').click();
    check(
      (await page.locator("html").getAttribute("data-theme")) === "laterite",
      "Laterite theme",
    );
    await page.reload();
    await page.waitForFunction(
      () => document.documentElement.dataset.theme === "laterite",
    );
    check(errors.length === 0, JSON.stringify(errors));
    check(failed.length === 0, JSON.stringify(failed));
    const broken = await browser.newPage();
    await broken.route("**/data/daily-balance.json", (r) =>
      r.fulfill({ status: 503, body: "Unavailable" }),
    );
    await broken.goto(base);
    await visible(broken.locator("#loadError"), "Fetch error is actionable");
    check(
      await broken.getByRole("button", { name: "Reload evidence" }).isVisible(),
      "Retry control",
    );
    console.log(
      "V2 browser checks passed: narrative, charts, controls, links, data failures and responsive layouts.",
    );
  } finally {
    if (browser) await browser.close();
    await new Promise((resolve) => httpd.close(resolve));
  }
}
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

