"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const {
  monthly,
  chronological,
  validateObserved,
  finite,
} = require("../docs/assets/app.js");
const root = path.join(__dirname, "..");
const read = (n) =>
  JSON.parse(fs.readFileSync(path.join(root, "public", n), "utf8"));
const daily = read("daily-balance.json").records,
  baseline = read("baseline-summary.json");
test("published observed accounting reconciles without adding hydro twice", () => {
  validateObserved(daily, baseline);
  const sum = (k) => daily.reduce((a, r) => a + r[k], 0) / 1000;
  assert.ok(
    Math.abs(
      sum("internal_generation_mu") +
        sum("net_import_interface_mu") -
        sum("consumption_mu"),
    ) < 0.00001,
  );
  assert.ok(sum("hydel_total_mu") < sum("internal_generation_mu"));
  assert.throws(() => validateObserved(daily.slice(1), baseline), /coverage/);
  const corrupt = structuredClone(daily);
  corrupt[0].consumption_mu += 2;
  assert.throws(() => validateObserved(corrupt, baseline), /accounting/);
});
test("monthly means preserve actual coverage and use ratio of energy, not average daily shares", () => {
  const m = monthly(daily);
  assert.equal(m.length, 12);
  assert.equal(
    m.reduce((s, r) => s + r.missing, 0),
    11,
  );
  const aug = m.find((r) => r.month === "2024-08");
  assert.equal(aug.observed, 30);
  assert.equal(aug.missing, 1);
  assert.ok(Math.abs(aug.share - 57.5941945) < 0.0001);
  const rows = [
    {
      date: "2024-04-01",
      consumption_mu: 100,
      net_import_interface_mu: 80,
      internal_generation_mu: 20,
    },
    {
      date: "2024-04-02",
      consumption_mu: 20,
      net_import_interface_mu: 0,
      internal_generation_mu: 20,
    },
  ];
  assert.ok(Math.abs(monthly(rows)[0].share - (100 * 80) / 120) < 1e-10);
});
test("daily chronology contains eleven explicit gaps; null and zero stay distinct", () => {
  const r = chronological(daily, "consumption_mu");
  assert.equal(r.length, 365);
  assert.equal(r.filter((x) => x.value === null).length, 11);
  assert.equal(r.find((x) => x.label === "2024-08-12").value, null);
  assert.equal(finite(null), false);
  assert.equal(finite(0), true);
  assert.deepEqual(chronological([], "x"), []);
});
test("every story anchor is real and original identity accompanies live charts", () => {
  const html = fs.readFileSync(path.join(root, "docs/index.html"), "utf8");
  const ids = [...html.matchAll(/id="([^"]+)"/g)].map((x) => x[1]);
  assert.equal(ids.length, new Set(ids).size);
  for (const [, id] of html.matchAll(/href="#([^"]+)"/g))
    assert.ok(ids.includes(id), id);
  assert.match(html, /scene-landscape/);
  assert.match(html, /data-theme-choice="laterite"/);
  assert.match(html, /prefers|canvas/);
  assert.match(html, /Illustrative experiment/);
  assert.match(
    html.replace(/\s+/g, " "),
    /not Kerala’s recommended capacity plan/,
  );
});
test("published economics comparisons retain units, horizon and capacity-plan restriction", () => {
  const d = JSON.parse(
    fs.readFileSync(
      path.join(
        root,
        "data/evidence/models/full_pypsa_import_economics_v1_0_2026_09_26.json",
      ),
      "utf8",
    ),
  );
  assert.equal(d.matrix.cases_solved, 108);
  assert.equal(d.matrix.hours_per_case, 8760);
  assert.equal(d.model_admission.validated_capacity_plan, false);
  const c = d.key_results.reference_FY2030_31_reference_envelope_low_BESS;
  assert.equal(c.full_ATC.unserved_mwh / 1e6, 0.3750303);
  assert.ok(c.ATC_60pct.unserved_mwh > c.ATC_80pct.unserved_mwh);
});
