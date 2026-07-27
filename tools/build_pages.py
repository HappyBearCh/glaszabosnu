# -*- coding: utf-8 -*-
"""
Generate the modern static pages for glaszabosnu.ch.

Fetches each article from the live Joomla site, keeps the content verbatim,
strips the legacy inline typography (hardcoded colours / fonts / sizes that
fight the new stylesheet), rewrites internal links to the local pages, mirrors
same-origin images into assets/img/, and wraps everything in the shared shell.

Run from the repo root:  python tools/build_pages.py
"""

import os
import re
import posixpath
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup, NavigableString

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "assets", "img")
SITE = "https://www.glaszabosnu.ch/"
BASE = SITE + "index.php/en/"

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (compatible; glaszabosnu-static-build)"

# --------------------------------------------------------------------------- #
# Page map: local file -> source path, title, menu key, hero subtitle
# --------------------------------------------------------------------------- #

PAGES = [
    dict(file="dosadasnje-aktivnosti.html", src="theme-features/setup-sidebar-color",
         title="Dosadašnje aktivnosti", menu="o-nama", parent="O nama",
         desc="Dosadašnje aktivnosti organizacije Glas za Bosnu — manifestacije, tribine i obilježavanja."),
    dict(file="gzb-u-akciji.html", src="theme-features/gzb-u-akciji",
         title="GZB u akciji", menu="o-nama", parent="O nama", gallery=True,
         desc="Foto galerija — Glas za Bosnu u akciji."),

    dict(file="informacije-o-bih.html", src="layouts1/informacije-o-bih",
         title="Informacije o BiH", menu="bih", parent="Bosna i Hercegovina",
         desc="Osnovne informacije o Bosni i Hercegovini: geografija, administrativna podjela, stanovništvo i simboli."),
    dict(file="istorija-bih.html", src="layouts1/sidebar-scroll",
         title="Istorija Bosne i Hercegovine", menu="bih", parent="Bosna i Hercegovina",
         desc="Istorija Bosne i Hercegovine ukratko — od ilirskog doba do današnjih dana."),
    dict(file="politicko-uredenje.html", src="layouts1/politicko-uredenje",
         title="Političko uređenje", menu="bih", parent="Bosna i Hercegovina",
         desc="Političko uređenje i ustavna struktura Bosne i Hercegovine."),
    dict(file="ustav.html", src="layouts1/ustav",
         title="Ustav", menu="bih", parent="Bosna i Hercegovina",
         desc="Ustav Bosne i Hercegovine — puni tekst."),
    dict(file="bosanski-jezik.html", src="layouts1/sidebar-left",
         title="Bosanski jezik", menu="bih", parent="Bosna i Hercegovina",
         desc="O bosanskom jeziku — historija, karakteristike i rječnik."),
    dict(file="rekli-o-bih.html", src="layouts1/sticky-menu-off",
         title="Rekli/napisali su o Bosni i Hercegovini", menu="bih", parent="Bosna i Hercegovina",
         desc="Citati i zapisi istaknutih ličnosti o Bosni i Hercegovini."),

    dict(file="izborni-rezultati.html", src="theme-styles/2013-06-22-21-23-41",
         title="Izborni rezultati", menu="izbori", parent="Izbori u BiH",
         desc="Rezultati općih izbora u Bosni i Hercegovini."),
    dict(file="obrazac-prijave.html", src="theme-styles/prp-obrasci",
         title="Obrazac prijave za upis birača izvan BiH", menu="izbori", parent="Izbori u BiH",
         desc="Obrazac prijave za upis birača u Centralni birački spisak za glasanje izvan BiH."),

    dict(file="popis-1991.html", src="popis-stanovnistva/1991-godina",
         title="Popis stanovništva 1991. godine", menu="popis", parent="Popis stanovništva",
         desc="Rezultati popisa stanovništva Bosne i Hercegovine iz 1991. godine."),
    dict(file="popis-2013.html", src="popis-stanovnistva/2013-godina",
         title="Popis stanovništva 2013. godine", menu="popis", parent="Popis stanovništva",
         desc="Rezultati popisa stanovništva Bosne i Hercegovine iz 2013. godine."),

    dict(file="impressum.html", src="pages",
         title="Impressum", menu=None, parent=None,
         desc="Impressum — Glas za Bosnu, Zürich."),
    dict(file="datenschutz.html", src="sample-levels/2-uncategorised/70-datenschutz",
         title="Datenschutz", menu=None, parent=None,
         desc="Datenschutzerklärung — Glas za Bosnu."),
]

# Live Joomla URL -> local file. Used to rewrite internal links everywhere.
URL_MAP = {
    BASE: "index.html",
    SITE: "index.html",
    BASE + "theme-features": "o-nama.html",
    BASE + "aktuell": "aktivizam.html",
    # /home is a duplicate of the O nama article (see README note)
    BASE + "home": "o-nama.html",
}
for p in PAGES:
    URL_MAP[BASE + p["src"]] = p["file"]

# --------------------------------------------------------------------------- #
# Shared shell
# --------------------------------------------------------------------------- #

NAV_ITEMS = [
    ("start", "Start", "index.html", []),
    ("o-nama", "O nama", "o-nama.html", [
        ("Memorandum", "assets/pdf/GZB_MEMORANDUM.pdf", True),
        ("Dosadašnje aktivnosti", "dosadasnje-aktivnosti.html", False),
        ("GZB u akciji", "gzb-u-akciji.html", False),
    ]),
    ("bih", "Bosna i Hercegovina", "#", [
        ("Informacije o BiH", "informacije-o-bih.html", False),
        ("Istorija Bosne i Hercegovine", "istorija-bih.html", False),
        ("Političko uređenje", "politicko-uredenje.html", False),
        ("Ustav", "ustav.html", False),
        ("Statistički podaci", "o-nama.html", False),
        ("Bosanski jezik", "bosanski-jezik.html", False),
        ("Rekli/napisali su o Bosni i Hercegovini", "rekli-o-bih.html", False),
        ("Fotografijom kroz BiH", "gzb-u-akciji.html", False),
    ]),
    ("izbori", "Izbori u BiH", "#", [
        ("Izborni rezultati", "izborni-rezultati.html", False),
        ("Informacije o procesu registracije i glasanja 2026", "https://eizbori.izbori.ba/", True),
        ("Obrazac prijave za upis birača izvan BiH", "obrazac-prijave.html", False),
    ]),
    ("popis", "Popis stanovništva", "#", [
        ("1991. godina", "popis-1991.html", False),
        ("2013. godina", "popis-2013.html", False),
    ]),
    ("linkovi", "Linkovi", "index.html#linkovi", []),
    ("aktivizam", "Aktivizam", "aktivizam.html", [
        ("Prijava", "https://www.glaszabosnu.ch/index.php/en/aktuell/prijava", False),
    ]),
]

CARET = ('<svg class="caret" viewBox="0 0 12 12" fill="none" stroke="currentColor" '
         'stroke-width="2" aria-hidden="true"><path d="m2 4 4 4 4-4"/></svg>')
ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
         'aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/>'
         '<path d="m2 7 10 6 10-6"/></svg>')


def build_nav(current):
    out = []
    for key, label, href, subs in NAV_ITEMS:
        classes = []
        if subs:
            classes.append("has-sub")
        if key == current:
            classes.append("current")
        cls = f' class="{" ".join(classes)}"' if classes else ""
        out.append(f"      <li{cls}>")
        if subs:
            out.append(f'        <a href="{href}" aria-expanded="false">{label}\n          {CARET}\n        </a>')
            out.append('        <ul class="submenu">')
            for text, link, blank in subs:
                tgt = ' target="_blank" rel="noopener"' if blank else ""
                out.append(f'          <li><a href="{link}"{tgt}>{text}</a></li>')
            out.append("        </ul>")
        else:
            out.append(f'        <a href="{href}">{label}</a>')
        out.append("      </li>")
    return "\n".join(out)


TEMPLATE = """<!DOCTYPE html>
<html lang="bs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Glas za Bosnu</title>
<meta name="description" content="{desc}">
<link rel="icon" href="assets/img/logo.png" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>

<a class="skip-link" href="#main">Preskoči na sadržaj</a>

<div class="utility">
  <div class="container">
    <a class="util-mail" href="mailto:info@glaszabosnu.ch">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 6 10-6"/></svg>
      info@glaszabosnu.ch
    </a>
    <a href="impressum.html">Impressum</a>
    <span class="sep">|</span>
    <a href="datenschutz.html">Datenschutz</a>
  </div>
</div>

<header class="masthead">
  <div class="container">
    <a class="brand" href="index.html">
      <img src="assets/img/logo.png" alt="Glas za Bosnu" width="300" height="125">
    </a>
    <p class="tagline">Čuvajmo domovinu<br>Bosnu i Hercegovinu!</p>
  </div>
</header>

<nav class="nav" aria-label="Glavna navigacija">
  <div class="container">
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="mainmenu">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
      Meni
    </button>

    <ul class="menu" id="mainmenu">
{nav}
    </ul>
  </div>
</nav>

<main id="main">

  <section class="hero hero-sm">
    <div class="container">
      <div class="hero-inner">
        <ul class="breadcrumb">
          <li><a href="index.html">Start</a></li>
{crumb}          <li>{title}</li>
        </ul>
        <h1>{h1}</h1>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <article class="{wrap}">
{content}
      </article>
    </div>
  </section>

</main>

<footer class="footer">
  <div class="container">
    <div class="footer-grid">

      <div class="footer-brand">
        <img src="assets/img/logo.png" alt="Glas za Bosnu" width="220" height="92">
        <p>Nezavisna, vanstranačka i nevladina organizacija sa sjedištem u Cirihu.
           Osnovana u decembru 2015. godine u Švicarskoj.</p>
        <div class="social">
          <a href="https://de-de.facebook.com/public/Glas-Za-Bosnu" target="_blank" rel="noopener" aria-label="Facebook">
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M14 9h3V6h-3c-2.2 0-4 1.8-4 4v2H8v3h2v7h3v-7h3l1-3h-4v-2c0-.55.45-1 1-1z"/></svg>
          </a>
          <a href="mailto:info@glaszabosnu.ch" aria-label="E-mail">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 6 10-6"/></svg>
          </a>
          <a href="https://www.youtube.com/watch?v=MgRGXDqKTyQ" target="_blank" rel="noopener" aria-label="YouTube">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="2" y="5" width="20" height="14" rx="4"/><path d="m10 9 5 3-5 3z" fill="currentColor" stroke="none"/></svg>
          </a>
        </div>
      </div>

      <div>
        <h3>Sadržaji</h3>
        <ul>
          <li><a href="index.html">Start</a></li>
          <li><a href="o-nama.html">O nama</a></li>
          <li><a href="dosadasnje-aktivnosti.html">Dosadašnje aktivnosti</a></li>
          <li><a href="gzb-u-akciji.html">GZB u akciji</a></li>
          <li><a href="informacije-o-bih.html">Informacije o BiH</a></li>
          <li><a href="istorija-bih.html">Istorija BiH</a></li>
          <li><a href="index.html#linkovi">Linkovi</a></li>
          <li><a href="aktivizam.html">Aktivizam</a></li>
        </ul>
      </div>

      <div>
        <h3>Izbori i podaci</h3>
        <ul>
          <li><a href="https://eregistracija.izbori.ba/" target="_blank" rel="noopener">eRegistracija birača</a></li>
          <li><a href="https://eizbori.izbori.ba/" target="_blank" rel="noopener">Registracija i glasanje 2026</a></li>
          <li><a href="izborni-rezultati.html">Izborni rezultati</a></li>
          <li><a href="obrazac-prijave.html">Obrazac prijave za upis birača</a></li>
          <li><a href="popis-1991.html">Popis stanovništva 1991.</a></li>
          <li><a href="popis-2013.html">Popis stanovništva 2013.</a></li>
        </ul>
        <p style="margin-top:18px">
          <a class="footer-mail" href="mailto:info@glaszabosnu.ch">
            {arrow}
            info@glaszabosnu.ch
          </a>
        </p>
      </div>

    </div>

    <div class="footer-bottom">
      <span>© <span id="year">2026</span> Glas za Bosnu — Zürich, Švicarska</span>
      <nav aria-label="Pravne informacije">
        <a href="impressum.html">Impressum</a>
        <a href="datenschutz.html">Datenschutz</a>
      </nav>
    </div>
  </div>
</footer>

<button class="totop" type="button" aria-label="Nazad na vrh">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
</button>

<script src="assets/js/site.js"></script>
<script>document.getElementById('year').textContent = new Date().getFullYear();</script>
</body>
</html>
"""

# --------------------------------------------------------------------------- #
# Content cleaning
# --------------------------------------------------------------------------- #

# Legacy declarations that clash with the new stylesheet.
DROP_DECLS = ("color", "font-family", "font-size", "background", "background-color",
              "line-height", "font-weight")


def clean_style(value):
    kept = []
    for decl in value.split(";"):
        if ":" not in decl:
            continue
        prop = decl.split(":", 1)[0].strip().lower()
        if prop in DROP_DECLS:
            continue
        kept.append(decl.strip())
    return "; ".join(kept)


def slugify_image(url):
    name = posixpath.basename(urlparse(url).path)
    name = unquote(name)
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return name or "image"


def mirror_image(url, cache):
    """Download a same-origin image into assets/img/ and return the local path."""
    if url in cache:
        return cache[url]
    local_name = slugify_image(url)
    dest = os.path.join(IMG_DIR, local_name)
    if not os.path.exists(dest):
        try:
            r = session.get(url, timeout=60)
            r.raise_for_status()
            with open(dest, "wb") as fh:
                fh.write(r.content)
            print(f"      + image {local_name} ({len(r.content)} bytes)")
        except Exception as exc:
            print(f"      ! image failed {url}: {exc}")
            cache[url] = url
            return url
    cache[url] = "assets/img/" + local_name
    return cache[url]


def map_link(href):
    """Rewrite an internal Joomla URL to its local page, if we have one."""
    if not href:
        return href
    absolute = urljoin(BASE, href)
    trimmed = absolute.split("#")[0].split("?")[0].rstrip("/")
    for src, dest in URL_MAP.items():
        if trimmed == src.rstrip("/"):
            frag = absolute.split("#", 1)[1] if "#" in absolute else ""
            return dest + ("#" + frag if frag else "")
    return absolute if href.startswith("/") else href


def clean_content(main, page, img_cache):
    soup = main

    # Joomla wraps the body in <article>; unwrap it and lift the title out.
    h1_text = page["title"]
    for h1 in soup.select("h1"):
        text = h1.get_text(" ", strip=True)
        if text:
            h1_text = text
        h1.decompose()
        break
    for art in soup.select("article"):
        art.unwrap()

    # Drop Joomla chrome we do not want in the new shell.
    for sel in ("#system-message-container", ".uk-article-meta", "script", "style",
                ".pagenavigation", ".content_rating", ".icons"):
        for el in soup.select(sel):
            el.decompose()

    # Joomla cloaks e-mail addresses and un-cloaks them with its own JS, which
    # we no longer ship. Replace the placeholder with a real mailto link.
    for span in soup.select('span[id^="cloak"]'):
        link = BeautifulSoup(
            '<a href="mailto:info@glaszabosnu.ch">info@glaszabosnu.ch</a>',
            "html.parser")
        span.replace_with(link)

    # Legacy inline typography.
    for el in soup.select("[style]"):
        cleaned = clean_style(el["style"])
        if cleaned:
            el["style"] = cleaned
        else:
            del el["style"]

    # <font> and colour-only spans add nothing now.
    for el in soup.select("font"):
        el.unwrap()
    for span in soup.select("span"):
        if not span.attrs:
            span.unwrap()

    # Images: mirror same-origin, make responsive, drop float on narrow screens.
    for img in soup.select("img"):
        src = img.get("data-src") or img.get("src") or ""
        if "blank.gif" in src and img.get("data-src"):
            src = img["data-src"]
        absolute = urljoin(BASE, src)
        if urlparse(absolute).netloc.endswith("glaszabosnu.ch"):
            img["src"] = mirror_image(absolute, img_cache)
        else:
            img["src"] = absolute          # keep third-party hotlinks as-is
        for attr in ("width", "height", "data-src", "srcset", "sizes"):
            if attr in img.attrs:
                del img[attr]
        img["loading"] = "lazy"
        if not img.get("alt"):
            img["alt"] = ""

    # Links: internal -> local file, external -> new tab.
    for a in soup.select("a[href]"):
        href = a["href"]
        if href.startswith(("mailto:", "tel:", "#")):
            continue
        new = map_link(href)
        a["href"] = new
        if "onclick" in a.attrs:
            del a["onclick"]
        parsed = urlparse(new)
        if parsed.scheme in ("http", "https") and not parsed.netloc.endswith("glaszabosnu.ch"):
            a["target"] = "_blank"
            a["rel"] = "noopener"

    # Tables need their own scroll container on narrow screens.
    for table in soup.select("table"):
        if table.find_parent(class_="table-wrap"):
            continue
        wrapper = BeautifulSoup('<div class="table-wrap"></div>', "html.parser").div
        table.wrap(wrapper)

    # Strip the &nbsp;-only paragraphs Joomla's editor leaves behind.
    for p in soup.select("p"):
        if not p.find(["img", "a", "br", "iframe"]) and not p.get_text(strip=True).replace("\xa0", ""):
            p.decompose()

    return h1_text, soup.decode_contents()


# --------------------------------------------------------------------------- #
# EventGallery: the photos are lazy-loaded, so pull them from the thumbnail
# links and mirror a web-sized copy of each into assets/img/gallery/.
# --------------------------------------------------------------------------- #

GRID_WIDTH = 600     # what the grid shows
FULL_WIDTH = 1600    # what the lightbox shows


def gallery_image(folder, filename, width, subdir):
    """Mirror one EventGallery photo at the requested width; return local path."""
    dest_dir = os.path.join(IMG_DIR, "gallery", subdir)
    os.makedirs(dest_dir, exist_ok=True)
    local = re.sub(r"[^A-Za-z0-9._-]+", "_", unquote(filename))
    dest = os.path.join(dest_dir, local)
    rel = f"assets/img/gallery/{subdir}/{local}"
    if os.path.exists(dest):
        return rel
    url = (f"{SITE}components/com_eventgallery/helpers/image.php"
           f"?mode=nocrop&width={width}&folder={folder}&file={filename}")
    try:
        r = session.get(url, timeout=120)
        r.raise_for_status()
        with open(dest, "wb") as fh:
            fh.write(r.content)
        print(f"      + {subdir}/{local} ({len(r.content) // 1024} KB)")
    except Exception as exc:
        print(f"      ! {filename} failed: {exc}")
        return url
    return rel


def build_gallery(main):
    """Turn the EventGallery markup into a plain grid of mirrored photos."""
    shots = []
    for a in main.select("a.event-thumbnail[href]"):
        q = urlparse(a["href"]).query
        folder = re.search(r"folder=([^&]+)", q)
        filename = re.search(r"file=([^&]+)", q)
        if not (folder and filename):
            continue
        img = a.select_one("img")
        alt = (img.get("alt") if img else "") or "Glas za Bosnu"
        shots.append((folder.group(1), filename.group(1), alt))

    print(f"      {len(shots)} photos in gallery")
    items = []
    for folder, filename, alt in shots:
        grid = gallery_image(folder, filename, GRID_WIDTH, "thumb")
        full = gallery_image(folder, filename, FULL_WIDTH, "full")
        items.append(
            '        <figure>\n'
            f'          <button type="button" data-full="{full}">\n'
            f'            <img src="{grid}" alt="{alt}" loading="lazy">\n'
            '          </button>\n'
            '        </figure>'
        )

    return (
        '<div class="gallery">\n' + "\n".join(items) + "\n</div>\n\n"
        '<div class="lightbox" role="dialog" aria-modal="true" aria-label="Foto galerija">\n'
        '  <button class="lightbox-close" type="button" aria-label="Zatvori">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">'
        '<path d="M18 6 6 18M6 6l12 12"/></svg></button>\n'
        '  <button class="lightbox-prev" type="button" aria-label="Prethodna">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">'
        '<path d="m15 18-6-6 6-6"/></svg></button>\n'
        '  <img src="" alt="">\n'
        '  <button class="lightbox-next" type="button" aria-label="Sljedeća">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">'
        '<path d="m9 18 6-6-6-6"/></svg></button>\n'
        '  <span class="lightbox-count"></span>\n'
        '</div>'
    )


def fetch(page, img_cache):
    url = BASE + page["src"]
    print(f"  -> {page['file']}  ({url})")
    r = session.get(url, timeout=60)
    r.raise_for_status()
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")
    main = soup.select_one("main.tm-content") or soup.select_one(".tm-content")
    if main is None:
        raise RuntimeError("content container not found")
    if page.get("gallery"):
        return page["title"], build_gallery(main)
    return clean_content(main, page, img_cache)


# --------------------------------------------------------------------------- #
# Relink the hand-written pages (index / o-nama / aktivizam) so every menu and
# footer entry points at the local file instead of the live Joomla URL.
# --------------------------------------------------------------------------- #

HANDWRITTEN = ["index.html", "o-nama.html", "aktivizam.html"]

RELINK = {
    BASE + "theme-features/setup-sidebar-color": "dosadasnje-aktivnosti.html",
    BASE + "theme-features/gzb-u-akciji": "gzb-u-akciji.html",
    BASE + "layouts1/informacije-o-bih": "informacije-o-bih.html",
    BASE + "layouts1/sidebar-scroll": "istorija-bih.html",
    BASE + "layouts1/politicko-uredenje": "politicko-uredenje.html",
    BASE + "layouts1/ustav": "ustav.html",
    BASE + "layouts1/sidebar-left": "bosanski-jezik.html",
    BASE + "layouts1/sticky-menu-off": "rekli-o-bih.html",
    BASE + "theme-styles/2013-06-22-21-23-41": "izborni-rezultati.html",
    BASE + "theme-styles/prp-obrasci": "obrazac-prijave.html",
    BASE + "popis-stanovnistva/1991-godina": "popis-1991.html",
    BASE + "popis-stanovnistva/2013-godina": "popis-2013.html",
    BASE + "sample-levels/2-uncategorised/70-datenschutz": "datenschutz.html",
    BASE + "pages": "impressum.html",
    BASE + "home": "o-nama.html",
}


def relink():
    # Longest first so /pages does not clobber a longer path that contains it.
    ordered = sorted(RELINK.items(), key=lambda kv: -len(kv[0]))
    for name in HANDWRITTEN:
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            print(f"  ! {name} missing, skipped")
            continue
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        before = html
        for url, local in ordered:
            html = html.replace(f'"{url}"', f'"{local}"')
        if html != before:
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(html)
            print(f"  relinked {name}")
        else:
            print(f"  {name} already current")


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    img_cache = {}
    for page in PAGES:
        h1, content = fetch(page, img_cache)
        crumb = ""
        if page.get("parent"):
            crumb = f"          <li>{page['parent']}</li>\n"
        html = TEMPLATE.format(
            title=page["title"],
            desc=page["desc"],
            h1=h1,
            nav=build_nav(page.get("menu")),
            crumb=crumb,
            content=content,
            arrow=ARROW,
            wrap="reveal" if page.get("gallery") else "prose legacy reveal",
        )
        with open(os.path.join(ROOT, page["file"]), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(html)
        print(f"     wrote {page['file']}  ({len(html)} bytes)")
    print("\nRelinking hand-written pages:")
    relink()
    print(f"\nDone: {len(PAGES)} pages, {len(img_cache)} images mirrored.")


if __name__ == "__main__":
    main()
