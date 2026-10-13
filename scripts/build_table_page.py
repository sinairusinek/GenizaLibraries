"""Build index.html, the self-contained page served by GitHub Pages, from the data files."""
import json, re
E = json.load(open("data/allony_index.json")); C = json.load(open("data/fgp_categories.json"))
CAT = {c["code"]: c for c in C}
cats = {c["code"]: [c["name"] if c["level"] == 1 else re.sub(r"^(הלכה|שאלות ותשובות) - ", "", c["name"]), c["color"], c["ink"], c["seq"], c["path"], c["shelfmarks"], c["units"]] for c in C}
rows = []
for e in E:
    k = e["classification"]
    refs = "; ".join(f'{r["list"]}: {", ".join(r["lines"])}' + (f' ({r["note"]})' if r["note"] else "") for r in e["refs"])
    xr = " · ".join(("ראו " if x["type"] == "see" else "ראו גם ") + x["target"] + ("" if x["ids"] else " (?)") for x in e["xrefs"])
    rows.append([e["id"], e["headword"], e["gloss"], e["attributed_to"], k["type"], k["fgp_code"], k["confidence"],
                 e["n_lists"], e["n_refs"], refs, xr, (k["note"] + (" · " + k["rule"] if k["rule"] else "")).strip(" ·"), e["highlight"]])
LL = json.load(open("data/allony_lists.json"))
lists = [[l["list"], l["shelfmark"], l["type_code"], l["type_en"], l["type_he"], l["subgroup_he"], l["description_he"], l["page"], l["date_stated"], l["pgp_date"],
          l["date_inferred"], l["place_stated"], l["pgp_place"], l["place_inferred"], l["index_entries"], l["index_references"], l["pgp_url"], l["pgp_description"],
          l["sort_year"] or (int(re.search(r"\d{4}", l["date_inferred"]).group()) if re.search(r"\d{4}", l["date_inferred"]) else 0)] for l in LL]
import collections
fgp = [[c["code"], c["shelfmarks"], c["units"]] for c in C if c["level"] == 1]
lf = collections.defaultdict(lambda: collections.Counter())
for e in E:
    code = e["classification"]["fgp_code"]
    if not code: continue
    for r in e["refs"]:
        if 1 <= r["list"] <= 114: lf[r["list"]][code.split(".")[0]] += len(r["lines"])
data = json.dumps({"cats": cats, "rows": rows, "lists": lists, "fgp": fgp, "lf": {str(k): dict(v) for k, v in lf.items()}}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = open("scripts/table_template.html", encoding="utf-8").read().replace("/*DATA*/", data)
open("index.html", "w", encoding="utf-8").write(html)
print(len(rows), "rows", len(html) // 1024, "KB")
