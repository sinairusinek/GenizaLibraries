"""Colour scheme for the FGP hierarchy.

Tier 1: one base colour per field (distinct hues, two alternating lightness levels).
Tier 2: hue shifts around the parent's hue, lighter.
Tier 3: keeps its tier-2 parent's hue, lighter still.
"""
import json, csv, colorsys
rows = json.load(open("data/fgp_categories.json"))
by = {r["code"]: r for r in rows}
top = [r for r in rows if r["level"] == 1]
FAMILY = {"3": 215, "4": 4, "6": 135, "13": 282, "17": 38}      # fields that have sub-fields
SHORT = {"4": "ספרות הלכתית ופרשנות תלמוד", "6": "ספרות הגות", "9": "היסטוריוגרפיה וגיאוגרפיה",
         "20": "עזרי הוראה, נסיונות קולמוס…"}
leaf = [r for r in top if r["code"] not in FAMILY]
n = len(leaf)
def hexc(h, s, l):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l, s)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))
def ink(hexcol):
    r, g, b = (int(hexcol[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lum = 0.2126 * r ** 2.2 + 0.7152 * g ** 2.2 + 0.0722 * b ** 2.2
    return "#ffffff" if lum < 0.30 else "#1a1a1a"
for i, r in enumerate(leaf):
    r["hue"] = (20 + (i * 7 % n) * 360 / n) % 360      # neighbours in the list get distant hues
    r["color"] = hexc(r["hue"], 0.55, 0.36 if i % 2 else 0.47)
by["22"]["color"] = "#7a7a7a"                          # 'field not determined' stays grey
for code, h in FAMILY.items():
    by[code]["hue"] = h; by[code]["color"] = hexc(h, 0.70, 0.40)
for r in rows:
    if r["level"] == 2:
        p = by[r["parent"]]; sib = [k for k in rows if k["parent"] == p["code"]]
        j = sib.index(r); span = min(56, 9 * (len(sib) - 1))
        r["hue"] = p["hue"] - span / 2 + (span * j / (len(sib) - 1) if len(sib) > 1 else 0)
        r["color"] = hexc(r["hue"], 0.30 if r["residual"] else 0.62, 0.66 if j % 2 else 0.60)
for r in rows:
    if r["level"] == 3:
        p = by[r["parent"]]; sib = [k for k in rows if k["parent"] == p["code"]]
        j = sib.index(r); r["hue"] = p["hue"]
        m = len(sib)                                   # light-to-lighter ramp, interleaved so neighbours differ
        order = [x for x in range(0, m, 2)] + [x for x in range(1, m, 2)]
        r["color"] = hexc(r["hue"] + (6 if j % 2 else -6), 0.22 if r["residual"] else 0.62, 0.74 + 0.16 * order.index(j) / max(1, m - 1))
for i, r in enumerate(rows):
    r["ink"] = ink(r["color"]); r["seq"] = i; r["root"] = r["code"].split(".")[0]
    r["short"] = SHORT.get(r["code"], r["name"])
json.dump(rows, open("data/fgp_categories.json", "w"), ensure_ascii=False, indent=1)
cols = ["seq", "code", "level", "par", "root", "name", "short", "path", "shelf", "units", "color", "ink"]
with open("data/fgp_chart_rows.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(cols)
    for r in rows:
        w.writerow([r["seq"], r["code"], r["level"], r["parent"], r["root"], r["name"], r["short"], r["path"], r["shelfmarks"], r["units"], r["color"], r["ink"]])
with open("data/fgp_categories.csv", "w", newline="", encoding="utf-8-sig") as f:
    k = ["code", "level", "parent", "name", "path", "shelfmarks", "units", "residual", "n_children", "color"]
    w = csv.DictWriter(f, fieldnames=k); w.writeheader()
    for r in rows: w.writerow({x: r[x] for x in k})
tot = sum(r["shelfmarks"] for r in top)
for r in sorted(top, key=lambda r: -r["shelfmarks"])[:8]: print(r["code"], r["name"], r["shelfmarks"], f'{r["shelfmarks"]/tot:.1%}', f'{r["units"]/339789:.1%}', r["color"])
print(len(set(r["color"] for r in rows)), "distinct colours of", len(rows))
