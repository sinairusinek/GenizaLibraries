"""Match the 114 Allony lists to Princeton Geniza Project records (pgp-metadata documents.csv) and pull date/place."""
import csv, sys, re, json, collections, html
csv.field_size_limit(10**9)
D = list(csv.DictReader(open(sys.argv[1], encoding="utf-8-sig")))
L = json.load(open("data/allony_lists.json"))
def nk(s):
    s = s.upper().replace("T-S", "TS").replace("VERSO", "").replace("RECTO", "")
    s = re.sub(r"\b(BODL|MS|FOLS?|FS|F)\b\.?", " ", s)
    s = re.sub(r"(\d)\s*[-–]\s*\d+[AB]?\b", r"\1", s)          # ranges: keep the first number
    s = re.sub(r"(\d)[RVAB]\b", r"\1", s)                      # 6r, 35b -> 6, 35
    return re.sub(r"[^A-Z0-9]", "", s)
idx = collections.defaultdict(list)
for d in D:
    for part in re.split(r"\s*\+\s*", d["shelfmark"]): idx[nk(part)].append(d)
def allony_pages(d):
    out = []
    for rec in d["scholarship_records"].split(";"):
        if re.search(r"Allony|אלוני|Jewish Library in the Middle Ages", rec):
            t = re.sub(r"<[^>]+>", "", html.unescape(rec))
            out += [int(a) for a in re.findall(r"(\d{1,3})\s*[–-]\s*\d{1,3}", t)] + [int(a) for a in re.findall(r"\bp?p?\.?\s*(\d{1,3})\b", t.split(")")[-1])]
    return out
AL = [d for d in D if re.search(r"Allony|אלוני|Jewish Library in the Middle Ages", d["scholarship_records"])]
pages = {l["page"]: l for l in L}
res = {}
for l in L:
    c = []
    for part in re.split(r"\s*\+\s*", l["shelfmark"]): c += idx.get(nk(part), [])
    c = list({d["pgpid"]: d for d in c}.values())
    how = "shelfmark"
    ca = [d for d in c if d in AL]
    if ca: c = ca; how = "shelfmark + cites Allony"
    if not c:
        c = [d for d in AL if l["page"] in allony_pages(d)]; how = "Allony page number"
    if len(c) > 1:
        cc = [d for d in c if l["page"] in allony_pages(d)] or [d for d in c if re.search(r"book|list|inventor|librar", d["description"] + d["type"], re.I)]
        if cc: c = cc
    res[l["list"]] = (c, how)
m = sum(1 for c, _ in res.values() if c); print("matched", m, "of 114;", collections.Counter(h for c, h in res.values() if c), "multi:", sum(1 for c, _ in res.values() if len(c) > 1))
print("unmatched:", [(n, by["shelfmark"]) for n, by in ((l["list"], l) for l in L) if not res[n][0]])
def clean(s): return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(s or ""))).strip()
out = []
for l in L:
    c, how = res[l["list"]]
    d = c[0] if c else None
    row = dict(list=l["list"], pgp_match=how if d else "", pgpid=d["pgpid"] if d else "", pgp_url=d["url"] if d else "", pgp_shelfmark=d["shelfmark"] if d else "",
               pgp_type=d["type"] if d else "", pgp_date_original=clean(d["doc_date_original"]) if d else "", pgp_date_standard=d["doc_date_standard"] if d else "",
               pgp_inferred_date=clean(d["inferred_date_display"]) if d else "", pgp_inferred_date_standard=d["inferred_date_standard"] if d else "",
               pgp_inferred_rationale=clean(d["inferred_date_rationale"]) if d else "", pgp_origin=clean(d["origin"]) if d else "", pgp_location=clean(d["location"]) if d else "",
               pgp_destination=clean(d["destination"]) if d else "", pgp_mentioned=clean(d["mentioned"]) if d else "", pgp_region=clean(d["region"]) if d else "",
               pgp_description=clean(d["description"]) if d else "", pgp_other_candidates=" ".join(x["pgpid"] for x in c[1:]))
    out.append(row)
json.dump(out, open("data/allony_lists_pgp.json", "w"), ensure_ascii=False, indent=1)
has = lambda k: sum(1 for r in out if r[k])
print({k: has(k) for k in ("pgp_date_standard", "pgp_inferred_date_standard", "pgp_origin", "pgp_location", "pgp_destination", "pgp_mentioned", "pgp_region", "pgp_description")})
print("any pgp date:", sum(1 for r in out if r["pgp_date_standard"] or r["pgp_inferred_date_standard"]), "any place:", sum(1 for r in out if r["pgp_origin"] or r["pgp_location"] or r["pgp_region"]))
for r in out[:12]: print(r["list"], r["pgp_shelfmark"], "|", r["pgp_date_standard"], "|", r["pgp_inferred_date"], r["pgp_inferred_date_standard"], "|", r["pgp_origin"], "|", r["pgp_location"], "|", r["pgp_mentioned"][:40], "|", r["pgp_description"][:90])
