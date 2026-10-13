# GenizaLibraries

Working data and a browsable page for comparing two views of the medieval Jewish library:

- the **book lists from the Cairo Genizah** published by N. Allony, through the index to that edition;
- the **surviving Genizah fragments**, through the subject statistics of the Friedberg Genizah Project (FGP).

**Page:** https://sinairusinek.github.io/GenizaLibraries/

## What the page shows

| Tab | Content |
| --- | --- |
| Overview | Share of each FGP field among Genizah fragments against its share of mentions in the book lists, and one pie per list. Clicking a slice lists the works behind it. |
| Talmud and halakha | The same, restricted to rabbinic and halakhic literature and broken into sub-fields. |
| Index entries | All 3,365 index entries with a suggested FGP class, sortable and searchable. |
| Book lists | The 114 lists with shelfmark, type, date and place by source. |

The whole dataset can be downloaded from the page as `allony_data.xlsx`.

## Read this before using the numbers

- **The FGP class of each entry is a suggestion.** It was assigned from general knowledge of the literature, in batches, by a language model (Claude), and was not checked against the book lists. Each class carries a confidence grade (H, M, L).
- **Identifications in the index are themselves uncertain.** The editors of the volume say so.
- **Over a quarter of all mentions come from one scholar's lists** (R. Yosef Rosh ha-Seder, lists 97–114).
- **The lists are of different kinds**: inventories, booksellers' notebooks, estates, loans, copying plans. Only some record ownership.
- **Dates and places are sparse.** Each value is marked by source: the book's contents page, the Princeton Geniza Project, or an inference from the person named. Inferred values are not from the book.
- **Shelfmarks were transcribed by eye** from a scanned contents page and may contain reading errors. 90 of the 114 were matched to Princeton Geniza Project records.

## Sources

1. Index to Nehemya Allony, *The Jewish Library in the Middle Ages: Book Lists from the Cairo Genizah*, ed. Miriam Frenkel and Haggai Ben-Shammai with Moshe Sokolow (Jerusalem: Ben-Zvi Institute, 2006), pp. 457–508, and the volume's table of contents.
2. Friedberg Genizah Project, list of fields with statistics (shelf numbers and units), as displayed on 9 October 2026.
3. Princeton Geniza Project, public document metadata ([pgp-metadata](https://github.com/princetongenizalab/pgp-metadata)), for dates and descriptions of the lists.

The source files themselves (the index as a Word file, the FGP printout, the scanned front matter) are not in this repository.

## Files

| Path | Content |
| --- | --- |
| `index.html` | The page. Self-contained; built by `scripts/build_table_page.py`. |
| `allony_data.xlsx` | All tables in one workbook; built by `scripts/build_xlsx.py`. |
| `data/allony_index.*` | The index entries: headword, gloss, attributed author, references, cross-references, classification. |
| `data/allony_classification.csv` | One row per entry with type, FGP class, confidence and note. |
| `data/allony_references.csv` | One row per line reference, with list, shelfmark and list type. |
| `data/allony_crossrefs.csv` | The 1,194 cross-references and how each target was matched. |
| `data/allony_lists.*` | The 114 lists: shelfmark, type, date and place by source, Princeton match. |
| `data/fgp_categories.*` | The 96 FGP categories in three levels, with counts and the colour used on the page. |
| `data/classification_raw/` | The six raw classification batches before harmonisation. |
| `scripts/` | Parsing, classification merge, list matching and build scripts. |

## Rebuilding

After editing a data file:

```
python3 scripts/build_xlsx.py
python3 scripts/build_table_page.py
```

The parsing scripts (`parse_fgp.py`, `parse_allony.py`) need the source files, which are not included. `match_pgp.py` takes the path to a downloaded copy of the Princeton `documents.csv`.

To correct a classification, edit `classification` in `data/allony_index.json` (the build scripts read that file), then rebuild.
