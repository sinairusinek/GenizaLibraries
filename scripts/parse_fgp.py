"""Parse the FGP 'fields with statistics' printout into a 3-level hierarchy."""
import fitz, collections, json, csv, sys, re
src, outdir = sys.argv[1], sys.argv[2]
rows = []
for page in fitz.open(src):
    lines = collections.defaultdict(list)
    for w in page.get_text("words"):
        lines[round(w[1] / 3)].append(w)
    for k in sorted(lines):
        ws = sorted(lines[k], key=lambda w: w[0])
        nums = [w for w in ws if re.fullmatch(r"\d+", w[4]) and w[0] < 340]
        label = [w for w in ws if w[0] >= 340]
        if len(nums) != 2 or not label:
            continue
        right = max(w[2] for w in label)
        level = 1 if right > 512 else 2 if right > 497 else 3
        # words come left-to-right visually; Hebrew reads right-to-left
        text = ""
        for w in sorted(label, key=lambda w: -w[0]):
            t = w[4]
            text += t if (not text or t in ',)"' or text.endswith(('(', '"', '-')) or t == '-' or len(t) == 1 and t in 'ל') else " " + t
        rows.append(dict(level=level, name=text, units=int(nums[0][4]), shelfmarks=int(nums[1][4])))
json.dump(rows, open(outdir + "/fgp_raw_rows.json", "w"), ensure_ascii=False, indent=1)
for r in rows: print(r["level"], r["name"], r["shelfmarks"], r["units"])
