#!/usr/bin/env python3
"""Build the offline editions of The Language of College.

Run after build.py:   python3 _src/export.py

Writes two files that the home page links to:
  downloads/language-of-college.pdf    tagged PDF with bookmarks
  downloads/language-of-college.epub   EPUB 3 with accessibility metadata

Both include every built page, in the order of the table of contents in
build.py. Pages marked "Coming soon" are left out.

Needs: playwright (Chromium), beautifulsoup4, pikepdf, lxml.
"""
import datetime
import re
import sys
import tempfile
import uuid
import zipfile
from pathlib import Path

from bs4 import BeautifulSoup
from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

ROOT = build.ROOT
OUT = ROOT / "downloads"
SITE_URL = "https://octc-id.github.io/language-of-college/"
TITLE = "The Language of College: A Reading, Writing & Communication Toolkit"
PUBLISHER = "Owensboro Community & Technical College"
TODAY = datetime.date.today()
MADE = f"{TODAY.strftime('%B')} {TODAY.day}, {TODAY.year}"


def parts():
    """[(part title, is_instructor, [(key, page title), ...])] for built pages only."""
    out = []
    for sec in build.SECTIONS:
        pages = [(k, t) for k, t, p in sec[3] if p]
        if pages:
            out.append((sec[1], False, pages))
    pages = [(k, t) for k, t, p in build.INSTRUCTOR[3] if p]
    if pages:
        out.append((build.INSTRUCTOR[1], True, pages))
    return out


def link(target, epub):
    key, _, frag = target.partition("#")
    if key == "home":
        return "nav.xhtml" if epub else "#contents"
    if epub:
        return f"{key}.xhtml" + (f"#{key}--{frag}" if frag else "")
    return f"#{key}--{frag}" if frag else f"#p-{key}"


def page_body(key, epub):
    """One page body, made safe to combine with others and to read offline."""
    raw = (build.SRC / f"{key}.html").read_text()
    raw = re.sub(r"\{\{url:([^}]+)\}\}", lambda m: link(m.group(1), epub), raw)
    raw = raw.replace("{{root}}", SITE_URL)
    soup = BeautifulSoup(raw, "html.parser")

    # Interactive parts do not work offline. Point to the website instead.
    for form in soup.select("form"):
        note = soup.new_tag("p", attrs={"class": "note note-tip"})
        note.string = ("The fill-in builder works on the website. Open this page online to use it: "
                       + SITE_URL + build.PATHS[key])
        form.replace_with(note)
    for el in soup.select("#pb-out, noscript, .actions"):
        el.decompose()

    # Answers are always shown.
    for d in soup.select("details.answer"):
        d.name = "div"
        d["class"] = ["answer-open"]
        if d.has_attr("open"):
            del d["open"]
        s = d.find("summary")
        if s:
            s.name = "p"
            s["class"] = ["answer-title"]
            s.string = "Suggested answers"

    # Keep ids unique when pages are combined.
    for el in soup.select("[id]"):
        el["id"] = f"{key}--{el['id']}"
    for a in soup.select('a[href^="#"]'):
        if "--" not in a["href"] and not a["href"].startswith("#p-") and a["href"] != "#contents":
            a["href"] = f"#{key}--{a['href'][1:]}"

    for h in soup.find_all("h2"):
        h["class"] = h.get("class", []) + ["sec"]
    if not epub:  # in the PDF, parts are h1 and pages are h2, so shift page headings down
        for old, new in (("h4", "h5"), ("h3", "h4"), ("h2", "h3")):
            for h in soup.find_all(old):
                h.name = new
    return soup.decode(formatter="minimal")


def page_head(key, title, part, instructor, level):
    info = build.PAGES[key]
    cls = "page instructor" if instructor else "page"
    return (f'<article class="{cls}" id="p-{key}">\n'
            f'<p class="kicker">{build.esc(part)}</p>\n'
            f'<h{level} class="page-title">{build.esc(info["h1"])}</h{level}>\n'
            f'<p class="use-when"><strong>Use this page when</strong> {info["when"]}</p>\n'
            f'<p class="online">Online: {SITE_URL}{build.PATHS[key]}</p>\n')


def styles():
    return (ROOT / "css/styles.css").read_text() + "\n" + (ROOT / "_src/export.css").read_text()


# ---------------------------------------------------------------- PDF
def build_pdf():
    import pikepdf
    from playwright.sync_api import sync_playwright

    logo = (ROOT / "images/octc-logo.png").resolve().as_uri()
    toc, body = [], []
    for part, instructor, pages in parts():
        items = "".join(f'<li><a href="#p-{k}">{build.esc(build.PAGES[k]["h1"])}</a></li>' for k, _ in pages)
        toc.append(f"<li>{build.esc(part)}<ul>{items}</ul></li>")
        body.append(f'<section class="part"><h1>{build.esc(part)}</h1>')
        if instructor:
            body.append('<p class="part-note">For faculty and staff. Students are welcome to read it too.</p>')
        for k, t in pages:
            body.append(page_head(k, t, part, instructor, 2) + page_body(k, False) + "</article>")
        body.append("</section>")

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{build.esc(TITLE)}</title>
<meta name="author" content="{build.esc(PUBLISHER)}">
<style>{styles()}</style></head>
<body class="export pdf">
<section class="cover">
  <img src="{logo}" alt="Owensboro Community &amp; Technical College">
  <h1>The Language of College</h1>
  <p class="sub">{build.SUBTITLE}</p>
  <p>Offline edition, made on {MADE}.</p>
  <p>The newest version is on the website: {SITE_URL}</p>
</section>
<nav class="book-toc" id="contents" aria-label="Contents"><h1>Contents</h1><ul>{''.join(toc)}</ul></nav>
{''.join(body)}
<section class="colophon"><h1>About this edition</h1>
<p>{build.esc(TITLE)}. {build.esc(PUBLISHER)}.</p>
<p>{build.EEO}</p></section>
</body></html>"""

    OUT.mkdir(exist_ok=True)
    final = OUT / "language-of-college.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "print.html"
        raw = Path(tmp) / "raw.pdf"
        src.write_text(html)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(src.as_uri())
            page.wait_for_load_state("networkidle")
            page.pdf(
                path=str(raw), format="Letter", print_background=True, tagged=True, outline=True,
                display_header_footer=True, header_template="<span></span>",
                footer_template=('<div style="font-size:9pt;font-family:Arial,sans-serif;color:#52606d;width:100%;'
                                 'padding:0 0.8in;display:flex;justify-content:space-between">'
                                 '<span>The Language of College</span><span>Page <span class="pageNumber"></span></span></div>'),
                margin={"top": "0.75in", "bottom": "0.9in", "left": "0.8in", "right": "0.8in"},
            )
            browser.close()
        # Accessibility settings Chromium does not write: language and "show the title, not the file name".
        with pikepdf.open(raw) as pdf:
            pdf.Root.Lang = pikepdf.String("en-US")
            pdf.Root.ViewerPreferences = pikepdf.Dictionary(DisplayDocTitle=True)
            with pdf.open_metadata() as meta:
                meta["dc:title"] = TITLE
                meta["dc:creator"] = [PUBLISHER]
                meta["dc:language"] = ["en-US"]
            pdf.docinfo["/Title"] = TITLE
            pdf.docinfo["/Author"] = PUBLISHER
            pdf.save(final)
    print("built", final.relative_to(ROOT))


# ---------------------------------------------------------------- EPUB
XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head><meta charset="utf-8"/><title>{title}</title><link rel="stylesheet" type="text/css" href="css/book.css"/></head>
<body class="export epub">
{body}
</body></html>
"""


def xhtml(title, body):
    doc = XHTML.format(title=build.esc(title), body=body)
    etree.fromstring(doc.encode("utf-8"))  # stops the build if a page is not well-formed
    return doc


def clean(fragment):
    """Re-serialize an HTML fragment as XHTML (closed tags, numeric characters)."""
    return BeautifulSoup(fragment, "html.parser").decode(formatter="minimal")


def build_epub():
    files, manifest, spine, nav = {}, [], [], []
    files["OEBPS/css/book.css"] = styles()
    files["OEBPS/images/octc-logo.png"] = (ROOT / "images/octc-logo.png").read_bytes()

    cover = clean(f"""<section class="cover">
<img src="images/octc-logo.png" alt="Owensboro Community &amp; Technical College"/>
<h1>The Language of College</h1>
<p class="sub">{build.SUBTITLE}</p>
<p>Offline edition, made on {MADE}.</p>
<p>The newest version is on the website: <a href="{SITE_URL}">{SITE_URL}</a></p>
<p class="eeo">{build.EEO}</p></section>""")
    files["OEBPS/title.xhtml"] = xhtml(TITLE, cover)
    manifest.append('<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>')
    spine.append('<itemref idref="title"/>')

    for part, instructor, pages in parts():
        items = []
        for k, t in pages:
            body = clean(page_head(k, t, part, instructor, 1) + page_body(k, True) + "</article>")
            files[f"OEBPS/{k}.xhtml"] = xhtml(build.PAGES[k]["h1"], body)
            manifest.append(f'<item id="p-{k}" href="{k}.xhtml" media-type="application/xhtml+xml"/>')
            spine.append(f'<itemref idref="p-{k}"/>')
            items.append(f'<li><a href="{k}.xhtml">{build.esc(build.PAGES[k]["h1"])}</a></li>')
        nav.append(f'<li><span>{build.esc(part)}</span><ol>{"".join(items)}</ol></li>')

    files["OEBPS/nav.xhtml"] = xhtml("Contents", f"""<nav epub:type="toc" id="toc" role="doc-toc" aria-labelledby="toc-h">
<h1 id="toc-h">Contents</h1>
<ol><li><a href="title.xhtml">Title page</a></li>{''.join(nav)}</ol></nav>""")
    manifest.append('<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
    manifest.append('<item id="css" href="css/book.css" media-type="text/css"/>')
    manifest.append('<item id="logo" href="images/octc-logo.png" media-type="image/png"/>')
    spine.insert(1, '<itemref idref="nav"/>')

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    book_id = uuid.uuid5(uuid.NAMESPACE_URL, SITE_URL)
    files["OEBPS/content.opf"] = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id" xml:lang="en">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:identifier id="book-id">urn:uuid:{book_id}</dc:identifier>
  <dc:title>{build.esc(TITLE)}</dc:title>
  <dc:language>en</dc:language>
  <dc:creator>{build.esc(PUBLISHER)}</dc:creator>
  <dc:publisher>{build.esc(PUBLISHER)}</dc:publisher>
  <dc:date>{TODAY.isoformat()}</dc:date>
  <dc:source>{SITE_URL}</dc:source>
  <meta property="dcterms:modified">{stamp}</meta>
  <meta property="schema:accessMode">textual</meta>
  <meta property="schema:accessModeSufficient">textual</meta>
  <meta property="schema:accessibilityFeature">structuralNavigation</meta>
  <meta property="schema:accessibilityFeature">tableOfContents</meta>
  <meta property="schema:accessibilityFeature">readingOrder</meta>
  <meta property="schema:accessibilityFeature">alternativeText</meta>
  <meta property="schema:accessibilityHazard">none</meta>
  <meta property="schema:accessibilitySummary">All content is text with headings, lists, and data tables in reading order. The one image is a logo with a text alternative. Text can be resized and reflowed.</meta>
</metadata>
<manifest>
  {chr(10).join(manifest)}
</manifest>
<spine>
  {chr(10).join(spine)}
</spine>
</package>
"""
    etree.fromstring(files["OEBPS/content.opf"].encode("utf-8"))
    container = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>
"""
    OUT.mkdir(exist_ok=True)
    final = OUT / "language-of-college.epub"
    with zipfile.ZipFile(final, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        for name in sorted(files):
            z.writestr(name, files[name], compress_type=zipfile.ZIP_DEFLATED)
    print("built", final.relative_to(ROOT))


if __name__ == "__main__":
    build_epub()
    build_pdf()
