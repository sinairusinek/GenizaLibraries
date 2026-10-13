"""The 114 book lists of Allony's volume, transcribed from its table of contents (pp. 5-9 of the front matter).

Dates and places are given only where the table of contents states them; the 'inferred' columns
come from general knowledge of the persons named and are NOT from the book's front matter.
"""
import csv, json, collections
G = {"A": ("רשימות מלאי של ספריות פרטיות", "Private library inventories"),
     "B": ("שיטות קיטלוג ומיון", "Cataloguing and classification methods"),
     "C": ("רשימות של וראק", "Lists of a warraq (bookseller)"),
     "D": ("המסחר בספרים", "Book trade"),
     "E": ("עזבונות", "Estates"),
     "F": ("השאלות ספרים", "Book loans"),
     "G": ("רשימות ספרים להעתקה", "Lists of books for copying"),
     "H": ("ספריות של בתי כנסת", "Synagogue libraries"),
     "I": ("פהארסה", "Fihrist (author bibliographies)"),
     "J": ("רשימות שונות", "Various lists"),
     "K": ("רשימות ר' יוסף ראש הסדר", "Lists of R. Yosef Rosh ha-Seder")}
SUB = [(1, 3, "שלוש רשימות מלאי מהמאה האחת-עשרה"), (4, 6, "שלוש רשימות מלאי מהמאה השתים-עשרה"),
       (7, 11, "חמש רשימות מלאי מהמאה השלוש-עשרה"), (12, 14, "שלוש רשימות מלאי מאוחרות"),
       (15, 19, "חמש רשימות מלאי קצרות"), (20, 22, "ספריות של מעתיקי ספרים מקצועיים"), (23, 29, "ספריות של חזנים"),
       (34, 35, "שתי רשימות מיד רושם אחד"), (37, 39, "שלושה קטלוגים מסווגים בכתיבת ידו של מאיר בן הלל בן צדוק אב"),
       (40, 42, "מפנקסו של וראק"), (43, 45, "שלוש רשימות בכתיבת שלמה הלוי"),
       (46, 51, "רשימות ספרים ומחיריהם"), (52, 54, "רשימות רוכשי ספרים"), (55, 58, "עסקות תיווך"),
       (59, 61, "רשימות של מלווי כספים בערבות ספרים"),
       (80, 82, "שלוש רשימות ספרים של בית כנסת הבבליים בפסטאט, ספרים שהיו שמורים בבית כנסת הירושלמיים")]
# list: (shelfmark, page, description in the table of contents)
L = {1: ("TS K 6.45", 3, ""), 2: ("ENA 1290, f. 6r", 6, ""), 3: ("TS NS J 585", 8, "ספרייתו של אבו גאלב מהמאה האחת-עשרה"),
 4: ("TS 10 K 20.9 + TS Misc 36.147", 11, ""), 5: ("TS NS 312.84", 28, "רשימת מלאי של ספריה פרטית בת עשרים וחמישה ספרים מהמאה השתים-עשרה"),
 6: ("TS NS J 94.53", 35, "רשימת מלאי חלקית מהמאה השתים-עשרה"), 7: ("ENA 2687, 1", 39, ""),
 8: ("TS 16.19", 42, "רשימת מלאי שלמה של ספריה פרטית מהמאה השלוש-עשרה בת מאה ושבעים ספרים"),
 9: ("Mosseri I. 106", 49, "רשימת מלאי קצרה מהמאה השלוש-עשרה"), 10: ("Bodl MS Heb d 66, f. 68", 51, ""),
 11: ("TS K 3.25-26", 54, "ספרייתו של שלמה בן אליה הדיין"), 12: ("TS K 3.27", 57, "רשימת ספרים מסופררת על פתק מהמאה הארבע-עשרה"),
 13: ("Harkavy K.5", 59, "רשימת מלאי קראית מהמאה השש-עשרה מסודרת לפי נושאים"), 14: ("JRL B 4337", 64, "רשימת ספרים מהמאה השש-עשרה"),
 15: ("TS Ar. 51.80", 66, "רשימת ספרים מסופררת"), 16: ("TS 10 K 20.7", 68, "רשימת מלאי ובה עשרים ושבעה עיולים מסופררים"),
 17: ("TS Ar. 52.213", 70, "קטלוג של ספריה פרטית"), 18: ("TS Ar. 39.491", 72, ""), 19: ("TS 8 K 22.7", 75, "קטע מרשימת מלאי"),
 20: ("TS Ar. 51.89", 76, ""), 21: ("BL Or 10118.1", 79, "ספרייתו של עזרא בן מאיר"), 22: ("TS K 3.41", 83, "ספרים נוספים מספריית עזרא בן מאיר"),
 23: ("Bodl MS Heb f. 36, f. 99", 89, ""), 24: ("TS 10 K 20.6", 91, "ספרייתו של הלל בן עלי החזן"), 25: ("ENA 2687, f. 5", 93, "ספריית שירה ופיוט"),
 26: ("TS NS 298.52", 94, "ספרייתו של ר' ישועה"), 27: ("TS NS 298.9", 99, "ספרייתו של ר' זכאי"), 28: ("ENA 2687, f. 2", 102, "רשימת ספרים שלא למכירה"),
 29: ("TS 8 K1", 105, "העברת בעלות על קובץ ספרים, משנת 1174"),
 30: ("TS Misc 36.150", 109, "רשימת מלאי מהמאה השתים-עשרה מסודרת לפי מדפים"), 31: ("TS Misc 36.149", 117, "רשימת מלאי מהמאה השתים-עשרה המסודרת לפי פתיחות הספרים"),
 32: ("TS NS J 125", 129, "רשימת מלאי מסודרת לפי שמות מחברי הספרים"), 33: ("TS K 19.11", 137, "לפי מחברים: פירוט פירושי התורה לרס\"ג בבעלות פרטית"),
 34: ("ENA 1290, f. 2", 138, "רשימת נושאים מסופררת"), 35: ("ENA 2687, f. 4", 141, "טיוטה של קטלוג ספרים לפי נושאים"),
 36: ("Frank I, 34", 143, "רשימת מלאי של ספרים לפי סוגיהם"), 37: ("TS K 3.16", 145, "קטלוג ספרים לפי מקצועות"),
 38: ("TS Ar. 51.79", 148, "רשימת ספרים מסופררת ומסודרת לפי סוגי הספרים"), 39: ("ENA 1290, f. 5", 152, "פירוט ספרי הגאונים המצויים בספריה פרטית"),
 40: ("Bodl MS Heb f 22, fs. 25b-52b", 157, ""), 41: ("Bodl MS Heb d 66, f. 129", 181, "איגרת של וראק: נסים ברבי שלה"),
 42: ("TS NS 228.3", 183, "עסקי הספרים של מאיר בן הלל בן צדוק אב"), 43: ("TS K 3.14", 186, ""), 44: ("ENA 2687, f. 6", 190, ""), 45: ("TS K 3.28", 196, ""),
 46: ("Bodl MS Heb d 66, fs. 131-132", 201, ""), 47: ("ENA 1290, f. 7", 206, ""), 48: ("Bodl MS Heb b3, f. 35b", 208, ""), 49: ("TS AS 86.228", 209, ""),
 50: ("TS 10 K 20.4", 210, "רשימת ספרים על קלף בצירוף מחיר"), 51: ("Bodl MS Heb C 96", 211, "רשימה קצרה של ספרי רפואה ומחיריהם"),
 52: ("TS AS 147.26", 212, ""), 53: ("TS K 3.46", 214, ""), 54: ("ENA 1290, f. 3", 216, "מכירת עיזבון"),
 55: ("TS Ar. 51.78", 218, "יפת, סוכן הספרים מתווך בין הבעלים לנשיא, הקונה"), 56: ("Bodl MS Heb d 66, f. 119", 220, "עיסקה בתיווך ספרים של שלמה בן אליה הדיין"),
 57: ("TS 8 J 6.7", 221, "זכרון עדות על רכישת ספרים בידי שלמה בן אליה הדיין"), 58: ("TS NS 83.37", 223, "רכישת ספריה"),
 59: ("TS Ar. 51.76-77", 225, ""), 60: ("ENA 3774, f. 10", 228, ""), 61: ("TS Ar. 52.214", 230, ""),
 62: ("TS 10 K 20.8", 235, "עיזבון מסוף המאה האחת-עשרה"), 63: ("ENA 1290, f. 16", 238, "מעזבונו של הרופא אבו אלעז: רשימת הספרים וקוניהם"),
 64: ("TS NS J 173", 241, "מעזבונו של הרופא אבו סעד"), 65: ("TS K 3.32", 252, "מעזבונו של ר' יצחק בן משה"), 66: ("JRL 66B 358.4", 255, "מעזבונו של ר' יוסף"),
 67: ("TS 20.44", 256, "מעזבונו של ר' אברהם החסיד"), 68: ("TS 16.284 verso", 264, "מרכושו של ר' יצחק - ספרים ערביים וחומרי כריכה"),
 69: ("TS Ar. 51.75", 265, "עיזבון מאלכסנדריה"), 70: ("TS NS 108.151", 268, "בן רושם את עזבון אביו"), 71: ("TS K 3.45", 273, "עיזבון אנונימי"),
 72: ("WC Misc I, f. 51", 277, "רשימת ספרים שהושאלו לאבו סעד"), 73: ("TS 10 K 131", 279, "רשימת ספרים שהושאלו לנתן בן ישועה"),
 74: ("Bodl MS Heb 35a", 281, "רשימת ספרים שהושאלו לשלמה"), 75: ("TS Misc 36.134", 282, "בקשה להשאלת ספרים"),
 76: ("TS Misc 8.45", 285, "העתקת ספרים ומחירה"), 77: ("Bodl MS Heb d 66, f. 130", 286, "בקשה להעתקת ספרים"),
 78: ("BL Or 10656.5", 287, "רשימת מוכר ספרים המעסיק מעתיקים"), 79: ("TS K 3.15", 290, "העתקת ספרים על ידי תלמידים"),
 80: ("TS 20.47", 295, ""), 81: ("Bodl MS Heb f 56, f. 50", 299, ""), 82: ("Bodl MS Heb f 56, f. 49", 303, ""),
 83: ("RNL Yevr. Arab. II. 1118", 306, "רשימת ספרים קראית בארון הקודש"),
 84: ("JRL Gaster Parch. 47", 311, "פהרסת ספרי רס\"ג"), 85: ("TS 10 G 5.7", 312, "פהרסת רס\"ג שחובר בידי בניו"), 86: ("BL Or 5552 B", 315, "פהרסת ספרי רב שמואל בן חופני"),
 87: ("TS K 6.117", 319, ""), 88: ("TS Misc 28.31", 320, ""), 89: ("TS Misc 28.42", 321, ""), 90: ("ENA 1290, f. 4", 322, ""), 91: ("TS AS 146.55", 323, ""),
 92: ("TS AS 55.46", 324, ""), 93: ("Antonin 349", 326, ""), 94: ("Mosseri Li II", 327, ""), 95: ("RNL [Firkovitch II] Evr.-Ar. 1:127, fol. 1a", 328, ""), 96: ("TS J 1.47", 330, ""),
 97: ("ENA 2539", 333, ""), 98: ("TS Misc 36.148", 346, ""), 99: ("TS K6.170", 357, ""), 100: ("TS NS 298.3", 373, ""), 101: ("TS K 3.44", 379, ""),
 102: ("TS 10 K 20.10", 386, ""), 103: ("TS NS 309.65", 390, ""), 104: ("ENA 2687, f. 36", 396, ""), 105: ("TS C 2.146", 400, ""), 106: ("DK 123g", 403, ""),
 107: ("WC Talmudica II, f. 30", 405, ""), 108: ("TS K 3.42", 407, ""), 109: ("TS NS 308.39", 409, ""), 110: ("TS C 7.169", 413, ""),
 111: ("TS Misc 36.184", 414, "רשימת ספרי רפואה ותוכן ספר היסטוריה"), 112: ("Bodl MS Heb d 44, fs 83-84", 416, ""), 113: ("TS K 3.1", 421, ""), 114: ("TS NS J 94.126", 427, "")}
GR = [(1, 29, "A"), (30, 39, "B"), (40, 45, "C"), (46, 61, "D"), (62, 71, "E"), (72, 75, "F"), (76, 79, "G"), (80, 83, "H"), (84, 86, "I"), (87, 96, "J"), (97, 114, "K")]
DATE = {}                                              # stated in the table of contents
for n in (1, 2, 3): DATE[n] = ("11th century", 1000, 1099)
for n in (4, 5, 6, 30, 31): DATE[n] = ("12th century", 1100, 1199)
for n in (7, 8, 9, 10, 11): DATE[n] = ("13th century", 1200, 1299)
DATE[12] = ("14th century", 1300, 1399); DATE[13] = DATE[14] = ("16th century", 1500, 1599)
DATE[29] = ("1174", 1174, 1174); DATE[62] = ("end of the 11th century", 1075, 1099)
PLACE = {69: "Alexandria", 80: "Fustat (Babylonian synagogue)", 81: "Fustat (Babylonian synagogue)", 82: "Fustat (Babylonian synagogue)"}
INF = {}                                               # NOT from the front matter: general knowledge of the persons named
for n in range(97, 115): INF[n] = ("c. 1190-1220 (Yosef Rosh ha-Seder)", "Fustat")
for n in (11, 56, 57): INF[n] = ("first half of the 13th century (Shlomo b. Eliyah)", "Fustat")
INF[67] = ("1223 (death of Abraham he-Hasid)", "Fustat")
for n in (84, 85): INF[n] = ("works of Saadia Gaon (d. 942); list later", "")
INF[86] = ("works of Shmuel b. Hofni (d. 1013); list later", "")
E = json.load(open("data/allony_index.json"))
nref = collections.Counter(); nent = collections.defaultdict(set)
for e in E:
    for r in e["refs"]: nref[r["list"]] += len(r["lines"]); nent[r["list"]].add(e["id"])
rows = []
for n in range(1, 115):
    g = next(c for a, b, c in GR if a <= n <= b); sub = next((s for a, b, s in SUB if a <= n <= b), "")
    d = DATE.get(n, ("", "", "")); inf = INF.get(n, ("", ""))
    rows.append(dict(list=n, shelfmark=L[n][0], type_code=g, type_he=G[g][0], type_en=G[g][1], subgroup_he=sub, description_he=L[n][2], page=L[n][1],
                     date_stated=d[0], date_from=d[1], date_to=d[2], place_stated=PLACE.get(n, ""),
                     date_inferred=inf[0], place_inferred=inf[1], index_entries=len(nent[n]), index_references=nref[n]))
with open("data/allony_lists.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
json.dump(rows, open("data/allony_lists.json", "w"), ensure_ascii=False, indent=1)
by = {r["list"]: r for r in rows}
# references file: add shelfmark and list type
with open("data/allony_references.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["entry_id", "headword", "entry_type", "fgp_code", "list", "shelfmark", "list_type_code", "list_type", "list_date_stated", "lines", "note"])
    for e in E:
        k = e["classification"]
        for r in e["refs"]:
            b = by.get(r["list"])
            for ln in r["lines"]:
                w.writerow([e["id"], e["headword"], k["type"], k["fgp_code"], r["list"], b["shelfmark"] if b else "", b["type_code"] if b else "", b["type_en"] if b else "", b["date_stated"] if b else "", ln, r["note"]])
print(len(rows), "lists;", sum(bool(r["date_stated"]) for r in rows), "with a stated date;", sum(bool(r["place_stated"]) for r in rows), "with a stated place;",
      sum(bool(r["date_stated"] or r["date_inferred"]) for r in rows), "dated incl. inferred")
print("refs in dated lists:", sum(r["index_references"] for r in rows if r["date_stated"]), "of", sum(nref.values()), "| incl inferred:", sum(r["index_references"] for r in rows if r["date_stated"] or r["date_inferred"]))
# Q1: where do non-work entries occur?
T = collections.defaultdict(collections.Counter)
for e in E:
    for r in e["refs"]:
        b = by.get(r["list"])
        if b: T[e["classification"]["type"]][b["type_code"]] += len(r["lines"])
for t, c in T.items(): print(t, sum(c.values()), dict(sorted(c.items())))
P = [e for e in E if e["classification"]["type"] == "person" and e["refs"]]
pl = collections.Counter(r["list"] for e in P for r in e["refs"] for _ in r["lines"])
print("person refs top lists:", pl.most_common(10))
print("person entries with refs only in list 40:", sum(1 for e in P if {r["list"] for r in e["refs"]} == {40}), "of", len(P))
import random; random.seed(3)
for e in random.sample(P, 14): print("  P", e["headword"], [(r["list"]) for r in e["refs"]], e["classification"]["note"])
O = sorted([e for e in E if e["classification"]["type"] == "object/term"], key=lambda e: -e["n_refs"])[:14]
print("  O", [(e["headword"], e["gloss"], e["n_refs"]) for e in O])
