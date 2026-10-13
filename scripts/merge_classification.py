"""Merge the six classification batches, harmonise conventions, write the outputs.

Types: W work/genre, A author, P person, O object or codicological term, G place/group, X other.
"""
import json, csv, collections, re, glob
E = json.load(open("data/allony_index.json")); byid = {e["id"]: e for e in E}
CAT = {c["code"]: c for c in json.load(open("data/fgp_categories.json"))}
cls = {}
for fn in sorted(glob.glob("data/classification_raw/out*.tsv")):
    for line in open(fn, encoding="utf-8"):
        p = line.rstrip("\n").split("\t") + [""] * 5
        cls[int(p[0])] = dict(type=p[1].strip(), code=p[2].strip(), conf=p[3].strip(), note=p[4].strip(), rule="")
log = collections.Counter()
CONT = {2270, 2271, 2421}                    # wrapped lines of the preceding entry, not entries
for e in E:
    c = cls[e["id"]]; hw = e["headword_plain"]
    if e["id"] in CONT:
        c.update(type="X", code="", conf="", note="continuation of the previous index line", rule="continuation"); continue
    if c["type"] not in ("W", "A"): c["code"] = ""
    if c["type"] == "W":
        if "אלפאט" in hw and c["code"] != "16":
            c.update(code="16", conf="M", rule="glossary -> 16"); log["glossary"] += 1
        if ("שראיע" in hw or re.search(r"(ספר )?המצוות ל", hw)) and c["code"] in ("4.4.1", "4.4.2", "4.4.8"):
            c.update(code="4.5", conf="M", rule="book of commandments -> 4.5"); log["mitzvot"] += 1
    if e["id"] == 665: c.update(code="3.7", rule="tractate alone -> 3.7")
# a pure 'see' entry pointing at exactly one work takes that work's class
for e in E:
    if e["kind"] != "see-only" or e["id"] in CONT: continue
    xs = [x for x in e["xrefs"] if x["type"] == "see"]
    if len(xs) != 1 or xs[0]["match"] not in ("exact", "normalized", "prefix") or len(xs[0]["ids"]) != 1: continue
    t = cls[xs[0]["ids"][0]]; c = cls[e["id"]]
    if c["type"] == "W" and t["type"] == "W" and t["code"] and t["code"] != c["code"]:
        c.update(code=t["code"], conf=min(c["conf"] or "M", t["conf"] or "M", key="HML".index) if False else ("L" if "L" in (c["conf"], t["conf"]) else "M"),
                 rule=f'class of see-target #{xs[0]["ids"][0]} (was {c["code"]})'); log["inherit"] += 1
print(dict(log))
TYPE = dict(W="work", A="author", P="person", O="object/term", G="place/group", X="other")
def lvl(code, n):
    parts = code.split(".")
    return ".".join(parts[:n]) if len(parts) >= n else ""
out = []
for e in E:
    c = cls[e["id"]]; code = c["code"]
    row = dict(id=e["id"], headword=e["headword"], gloss=e["gloss"], attributed_to=e["attributed_to"], kind=e["kind"],
               highlight=e["highlight"], n_lists=e["n_lists"], n_refs=e["n_refs"], type=TYPE[c["type"]], fgp_code=code,
               fgp_path=CAT[code]["path"] if code else "", confidence=c["conf"] if code else "", note=c["note"], rule=c["rule"],
               field=CAT[lvl(code, 1)]["name"] if code else "", sub_field=CAT[lvl(code, 2)]["name"] if lvl(code, 2) else "",
               sub_sub_field=CAT[lvl(code, 3)]["name"] if lvl(code, 3) else "", colour=CAT[code]["color"] if code else "")
    e["classification"] = {k: row[k] for k in ("type", "fgp_code", "fgp_path", "confidence", "note", "rule")}
    out.append(row)
json.dump(E, open("data/allony_index.json", "w"), ensure_ascii=False, indent=1)
with open("data/allony_classification.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print(collections.Counter(r["type"] for r in out))
cl = [r for r in out if r["fgp_code"]]
print("classified", len(cl), collections.Counter(r["confidence"] for r in cl))
by1 = collections.Counter(r["fgp_code"].split(".")[0] for r in cl); refs1 = collections.Counter()
for r in cl: refs1[r["fgp_code"].split(".")[0]] += r["n_refs"]
tot = sum(by1.values()); tr = sum(refs1.values())
for k, v in by1.most_common(): print(k, CAT[k]["name"], v, f"{v/tot:.1%}", "refs", refs1[k], f"{refs1[k]/tr:.1%}", "FGP shelf", f'{CAT[k]["shelfmarks"]/340533:.1%}')
print("yellow highlighted:", collections.Counter(r["type"] for r in out if r["highlight"]), collections.Counter(r["fgp_code"].split(".")[0] for r in out if r["highlight"]).most_common(6))
# ---- table data for the doc: classified entries, ~9 parts
SHORT = {c: v["short"] for c, v in CAT.items()}
def cell(code, n):
    k = lvl(code, n)
    if not k: return ["", "", ""]
    name = SHORT[k] if n == 1 else re.sub(r"^(הלכה|שאלות ותשובות) - ", "", CAT[k]["name"])
    return [CAT[k]["color"], name, CAT[k]["ink"]]
def trunc(s, n): return s if len(s) <= n else s[:n - 1] + "…"
parts = 12; size = -(-len(cl) // parts)
for k in range(parts):
    chunk = cl[k * size:(k + 1) * size]
    with open(f"data/table_part{k+1}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["id", "head", "full", "conf", "code", "c1", "n1", "k1", "c2", "n2", "k2", "c3", "n3", "k3"])
        for r in chunk:
            full = r["headword"] + (f' (={r["gloss"]})' if r["gloss"] else "") + f' · {r["fgp_code"]} {r["fgp_path"]} · {r["type"]}, confidence {r["confidence"]}' + (f' · {r["note"]}' if r["note"] else "")
            w.writerow([r["id"], trunc(r["headword"], 44), full, r["confidence"], r["fgp_code"]] + cell(r["fgp_code"], 1) + cell(r["fgp_code"], 2) + cell(r["fgp_code"], 3))
    print(k + 1, len(chunk), chunk[0]["id"], chunk[-1]["id"], chunk[0]["headword"][:20], "|", chunk[-1]["headword"][:20])
