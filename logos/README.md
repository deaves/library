# Publication logos

Drop logo files in this folder to make them appear next to publications on
library.eaves.ca — both on the New & Notable cards and in the library list.

## How it works
- The page looks up each venue in the `VENUE_LOGOS` map in `index.html`.
- It tries `<basename>.svg` first, then `<basename>.png`. Either format works —
  just match the basename below.
- If no file is found, the page falls back to the typographic venue mark.
  So missing logos never break anything.

## File specs
- SVG preferred (crispest at small sizes); transparent PNG also fine.
- Transparent background. Trim whitespace around the mark.
- Roughly landscape or square; the page sizes them automatically
  (~15px tall in the list, centered on the cards).

## Filenames to add (most-used venues first)
| Basename | Venue(s) it covers | # pieces |
|---|---|---|
| ucl-iipp | UCL IIPP (+ Working Paper Series, Blog, & Bennett) | 11 |
| harvard-hks | Harvard Kennedy School / Ash Center / digital HKS / KS Review | 11 |
| foreign-policy | Foreign Policy | 3 |
| lawfare | Lawfare | 2 |
| tech-policy-press | Tech Policy Press | 2 |
| project-syndicate | Project Syndicate | 2 |
| new-america | New America | 2 |
| arxiv | arXiv | 2 |
| wef | World Economic Forum | 1 |
| imf | Finance & Development (IMF) | 1 |
| economist | The Economist | 1 |
| slate | Slate | 1 |
| nextgov | Nextgov/FCW | 1 |
| ssrn | SSRN | 1 |
| adbi | Asian Development Bank Institute | 1 |
| lisbon-council | The Lisbon Council | 1 |
| antimonopoly | Canadian Anti-Monopoly Project | 1 |
| eu-council | Eurogroup / Council of the EU | 1 |
| tpsda | Teaching Public Service in the Digital Age | 1 |

Venues not listed keep the typographic mark. Add them to VENUE_LOGOS in
index.html if you want logos there too.
