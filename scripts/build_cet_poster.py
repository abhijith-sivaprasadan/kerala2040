"""A0 scientific poster: source-backed figures and a native PDF system schematic."""

import calendar
import json
import math
from itertools import pairwise
from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/pdf"
OUT.mkdir(parents=True, exist_ok=True)
for name, filename in [("Sans", "arial.ttf"), ("Bold", "arialbd.ttf"), ("Italic", "ariali.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(Path("C:/Windows/Fonts") / filename)))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Bold", italic="Italic")
W, H = 1684, 2384
PW, PH = 2383.937, 3370.394
NAVY, INK, BLUE, GREEN, GOLD, PALE, LINE, MUTED, RED = map(
    HexColor,
    [
        "#08065a",
        "#202739",
        "#277cad",
        "#247b66",
        "#ce8c31",
        "#eef3f7",
        "#c5d1dc",
        "#536574",
        "#ae4d45",
    ],
)
OUTPUT = OUT / "Kerala2040_CET2026_Scientific_Poster_v5.pdf"
c = canvas.Canvas(str(OUTPUT), pagesize=(PW, PH), pageCompression=1)
c.scale(PW / W, PH / H)
c.setTitle("Kerala2040: electricity flexibility | CET 2026 scientific poster")
c.setAuthor("Abhijith Sivaprasadan")
BOUNDS = []


def txt(x, y, s, size=18, font="Sans", colour=INK, align="left"):
    c.setFillColor(colour)
    c.setFont(font, size)
    {"left": c.drawString, "center": c.drawCentredString, "right": c.drawRightString}[align](
        x, H - y - size, str(s)
    )


def para(x, y, s, w, size=18, colour=INK, maxh=None):
    p = Paragraph(
        s,
        ParagraphStyle("p", fontName="Sans", fontSize=size, leading=size * 1.25, textColor=colour),
    )
    _, h = p.wrap(w, H)
    if maxh is not None and h > maxh + 0.1:
        raise ValueError(f"Overflow ({h}>{maxh}): {s[:75]}")
    if y + h > H - 10:
        raise ValueError("Off page")
    p.drawOn(c, x, H - y - h)
    BOUNDS.append((x, y, w, h, s))
    return y + h


def box(x, y, w, h, fill=white, stroke=LINE, lw=1):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(lw)
    c.rect(x, H - y - h, w, h, fill=1, stroke=1)


def line(x1, y1, x2, y2, col=LINE, lw=1, dash=None):
    c.setStrokeColor(col)
    c.setLineWidth(lw)
    c.setDash(dash or [])
    c.line(x1, H - y1, x2, H - y2)
    c.setDash([])


def section(x, y, w, title, height=62):
    """Separate heading and content frames follow the supplied course poster."""
    box(x, y, w, height, white, INK, 1.5)
    txt(x + w / 2, y + (height - 38) / 2 - 3, title, 38, "Bold", NAVY, "center")


def figure_heading(x, y, w, title, source):
    txt(x + w / 2, y, title, 24, "Bold", NAVY, "center")
    txt(x + w / 2, y + 36, source, 17, colour=MUTED, align="center")


def legend(x, y, entries, size=15, gap=18):
    for title, col in entries:
        box(x, y + 4, 16, 10, col, col)
        txt(x + 24, y, title, size)
        x += 24 + pdfmetrics.stringWidth(title, "Sans", size) + gap


def axes(x, y, w, h, ymax, ticks, unit, xticks, xlabels, xmax):
    txt(x, y - 29, unit, 18, colour=MUTED)
    for t in ticks:
        yy = y + h - h * t / ymax
        line(x, yy, x + w, yy, LINE, 0.7)
        txt(x - 10, yy - 8, f"{t:g}", 17, colour=MUTED, align="right")
    line(x, y, x, y + h, MUTED)
    line(x, y + h, x + w, y + h, MUTED)
    for t, s in zip(xticks, xlabels):
        xx = x + w * t / xmax
        line(xx, y + h, xx, y + h + 4, MUTED)
        txt(xx, y + h + 9, s, 16, colour=MUTED, align="center")


def plotline(x, y, w, h, vals, ymax, col, steps=False, markers=False):
    if steps:
        vals = list(vals) + [vals[-1]]
    p = c.beginPath()
    prev = H - y - h + h * vals[0] / ymax
    for i, v in enumerate(vals):
        xx = x + w * i / (len(vals) - 1)
        yy = H - y - h + h * v / ymax
        if i == 0:
            p.moveTo(xx, yy)
        else:
            if steps:
                p.lineTo(xx, prev)
            p.lineTo(xx, yy)
        prev = yy
        if markers:
            c.setFillColor(col)
            c.circle(xx, yy, 3, fill=1, stroke=0)
    c.setStrokeColor(col)
    c.setLineWidth(2.5)
    c.drawPath(p)


def arrow(points, col=GREEN, both=False, dashed=False):
    for a, b in pairwise(points):
        line(*a, *b, col, 2.4, [5, 4] if dashed else None)

    def head(a, b):
        angle = math.atan2(b[1] - a[1], b[0] - a[0])
        p = c.beginPath()
        p.moveTo(b[0], H - b[1])
        for turn in [-0.47, 0.47]:
            p.lineTo(b[0] - 10 * math.cos(angle + turn), H - (b[1] - 10 * math.sin(angle + turn)))
        p.close()
        c.setFillColor(col)
        c.drawPath(p, fill=1, stroke=0)

    head(points[-2], points[-1])
    if both:
        head(points[1], points[0])


def node(x, y, w, h, title, desc, col=GREEN, fill=white):
    box(x, y, w, h, fill, col, 1.5)
    txt(x + 15, y + 11, title, 19, "Bold", col)
    para(x + 57, y + 37, desc, w - 71, 18, maxh=h - 39)
    ix, iy = x + 17, y + 43
    if title == "Solar & wind":
        box(ix, iy, 29, 20, fill, col, 1.2)
        for dx in [10, 20]:
            line(ix + dx, iy, ix + dx, iy + 20, col, 1)
        line(ix, iy + 10, ix + 29, iy + 10, col, 1)
        line(ix + 14, iy + 20, ix + 14, iy + 27, col, 1.2)
        line(ix + 5, iy + 27, ix + 24, iy + 27, col, 1.2)
    elif title == "Interstate grid":
        for dx in [-12, 12]:
            line(ix + 15, iy - 3, ix + 15 + dx, iy + 29, col, 1.5)
        for dy, half in [(4, 10), (14, 15)]:
            line(ix + 15 - half, iy + dy, ix + 15 + half, iy + dy, col, 1.5)
        line(ix + 6, iy + 22, ix + 22, iy + 8, col, 1)
        line(ix + 24, iy + 22, ix + 8, iy + 8, col, 1)
    elif title == "Idukki reservoir":
        for dy in [9, 18, 27]:
            line(ix, iy + dy, ix + 19, iy + dy, col, 1.3)
        p = c.beginPath()
        p.moveTo(ix + 23, H - iy)
        p.lineTo(ix + 31, H - iy - 29)
        p.lineTo(ix + 17, H - iy - 29)
        p.close()
        c.setFillColor(col)
        c.drawPath(p, fill=1, stroke=0)
    elif title == "Storage":
        box(ix, iy + 3, 30, 22, fill, col, 1.5)
        box(ix + 30, iy + 9, 3, 10, col, col)
        for dx in [5, 12, 19]:
            box(ix + dx, iy + 8, 4, 12, col, col, 0.2)
    elif title == "Demand & service":
        line(ix, iy + 15, ix + 7, iy + 15, col, 1.5)
        box(ix + 7, iy + 6, 17, 19, fill, col, 1.5)
        line(ix + 24, iy + 15, ix + 31, iy + 15, col, 1.5)
        txt(ix + 15.5, iy + 6, "L", 14, "Bold", col, "center")
    else:
        c.setStrokeColor(col)
        c.setLineWidth(1.5)
        c.circle(ix + 15, H - iy - 14, 14, fill=0, stroke=1)
        if title == "Hydropower":
            for angle in [0, 2.094, 4.189]:
                line(
                    ix + 15,
                    iy + 14,
                    ix + 15 + 11 * math.cos(angle),
                    iy + 14 + 11 * math.sin(angle),
                    col,
                    2,
                )
        else:
            line(ix + 18, iy + 3, ix + 11, iy + 15, col, 2)
            line(ix + 11, iy + 15, ix + 20, iy + 15, col, 2)
            line(ix + 20, iy + 15, ix + 12, iy + 25, col, 2)


def read(name):
    return json.loads((ROOT / "_site/data" / name).read_text(encoding="utf-8"))


daily = read("daily-balance.json")["records"]
solar = read("research-ledger.json")["solar_phase1"]["aggregate"]["statewide"]
ev = read("wp6-ev-pilot.json")
hydro = read("idukki-reservoir.json")
windows = read("hydro-interday.json")
econdata = read("import-economics.json")


# Reader-first scientific layout: short claims, larger plots, local caveats.
def rounded(value):
    """Two significant figures for display; calculations retain original values."""
    rounded_value = float(f"{value:.2g}")
    if abs(rounded_value) >= 100:
        return f"{rounded_value:,.0f}"
    return f"{rounded_value:g}"


def dot(x, y, colour, radius=7):
    c.setFillColor(colour)
    c.circle(x, H - y, radius, fill=1, stroke=0)


# A0 portrait: project and technologies, system framework, analysis, conclusions.
box(0, 0, W, 222, NAVY, NAVY)
txt(W / 2, 23, "Electricity flexibility in Kerala", 54, "Bold", white, "center")
txt(W / 2, 89, "Import dependence, hydropower and demand timing", 36, "Bold", white, "center")
txt(W / 2, 150, "Abhijith Sivaprasadan", 27, "Bold", white, "center")
txt(
    W / 2,
    188,
    "Independent study  |  KTH Royal Institute of Technology  |  CET 2026",
    21,
    colour=white,
    align="center",
)

section(30, 242, 793, "Project description")
section(841, 242, 813, "Resources and technologies")
box(30, 318, 793, 461, white, INK, 1.5)
box(841, 318, 813, 461, white, INK, 1.5)
txt(426.5, 335, "Context and objective", 25, "Bold", NAVY, "center")
para(
    52,
    378,
    "Kerala's FY2024-25 electricity record is <b>74% net imports</b>. Hydropower supplies most in-state generation.",
    747,
    22,
    maxh=61,
)
para(
    52,
    445,
    "<b>Objective:</b> test how import constraints, hydro operation and demand timing affect electricity adequacy.",
    747,
    22,
    maxh=58,
)
txt(426.5, 512, "A. Observed electricity balance [1]", 23, "Bold", NAVY, "center")
mx, my, mw, mh = 99, 575, 679, 121
axes(
    mx,
    my,
    mw,
    mh,
    120,
    [0, 40, 80, 120],
    "GWh per observed day",
    [i + 0.5 for i in range(12)],
    ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"],
    12,
)
for i, month in enumerate(sorted({r["date"][:7] for r in daily})):
    rows = [r for r in daily if r["date"].startswith(month)]
    internal = sum(r["internal_generation_mu"] for r in rows) / len(rows)
    imports = sum(r["net_import_interface_mu"] for r in rows) / len(rows)
    xx = mx + (i + 0.18) * mw / 12
    for v, offset, col in [(internal, 0, GREEN), (imports, internal, GOLD)]:
        box(xx, my + mh - mh * (v + offset) / 120, mw / 12 * 0.64, mh * v / 120, col, col, 0.1)
    year, m = map(int, month.split("-"))
    if len(rows) < calendar.monthrange(year, m)[1]:
        txt(xx + 17, my + mh - mh * (imports + internal) / 120 - 23, "*", 22, "Bold", RED, "center")
legend(82, 731, [("In-state", GREEN), ("Net imports", GOLD)], 18)
txt(443, 731, "* Incomplete month", 18, colour=MUTED)
txt(
    426.5,
    755,
    "354 observed days; 11 gaps retained. Available-day means.",
    17,
    colour=MUTED,
    align="center",
)

figure_heading(857, 335, 781, "B. Seasonal solar resource", "Global Solar Atlas 2 climatology [2]")
axes(
    907,
    422,
    433,
    107,
    6,
    [0, 2, 4, 6],
    "Solar yield (kWh/kWp/day)",
    [0, 2, 4, 6, 8, 10, 11],
    ["Jan", "Mar", "May", "Jul", "Sep", "Nov", "Dec"],
    11,
)
plotline(
    907,
    422,
    433,
    107,
    list(solar["monthly_marginal_pixel_median_PVOUT_kWh_kWp_day"].values()),
    6,
    BLUE,
    markers=True,
)
para(
    1370,
    413,
    "1999-2018 source-grid medians.<br/><br/>Resource evidence, not plant output.",
    258,
    20,
    maxh=132,
)
line(862, 565, 1633, 565, LINE)
figure_heading(857, 579, 781, "C. Managed vehicle charging", "Synthetic three-vehicle site [3]")
axes(
    907,
    662,
    433,
    65,
    15,
    [0, 5, 10, 15],
    "Site demand (kW)",
    [0, 6, 12, 18, 24],
    ["00", "06", "12", "18", "24"],
    24,
)
plotline(
    907, 662, 433, 65, [r["site_total_kw"] for r in ev["baseline"]["hourly"]], 15, GOLD, steps=True
)
plotline(
    907, 662, 433, 65, [r["site_total_kw"] for r in ev["managed"]["hourly"]], 15, GREEN, steps=True
)
para(
    1370,
    653,
    "<b>Peak demand</b><br/>13.3 → 12.0 kW<br/>Same energy and service.",
    258,
    21,
    maxh=109,
)
legend(914, 754, [("Original", GOLD), ("Managed", GREEN)], 17)
txt(1340, 754, "Hour", 17, colour=MUTED, align="right")

section(30, 799, 1624, "System framework and methods")
box(30, 875, 1624, 412, white, INK, 1.5)
txt(605, 891, "Linked research modules", 25, "Bold", NAVY, "center")
node(55, 947, 210, 80, "Solar & wind", "Resource limits")
node(55, 1069, 210, 80, "Interstate grid", "Transfer / price")
node(330, 932, 240, 100, "Idukki reservoir", "Daily water state", BLUE)
node(660, 932, 220, 100, "Hydropower", "Energy / power limits", BLUE)
node(460, 1069, 250, 80, "Electricity balance", "Supply + demand", GREEN)
node(945, 932, 220, 100, "Storage", "Battery / hydro")
node(945, 1069, 220, 80, "Demand & service", "Load / charging")
arrow([(265, 987), (300, 987), (300, 1095), (460, 1095)])
arrow([(265, 1112), (460, 1112)])
arrow([(570, 972), (660, 972)], BLUE)
arrow([(768, 1032), (768, 1089), (710, 1089)], BLUE)
arrow([(945, 970), (913, 970), (913, 1099), (710, 1099)], GREEN, both=True)
arrow([(710, 1130), (945, 1130)])
legend(233, 1175, [("Electricity", GREEN), ("Water / hydro", BLUE)], 18)
txt(818, 1175, "Arrows are unscaled.", 18, colour=MUTED)
para(
    59,
    1217,
    "<b>Scope:</b> separate model experiments, not a validated statewide capacity plan. Land, ecology and industrial integration remain future work.",
    1098,
    21,
    maxh=55,
)
line(1190, 895, 1190, 1265, LINE, 1)
para(
    1210,
    901,
    "<b>Electricity balance</b><br/>G + M + P<sub>dis</sub> + U = D + P<sub>ch</sub>",
    414,
    22,
    maxh=58,
)
para(
    1210,
    970,
    "G generation; M imports; D demand; U unmet load; P storage charge/discharge.",
    414,
    18,
    maxh=71,
)
para(
    1210,
    1055,
    "<b>Daily reservoir balance</b><br/>S<sub>d+1</sub> = S<sub>d</sub> + W<sub>d</sub> - E<sub>d</sub>/κ - R<sub>d</sub>",
    414,
    22,
    maxh=58,
)
para(
    1210,
    1124,
    "S storage; W net water; E hydro energy; R extra release; κ = 1,470 MWh/Mm³.",
    414,
    18,
    maxh=71,
)
para(1210, 1205, "<b>W is reconstructed, not measured inflow.</b>", 414, 20, maxh=53)

section(30, 1307, 1624, "Analysis and assessment")
box(30, 1383, 1624, 578, white, INK, 1.5)
line(571, 1403, 571, 1939, LINE, 1)
line(1112, 1403, 1112, 1939, LINE, 1)
figure_heading(45, 1403, 511, "D. Import-price sensitivity", "Partial economics v1.0 [4]")
figure_heading(586, 1403, 511, "E. Stateful reservoir model", "364 days / 8,736 hours · v1.3 [5]")
figure_heading(1127, 1403, 511, "F. Hydro timing windows", "365 days / 8,760 hours · v1.2 [5]")

econ = econdata["key_results"]["lower_FY2030_full_ATC_high_envelope_low_BESS"]
enames = ["ksebl_weighted_purchase", "iex_dam_wholesale", "delivered_bulk_stress"]
ex, ey, ew, eh = 92, 1535, 422, 189
axes(
    ex,
    ey,
    ew,
    eh,
    8,
    [0, 2, 4, 6, 8],
    "Selected solar build (GW)",
    [0.5, 1.5, 2.5],
    ["4.49", "4.66", "6.35"],
    3,
)
for i, key in enumerate(enames):
    v = econ[key]["solar_mw"] / 1000
    xx = ex + i * ew / 3 + 43
    box(xx, ey + eh - eh * v / 8, 55, eh * v / 8, BLUE, BLUE)
    txt(xx + 27.5, ey + eh - eh * v / 8 - 33, rounded(v), 25, "Bold", NAVY, "center")
txt(303, 1760, "Import-price proxy (INR/kWh)", 19, colour=MUTED, align="center")
txt(303, 1786, "Real FY2021-22 prices", 17, colour=MUTED, align="center")
para(
    53,
    1820,
    "<b>Higher import prices select more solar.</b> Lower demand, full transfer, high renewables and low battery cost.",
    495,
    21,
    maxh=83,
)
para(53, 1910, "Partial costs; not project finance.", 495, 19, maxh=28)

legend(601, 1491, [("1-day timing", HexColor("#939daa")), ("Idukki state", GREEN)], 17, 18)
start_x, plot_w = 701, 340
casekeys = ["atc_snapshot_reference", "atc_80pct_stress", "atc_60pct_stress"]
for i, (key, pct) in enumerate(zip(casekeys, ["100%", "80%", "60%"])):
    yy = 1570 + i * 72
    r = hydro["reference_demand_full_idukki_availability"][key]
    old, new = r["same_horizon_1d_unserved_gwh"], r["stateful_unserved_gwh"]
    txt(598, yy - 13, pct, 21, "Bold", NAVY)
    line(start_x, yy, start_x + plot_w, yy, LINE, 1)
    a, b = start_x + plot_w * old / 6000, start_x + plot_w * new / 6000
    line(a, yy, b, yy, GREEN, 4)
    dot(a, yy, HexColor("#939daa"), 7)
    dot(b, yy, GREEN, 5)
    txt(1068, yy - 31, f"{rounded(old)} → {rounded(new)}", 21, "Bold", GREEN, "right")
for tick in [0, 2000, 4000, 6000]:
    txt(start_x + plot_w * tick / 6000, 1737, f"{tick:,}", 16, colour=MUTED, align="center")
txt(850, 1763, "Unserved energy (GWh)", 19, colour=MUTED, align="center")
txt(846, 1788, "Transfer limit: 100% = 4,455 MW", 17, colour=MUTED, align="center")
para(
    594,
    1820,
    "<b>69% less shortage at 80% transfer.</b> FY2030-31 reference demand and renewables; full Idukki; low battery cost; KSEBL price.",
    495,
    21,
    maxh=107,
)

# Different chart form and explicit horizons distinguish E from F.
txt(1136, 1491, "Unserved energy (GWh)", 19, colour=MUTED)
hmx, hmy, cw, ch = 1214, 1577, 100, 48
for j, t in enumerate(["1 day", "3 days", "15 days", "30 days"]):
    txt(hmx + cw * (j + 0.5), hmy - 34, t, 18, "Bold", align="center")
heatkeys = [
    "reference_demand_full_atc_full_hydro",
    "reference_demand_80pct_atc_full_hydro",
    "reference_demand_60pct_atc_full_hydro",
]
for i, (name, key) in enumerate(zip(["100%", "80%", "60%"], heatkeys)):
    txt(hmx - 12, hmy + i * ch + 12, name, 20, "Bold", align="right")
    for j, days in enumerate([1, 3, 15, 30]):
        v = windows["key_findings"][key][f"{days}d_unserved_gwh"]
        ratio = v / 6000
        col = Color(0.91 - 0.78 * ratio, 0.95 - 0.58 * ratio, 0.97 - 0.43 * ratio)
        box(hmx + j * cw, hmy + i * ch, cw, ch, col, white, 2)
        txt(
            hmx + cw * (j + 0.5),
            hmy + i * ch + 11,
            rounded(v),
            22,
            "Bold",
            white if ratio > 0.6 else NAVY,
            "center",
        )
txt(1136, 1539, "Transfer", 17, "Bold", NAVY)
# Quantitative legend rather than a sentence about the colour scale.
for j in range(100):
    ratio = j / 99
    col = Color(0.91 - 0.78 * ratio, 0.95 - 0.58 * ratio, 0.97 - 0.43 * ratio)
    box(1214 + j * 4, 1744, 4, 12, col, col, 0)
for value in [0, 3000, 6000]:
    txt(1214 + value / 6000 * 400, 1762, f"{value:,}", 16, colour=MUTED, align="center")
para(
    1135,
    1820,
    "<b>Longer windows give limited relief under deep transfer stress.</b> Reference demand; full hydro; annual energy fixed at 7.43 TWh.",
    495,
    21,
    maxh=107,
)
para(1135, 1910, "Windows are not reservoir durations.", 495, 19, maxh=28)

section(30, 1981, 793, "Conclusions", 58)
section(841, 1981, 813, "Limitations and next steps", 58)
box(30, 2053, 793, 158, white, INK, 1.5)
box(841, 2053, 813, 158, white, INK, 1.5)
para(
    53,
    2069,
    "Reservoir flexibility reduces shortage, but <b>5.1 TWh remains unserved at 60% transfer</b> in the stateful pilot (E).",
    745,
    23,
    maxh=87,
)
para(53, 2161, "<b>Assess timing and interconnection together.</b>", 745, 23, maxh=34)
para(
    864,
    2069,
    "<b>Validation:</b> inflow, releases and efficiency remain unvalidated; 11 generation and 11 storage gaps interpolated in v1.3 only.",
    763,
    21,
    maxh=81,
)
para(
    864,
    2155,
    "<b>Next:</b> admit official KSEB records and catchment evidence before physical validation [6].",
    763,
    20,
    maxh=53,
)

line(30, 2234, 1654, 2234, INK, 1)
txt(30, 2248, "References and reproducibility", 23, "Bold", NAVY)
para(
    30,
    2285,
    "[1] Kerala SLDC daily statistics, FY2024-25.<br/>[2] GSA2, 1999-2018. [3] WP6 synthetic EV dispatch.<br/>[4] PyPSA economics v1.0. [5] Hydro v1.2 / Idukki v1.3.",
    790,
    17,
    maxh=65,
)
para(
    851,
    2285,
    "[6] KSEB v1.5: workbook acquisition blocked. LRIS catchment<br/>PR105: under review; catchment not admitted (27 Sep 2026).<br/>Full-precision data, assumptions and code: <b>kerala2040.github.io/#data</b>",
    803,
    17,
    maxh=65,
)
c.linkURL("https://kerala2040.github.io/#data", (851, H - 2352, 1654, H - 2324), relative=1)
c.linkURL(
    "https://github.com/abhijith-sivaprasadan/kerala2040/pull/105",
    (851, H - 2324, 1654, H - 2304),
    relative=1,
)
c.linkURL(
    "https://github.com/abhijith-sivaprasadan/kerala2040/blob/49acde2877e4d58f91d471bacb82cc3dab7ca1f4/docs/KSEB_MONTHLY_ACQUIRE_PARSE_V1_5.md",
    (851, H - 2304, 1654, H - 2280),
    relative=1,
)
txt(30, 2366, "Kerala2040  |  Abhijith Sivaprasadan  |  Independent study", 12, "Bold", MUTED)
txt(
    1654,
    2366,
    "A0 portrait  |  Scientific draft 05  |  27 September 2026",
    12,
    colour=MUTED,
    align="right",
)
c.save()
print(OUTPUT)
print(f"Checked {len(BOUNDS)} paragraph regions; native PDF text and vector figures.")
