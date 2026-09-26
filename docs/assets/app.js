/* Kerala2040 v2. First-party Canvas plots; source records remain inspectable. */
(function () {
  "use strict";
  const finite = (v) => typeof v === "number" && Number.isFinite(v);
  const fmt = (v, n = 1) =>
    finite(v)
      ? (Object.is(v, -0) ? 0 : v).toLocaleString("en-IN", {
          minimumFractionDigits: n,
          maximumFractionDigits: n,
        })
      : "Unavailable";
  function monthly(records) {
    const groups = new Map();
    for (const r of records) {
      const key = r.date.slice(0, 7);
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(r);
    }
    return [...groups]
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([month, rows]) => {
        const sum = (k) =>
          rows.every((r) => finite(r[k]))
            ? rows.reduce((a, r) => a + r[k], 0)
            : null;
        const consumption = sum("consumption_mu"),
          imports = sum("net_import_interface_mu"),
          internal = sum("internal_generation_mu");
        const days = new Date(
          Number(month.slice(0, 4)),
          Number(month.slice(5)),
          0,
        ).getDate();
        return {
          month,
          observed: rows.length,
          missing: days - rows.length,
          consumption: consumption / rows.length,
          imports: imports / rows.length,
          internal: internal / rows.length,
          share: (100 * imports) / consumption,
        };
      });
  }
  function chronological(records, key) {
    const byDate = new Map(records.map((r) => [r.date, r]));
    if (!records.length) return [];
    const start = new Date(records[0].date + "T00:00:00Z"),
      end = new Date(records.at(-1).date + "T00:00:00Z"),
      out = [];
    for (let d = start; d <= end; d.setUTCDate(d.getUTCDate() + 1)) {
      const date = d.toISOString().slice(0, 10);
      out.push({
        label: date,
        value: finite(byDate.get(date)?.[key]) ? byDate.get(date)[key] : null,
      });
    }
    return out;
  }
  function validateObserved(d, b) {
    if (d.length !== b.rows || new Set(d.map((x) => x.date)).size !== d.length)
      throw Error(
        "Observation coverage does not match the published baseline.",
      );
    if (
      d.some(
        (r) =>
          !finite(r.consumption_mu) ||
          !finite(r.net_import_interface_mu) ||
          !finite(r.internal_generation_mu) ||
          Math.abs(
            r.consumption_mu -
              r.net_import_interface_mu -
              r.internal_generation_mu,
          ) > 0.05,
      )
    )
      throw Error("Electricity accounting check failed.");
    const total = d.reduce((a, r) => a + r.consumption_mu, 0) / 1000;
    if (Math.abs(total - b.consumption_twh) > 0.001)
      throw Error("Observation totals do not match the published baseline.");
  }
  if (typeof module !== "undefined")
    module.exports = { monthly, chronological, validateObserved, finite };
  if (typeof document === "undefined") return;
  const $ = (id) => document.getElementById(id),
    text = (id, value) => {
      $(id).textContent = value;
    };
  const colours = () => {
    const c = getComputedStyle(document.documentElement);
    return [
      "--green",
      "--gold",
      "--clay",
      "--muted",
      "--line",
      "--ink",
      "--paper",
    ].map((k) => c.getPropertyValue(k).trim());
  };
  const charts = new Map();
  class Plot {
    constructor(id, config) {
      this.el = $(id);
      this.config = config;
      this.index = 0;
      this.el.replaceChildren();
      this.canvas = document.createElement("canvas");
      this.canvas.tabIndex = 0;
      this.canvas.setAttribute("role", "img");
      this.canvas.setAttribute(
        "aria-label",
        config.title + ". Use left and right arrow keys to inspect values.",
      );
      this.readout = document.createElement("div");
      this.readout.className = "chart-readout";
      this.readout.setAttribute("aria-live", "polite");
      this.el.append(this.canvas, this.readout);
      this.canvas.addEventListener("keydown", (e) => {
        if (["ArrowLeft", "ArrowRight", "Home", "End"].includes(e.key)) {
          e.preventDefault();
          this.index =
            e.key === "Home"
              ? 0
              : e.key === "End"
                ? this.config.rows.length - 1
                : Math.max(
                    0,
                    Math.min(
                      this.config.rows.length - 1,
                      this.index + (e.key === "ArrowRight" ? 1 : -1),
                    ),
                  );
          this.describe();
          this.draw();
        }
      });
      this.canvas.addEventListener("pointermove", (e) => {
        const r = this.canvas.getBoundingClientRect();
        if (this.config.kind === "scatter") {
          const p = this.points || [];
          let best = Infinity;
          p.forEach((p, i) => {
            let z =
              (p.x - e.clientX + r.left) ** 2 + (p.y - e.clientY + r.top) ** 2;
            if (z < best) {
              best = z;
              this.index = i;
            }
          });
        } else
          this.index = Math.max(
            0,
            Math.min(
              this.config.rows.length - 1,
              Math.floor(
                ((e.clientX - r.left - 52) / (r.width - 72)) *
                  this.config.rows.length,
              ),
            ),
          );
        this.describe();
        this.draw();
      });
      new ResizeObserver(() => this.draw()).observe(this.el);
      this.describe();
      this.draw();
    }
    describe() {
      const c = this.config,
        r = c.rows[this.index];
      if (!r) return;
      this.readout.textContent = c.describe
        ? c.describe(r)
        : `${r.label} · ${c.series.map((s) => `${s.name}: ${fmt(r[s.key], s.decimals ?? 1)} ${c.unit || ""}`).join(" · ")}`;
    }
    draw() {
      const c = this.config,
        canvas = this.canvas,
        w = this.el.clientWidth,
        h = this.el.clientHeight;
      if (w < 30 || h < 30) return;
      const scale = Math.min(devicePixelRatio || 1, 2);
      canvas.width = w * scale;
      canvas.height = h * scale;
      canvas.style.height = h + "px";
      const ctx = canvas.getContext("2d");
      ctx.scale(scale, scale);
      const [green, gold, clay, muted, line, ink] = colours(),
        pal = [green, gold, clay];
      const dark = this.el.closest(".industry-section");
      if (dark) pal.splice(0, 3, "#95c8a5", "#e2bb70", "#e89b7e");
      const fg = dark ? "#e5e8d9" : muted;
      ctx.clearRect(0, 0, w, h);
      ctx.font = '11px "DM Sans", sans-serif';
      const left = 52,
        right = w - 20,
        top = w < 450 && c.series.length > 1 ? 57 : 39,
        bottom = h - 45,
        pw = right - left,
        ph = bottom - top,
        n = c.rows.length;
      const max =
        c.max ||
        Math.max(
          1,
          ...c.rows.map((r) =>
            c.stacked
              ? c.series.reduce(
                  (v, s) => v + (finite(r[s.key]) ? r[s.key] : 0),
                  0,
                )
              : Math.max(
                  ...c.series.map((s) => (finite(r[s.key]) ? r[s.key] : 0)),
                ),
          ),
        ) * 1.12;
      ctx.fillStyle = fg;
      ctx.fillText(c.unit || "", left, 14);
      ctx.textAlign = "right";
      for (let i = 0; i <= 4; i++) {
        let v = (max * i) / 4,
          y = bottom - (ph * i) / 4;
        ctx.strokeStyle = dark ? "#627569" : line;
        ctx.lineWidth = 0.6;
        ctx.beginPath();
        ctx.moveTo(left, y);
        ctx.lineTo(right, y);
        ctx.stroke();
        ctx.fillText(fmt(v, max <= 10 ? 1 : 0), left - 9, y + 4);
      }
      ctx.textAlign = "left";
      if (c.kind === "scatter") {
        const xmax = c.xmax || 20;
        this.points = [];
        c.rows.forEach((r, i) => {
          let x = left + (pw * r.x) / xmax,
            y = bottom - (ph * r.y) / max;
          this.points.push({ x, y });
          ctx.fillStyle = i === this.index ? gold : green;
          ctx.beginPath();
          ctx.arc(x, y, i === this.index ? 8 : 5, 0, Math.PI * 2);
          ctx.fill();
          if (i === this.index) {
            ctx.fillStyle = fg;
            ctx.textAlign = x > w * 0.6 ? "right" : "left";
            ctx.fillText(r.label, x + (x > w * 0.6 ? -12 : 12), y - 8);
          }
        });
        ctx.textAlign = "center";
        for (let i = 0; i <= 4; i++)
          ctx.fillText(
            fmt((xmax * i) / 4, 0),
            left + (pw * i) / 4,
            bottom + 20,
          );
        ctx.fillText(c.xunit || "", left + pw / 2, h - 5);
        return;
      }
      const step = pw / n,
        x = (i) => left + step * (i + 0.5);
      if (c.kind === "line") {
        c.series.forEach((s, j) => {
          ctx.strokeStyle = pal[j % 3];
          ctx.lineWidth = 2;
          ctx.beginPath();
          let pen = false;
          c.rows.forEach((r, i) => {
            if (!finite(r[s.key])) {
              pen = false;
              return;
            }
            let y = bottom - (ph * r[s.key]) / max;
            if (pen) ctx.lineTo(x(i), y);
            else ctx.moveTo(x(i), y);
            pen = true;
          });
          ctx.stroke();
        });
      } else
        c.rows.forEach((r, i) => {
          let offset = 0;
          c.series.forEach((s, j) => {
            if (!finite(r[s.key])) return;
            let bh = (ph * r[s.key]) / max,
              bw = c.stacked ? step * 0.62 : (step * 0.7) / c.series.length,
              bx = c.stacked ? x(i) - bw / 2 : x(i) - step * 0.35 + j * bw;
            ctx.globalAlpha = i === this.index ? 1 : 0.78;
            ctx.fillStyle = pal[j % 3];
            ctx.fillRect(bx, bottom - offset - bh, Math.max(1, bw - 1), bh);
            if (c.stacked) offset += bh;
          });
          ctx.globalAlpha = 1;
          if (r.missing) {
            ctx.fillStyle = gold;
            ctx.fillRect(x(i) - 4, bottom + 3, 8, 3);
          }
        });
      ctx.strokeStyle = gold;
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 4]);
      ctx.beginPath();
      ctx.moveTo(x(this.index), top);
      ctx.lineTo(x(this.index), bottom);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = fg;
      ctx.textAlign = "center";
      const every = Math.max(1, Math.ceil(n / (w < 450 ? 6 : 12)));
      c.rows.forEach((r, i) => {
        if (i % every === 0)
          ctx.fillText(r.short || r.label, x(i), bottom + 22);
      });
      ctx.textAlign = "left";
      let lx = left;
      for (let j = 0; j < c.series.length; j++) {
        const name = c.series[j].name;
        ctx.fillStyle = pal[j % 3];
        let ly = w < 450 ? 23 + j * 16 : 23;
        if (w < 450) lx = left;
        ctx.fillRect(lx, ly, 12, 3);
        ctx.fillStyle = fg;
        ctx.fillText(name, lx + 17, ly + 5);
        lx += ctx.measureText(name).width + 40;
      }
    }
  }
  function plot(id, c) {
    if (charts.has(id)) {
      charts.get(id).config = c;
      charts.get(id).index = 0;
      charts
        .get(id)
        .canvas.setAttribute(
          "aria-label",
          c.title + ". Use left and right arrow keys to inspect values.",
        );
      charts.get(id).describe();
      charts.get(id).draw();
    } else charts.set(id, new Plot(id, c));
  }
  function table(id, headers, rows) {
    const t = document.createElement("table"),
      head = document.createElement("thead"),
      tr = document.createElement("tr");
    headers.forEach((h) => {
      const th = document.createElement("th");
      th.textContent = h;
      th.scope = "col";
      tr.append(th);
    });
    head.append(tr);
    t.append(head);
    const body = document.createElement("tbody");
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      row.forEach((v) => {
        const td = document.createElement("td");
        td.textContent = v;
        tr.append(td);
      });
      body.append(tr);
    });
    t.append(body);
    $(id).replaceChildren(t);
  }
  const safeText = (s) => String(s || "").replaceAll("\ufffd", "–");
  let data,
    months,
    balanceMode = "energy",
    modelMode = "price",
    showAll = false;
  async function get(name) {
    const controller = new AbortController(),
      timer = setTimeout(() => controller.abort(), 20000);
    try {
      const r = await fetch("data/" + name, { signal: controller.signal });
      if (!r.ok) throw Error(name + " is unavailable (" + r.status + ").");
      return await r.json();
    } finally {
      clearTimeout(timer);
    }
  }
  function ring() {
    if (!months) return;
    let i = Number($("heroMonth").value),
      r = months[i],
      canvas = $("balanceRing"),
      w = canvas.clientWidth,
      h = canvas.clientHeight,
      s = Math.min(devicePixelRatio || 1, 2);
    canvas.width = w * s;
    canvas.height = h * s;
    let c = canvas.getContext("2d");
    c.scale(s, s);
    const [green, gold, , muted, line] = colours();
    let radius = Math.min(w, h) / 2 - 24;
    c.lineWidth = 27;
    c.lineCap = "butt";
    let a = -Math.PI / 2,
      gap = 0.025;
    [
      [r.share / 100, gold],
      [(100 - r.share) / 100, green],
    ].forEach(([fraction, color]) => {
      c.beginPath();
      c.strokeStyle = color;
      c.arc(w / 2, h / 2, radius, a + gap, a + Math.PI * 2 * fraction - gap);
      c.stroke();
      a += Math.PI * 2 * fraction;
    });
    c.strokeStyle = line;
    c.lineWidth = 1;
    for (let k = 0; k < 60; k++) {
      let a = (k * Math.PI) / 30;
      c.beginPath();
      c.moveTo(
        w / 2 + Math.cos(a) * (radius + 21),
        h / 2 + Math.sin(a) * (radius + 21),
      );
      c.lineTo(
        w / 2 + Math.cos(a) * (radius + 25),
        h / 2 + Math.sin(a) * (radius + 25),
      );
      c.stroke();
    }
    text("ringValue", fmt(r.share) + "%");
    const label = new Date(r.month + "-01T12:00:00Z").toLocaleDateString(
      "en-GB",
      { month: "long", year: "numeric", timeZone: "UTC" },
    );
    text("heroMonthLabel", label);
    text(
      "heroScope",
      `${r.observed} observed days · ${r.missing} missing reports · ${fmt(r.consumption)} MU per observed day`,
    );
    canvas.setAttribute(
      "aria-label",
      `${label}: ${fmt(r.share)}% net imports, ${fmt(100 - r.share)}% in-state generation, ${r.observed} observed days.`,
    );
  }
  function renderMonthly() {
    let rows = months.map((r) => ({
      ...r,
      label: r.month,
      short: new Date(r.month + "-01").toLocaleString("en", { month: "short" }),
    }));
    plot("monthlyChart", {
      title: "Monthly observed electricity balance",
      rows,
      kind: "bar",
      stacked: balanceMode === "energy",
      unit:
        balanceMode === "energy"
          ? "MU / observed day"
          : "% of observed consumption",
      max: balanceMode === "share" ? 100 : undefined,
      series:
        balanceMode === "energy"
          ? [
              { key: "internal", name: "In-state generation" },
              { key: "imports", name: "Net imports" },
            ]
          : [{ key: "share", name: "Net imports" }],
      describe: (r) =>
        `${r.label} · ${fmt(r.share)}% net imports · ${fmt(r.internal)} MU in-state + ${fmt(r.imports)} MU imports per observed day · ${r.observed} days observed, ${r.missing} missing`,
    });
    text(
      "balanceDesc",
      balanceMode === "energy"
        ? "Average energy per observed day, in million units (MU). One MU = one million kWh."
        : "Net imported energy divided by recorded consumption in each month. Amber marks indicate missing reports.",
    );
    const lo = months.reduce((a, b) => (a.share < b.share ? a : b)),
      hi = months.reduce((a, b) => (a.share > b.share ? a : b));
    text(
      "monthInsight",
      `The observed import share ranges from ${fmt(lo.share)}% in ${lo.month} to ${fmt(hi.share)}% in ${hi.month}. Timing matters as much as the annual balance.`,
    );
    table(
      "monthlyTable",
      [
        "Month",
        "Observed days",
        "Missing",
        "In-state MU/day",
        "Imports MU/day",
        "Import %",
      ],
      months.map((r) => [
        r.month,
        r.observed,
        r.missing,
        fmt(r.internal, 2),
        fmt(r.imports, 2),
        fmt(r.share, 2),
      ]),
    );
  }
  function renderDaily() {
    let key = $("dailyMetric").value,
      season = $("dailySeason").value;
    let records = data.daily.records.filter((r) => {
      let m = Number(r.date.slice(5, 7));
      return (
        season === "all" ||
        (season === "summer" && [3, 4, 5].includes(m)) ||
        (season === "monsoon" && [6, 7, 8, 9].includes(m)) ||
        (season === "other" && [10, 11, 12, 1, 2].includes(m))
      );
    });
    const rows = chronological(records, key).map((r) => ({
      ...r,
      value:
        key === "import_share" && finite(r.value) ? 100 * r.value : r.value,
      short: r.label.slice(5),
    }));
    plot("dailyChart", {
      title: "Daily observations with missing-date gaps",
      rows,
      kind: "line",
      unit: key.includes("share") || key.includes("pct") ? "%" : "MU / day",
      series: [
        {
          key: "value",
          name: $("dailyMetric").selectedOptions[0].textContent.split(" · ")[0],
        },
      ],
    });
  }
  function renderResources() {
    const solar = data.ledger.solar_phase1.aggregate.statewide;
    plot("solarChart", {
      title: "Monthly median source-grid solar yield",
      rows: Object.entries(
        solar.monthly_marginal_pixel_median_PVOUT_kWh_kWp_day,
      ).map(([label, value]) => ({ label, value })),
      kind: "line",
      unit: "kWh / kWp / day",
      series: [{ key: "value", name: "Solar yield" }],
    });
    const districts = data.ledger.nwic_district.districts;
    $("district").replaceChildren(
      ...districts.map((d) => {
        const o = document.createElement("option");
        o.value = d.district;
        o.textContent = d.district;
        return o;
      }),
    );
    $("district").value = "Idukki";
    renderDistrict();
  }
  function renderDistrict() {
    const rows = data.ledger.nwic_district.districts,
      district = rows.find((d) => d.district === $("district").value),
      wi = +$("windThreshold").value,
      si = +$("slopeThreshold").value;
    plot("districtChart", {
      title: "District median wind and surface slope",
      kind: "scatter",
      rows: rows.map((d) => ({
        label: d.district,
        x: d.slope_median_degrees,
        y: d.wind_speed_median_m_s,
      })),
      unit: "Wind at 150 m · m/s",
      xunit: "Median surface slope · degrees",
      xmax: 20,
      max: 8,
      series: [{ key: "y", name: "Wind" }],
      describe: (r) =>
        `${r.label} · median wind ${fmt(r.y, 2)} m/s · median surface slope ${fmt(r.x, 2)}°`,
    });
    const p = charts.get("districtChart");
    p.index = rows.indexOf(district);
    p.describe();
    p.draw();
    text("districtTitle", district.district);
    text(
      "districtResult",
      `${fmt(district.threshold_matrix[wi][si], 0)} point centres`,
    );
    text(
      "districtScope",
      `Of ${fmt(district.slope_finite, 0)} centres with slope data, ${fmt((100 * district.threshold_matrix[wi][si]) / district.slope_finite)}% meet these hypothetical thresholds. ${district.slope_missing} centres have no slope sample.`,
    );
    $("thresholdGrid").replaceChildren();
    district.threshold_matrix.forEach((row, i) =>
      row.forEach((v, j) => {
        const b = document.createElement("button");
        b.textContent = fmt(v, 0);
        b.setAttribute(
          "aria-label",
          `Wind at least ${5 + i} m/s, slope at most ${[5, 10, 15, 20][j]} degrees: ${v} point centres`,
        );
        b.setAttribute("aria-pressed", String(i === wi && j === si));
        b.addEventListener("click", () => {
          $("windThreshold").value = i;
          $("slopeThreshold").value = j;
          renderDistrict();
        });
        $("thresholdGrid").append(b);
      }),
    );
  }
  function mini(id, entries) {
    $(id).replaceChildren(
      ...entries.map(([value, label]) => {
        const d = document.createElement("div"),
          s = document.createElement("strong"),
          p = document.createElement("span");
        s.textContent = value;
        p.textContent = label;
        d.append(s, p);
        return d;
      }),
    );
  }
  function renderPilot() {
    const kind = $("pilot").value;
    if (["cooling", "integrated"].includes(kind)) {
      renderCombinedPilot(kind);
      return;
    }
    const isStore = ["bess", "psp"].includes(kind),
      p = isStore ? data.storage : data[kind],
      base = isStore
        ? p.input.hourly_background_site_kw
        : p.baseline.hourly.map((r) => r.site_total_kw),
      changed = isStore
        ? p.cases[kind].hourly.map((r) => r.grid_site_kw)
        : p.managed.hourly.map((r) => r.site_total_kw),
      summary = isStore ? p.cases[kind].summary : p.managed.summary;
    const rows = base.map((v, i) => ({
      label: String(i).padStart(2, "0") + ":00",
      before: v,
      after: changed[i],
    }));
    const series = $("baselineToggle").checked
      ? [
          { key: "after", name: "Managed / stored" },
          { key: "before", name: "Original demand" },
        ]
      : [{ key: "after", name: "Managed / stored" }];
    plot("pilotChart", {
      title: "Illustrative one-day site demand",
      rows,
      kind: "line",
      unit: "Site electricity · kW",
      series,
    });
    mini("pilotStats", [
      [
        fmt(summary.whole_day_site_peak_kw, 2) + " kW",
        "whole-day peak after shifting",
      ],
      [
        fmt(summary.evening_site_peak_kw, 2) + " kW",
        "17–21 evening peak after shifting",
      ],
      [
        isStore
          ? "+" + fmt(summary.daily_grid_energy_change_kwh, 2) + " kWh"
          : "0 kWh",
        "change in daily electricity use",
      ],
    ]);
    text(
      "pilotMeaning",
      isStore
        ? "Storage reduces the evening load, but charging and losses increase daily electricity use. The store begins and ends empty."
        : "The same required service is completed before its deadlines. Electricity use is unchanged; only its timing changes.",
    );
    text(
      "pilotScope",
      isStore
        ? "A hypothetical 16 kWh store delivers 2 kW during five evening hours. The pumped-storage case is a tiny hydraulic analogue with an authored 300 m head, not a Kerala project. All efficiencies and schedules are illustrative; no tariff savings or statewide benefits are claimed."
        : kind === "ev"
          ? "Three fictional EVs share an 8 kW charging connection. Arrival times, departures and battery requirements are authored. Both policies deliver 59.6 kWh to batteries before departure. This is not a measured Kerala fleet."
          : "Optional jobs at a fictional industrial site share an 8 kW flexible-load limit. Safety-critical background demand is fixed. All jobs meet the same deadlines. This is not measured KMML flexibility.",
    );
    table(
      "pilotTable",
      ["Hour", "Original kW", "Managed / stored kW"],
      rows.map((r) => [r.label, fmt(r.before, 3), fmt(r.after, 3)]),
    );
    $("pilotDownload").href =
      "data/" + (isStore ? "wp6-bess-psp.json" : `wp6-${kind}-pilot.json`);
  }
  function renderCombinedPilot(kind) {
    const cooling = kind === "cooling",
      d = data[kind],
      base = d.cases[cooling ? "conventional" : "unmanaged"],
      managed = d.cases[cooling ? "chilled_water_storage" : "combined"],
      key = cooling ? "grid_kWh_e" : "net_site_kw",
      rows = base.hourly.map((r, i) => ({
        label: String(i).padStart(2, "0") + ":00",
        before: r[key],
        after: managed.hourly[i][key],
      }));
    const series = $("baselineToggle").checked
      ? [
          { key: "after", name: "Managed / stored" },
          { key: "before", name: "Original demand" },
        ]
      : [{ key: "after", name: "Managed / stored" }];
    plot("pilotChart", {
      title: cooling
        ? "Illustrative cooling-zone electricity"
        : "Illustrative combined-site electricity",
      rows,
      kind: "line",
      unit: "Electricity · kW (1-hour slots)",
      series,
    });
    const b = base.summary,
      m = managed.summary,
      delta = cooling
        ? m.total_grid_kWh_e - b.total_grid_kWh_e
        : m.daily_grid_kwh - b.daily_grid_kwh;
    mini("pilotStats", [
      [
        fmt(cooling ? m.whole_day_peak_kW_e : m.whole_day_peak_kw, 2) + " kW",
        "whole-day peak after shifting",
      ],
      [
        fmt(cooling ? m.evening_peak_kW_e : m.evening_peak_kw, 2) + " kW",
        "17–21 evening peak after shifting",
      ],
      [
        (delta >= 0 ? "+" : "") + fmt(delta, 2) + " kWh",
        "change in daily electricity use",
      ],
    ]);
    text(
      "pilotMeaning",
      cooling
        ? "Cooling remains within the authored comfort limits. Thermal storage shifts demand into charging hours and increases total electricity in this example."
        : "Combining flexible jobs, EV charging, cooling and a battery reduces the evening peak. The whole-day peak and daily energy tell a different part of the story.",
    );
    text(
      "pilotScope",
      cooling
        ? "One synthetic cooling zone with an authored 24-hour temperature profile. The chilled-water case delivers 39.68 kWh of cooling, has zero comfort-violation hours and ends with an empty store. This is not an observed Kerala building."
        : "A synchronised hypothetical site, not Kerala grid dispatch. EV service is 59.6 kWh, industrial service is 46 kWh, cooling has no comfort violations, and the battery ends empty. Results cannot be scaled directly to statewide savings.",
    );
    table(
      "pilotTable",
      ["Hour", "Original kW", "Managed / stored kW"],
      rows.map((r) => [r.label, fmt(r.before, 3), fmt(r.after, 3)]),
    );
    $("pilotDownload").href =
      "data/" +
      (cooling ? "wp6-cooling-pilot.json" : "wp6-integrated-dispatch.json");
  }
  function renderModel() {
    const k = data.economics.key_results;
    if (modelMode === "price") {
      let envelope = $("envelope").value;
      const cases = k[`lower_FY2030_full_ATC_${envelope}_envelope_low_BESS`],
        names = ["KSEBL purchase", "IEX wholesale", "Bulk stress"],
        rows = Object.entries(cases)
          .filter(([, r]) => typeof r === "object")
          .map(([key, r], i) => ({
            label: names[i],
            short: ["KSEBL", "IEX", "Stress"][i],
            solar: r.solar_mw / 1000,
            imports: r.imports_gwh / 1000,
            price:
              data.economics.matrix.import_price_cases_real_2021_22_inr_per_mwh[
                key
              ] / 1000,
          }));
      $("modelControlLabel").hidden = false;
      text(
        "modelContext",
        `Lower FY2030 demand · 4,455 MW transfer · ${envelope} renewable envelope · low battery cost`,
      );
      plot("modelChart", {
        title: "Solar build changes with import-price assumptions",
        rows,
        kind: "bar",
        unit: "Candidate solar · GW",
        series: [{ key: "solar", name: "Solar" }],
        describe: (r) =>
          `${r.label} · ₹${fmt(r.price, 2)}/kWh (real FY2021–22) · ${fmt(r.solar, 3)} GW solar · ${fmt(r.imports, 3)} TWh imports`,
      });
      results(
        rows.map((r) => [
          r.label,
          fmt(r.solar, 2) + " GW solar",
          fmt(r.imports, 2) +
            " TWh imports · ₹" +
            fmt(r.price, 2) +
            "/kWh proxy",
        ]),
      );
      text(
        "modelInsight",
        envelope === "high"
          ? "With room to build, a higher import-price assumption selects more local solar and less imported energy."
          : "At this solar limit, the stress-price case adds 119.34 MW of wind and removes the small battery addition. Price cannot expand the solar envelope.",
      );
    } else {
      const cases = k.reference_FY2030_31_reference_envelope_low_BESS,
        rows = ["full_ATC", "ATC_80pct", "ATC_60pct"].map((key, i) => ({
          label: ["100% ATC", "80% ATC", "60% ATC"][i],
          value: cases[key].unserved_mwh / 1e6,
          atc: [4455, 3564, 2673][i],
        }));
      $("modelControlLabel").hidden = true;
      text(
        "modelContext",
        "Reference FY2030–31 demand · reference renewable envelope · low battery cost",
      );
      plot("modelChart", {
        title: "Modelled shortage under transfer stress",
        rows,
        kind: "bar",
        unit: "Unserved energy · TWh",
        series: [{ key: "value", name: "Shortage" }],
        describe: (r) =>
          `${r.label} · ${r.atc} MW transfer limit · ${fmt(r.value, 3)} TWh modelled shortage`,
      });
      results(
        rows.map((r) => [
          r.label,
          fmt(r.value, 3) + " TWh",
          fmt(r.atc, 0) + " MW transfer sensitivity",
        ]),
      );
      text(
        "modelInsight",
        "All candidate limits bind: 4,210.74 MW solar, 2,549.475 MW wind and 250 MW battery. Higher import prices cannot fix the remaining shortage.",
      );
    }
  }
  function renderHydro() {
    const choice = $("hydroTransfer").value;
    if ($("hydroStudy").value === "idukki") {
      const record =
        data.idukki.reference_demand_full_idukki_availability[
          choice === "full" ? "atc_snapshot_reference" : `atc_${choice}_stress`
        ];
      const rows = [
        { label: "1-day timing", value: record.same_horizon_1d_unserved_gwh },
        { label: "30-day timing", value: record.same_horizon_30d_unserved_gwh },
        { label: "Idukki state", value: record.stateful_unserved_gwh },
      ];
      text("hydroBadge", "12 stateful cases + 24 comparisons");
      text(
        "hydroBoundary",
        "V1.3 pilot: 364 days / 8,736 hours, with 11 generation gaps and 11 storage gaps interpolated for this model only. Its reconstructed net water-balance term is not observed catchment inflow. All three bars use the same 364-day comparison horizon; they are not the full-year v1.2 values.",
      );
      plot("hydroChart", {
        title: "Idukki stateful pilot and same-horizon timing comparisons",
        rows,
        kind: "bar",
        unit: "Unserved energy · GWh",
        series: [{ key: "value", name: "364-day comparison" }],
        describe: (r) =>
          `${r.label} · ${fmt(r.value, 3)} GWh · same 8,736-hour model horizon`,
      });
      mini(
        "hydroStats",
        rows.map((r) => [fmt(r.value, 3) + " GWh", r.label + " experiment"]),
      );
      text(
        "hydroInsight",
        choice === "full"
          ? "At full transfer, the Idukki pilot reaches the same 0.160 GWh residual shortage as the same-horizon 30-day timing case. Numerical water-state closure is not validation of real reservoir operations."
          : choice === "80pct"
            ? "At 80% transfer, seasonal Idukki storage reduces the pilot's shortage to 367.143 GWh, below the same-horizon 30-day timing case. A seasonal state can move water beyond a 30-day window; these are different constraints."
            : "At 60% transfer, the stateful pilot still leaves 5,131.227 GWh unserved. Reservoir flexibility alone cannot resolve this deep transfer stress.",
      );
      table(
        "hydroTable",
        ["Same-horizon experiment", "Unserved energy (GWh)"],
        rows.map((r) => [r.label, fmt(r.value, 3)]),
      );
      return;
    }
    text("hydroBadge", "48 full-year experiments");
    text(
      "hydroBoundary",
      "V1.2: 365 days / 8,760 hours. Hydro energy may move within nested synthetic time windows. Window length is not reservoir storage duration, and this experiment has no reservoir water-balance state.",
    );

    const key = `reference_demand_${choice === "full" ? "full" : choice}_atc_full_hydro`;
    const source = data.hydro.key_findings[key];
    const rows = [1, 3, 15, 30].map((days) => ({
      label: `${days} day${days === 1 ? "" : "s"}`,
      value: source[`${days}d_unserved_gwh`],
    }));
    plot("hydroChart", {
      title: "Hydro timing windows and modelled unserved energy",
      rows,
      kind: "bar",
      unit: "Unserved energy · GWh",
      series: [{ key: "value", name: "Modelled shortage" }],
      describe: (r) =>
        `${r.label} timing window · ${fmt(r.value, 3)} GWh unserved energy · synthetic flexibility bound`,
    });
    mini("hydroStats", [
      [fmt(rows[0].value, 3) + " GWh", "1-day timing window"],
      [fmt(rows[3].value, 3) + " GWh", "30-day timing window"],
      [
        fmt(100 * (1 - rows[3].value / rows[0].value)) + "%",
        "reduction in modelled shortage",
      ],
    ]);
    text(
      "hydroInsight",
      choice === "full"
        ? "At full transfer, 15 days captures essentially all the modelled timing benefit. This result motivates reservoir research; it does not prove that real reservoirs can provide this flexibility."
        : choice === "80pct"
          ? "Longer timing windows help, but the 30-day case still leaves 965.093 GWh unserved. Timing alone cannot close this gap."
          : "Even 30 days leaves 5,454.820 GWh unserved. Under this transfer stress, changing hydro timing barely changes the deeper adequacy constraint.",
    );
    table(
      "hydroTable",
      ["Synthetic window", "Unserved energy (GWh)"],
      rows.map((r) => [r.label, fmt(r.value, 6)]),
    );
  }
  function connection(key) {
    const entries = {
      water: [
        "Water sets the rhythm.",
        "Monsoon inflows and hydro timing shape electricity supply. Irrigation, ecology and downstream needs also matter.",
        "electricity",
      ],
      electric: [
        "Timing changes the question.",
        "Generation, interstate connections and flexible demand work together. The same daily energy can create a very different evening peak.",
        "pathways",
      ],
      leaf: [
        "A resource needs a responsible place.",
        "Good sun or wind is only a starting point. Terrain, forests, wetlands, communities and grid access shape what can actually be built.",
        "atlas",
      ],
      cycle: [
        "Value moves through materials too.",
        "Industrial heat, fuels and recovery opportunities connect energy decisions to local production. Measured process balances come before claims of savings.",
        "industry",
      ],
    };
    const [title, copy, target] = entries[key];
    text("connectionTitle", title);
    text("connectionText", copy);
    $("connectionLink").href = "#" + target;
  }
  document.querySelectorAll("[data-connection]").forEach((b) =>
    b.addEventListener("click", () => {
      pressed("[data-connection]", b);
      connection(b.dataset.connection);
    }),
  );

  function results(rows) {
    $("modelResults").replaceChildren(
      ...rows.map(([label, value, note]) => {
        const row = document.createElement("div");
        row.className = "result-row";
        const a = document.createElement("span"),
          b = document.createElement("strong"),
          c = document.createElement("small");
        a.textContent = label;
        b.textContent = value;
        c.textContent = note;
        a.append(c);
        row.append(a, b);
        return row;
      }),
    );
  }
  function material(kind) {
    const content = {
      process:
        "KMML’s titanium route links mineral separation, beneficiation, chlorination and pigment production. Each stage has different energy and material needs. Understanding the process comes before assigning a recovery benefit.",
      recovery:
        "Recovery research examines streams such as iron-rich residues and process heat. A dated trial or a possible outlet is a research lead; it does not establish continuous recovery, market demand or net savings.",
      proof:
        "A defensible industrial case needs measured mass and energy balances, stream quality, production schedules, safe operating limits, buyer specifications and project costs.",
    };
    text("materialContent", content[kind]);
  }
  function library() {
    const query = $("sourceSearch").value.toLowerCase().trim(),
      rows = data.catalogue.filter((x) =>
        (x.file + " " + x.classification).toLowerCase().includes(query),
      );
    text(
      "sourceCount",
      `${rows.length} datasets${query ? " matching your search" : ""} · original classifications retained`,
    );
    $("sourceList").replaceChildren(
      ...rows.slice(0, showAll || query ? rows.length : 8).map((r) => {
        const row = document.createElement("div");
        row.className = "source-row";
        const div = document.createElement("div"),
          strong = document.createElement("strong"),
          small = document.createElement("small"),
          a = document.createElement("a");
        strong.textContent = r.file.replace(".json", "").replaceAll("-", " ");
        small.textContent = String(r.classification).replaceAll("_", " ");
        a.href = "data/" + r.file;
        a.download = r.file;
        a.textContent = "JSON ↓";
        a.setAttribute("aria-label", "Download " + r.file);
        div.append(strong, small);
        row.append(div, a);
        return row;
      }),
    );
    $("moreSources").hidden = !!query || rows.length <= 8;
    text(
      "moreSources",
      showAll ? "Show fewer datasets" : "Show all " + rows.length + " datasets",
    );
  }

  function renderArchive() {
    const historical = data.atlas.emc_final_energy.observed_years;
    plot("totalEnergyHistoryChart", {
      title: "Historical Kerala final energy",
      kind: "line",
      unit: "Final energy · Mtoe",
      rows: historical.map((r) => ({
        label: "FY" + r.fy,
        short: r.fy.slice(2),
        value: r.value_mtoe,
      })),
      series: [{ key: "value", name: "Final energy" }],
    });
    const annual = data.ppac.annual_kerala_rows.map((r) => ({
      ...r,
      label: "FY" + r.fy,
      short: r.fy,
    }));
    plot("totalEnergyAnnualPPACChart", {
      title: "Annual Kerala all-POL petroleum sales",
      kind: "bar",
      unit: "Sales · thousand tonnes",
      rows: annual,
      series: [{ key: "all_pol_tmt", name: "All-POL" }],
      describe: (r) =>
        `${r.label} · ${fmt(r.all_pol_tmt)} thousand tonnes · ${r.all_pol_tier.replaceAll("_", " ")} · original image QA pending`,
    });
    plot("totalEnergyPPACProductsChart", {
      title: "Petrol and diesel sales, already included in all-POL",
      kind: "line",
      unit: "Sales · thousand tonnes",
      rows: annual,
      series: [
        { key: "ms_tmt", name: "Petrol" },
        { key: "hsd_tmt", name: "Diesel" },
      ],
      describe: (r) =>
        `${r.label} · Petrol ${fmt(r.ms_tmt)} (${r.ms_tier.replaceAll("_", " ")}) · Diesel ${fmt(r.hsd_tmt)} (${r.hsd_tier.replaceAll("_", " ")}) · thousand tonnes`,
    });
    plot("totalEnergyPPACChart", {
      title: "Selected petroleum sales, April to September 2024 only",
      kind: "bar",
      unit: "Half-year sales · thousand tonnes",
      rows: data.atlas.ppac_provisional_half_year_2024_25.items.map((r) => ({
        label: r.product,
        value: r.tmt,
      })),
      series: [{ key: "value", name: "Provisional sales" }],
    });
    plot("totalEnergyGHGChart", {
      title: "Selected categories of the calendar-2023 energy-sector inventory",
      kind: "bar",
      unit: "2023 emissions · MtCO₂e",
      rows: data.ghg.categories.map((r) => ({
        label: r.name,
        short: {
          transport: "Transport",
          residential: "Homes",
          industrial: "Industry",
        }[r.id],
        value: r.mtco2e,
      })),
      series: [{ key: "value", name: "Inventory" }],
    });
    $("energyView").addEventListener("change", () => {
      document.querySelectorAll("[data-energy-panel]").forEach((el) => {
        el.hidden = el.dataset.energyPanel !== $("energyView").value;
      });
    });
    $("kmmlFlow").replaceChildren(
      ...data.kmml.units.map((unit) => {
        const button = document.createElement("button");
        button.textContent = unit.id + " · " + unit.name;
        button.dataset.unit = unit.id;
        button.setAttribute("aria-pressed", String(unit.id === "MS"));
        button.addEventListener("click", () => {
          pressed("[data-unit]", button);
          renderUnit(unit);
        });
        return button;
      }),
    );
    renderUnit(data.kmml.units[0]);
  }
  function renderUnit(unit) {
    $("kmmlUnit").replaceChildren();
    for (const [label, value] of [
      [unit.name, unit.function],
      ["Inputs", unit.inputs],
      ["Outputs", unit.outputs],
    ]) {
      const p = document.createElement("p"),
        b = document.createElement("strong");
      b.textContent = label + ": ";
      p.append(b, document.createTextNode(value));
      $("kmmlUnit").append(p);
    }
    const links = data.kmml.links.filter(
      (r) => r[0] === unit.id || r[1] === unit.id,
    );
    const p = document.createElement("p");
    p.className = "micro";
    p.textContent = links
      .map(([a, b, name]) => `${a} → ${b}: ${name}`)
      .join(" · ");
    $("kmmlUnit").append(p);
    const streams = data.kmml.streams.filter((r) => r.unit === unit.id);
    $("kmmlStreams").replaceChildren(
      ...streams.map((r) => {
        const d = document.createElement("details"),
          s = document.createElement("summary"),
          a = document.createElement("p"),
          b = document.createElement("p");
        s.textContent = r.title;
        a.textContent = r.route;
        b.textContent = "Evidence needed: " + r.necessary;
        d.append(s, a, b);
        return d;
      }),
    );
    if (!streams.length) {
      const p = document.createElement("p");
      p.textContent =
        "No separately quantified residual stream is published for this unit. Current mass, energy and water measurements are still needed.";
      $("kmmlStreams").append(p);
    }
  }
  function renderStorageDetail() {
    const key = $("storageKind").value,
      c = data.storage.cases[key],
      s = c.summary;
    mini("wp6StorageCards", [
      [fmt(s.charge_grid_kwh, 2) + " kWh", "charging electricity"],
      [fmt(s.discharge_to_site_kwh, 2) + " kWh", "delivered to the site"],
      [fmt(s.terminal_stored_kwh, 2) + " kWh", "stored energy at day end"],
    ]);
    const rows = c.hourly.map((r) => ({
      ...r,
      label: String(r.hour).padStart(2, "0") + ":00",
    }));
    plot("wp6StorageChart", {
      title: "Storage charging and discharging across 24 hours",
      kind: "line",
      unit: "Electricity per 1-hour slot · kWh",
      rows,
      series: [
        { key: "grid_charge_kwh", name: "Charging" },
        { key: "grid_discharge_kwh", name: "Discharging" },
      ],
    });
    plot("wp6StorageStock", {
      title: "Stored energy through the illustrative day",
      kind: "line",
      unit: "Stored energy · kWh",
      rows,
      series: [{ key: "stock_kwh_stored", name: "Stock" }],
    });
    const cases = data.storage.sensitivities[key];
    function choose(r) {
      text(
        "storageSensitivityResult",
        r.feasible
          ? `${r.capacity_kwh_stored} kWh capacity · ${100 * r.charge_efficiency}% charging efficiency · ${fmt(r.daily_site_grid_kwh, 3)} kWh daily grid electricity · ${fmt(r.whole_day_site_peak_kw, 2)} kW whole-day peak. Full service delivered.`
          : `${r.capacity_kwh_stored} kWh capacity · ${100 * r.charge_efficiency}% charging efficiency · Infeasible: ${r.reason}. No full-service result is published.`,
      );
    }
    $("wp6StorageSensitivity").replaceChildren(
      ...cases.map((r, i) => {
        const b = document.createElement("button");
        b.dataset.storageCase = i;
        b.className = r.feasible ? "feasible" : "infeasible";
        b.textContent = `${r.capacity_kwh_stored} kWh · ${100 * r.charge_efficiency}% — ${r.feasible ? "Feasible" : "Infeasible"}`;
        b.setAttribute("aria-pressed", String(i === cases.length - 1));
        b.addEventListener("click", () => {
          pressed("[data-storage-case]", b);
          choose(r);
        });
        return b;
      }),
    );
    choose(cases.at(-1));
  }

  function progress() {
    const rows = [
      {
        title: "Official inflow evidence v1.4–v1.5 · 26 September",
        summary:
          "Strict daily inflow coverage remains incomplete. A separate cumulative sensitivity input is ready; its matrix is not yet reported complete. The official KSEB extractor and 12-month inventory are prepared, with monthly bytes and full-year schema validation still outstanding.",
      },
      {
        title: "Stateful Idukki reservoir pilot v1.3 · 26 September",
        summary:
          "12 stateful cases and 24 same-horizon comparisons solved across 364 days. Storage-state replay closes numerically. Interpolated gaps and reconstructed net water balance remain model assumptions, not observed catchment inflow or validated operations.",
      },

      {
        title: "Hydro timing bounds v1.2 · 26 September",
        summary:
          "48 full-year cases solved across 1, 3, 15 and 30-day timing windows. Annual hydro energy is preserved; these are synthetic flexibility bounds, not reservoir storage durations or a validated water-balance model.",
      },
      {
        title: "Intraday hydro flexibility v1.1 · 26 September",
        summary:
          "54 full-year cases preserve each day's hydro energy while changing its timing and available power. Hydro timing reduces modelled shortage but does not establish an adequate system under every transfer constraint.",
      },
      {
        title: "PyPSA import economics · 26 September",
        summary:
          "108 full-year sensitivity cases solved. Partial investment + import cost; no total-system-cost or validated capacity-plan claim.",
      },
      {
        title: "Numerical equivalence · 25 September",
        summary:
          "36 full-year cases reproduced in direct PyPSA against the earlier SciPy formulation. Solver agreement verifies the implementation, not the assumptions.",
      },
      ...data.ledger.workstreams,
    ];
    $("researchProgress").replaceChildren(
      ...rows.map((r) => {
        const d = document.createElement("div");
        d.className = "progress-row";
        const h = document.createElement("strong"),
          p = document.createElement("p");
        h.textContent = safeText(r.title);
        p.textContent = safeText(r.summary);
        d.append(h, p);
        return d;
      }),
    );
  }
  function pressed(selector, button) {
    document
      .querySelectorAll(selector)
      .forEach((b) => b.setAttribute("aria-pressed", String(b === button)));
  }
  $("menu").addEventListener("click", () => {
    const open = $("menu").getAttribute("aria-expanded") !== "true";
    $("menu").setAttribute("aria-expanded", String(open));
    $("navigation").classList.toggle("open", open);
    text("menu", open ? "Close −" : "Explore +");
  });
  $("navigation").addEventListener("click", (e) => {
    if (e.target.closest("a")) {
      $("navigation").classList.remove("open");
      $("menu").setAttribute("aria-expanded", "false");
      text("menu", "Explore +");
    }
  });
  function applyTheme(theme) {
    if (!["kasavu", "monsoon", "laterite"].includes(theme)) return;
    document.documentElement.dataset.theme = theme;
    document.querySelectorAll("[data-theme-choice]").forEach((button) => {
      button.setAttribute(
        "aria-pressed",
        String(button.dataset.themeChoice === theme),
      );
    });
    charts.forEach((p) => p.draw());
    ring();
  }
  try {
    applyTheme(localStorage.getItem("kerala2040-theme") || "kasavu");
  } catch {}
  document.querySelectorAll("[data-theme-choice]").forEach((button) => {
    button.addEventListener("click", () => {
      const theme = button.dataset.themeChoice;
      applyTheme(theme);
      try {
        localStorage.setItem("kerala2040-theme", theme);
      } catch {}
    });
  });
  function hashRoute() {
    const aliases = { sources: "data", research: "workbench" };
    let id = location.hash.slice(1);
    if (aliases[id]) {
      location.hash = aliases[id];
      return;
    }
    const target = $(id);
    if (target?.tagName === "DETAILS") {
      target.open = true;
      requestAnimationFrame(() => target.scrollIntoView());
    }
  }
  window.addEventListener("hashchange", hashRoute);
  async function boot() {
    try {
      const names = {
        daily: "daily-balance.json",
        baseline: "baseline-summary.json",
        ledger: "research-ledger.json",
        ev: "wp6-ev-pilot.json",
        industry: "wp6-industry-pilot.json",
        storage: "wp6-bess-psp.json",
        economics: "import-economics.json",
        hydro: "hydro-interday.json",
        idukki: "idukki-reservoir.json",
        cooling: "wp6-cooling-pilot.json",
        integrated: "wp6-integrated-dispatch.json",
        catalogue: "catalogue.json",
        metadata: "metadata.json",
        atlas: "total-energy-atlas.json",
        ppac: "ppac-annual-sales.json",
        ghg: "energy-ghg-bridge.json",
        kmml: "kmml-case.json",
      };
      const values = await Promise.all(Object.values(names).map(get));
      data = Object.fromEntries(
        Object.keys(names).map((k, i) => [k, values[i]]),
      );
      validateObserved(data.daily.records, data.baseline);
      months = monthly(data.daily.records);
      text("importStat", fmt(data.baseline.aggregate_import_share * 100) + "%");
      text(
        "hydroStat",
        fmt(data.baseline.hydro_share_internal_generation * 100) + "%",
      );
      renderMonthly();
      renderDaily();
      ring();
      renderResources();
      renderPilot();
      renderModel();
      renderHydro();
      material("process");
      renderFuel();
      renderArchive();
      renderStorageDetail();
      $("storageKind").addEventListener("change", renderStorageDetail);
      library();
      progress();
      text(
        "publication",
        `Observed bundle: ${data.metadata.generated_at_utc?.slice(0, 10) || "unavailable"} · Resource audit: ${data.ledger.reviewed_date} · Model results: ${data.economics.prepared_date} · Source: ${(data.metadata.research_source_commit || "unavailable").slice(0, 12)}`,
      );
      $("heroMonth").addEventListener("input", ring);
      new ResizeObserver(ring).observe($("balanceRing").parentElement);
      ["dailyMetric", "dailySeason"].forEach((id) =>
        $(id).addEventListener("change", renderDaily),
      );
      ["district", "windThreshold", "slopeThreshold"].forEach((id) =>
        $(id).addEventListener("change", renderDistrict),
      );
      ["pilot", "baselineToggle"].forEach((id) =>
        $(id).addEventListener("change", renderPilot),
      );
      $("hydroTransfer").addEventListener("change", renderHydro);
      $("hydroStudy").addEventListener("change", renderHydro);
      $("envelope").addEventListener("change", renderModel);
      $("sourceSearch").addEventListener("input", library);
      $("moreSources").addEventListener("click", () => {
        showAll = !showAll;
        library();
      });
      document.querySelectorAll("[data-balance]").forEach((b) =>
        b.addEventListener("click", () => {
          balanceMode = b.dataset.balance;
          pressed("[data-balance]", b);
          renderMonthly();
        }),
      );
      document.querySelectorAll("[data-model]").forEach((b) =>
        b.addEventListener("click", () => {
          modelMode = b.dataset.model;
          pressed("[data-model]", b);
          renderModel();
        }),
      );
      document.querySelectorAll("[data-material]").forEach((b) =>
        b.addEventListener("click", () => {
          pressed("[data-material]", b);
          material(b.dataset.material);
        }),
      );
      hashRoute();
    } catch (error) {
      $("loadError").hidden = false;
      const p = document.createElement("p");
      p.textContent = "The evidence could not be loaded. " + error.message;
      const button = document.createElement("button");
      button.className = "secondary";
      button.textContent = "Reload evidence";
      button.addEventListener("click", () => location.reload());
      const a = document.createElement("a");
      a.href = "https://github.com/abhijith-sivaprasadan/kerala2040";
      a.textContent = " Browse the research repository";
      $("loadError").replaceChildren(p, button, a);
      text(
        "heroScope",
        "Evidence unavailable. Use the source repository or retry loading.",
      );
    }
  }
  function renderFuel() {
    const mix = data.atlas.emc_final_energy.rounded_mix_pct;
    if (!Array.isArray(mix) || mix.length !== 5)
      throw Error("Historical fuel-share records are unavailable.");
    const short = ["Oil", "Electricity", "Coal (imp.)", "Gas", "Coal (other)"];
    plot("totalEnergyMixChart", {
      title: "Historical final energy shares FY2019–20",
      rows: mix.map((r, i) => ({
        label: r.fuel,
        short: short[i],
        value: r.pct,
      })),
      kind: "bar",
      unit: "% of final energy",
      max: 100,
      series: [{ key: "value", name: "Publisher-rounded share" }],
      describe: (r) =>
        `${r.label}: ${r.value}% (publisher-rounded, FY2019–20). A rounded zero is not proof of no consumption.`,
    });
  }
  boot();
})();
