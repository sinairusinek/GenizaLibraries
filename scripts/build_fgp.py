"""Assign codes to the FGP hierarchy, check additivity, write CSV + JSON."""
import json, csv
rows = json.load(open("data/fgp_raw_rows.json"))
for r in rows:
    if r["name"].startswith("עזרי הוראה"):
        r["name"] = "עזרי הוראה, נסיונות קולמוס, תרגילי כתיבה, שרבוטים"
    r["name"] = r["name"].replace("הלכה-", "הלכה - ").replace("ותשובות-", "ותשובות - ").replace("פתקים / רישומים", "פתקים/רישומים")
c = [0, 0, 0]; stack = {}
for r in rows:
    l = r["level"]; c[l - 1] += 1
    for j in range(l, 3): c[j] = 0
    r["code"] = ".".join(str(x) for x in c[:l])
    stack[l] = r
    r["parent"] = stack[l - 1]["code"] if l > 1 else ""
    r["path"] = " > ".join(stack[j]["name"] for j in range(1, l + 1))
    r["residual"] = r["name"].startswith("לא הוגדר")
by = {r["code"]: r for r in rows}
for r in rows:
    kids = [k for k in rows if k["parent"] == r["code"]]
    r["n_children"] = len(kids)
    for m in ("shelfmarks", "units"):
        if kids and sum(k[m] for k in kids) != r[m]:
            print("NOT ADDITIVE", r["code"], r["name"], m, r[m], sum(k[m] for k in kids))
top = [r for r in rows if r["level"] == 1]
print("top-level fields", len(top), "all rows", len(rows), "L2", sum(r["level"]==2 for r in rows), "L3", sum(r["level"]==3 for r in rows))
print("sum shelfmarks", sum(r["shelfmarks"] for r in top), "sum units", sum(r["units"] for r in top))
json.dump(rows, open("data/fgp_categories.json", "w"), ensure_ascii=False, indent=1)
with open("data/fgp_categories.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["code", "level", "parent", "name", "path", "shelfmarks", "units", "residual", "n_children"]); w.writeheader()
    for r in rows: w.writerow({k: r[k] for k in w.fieldnames})
