"""Parse the Allony index (Word file) into structured entries.

Each entry: headword, gloss (=...), attributed author (ל...), references
(list number + line numbers + note), cross-references (see / see also),
highlighting in the Word file.
"""
import docx, re, json, csv, sys, unicodedata, difflib, collections

SRC = "private/sources/מפתח אלוני ללא מובאות.docx"   # not in the repository
NIQQUD = re.compile(r"[֑-ׇ]")
DASH = r"(?:--|–|—|-)"
SEE = re.compile(r"(?:^|\s|;|\.|" + DASH + r")\s*(ראו גם|ר' גם|וראו גם|ראו|ראה גם|ראה)\s*:?\s*")

def hl(run):
    h = run.font.highlight_color
    return None if h is None else ("green" if "GREEN" in str(h) else "yellow" if "YELLOW" in str(h) else str(h))

def norm(s):
    s = NIQQUD.sub("", s)
    s = re.sub(r"\(=[^)]*\)", " ", s)
    s = re.sub(r"[<>\[\]\(\)\?\.,:;\"״]", " ", s)
    s = s.replace("׳", "'")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def key(s):
    """Loose matching key: drop article, generic 'book' words, final-letter/spelling noise."""
    s = norm(s)
    toks = []
    for t in s.split():
        t = re.sub(r"^(אל|ה)(?=.{3,})", "", t) if t not in ("אלא",) else t
        toks.append(t)
    while toks and toks[0] in ("ספר", "כתאב", "כתב", "ר'", "רבי", "רב", "רבנו", "רבינו", "מר"):
        toks = toks[1:]
    return " ".join(toks).replace("'", "")

def parse_refs(s):
    """'40 184, 393; 81 12 (note)' -> [{list, lines:[...], note}]"""
    refs, problems = [], []
    for seg in re.split(r";", s):
        seg = seg.strip(" .\t")
        if not seg: continue
        m = re.match(r"^(\d{1,3})\s+(.*)$", seg)
        if not m:
            if refs and re.fullmatch(r"[\d\s,\-]+", seg):   # 'N a; b-c' : continuation of the same list
                for a, b in re.findall(r"(\d+)(?:\s*-\s*(\d+))?", seg):
                    refs[-1]["lines"].append(f"{min(int(a),int(b))}-{max(int(a),int(b))}" if b else a)
            else:
                problems.append(seg)
            continue
        lst, rest = int(m.group(1)), m.group(2)
        notes = re.findall(r"\(([^)]*)\)", rest)
        body = re.sub(r"\([^)]*\)", " ", rest)
        lines = []
        for a, b in re.findall(r"(\d+)(?:\s*-\s*(\d+))?", body):
            if b:
                lo, hi = sorted((int(a), int(b)))   # ranges are written right-to-left: '19-10' = 10-19
                lines.append(f"{lo}-{hi}")
            else:
                lines.append(a)
        leftover = re.sub(r"[\d\s,\-]", "", body)
        if leftover: notes.append(leftover)
        if not lines: problems.append(seg)
        refs.append(dict(list=lst, lines=lines, note="; ".join(n.strip() for n in notes if n.strip())))
    return refs, problems

doc = docx.Document(SRC)
entries = []
for i, p in enumerate(doc.paragraphs):
    raw = p.text.replace("‏", "").replace("‎", "")
    text = raw.strip()
    if not text or p.style.name.startswith("Heading") or "שורות מתוך" in text or text.startswith("קובץ Alo_Ind"):
        continue
    if re.fullmatch(r"[\d\s,.;\-]+", text) and entries:      # orphan continuation line
        entries[-1]["raw"] += " " + text; entries[-1]["_cont"] = text
        continue
    if not SEE.search(text) and not re.search(r"\d", text) and re.search(r"\S\s+ר'\s+\S", text) and not re.match(r"^(ר'|רב|רבי)\s", text):
        text = re.sub(r"\s+ר'\s+", " -- ראו ", text, count=1)
    marks = {hl(r) for r in p.runs if r.text.strip()} - {None}
    e = dict(id=len(entries) + 1, para=i, raw=text,
             sub_entry=raw.startswith("\t") or bool(p.paragraph_format.first_line_indent),
             highlight=",".join(sorted(marks)))
    # 1. split off cross-references
    m = SEE.search(text)
    main, see_part = (text[:m.start()], text[m.start():]) if m else (text, "")
    main = re.sub(r"\s*" + DASH + r"\s*$", "", main).strip(" ;")
    see, see_also = [], []
    if see_part:
        pieces = SEE.split(see_part)  # ['', kw, body, kw, body ...]
        for kw, body in zip(pieces[1::2], pieces[2::2]):
            body = body.strip(" .;")
            if not body: continue
            (see_also if "גם" in kw else see).append(body)
    # 2. split headword from references (first standalone list number)
    m = re.search(r"(?<![\d\w])(\d{1,3})\s+(?=[\d\(])", main)
    if m:
        head, refpart = main[:m.start()].strip(), main[m.start():]
    else:
        head, refpart = main.strip(" ."), ""
    refs, problems = parse_refs(refpart)
    # 3. gloss, author
    gl = re.findall(r"\(=\s*([^)]*)\)", head)
    head_clean = re.sub(r"\s*\(=[^)]*\)", "", head).strip(" .,")
    am = re.search(r"\sל(<[^>]*>\s*)?((?:ר'|רב|רבי|רבנו|רבינו|בן|אבן|אבו|רס\"ג|רשב\"ח|רי\"ף|רמב\"ם|ר\"ח)\S*.*)$", head_clean)
    e.update(headword=head_clean, headword_plain=norm(head_clean), gloss="; ".join(gl),
             attributed_to=(norm(am.group(0))[1:] if am else ""),
             refs=refs, n_lists=len({r["list"] for r in refs}),
             n_refs=sum(len(r["lines"]) for r in refs),
             see=see, see_also=see_also,
             kind=("see-only" if (see and not refs) else "entry" if refs else "see-also-only" if see_also else "no-reference"),
             parse_problems=problems)
    entries.append(e)

# ---- resolve cross-references to entry ids
by_plain = collections.defaultdict(list); by_key = collections.defaultdict(list)
for e in entries:
    by_plain[e["headword_plain"]].append(e["id"]); by_key[key(e["headword"])].append(e["id"])
keys = list(by_key)

def compact(k):
    k = re.sub(r"\b(אבן|אבו|אבי|בר|ביר|ולד)\b", "בן", k)
    return k.replace(" ", "")
by_compact = collections.defaultdict(list)
for e in entries: by_compact[compact(key(e["headword"]))].append(e["id"])
compacts = list(by_compact)
tokset = {e["id"]: set(re.sub(r"\b(אבן|אבו|אבי|בר)\b", "בן", key(e["headword"])).split()) for e in entries}

def resolve(t):
    t0 = re.sub(r"\s*\(=[^)]*\)", "", t).strip(" .,")
    if norm(t0) in by_plain: return by_plain[norm(t0)], "exact"
    k = key(t0)
    if not k: return [], "unresolved"
    if k in by_key: return by_key[k], "normalized"
    if compact(k) in by_compact: return by_compact[compact(k)], "normalized"
    pre = [kk for kk in keys if kk.startswith(k + " ")]
    if len(pre) == 1: return by_key[pre[0]], "prefix"
    if 1 < len(pre) <= 12: return sorted({i for kk in pre for i in by_key[kk]}), "group"
    c = difflib.get_close_matches(compact(k), compacts, n=1, cutoff=0.84)
    if c: return by_compact[c[0]], "fuzzy"
    tt = set(re.sub(r"\b(אבן|אבו|אבי|בר)\b", "בן", k).split())
    if len(tt) >= 2:
        hits = [i for i, ts in tokset.items() if tt <= ts or (len(ts) >= 2 and ts <= tt)]
        if len(hits) == 1: return hits, "token-match"
    if len(pre) > 12: return sorted({i for kk in pre for i in by_key[kk]})[:12], "group"
    return [], "unresolved"

GOOD = ("exact", "normalized", "prefix", "group", "fuzzy", "token-match")
def resolve_field(body):
    """A cross-reference body may hold several targets (';' or ','), or one inverted name with a comma."""
    ids, how = resolve(body)
    if how in ("exact", "normalized"):
        return [dict(target=body, ids=ids, match=how)]
    out = []
    for part in [x.strip() for x in body.split(";") if x.strip()]:
        ids, how = resolve(part)
        if how not in ("exact", "normalized") and "," in part:
            names = [x.strip() for x in part.split(",") if x.strip()]
            subs = [resolve(x) for x in names]
            if sum(h in GOOD for _, h in subs) >= max(1, len(subs) - 1) and (how == "unresolved" or all(h in GOOD for _, h in subs)):
                out += [dict(target=x, ids=i, match=h) for x, (i, h) in zip(names, subs)]
                continue
        out.append(dict(target=part, ids=ids, match=how))
    return out

stats = collections.Counter()
for e in entries:
    e["xrefs"] = []
    for typ, bodies in (("see", e["see"]), ("see_also", e["see_also"])):
        for b in bodies:
            for r in resolve_field(b):
                r["type"] = typ; e["xrefs"].append(r); stats[(typ, r["match"])] += 1
for e in entries:
    e["referred_from"] = []
byid = {e["id"]: e for e in entries}
for e in entries:
    for r in e["xrefs"]:
        for t in r["ids"]:
            if t != e["id"]: byid[t]["referred_from"].append(e["id"])

json.dump(entries, open("data/allony_index.json", "w"), ensure_ascii=False, indent=1)
with open("data/allony_index.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["id", "headword", "gloss", "attributed_to", "kind", "sub_entry", "highlight", "n_lists", "n_refs", "references", "see", "see_also", "raw"])
    for e in entries:
        w.writerow([e["id"], e["headword"], e["gloss"], e["attributed_to"], e["kind"], int(e["sub_entry"]), e["highlight"], e["n_lists"], e["n_refs"],
                    "; ".join(f'{r["list"]}: {", ".join(r["lines"])}' + (f' ({r["note"]})' if r["note"] else "") for r in e["refs"]),
                    " | ".join(e["see"]), " | ".join(e["see_also"]), e["raw"]])
with open("data/allony_references.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["entry_id", "headword", "list", "lines", "note"])
    for e in entries:
        for r in e["refs"]:
            for ln in r["lines"]: w.writerow([e["id"], e["headword"], r["list"], ln, r["note"]])
with open("data/allony_crossrefs.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["from_id", "from_headword", "type", "target_text", "match", "target_ids", "target_headwords"])
    for e in entries:
        for r in e["xrefs"]:
            w.writerow([e["id"], e["headword"], r["type"], r["target"], r["match"], " ".join(map(str, r["ids"])), " | ".join(byid[t]["headword"] for t in r["ids"])])

print("entries", len(entries), collections.Counter(e["kind"] for e in entries))
print("with gloss", sum(bool(e["gloss"]) for e in entries), "attributed", sum(bool(e["attributed_to"]) for e in entries), "highlight", collections.Counter(e["highlight"] for e in entries))
print("lists cited", len({r["list"] for e in entries for r in e["refs"]}), "max list", max(r["list"] for e in entries for r in e["refs"]), "ref points", sum(e["n_refs"] for e in entries))
print("xrefs", sum(stats.values()), dict(stats))
print("parse problems", sum(bool(e["parse_problems"]) for e in entries))
for e in [e for e in entries if e["parse_problems"]][:25]: print("  P", e["id"], e["raw"][:110], "=>", e["parse_problems"])
print("no-reference:"); 
for e in [e for e in entries if e["kind"] == "no-reference"][:30]: print("  N", e["id"], e["raw"][:110])
print("unresolved sample:")
n=0
for e in entries:
    for r in e["xrefs"]:
        if r["match"] in ("unresolved",) and n<60: n+=1; print("  U", e["id"], e["headword"], "->", r["target"], r["match"])
print("fuzzy sample:"); n=0
for e in entries:
    for r in e["xrefs"]:
        if r["match"] in ("fuzzy","token-match") and n<40: n+=1; print("  F", r["match"], e["headword"], "->", r["target"], "=>", byid[r["ids"][0]]["headword"])
