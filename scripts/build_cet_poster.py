"""Create the early A1 CET 2026 poster from the same publication evidence.

Requires reportlab. Build the website first. No raster images or SVG assets.
The PDF contains selectable text and native PDF chart paths.
"""
import json
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf'
OUT.mkdir(parents=True, exist_ok=True)
FONT = Path('C:/Windows/Fonts')
for name, filename in [('Sans', 'arial.ttf'), ('Bold', 'arialbd.ttf'),
                       ('Serif', 'georgia.ttf'), ('Italic', 'georgiai.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT / filename)))

W, H = 1683.78, 2383.94  # A1 portrait, points
PAPER, INK, GOLD, GREEN, MUTED, LINE = map(HexColor,
    ['#f7f4e9', '#173f33', '#b27a24', '#287454', '#596b5f', '#cdd2bc'])
c = canvas.Canvas(str(OUT / 'Kerala2040_CET2026_Poster_Draft.pdf'), pagesize=(W, H))
c.setTitle('Kerala2040 | CET 2026 early poster')
c.setAuthor('Kerala2040 research project')
c.setFillColor(PAPER)
c.rect(0, 0, W, H, fill=1, stroke=0)


def txt(x, y, value, size=25, font='Sans', colour=INK):
    c.setFillColor(colour)
    c.setFont(font, size)
    c.drawString(x, H-y-size, value)


def para(x, y, value, width, size=24, colour=INK, font='Sans', leading=1.4):
    words = value.split()
    lines, current = [], ''
    for word in words:
        trial = (current + ' ' + word).strip()
        if current and pdfmetrics.stringWidth(trial, font, size) > width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    for line in lines:
        txt(x, y, line, size, font, colour)
        y += size*leading
    return y


def rule(y, x=65, width=W-130, colour=LINE):
    c.setStrokeColor(colour)
    c.setLineWidth(1.4)
    c.line(x, H-y, x+width, H-y)


def rect(x, y, width, height, colour):
    c.setFillColor(colour)
    c.rect(x, H-y-height, width, height, fill=1, stroke=0)


def read(name):
    return json.loads((ROOT / '_site/data' / name).read_text(encoding='utf-8'))


daily = read('daily-balance.json')['records']
base = read('baseline-summary.json')
ledger = read('research-ledger.json')
economics = read('import-economics.json')
months = []
for month in sorted({row['date'][:7] for row in daily}):
    rows = [r for r in daily if r['date'].startswith(month)]
    months.append((month, sum(r['internal_generation_mu'] for r in rows)/len(rows),
                   sum(r['net_import_interface_mu'] for r in rows)/len(rows)))

txt(65, 55, 'KERALA2040  /  CET 2026', 24, 'Bold')
txt(1160, 59, 'EARLY RESEARCH POSTER', 18, 'Bold', GOLD)
txt(65, 108, 'Our land. Our energy future.', 78, 'Serif')
para(65, 215, 'Investigating energy resilience through electricity, seasonal resources, '
     'land constraints, industrial systems and open modelling.', 1480, 29, MUTED)
rule(320, colour=GOLD)

txt(65, 363, 'THE RESEARCH QUESTION', 19, 'Bold', GOLD)
para(65, 409, 'How can Kerala meet future demand reliably while respecting '
     'its land and water?', 1480, 51, INK, 'Serif', 1.2)
para(65, 555, 'Early experiments show why timing and transfer capability matter alongside '
     'new generation. The current evidence supports comparison, not a final 2040 capacity plan.',
     1490, 29, MUTED)
rule(670)

left, right, cw = 65, 875, 740
txt(left, 712, '01 / OBSERVED ELECTRICITY', 19, 'Bold', GOLD)
txt(left, 751, 'A connected, seasonal system', 36, 'Serif')
txt(left, 817, f"{base['aggregate_import_share']*100:.1f}%", 70, 'Serif')
para(left+270, 830, 'of recorded consumption came from net imports.', 410, 25)
txt(left, 924, 'MU per observed day', 17, 'Sans', MUTED)
chart_x, chart_y, chart_w, chart_h = left+50, 968, 640, 250
for tick in [0, 30, 60, 90, 120]:
    yy = chart_y+chart_h-chart_h*tick/120
    rule(yy, chart_x, chart_w)
    txt(left, yy-9, str(tick), 16, colour=MUTED)
for i, (month, internal, imports) in enumerate(months):
    x = chart_x+i*chart_w/12+8
    for value, offset, colour in [(internal, 0, GREEN), (imports, internal, GOLD)]:
        rect(x, chart_y+chart_h-chart_h*(value+offset)/120, 34, chart_h*value/120, colour)
    txt(x-1, chart_y+chart_h+15, ['A','M','J','J','A','S','O','N','D','J','F','M'][i], 17)
rect(left, 1280, 18, 18, GREEN)
txt(left+28, 1276, 'In-state generation', 18)
rect(left+350, 1280, 18, 18, GOLD)
txt(left+378, 1276, 'Net imports', 18)
para(left, 1320, 'SLDC FY2024-25: 354 of 365 daily reports. The 11 missing days are not '
     'filled. Bars show available-day means, not complete monthly totals.', cw-10, 20, MUTED)

txt(right, 712, '02 / RESOURCE & LAND', 19, 'Bold', GOLD)
txt(right, 751, 'Solar follows the seasons', 36, 'Serif')
para(right, 822, 'Monthly median source-grid PV output', cw-10, 25)
txt(right, 924, 'kWh / kWp / day', 17, colour=MUTED)
solar = ledger['solar_phase1']['aggregate']['statewide']['monthly_marginal_pixel_median_PVOUT_kWh_kWp_day']
sx, sy, sw, sh = right+48, 968, 650, 250
for tick in [0, 2, 4, 6]:
    yy = sy+sh-sh*tick/6
    rule(yy, sx, sw)
    txt(right, yy-9, str(tick), 16, colour=MUTED)
path = c.beginPath()
for i, value in enumerate(solar.values()):
    x, y = sx+i*sw/11, H-(sy+sh-sh*value/6)
    if i == 0:
        path.moveTo(x, y)
    else:
        path.lineTo(x, y)
    txt(x-5, sy+sh+15, list(solar)[i][0], 17)
c.setStrokeColor(GREEN)
c.setLineWidth(4)
c.drawPath(path)
txt(right, 1276, 'Resource is not permission to build.', 24, 'Bold')
para(right, 1320, 'Global Solar Atlas 2, 1999-2018 climatology. Wind, terrain, ecology and '
     'grid access must also be checked. Eligible land and project capacity are unresolved.', cw-10, 20, MUTED)
rule(1442)

txt(left, 1484, '03 / 2030 MODEL EXPERIMENT', 19, 'Bold', GOLD)
txt(left, 1525, 'Transfer stress exposes a flexibility problem.', 42, 'Serif')
para(left, 1598, '108 full-year economic sensitivities now combine demand, renewable envelopes, '
     'battery costs, transfer limits and import-price assumptions in PyPSA.', 1480, 26, MUTED)

cases = economics['key_results']['reference_FY2030_31_reference_envelope_low_BESS']
labels = [('full_ATC', '4,455 MW', '100% transfer'), ('ATC_80pct', '3,564 MW', '80% stress'),
          ('ATC_60pct', '2,673 MW', '60% stress')]
for i, (key, label, sub) in enumerate(labels):
    x = 75+i*495
    txt(x, 1713, label, 28, 'Bold')
    txt(x, 1761, sub, 20, colour=MUTED)
    value = cases[key]['unserved_mwh']/1e6
    rect(x, 1810, 390*value/7, 27, GOLD)
    txt(x, 1860, f'{value:.3f} TWh', 41, 'Serif')
    txt(x, 1915, 'modelled unserved energy', 19, colour=MUTED)
para(left, 1970, 'Selected case: reference FY2030-31 demand, reference renewable envelope, low '
     'battery cost. All candidate capacity limits bind. These shortages describe the assumptions '
     'of this model; they are not a forecast of actual power cuts.', 1490, 22, MUTED)
rule(2074)

txt(left, 2110, 'METHOD', 17, 'Bold', GOLD)
para(left, 2147, 'Preserve source records and gaps. Characterise resources. Test constrained '
     'dispatch and investment. Check numerical equivalence. Keep assumptions traceable.', 705, 21)
txt(right, 2110, 'WHAT STILL NEEDS WORK', 17, 'Bold', GOLD)
para(right, 2147, 'Measured hourly demand; reservoir and cascade operation; outages; landed '
     'prices; statutory siting; project finance and grid feasibility.', 705, 21)
rule(2264)
txt(left, 2292, 'Explore the evidence: kerala2040.github.io', 24, 'Bold')
c.linkURL('https://kerala2040.github.io/', (left, H-2325, 690, H-2290), relative=0)
txt(left, 2340, 'Sources: SLDC daily archive; GSA2/NWIC resource ledger; PyPSA v1.0 evidence, 26 Sep 2026.', 15, colour=MUTED)
txt(1080, 2301, 'Independent research / Draft 01', 19, colour=MUTED)
c.save()
print(OUT / 'Kerala2040_CET2026_Poster_Draft.pdf')
