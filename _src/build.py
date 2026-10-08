#!/usr/bin/env python3
"""Build The Language of College.

Run from anywhere:   python3 _src/build.py
Optional preview:    python3 _src/build.py --preview <folder>
  (writes single-file copies with styles and images built in, for review
   before upload; do not publish the preview files)

How it works
- SECTIONS below is the table of contents. Each page has a key, a title,
  and a path. A page with path None shows as "Coming soon" and gets no link.
- The body of each built page lives in _src/pages/<key>.html.
- In a body, write {{url:key}} to link to another page and {{root}} for
  the site root. Mark each section as:
      <section id="example" data-nav="Example">
  and the sidebar "on this page" links are made for you.

Rules (same as the FYE guidebook)
- Never rename or move a published path. Course links point to them.
- Lowercase file names with hyphens.
- No dates, deadlines, or point values in pages.
- Raise V after any change to css/styles.css or js/site.js.
"""
import base64
import html
import re
import sys
from pathlib import Path

V = 5
SITE = "The Language of College"
SUBTITLE = "A Reading, Writing &amp; Communication Toolkit"
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src" / "pages"

EEO = (
    "The Kentucky Community and Technical College System is an equal educational and "
    "employment opportunity institution and does not discriminate on the basis of race, "
    "religion, color, sex, gender identity, gender presentation, national origin, age, "
    "disability, family medical history, or genetic information. Further, we vigilantly "
    "prevent discrimination based on sexual orientation, parental status, marital status, "
    "political affiliation, military service, or any other non-merit based factor."
)

# (section id, section title, goal line, [(key, title, path or None), ...])
SECTIONS = [
    ("words", "College words", "Know the words you will hear in your first weeks.", [
        ("college-terms", "College terms you will hear in your first weeks", None),
    ]),
    ("assignments", "Understand the assignment", "Know what an assignment asks before you start.", [
        ("writing-prompt", "Understanding a writing prompt", "assignments/writing-prompt.html"),
        ("task-verbs", "Task verbs: analyze, compare, evaluate", None),
        ("rubric", "Reading a rubric", None),
    ]),
    ("participate", "Take part in class", "Join discussions and reflect on your learning.", [
        ("discussion-post", "Writing a discussion post", "participate/discussion-post.html"),
        ("replying", "Replying to classmates", None),
        ("journal", "Writing a journal or reflection", None),
        ("interacting", "Interacting in class: common expectations", None),
    ]),
    ("reading", "Read college texts", "Understand difficult readings one step at a time.", [
        ("context-clues", "Using context clues", None),
        ("long-sentence", "Unpacking a long sentence", None),
    ]),
    ("writing", "Write", "Build clear sentences and paragraphs.", [
        ("paragraph", "Building a paragraph", None),
        ("sentences", "Sentences that say what you mean", None),
    ]),
    ("feedback", "Revise and use feedback", "Turn comments on your work into a plan.", [
        ("instructor-feedback", "Understanding instructor feedback", None),
    ]),
    ("sources", "Use sources", "Bring other people's ideas into your writing correctly.", [
        ("quote-paraphrase-summarize", "Quote, paraphrase, or summarize", None),
    ]),
    ("help", "Ask for help", "Ask questions in a clear, professional way.", [
        ("emailing-an-instructor", "Emailing an instructor and asking questions", None),
    ]),
    ("tools", "Tools and AI", "Use language tools and AI to learn, within your course rules.", [
        ("tools-check-rules", "Translation, grammar tools, and AI: check the rules first", None),
        ("ai-to-learn", "Using AI to learn", None),
        ("writing-record", "Keeping a record of your writing process", None),
    ]),
]

INSTRUCTOR = ("instructors", "Instructor Companion", "", [
    ("assignment-prompts", "Writing a clear assignment prompt", "instructors/assignment-prompts.html"),
    ("discussions-journals", "Setting expectations for discussions and journals", "instructors/discussions-journals.html"),
    ("prompt-builder", "Tool: Assignment prompt builder", "instructors/prompt-builder.html"),
    ("rubrics-language", "Rubrics and where language accuracy fits", None),
    ("actionable-feedback", "Focused, actionable feedback", None),
    ("tool-expectations", "Setting expectations for translation, grammar tools, and AI", None),
    ("process-authorship", "Talking about writing process and authorship", None),
    ("language-backgrounds", "Knowing your students' language backgrounds", None),
])

# Extra details for each built page: h1, "use this page when" line, meta line, description
PAGES = {
    "writing-prompt": dict(
        h1="Understanding a Writing Prompt",
        when="your instructor gives you a writing assignment and you want to be sure what it asks you to do.",
        meta="About 10 minutes. Includes practice with answers.",
        desc="How to read a college writing prompt: the task, the topic, the reader, the requirements, and the words that show what is required.",
    ),
    "assignment-prompts": dict(
        h1="Writing a Clear Assignment Prompt",
        when="you are writing or revising the instructions for a writing assignment.",
        meta="About 8 minutes. Includes wording you can copy.",
        desc="Six practices for writing assignment prompts that state expectations openly, with a before-and-after example and wording to copy.",
    ),
}

PAGES.update({
    "discussion-post": dict(
        h1="Writing a Discussion Post",
        when="your class has an online discussion and you need to write your first post.",
        meta="About 10 minutes. Includes practice with answers.",
        desc="How to write a first post in a college online discussion: answer, reason, support, and a closing question, with practice in forming questions.",
    ),
    "discussions-journals": dict(
        h1="Setting Expectations for Discussions and Journals",
        when="you assign discussion posts, journals, or reflections.",
        meta="About 8 minutes. Includes wording you can copy.",
        desc="Eight practices for stating the unwritten rules of discussions and journals, with a before-and-after example and wording to copy.",
    ),
    "prompt-builder": dict(
        h1="Assignment Prompt Builder",
        when="you want to draft a new assignment prompt or check one you already have.",
        meta="Nothing you type on this page is saved or sent anywhere.",
        desc="A fill-in tool that assembles a clear assignment prompt, plus a Copilot prompt for checking the clarity of an existing assignment.",
    ),
})

PATHS = {"home": "index.html"}
for _sec in SECTIONS + [INSTRUCTOR]:
    for _key, _title, _path in _sec[3]:
        if _path:
            PATHS[_key] = _path


def esc(text):
    return html.escape(text, quote=True)


class Mode:
    """Resolves links for the real site or for flat single-file previews."""

    def __init__(self, preview):
        self.preview = preview

    def root(self, page_path):
        return "" if self.preview else "../" * page_path.count("/")

    def url(self, key, page_path):
        key, _, frag = key.partition("#")
        frag = "#" + frag if frag else ""
        if self.preview:
            return ("home" if key == "home" else key) + ".html" + frag
        return self.root(page_path) + PATHS[key] + frag

    def asset(self, rel, page_path):
        if not self.preview:
            return self.root(page_path) + rel
        data = base64.b64encode((ROOT / rel).read_bytes()).decode()
        return "data:image/png;base64," + data


def head(title, desc, page_path, mode):
    r = mode.root(page_path)
    if mode.preview:
        css = "<style>" + (ROOT / "css/styles.css").read_text() + "</style>"
    else:
        css = f'<link rel="stylesheet" href="{r}css/styles.css?v={V}">'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{esc(desc)}">
<link rel="icon" type="image/png" sizes="48x48" href="{mode.asset('images/icon-48.png', page_path)}">
<link rel="apple-touch-icon" href="{mode.asset('images/icon-180.png', page_path)}">
{css}
</head>"""


def bar(page_path, mode):
    home = mode.url("home", page_path)
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="bar">
  <div class="inner">
    <a class="brand" href="{home}">
      <picture>
        <source media="(max-width: 560px)" srcset="{mode.asset('images/octc-logo-short-reversed.png', page_path)}">
        <img src="{mode.asset('images/octc-logo-reversed.png', page_path)}" alt="Owensboro Community &amp; Technical College" height="36">
      </picture>
      <span class="brand-text">{SITE}</span>
      <span class="sr-only">Home</span>
    </a>
    <nav class="bar-nav" aria-label="Site">
      <a href="{mode.url('home#contents', page_path)}">Contents</a>
      <a class="pill" href="{mode.url('home#instructors', page_path)}">Instructor Companion</a>
    </nav>
  </div>
</header>"""


def foot(page_path, mode):
    if mode.preview:
        js = "<script>" + (ROOT / "js/site.js").read_text() + "</script>"
    else:
        js = f'<script src="{mode.root(page_path)}js/site.js?v={V}"></script>'
    return f"""<footer>
  <div class="inner">
    <div class="who"><span>{SITE}: {SUBTITLE}</span><span>Owensboro Community &amp; Technical College</span></div>
    <p class="eeo">{EEO}</p>
  </div>
</footer>
{js}
</body>
</html>
"""


def fill(body, page_path, mode):
    body = re.sub(r"\{\{url:([^}]+)\}\}", lambda m: mode.url(m.group(1), page_path), body)
    return body.replace("{{root}}", mode.root(page_path))


def page_list(section, current, page_path, mode, onpage):
    items = []
    for key, title, path in section[3]:
        if key == current:
            sub = "".join(f'<a href="#{i}">{esc(label)}</a>' for i, label in onpage)
            items.append(
                f'<li><a class="pg" href="{mode.url(key, page_path)}" aria-current="page">{esc(title)}</a>'
                f'<div class="onpage">{sub}</div></li>'
            )
        elif path:
            items.append(f'<li><a class="pg" href="{mode.url(key, page_path)}">{esc(title)}</a></li>')
        else:
            items.append(f'<li><span class="pg">{esc(title)} <span class="soon">Coming soon</span></span></li>')
    return "\n        ".join(items)


def build_page(key, section, instructor, mode):
    page_path = PATHS[key]
    info = PAGES[key]
    title = next(t for k, t, _ in section[3] if k == key)
    body = fill((SRC / f"{key}.html").read_text(), page_path, mode)
    onpage = re.findall(r'<section id="([^"]+)" data-nav="([^"]+)"', body)
    home = mode.url("home", page_path)
    label = "Instructor Companion" if instructor else "Section"
    back = mode.url("home#instructors" if instructor else "home#contents", page_path)
    band = (
        '<div class="audience"><div class="inner"><strong>Instructor Companion</strong>'
        "For faculty and staff. Students are welcome to read it too.</div></div>"
        if instructor else ""
    )
    side_title = "For faculty and staff" if instructor else section[1]
    return f"""{head(f"{esc(info['h1'])} | {SITE}", info['desc'], page_path, mode)}
<body class="{'instructor' if instructor else 'student'}">
{bar(page_path, mode)}
{band}
<div class="shell">
  <nav class="sidenav" aria-label="{esc(section[1])}">
    <details open>
      <summary>
        <span><span class="side-label">{label}</span><span class="side-title">{esc(side_title)}</span></span>
        <span class="side-toggle"><span class="when-closed">Pages</span><span class="when-open">Close</span></span>
      </summary>
      <div class="panel">
      <ul>
        {page_list(section, key, page_path, mode, onpage)}
      </ul>
      <a class="all" href="{back}">All pages</a>
      </div>
    </details>
  </nav>
  <main class="reading" id="main">
    <img class="print-logo" src="{mode.asset('images/octc-logo.png', page_path)}" alt="Owensboro Community &amp; Technical College">
    <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="{home}">Home</a></li><li>{esc(section[1])}</li><li>{esc(title)}</li></ol></nav>
    <p class="kicker">{esc(section[1])}</p>
    <h1>{esc(info['h1'])}</h1>
    <p class="use-when"><strong>Use this page when</strong> {info['when']}</p>
    <p class="meta">{info['meta']}</p>
{body}
  </main>
</div>
{foot(page_path, mode)}"""


def toc_items(section, page_path, mode):
    out = []
    for key, title, path in section[3]:
        if path:
            out.append(f'<li class="live"><a href="{mode.url(key, page_path)}">{esc(title)}</a></li>')
        else:
            out.append(f'<li><span class="pg">{esc(title)} <span class="soon">Coming soon</span></span></li>')
    return "\n          ".join(out)


def build_home(mode):
    p = "index.html"
    cards = "\n".join(
        f"""      <li id="{sid}">
        <div class="tile-head">
          <h3>{esc(title)}</h3>
          <p class="goal">{esc(goal)}</p>
        </div>
        <ul>
          {toc_items((sid, title, goal, pages), p, mode)}
        </ul>
      </li>""" for sid, title, goal, pages in SECTIONS
    )
    body = fill((SRC / "home.html").read_text(), p, mode)
    body = body.replace("<!--TOC-->", cards).replace("<!--INSTRUCTOR-->", toc_items(INSTRUCTOR, p, mode))
    desc = "Short, free lessons for the reading, writing, and communication you do in college classes, with an Instructor Companion for faculty."
    return f"""{head(f"{SITE}: {SUBTITLE}", desc, p, mode)}
<body class="student">
{bar(p, mode)}
<main id="main">
{body}
</main>
{foot(p, mode)}"""


def main():
    preview = None
    if "--preview" in sys.argv:
        preview = Path(sys.argv[sys.argv.index("--preview") + 1])
        preview.mkdir(parents=True, exist_ok=True)
    mode = Mode(bool(preview))

    def write(key, text):
        out = (preview / f"{key}.html") if preview else (ROOT / PATHS[key])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        print("built", out.relative_to(preview if preview else ROOT))

    write("home", build_home(mode))
    for section in SECTIONS:
        for key, _title, path in section[3]:
            if path:
                write(key, build_page(key, section, False, mode))
    for key, _title, path in INSTRUCTOR[3]:
        if path:
            write(key, build_page(key, INSTRUCTOR, True, mode))


if __name__ == "__main__":
    main()
