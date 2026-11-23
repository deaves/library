#!/usr/bin/env python3
"""Build step for library.eaves.ca.

Everything this script writes is generated from publications.json. Never edit
its output by hand; edit publications.json and run:

    python3 build.py          # validate, then regenerate all outputs
    python3 build.py --check  # validate and fail if any output is stale (CI)

Outputs:
  index.html        the inline `const PUBS = [...]` fallback copy (only that line)
  <slug>/index.html one short-link page per slug and alias
  qr/<slug>.svg     QR code for https://library.eaves.ca/<slug>
  qr/<slug>.png     the same, high resolution for print

Slug rules (enforced here, so a mistake fails the build instead of going live):
  - lowercase letters, digits and single hyphens only; no dates (unless the
    entry sets "slug_allow_year": true, a deliberate one-off)
  - unique across all entries, slugs and aliases together
  - must not clash with a real file or folder in the repo (pdfs, logos, ...)
  - permanent: a slug page that was published can never vanish. If an entry
    loses its slug, the build stops and says which one.

Requires: segno (pip install segno) for the QR codes.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://library.eaves.ca"
DATA = ROOT / "publications.json"
INDEX = ROOT / "index.html"
QR_DIR = ROOT / "qr"
LOGO_DIR = ROOT / "logos"
MARKER = '<meta name="generator" content="library.eaves.ca build.py">'
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"(19|20)\d\d")
REQUIRED = ["title", "venue", "date", "type", "url", "coauthors", "summary", "topics", "paywalled"]

# Kept in step with VENUE_LOGOS in index.html. Read from there so there is one list.
def venue_logos():
    h = INDEX.read_text(encoding="utf-8")
    m = re.search(r"const VENUE_LOGOS = \{(.*?)\};", h, re.S)
    out = {}
    if m:
        for k, v in re.findall(r'"([^"]+)":\s*"([^"]+)"', m.group(1)):
            out[k] = v
    return out


class BuildError(Exception):
    pass


def esc(s):
    return html.escape(str(s), quote=True)


def load():
    raw = json.loads(DATA.read_text(encoding="utf-8"))
    pubs = raw["publications"] if isinstance(raw, dict) else raw
    return pubs


def validate(pubs):
    errors = []
    seen = {}
    reserved = {p.name for p in ROOT.iterdir()}  # real files/folders at the root
    for i, p in enumerate(pubs):
        label = f'entry {i} ("{p.get("title", "?")[:50]}")'
        for f in REQUIRED:
            if f not in p:
                errors.append(f"{label}: missing required field '{f}'")
        names = []
        if "slug" in p:
            names.append(p["slug"])
        names += p.get("aliases", [])
        if p.get("aliases") and "slug" not in p:
            errors.append(f"{label}: has aliases but no slug")
        if p.get("slug_mode", "landing") not in ("landing", "bounce"):
            errors.append(f"{label}: slug_mode must be 'landing' or 'bounce'")
        for s in names:
            if not isinstance(s, str) or not SLUG_RE.match(s):
                errors.append(f"{label}: slug '{s}' must be lowercase letters, digits and single hyphens")
                continue
            if DATE_RE.search(s) and not p.get("slug_allow_year"):
                errors.append(f"{label}: slug '{s}' looks like it contains a year; slugs carry no dates")
            if s in seen:
                errors.append(f"slug '{s}' is used twice ({seen[s]} and {label})")
            seen[s] = label
            d = ROOT / s
            if s in reserved and not (d.is_dir() and is_generated(d / "index.html")):
                errors.append(f"{label}: slug '{s}' clashes with an existing file or folder in the repo")
    # Permanence: every slug page ever generated must still have a source.
    for d in ROOT.iterdir():
        if d.is_dir() and is_generated(d / "index.html") and d.name not in seen:
            errors.append(
                f"slug '{d.name}' was published but no entry claims it any more. "
                "Slugs are permanent: restore it (as a slug or an alias) on the right entry."
            )
    if errors:
        raise BuildError("\n".join(errors))
    return seen


def is_generated(f):
    return f.is_file() and MARKER in f.read_text(encoding="utf-8", errors="ignore")


def fmt_date(d):
    y, m, _ = d.split("-")
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    return f"{months[int(m) - 1]} {y}"


def authors_line(p):
    co = p.get("coauthors") or []
    if not co:
        return ""
    eds = [c for c in co if "(author)" in c]
    if eds:
        names = ", ".join(esc(c.replace(" (author)", "")) for c in eds)
        return f"by {names} &middot; edited by David Eaves"
    return "with " + ", ".join(esc(c) for c in co)


def logo_html(p, logos):
    base = logos.get(p["venue"])
    if not base:
        return ""
    for ext in ("svg", "png"):
        if (LOGO_DIR / f"{base}.{ext}").exists():
            return f'<img class="logo" src="/logos/{base}.{ext}" alt="{esc(p["venue"])}">'
    return ""


def publisher_url(p):
    """Where the piece lives at its publisher, if not on this site."""
    if not p["url"].startswith(SITE):
        return p["url"]
    return p.get("original_url")


def pdf_url(p):
    if not p.get("pdf"):
        return None
    return p["pdf"] if p["pdf"].startswith("http") else f"/{p['pdf'].lstrip('/')}"


HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{marker}
<!-- Generated by build.py from publications.json. Do not edit by hand. -->
<title>{title}</title>
{extra}
<link rel="icon" type="image/png" sizes="32x32" href="https://secure.gravatar.com/blavatar/45a7cd750786f8b9ec93f02d98fc895d45be4e28672fccf404eab3a949b65e0b?s=32">
<link rel="apple-touch-icon" sizes="180x180" href="https://secure.gravatar.com/blavatar/45a7cd750786f8b9ec93f02d98fc895d45be4e28672fccf404eab3a949b65e0b?s=180">
"""

STYLE = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400..700;1,6..72,400..600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root { --paper:#faf8f3; --card:#fffefb; --ink:#221f1a; --ink-soft:#5a554c; --ink-faint:#8f897c;
          --accent:#1d5c47; --accent-deep:#14422f; --accent-soft:#e9f0ec; --rule:#e6e1d5;
          --serif:'Newsreader',Georgia,serif; --sans:'Inter','Helvetica Neue',Arial,sans-serif; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:var(--serif); background:var(--paper); color:var(--ink); line-height:1.6; }
  a { color:inherit; }
  .wrap { max-width:720px; margin:0 auto; padding:0 24px; }
  nav.top { font-family:var(--sans); font-size:.8rem; border-bottom:1px solid var(--rule); padding:14px 0; }
  nav.top .wrap { display:flex; align-items:baseline; gap:24px; }
  nav.top .wordmark { font-family:var(--serif); font-size:1.05rem; font-weight:600; text-decoration:none; }
  nav.top .links { margin-left:auto; display:flex; gap:20px; }
  nav.top .links a { text-decoration:none; color:var(--ink-soft); }
  nav.top .links a:hover { color:var(--accent); }
  main { padding:56px 0 40px; }
  .venue-line { font-family:var(--sans); font-size:.78rem; letter-spacing:.06em; text-transform:uppercase;
                color:var(--ink-faint); display:flex; align-items:center; gap:10px; }
  .venue-line b { color:var(--ink-soft); font-weight:600; }
  .logo { height:28px; width:auto; max-width:120px; object-fit:contain; }
  h1 { font-size:clamp(1.8rem,4.5vw,2.5rem); font-weight:500; letter-spacing:-.015em; line-height:1.15; margin-top:14px; }
  .authors { font-style:italic; color:var(--ink-soft); margin-top:10px; }
  .sum { margin-top:22px; font-size:1.1rem; }
  .lock { font-family:var(--sans); font-size:.78rem; color:var(--ink-faint); margin-top:10px; }
  .actions { display:flex; flex-wrap:wrap; gap:12px; margin-top:28px; font-family:var(--sans); }
  .btn { display:inline-block; padding:10px 18px; border-radius:4px; font-size:.88rem; font-weight:600;
         text-decoration:none; border:1px solid var(--accent); }
  .btn.primary { background:var(--accent); color:#fff; }
  .btn.primary:hover { background:var(--accent-deep); }
  .btn.ghost { color:var(--accent); background:var(--card); }
  .btn.ghost:hover { background:var(--accent-soft); }
  .share { margin-top:48px; padding-top:24px; border-top:1px solid var(--rule); display:flex; gap:20px;
           align-items:center; font-family:var(--sans); font-size:.8rem; color:var(--ink-faint); }
  .share img { width:96px; height:96px; background:#fff; }
  .share code { font-family:var(--sans); color:var(--ink); font-weight:600; font-size:.9rem; }
  .share a { color:var(--ink-soft); }
  footer { font-family:var(--sans); font-size:.8rem; color:var(--ink-faint); padding:32px 0 48px; }
</style>
"""

NAV = """<nav class="top"><div class="wrap">
  <a class="wordmark" href="https://eaves.ca">eaves.ca</a>
  <span class="links"><a href="https://eaves.ca">Blog</a><a href="https://eaves.ca/about-david/">About</a><a href="/">Writing &amp; Publications</a></span>
</div></nav>
"""


def landing_page(p, slug, logos):
    url = f"{SITE}/{slug}"
    desc = p["summary"]
    extra = "\n".join([
        f'<meta name="description" content="{esc(desc)}">',
        f'<link rel="canonical" href="{url}">',
        f'<meta property="og:title" content="{esc(p["title"])}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:url" content="{url}">',
        '<meta property="og:type" content="article">',
    ])
    pdf = pdf_url(p)
    pub = publisher_url(p)
    buttons = []
    if pdf:
        buttons.append(f'<a class="btn primary" href="{esc(pdf)}">Download PDF</a>')
    if pub:
        cls = "ghost" if pdf else "primary"
        buttons.append(f'<a class="btn {cls}" href="{esc(pub)}" rel="noopener">Read at {esc(p["venue"])}</a>')
    buttons.append('<a class="btn ghost" href="/">All my writing</a>')
    authors = authors_line(p)
    return (
        HEAD.format(marker=MARKER, title=f'{esc(p["title"])} — David Eaves', extra=extra)
        + STYLE + "</head>\n<body>\n" + NAV
        + '<div class="wrap"><main>\n'
        + f'<div class="venue-line">{logo_html(p, logos)}<span><b>{esc(p["venue"])}</b> &middot; {fmt_date(p["date"])}</span></div>\n'
        + f'<h1>{esc(p["title"])}</h1>\n'
        + (f'<p class="authors">{authors}</p>\n' if authors else "")
        + f'<p class="sum">{esc(p["summary"])}</p>\n'
        + ('<p class="lock">The publisher\'s version is behind a paywall.</p>\n' if p.get("paywalled") else "")
        + f'<div class="actions">{"".join(buttons)}</div>\n'
        + f'<div class="share"><img src="/qr/{slug}.svg" alt="QR code for library.eaves.ca/{slug}">'
        + f'<div>Short link<br><code>library.eaves.ca/{slug}</code><br>'
        + f'QR code: <a href="/qr/{slug}.svg">SVG</a> &middot; <a href="/qr/{slug}.png">PNG</a></div></div>\n'
        + '</main>\n<footer>&copy; David Eaves &middot; <a href="https://eaves.ca">eaves.ca</a></footer>\n</div>\n</body>\n</html>\n'
    )


def bounce_page(target, title, canonical, note):
    extra = "\n".join([
        '<meta name="robots" content="noindex">',
        f'<link rel="canonical" href="{esc(canonical)}">',
        f'<meta http-equiv="refresh" content="0; url={esc(target)}">',
    ])
    return (
        HEAD.format(marker=MARKER, title=esc(title), extra=extra) + "</head>\n<body>\n"
        + f'<p>{note} <a href="{esc(target)}">{esc(title)}</a>.</p>\n'
        + "</body>\n</html>\n"
    )


def qr_files(slug):
    import segno  # imported here so validation still runs without it
    q = segno.make(f"{SITE}/{slug}", error="q", micro=False)
    import io
    svg = io.BytesIO()
    q.save(svg, kind="svg", scale=10, border=4, xmldecl=False, svgclass=None, lineclass=None)
    png = io.BytesIO()
    q.save(png, kind="png", scale=40, border=4)  # ~1,800 px square: fine for print
    return svg.getvalue(), png.getvalue()


def outputs(pubs):
    """Return {path: bytes} for everything the build owns."""
    logos = venue_logos()
    out = {}
    # 1. The inline fallback copy in index.html (only the PUBS line changes).
    h = INDEX.read_text(encoding="utf-8")
    inline = "const PUBS = " + json.dumps(pubs, ensure_ascii=False, separators=(",", ":")) + ";\n"
    new_h, n = re.subn(r"const PUBS = \[.*?\];\n", lambda m: inline, h, count=1, flags=re.S)
    if n != 1:
        raise BuildError("index.html: could not find the `const PUBS = [...]` line")
    out[INDEX] = new_h.encode("utf-8")
    # 2. Slug pages and QR codes.
    for p in pubs:
        if "slug" not in p:
            continue
        primary = p["slug"]
        if p.get("slug_mode") == "bounce":
            target = pdf_url(p) or p["url"]
            target_abs = target if target.startswith("http") else SITE + target
            page = bounce_page(target, p["title"], target_abs, "Taking you to")
        else:
            page = landing_page(p, primary, logos)
        out[ROOT / primary / "index.html"] = page.encode("utf-8")
        for alias in p.get("aliases", []):
            out[ROOT / alias / "index.html"] = bounce_page(
                f"/{primary}/", p["title"], f"{SITE}/{primary}", "This link has moved to"
            ).encode("utf-8")
        for s in [primary] + p.get("aliases", []):
            svg, png = qr_files(s)
            out[QR_DIR / f"{s}.svg"] = svg
            out[QR_DIR / f"{s}.png"] = png
    return out


def png_pixels(data):
    """Header and decompressed image data of a PNG, so two files that differ only
    in how zlib compressed them (it varies by machine) count as the same."""
    import struct
    import zlib
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return data
    i, head, idat = 8, [], b""
    while i < len(data):
        n, kind = struct.unpack(">I4s", data[i:i + 8])
        body = data[i + 8:i + 8 + n]
        if kind == b"IDAT":
            idat += body
        elif kind in (b"IHDR", b"PLTE", b"tRNS"):
            head.append(kind + body)
        i += 12 + n
    return b"".join(head) + zlib.decompress(idat)


def unchanged(f, new):
    if not f.exists():
        return False
    old = f.read_bytes()
    if old == new:
        return True
    return f.suffix == ".png" and png_pixels(old) == png_pixels(new)


def main():
    check = "--check" in sys.argv
    try:
        pubs = load()
        validate(pubs)
        files = outputs(pubs)
    except BuildError as e:
        print("BUILD FAILED\n" + str(e), file=sys.stderr)
        return 1
    stale = [f for f, b in files.items() if not unchanged(f, b)]
    if check:
        if stale:
            print("Out of date (run python3 build.py):\n" + "\n".join(str(f.relative_to(ROOT)) for f in stale))
            return 1
        print(f"OK: {len(files)} outputs up to date")
        return 0
    for f in stale:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(files[f])
        print("wrote", f.relative_to(ROOT))
    print(f"Done: {len(stale)} of {len(files)} outputs changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
