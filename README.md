# eaves.ca — Writing & Publications Library

Live at **https://library.eaves.ca** (served by GitHub Pages).

## How to add a new publication

1. Open `publications.json` (on github.com, click the file → pencil icon to edit).
2. Copy an existing entry and add yours to the top of the `publications` list:

```json
{
  "title": "Title of the piece",
  "venue": "Foreign Policy",
  "date": "2026-06-01",
  "type": "op-ed",
  "url": "https://...",
  "coauthors": ["Name"],
  "summary": "Two or three sentences. Especially important for paywalled pieces.",
  "topics": ["AI", "DPI"],
  "paywalled": true,
  "featured": true
}
```

3. Commit. The live site updates in about a minute.

Notes:
- `type` must be one of: `op-ed`, `journal article`, `working paper`, `report`, `white paper`, `teaching case`, `chapter`, `book`.
- `featured: true` pins a piece in the "New & Notable" spotlight (keep to ~3; remove the flag from older pieces when adding new ones).
- Dates are `YYYY-MM-DD`; if only the month is known use the 1st.
- Order in the file doesn't matter — the page sorts by date.

## Short links and QR codes

Any entry can have a short link at `library.eaves.ca/<slug>`. Add a `slug` to the entry:

```json
"slug": "econofdpi"
```

On the next push, the build makes `econofdpi/index.html` (a landing page with the title, summary, PDF download and publisher link) and `qr/econofdpi.svg` + `qr/econofdpi.png` (QR codes for print and screen). The page and its QR come from the same step, so they can't drift apart.

Rules (the build enforces them and fails with the reason if one is broken):
- Lowercase letters, digits and hyphens only. GitHub Pages URLs are case-sensitive.
- Short and sayable (`maturitymodel`, `econofdpi`). No dates.
- **Permanent once published.** A slug can gain an `"aliases": ["other-name"]`, but never changes meaning or disappears.
- `"slug_mode": "bounce"` sends the link straight to the PDF (or the publisher) instead of the landing page.

## Files

- `publications.json` — the library data. **This is the only file you edit.**
- `build.py` — generates the slug pages, the QR codes and the fallback copy of the data inside `index.html`. Run `python3 build.py` before pushing, or let GitHub do it: the Action in `.github/workflows/build.yml` runs it on every push and commits anything that changed.
- `<slug>/` and `qr/` — generated. Never edit by hand.
- `index.html` — the page (design, search, filters). Don't touch unless changing the design.
- `pdfs/` — archival copies of pieces whose original links have gone dark.
- `CNAME` — tells GitHub Pages this serves library.eaves.ca. Don't delete.
