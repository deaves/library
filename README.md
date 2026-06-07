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

## Files

- `publications.json` — the library data. **This is the only file you edit.**
- `index.html` — the page (design, search, filters). Don't touch unless changing the design.
- `CNAME` — tells GitHub Pages this serves library.eaves.ca. Don't delete.
