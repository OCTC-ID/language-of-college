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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import semester  # noqa: E402  (current-term information; edit _src/semester.py each term)

V = 16
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
        ("task-verbs", "Task verbs: analyze, compare, evaluate", "assignments/task-verbs.html"),
        ("rubric", "Reading a rubric", "assignments/rubric.html"),
    ]),
    ("participate", "Take part in class", "Join discussions and reflect on your learning.", [
        ("discussion-post", "Writing a discussion post", "participate/discussion-post.html"),
        ("replying", "Replying to classmates", "participate/replying.html"),
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
    ("grammar", "Grammar for college writing", "Practice the grammar points that appear in every assignment.", [
        ("articles", "Articles: a, an, the", "grammar/articles.html"),
        ("subject-verb", "Subject-verb agreement", None),
        ("verb-tense", "Verb tense: staying consistent", None),
        ("sentence-boundaries", "Sentence boundaries: fragments and run-ons", None),
    ]),
    ("feedback", "Revise and use feedback", "Turn comments on your work into a plan.", [
        ("instructor-feedback", "Understanding instructor feedback", None),
    ]),
    ("sources", "Use sources", "Bring other people's ideas into your writing correctly.", [
        ("quote-paraphrase-summarize", "Quote, paraphrase, or summarize", None),
    ]),
    ("help", "Ask for help", "Ask questions in a clear, professional way.", [
        ("emailing-an-instructor", "Emailing an instructor and asking questions", None),
        ("tutor", "Working with a tutor", "help/working-with-a-tutor.html"),
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
    ("rubrics-language", "Rubrics and where language accuracy fits", "instructors/rubrics-language.html"),
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

PAGES.update({
    "replying": dict(
        h1="Replying to Classmates",
        when="you need to reply to a classmate&rsquo;s post in an online discussion.",
        meta="About 8 minutes. Includes practice with answers.",
        desc="How to reply to a classmate in a college online discussion: answer, agree and add, disagree politely, or ask, with language for softening disagreement.",
    ),
    "articles": dict(
        h1="Articles: A, An, The",
        when="you are not sure whether a noun needs <span translate=\"no\">a</span>, <span translate=\"no\">an</span>, <span translate=\"no\">the</span>, or no article.",
        meta="About 12 minutes. Includes practice with answers.",
        desc="How to choose a, an, the, or no article in college writing, with three questions to ask, common problems with uncountable nouns, and practice.",
    ),
})

PAGES.update({
    "task-verbs": dict(
        h1="Task Verbs: Analyze, Compare, Evaluate",
        when="a prompt uses a verb such as <span translate=\"no\">analyze</span> or <span translate=\"no\">evaluate</span>, and you are not sure what it asks you to do.",
        meta="About 12 minutes. Includes practice with answers.",
        desc="What common task verbs in college assignments ask you to do, in three groups, with one article answered three ways and language for comparing and judging.",
    ),
    "rubric": dict(
        h1="Reading a Rubric",
        when="your instructor gives you a rubric, and you want to know how your work will be graded.",
        meta="About 10 minutes. Includes practice with answers.",
        desc="How to read a college grading rubric: criteria, levels, and points, with an annotated example and the small words that separate one level from the next.",
    ),
    "rubrics-language": dict(
        h1="Rubrics and Where Language Accuracy Fits",
        when="you are building or revising a rubric, or deciding how much grammar should count.",
        meta="About 8 minutes. Includes wording you can copy.",
        desc="How to decide what language accuracy is worth in a rubric, six practices, a before-and-after language row, and wording to copy.",
    ),
})

PAGES.update({
    "tutor": dict(
        h1="Working with a Tutor",
        when="you are thinking about getting help from a tutor, or you are getting ready for your first session.",
        meta="About 8 minutes. Includes practice with answers.",
        desc="What a tutor does, when to go, what to bring, and what to say, with language for asking for exactly the help you need.",
    ),
})

PATHS = {"home": "index.html", "semester": "this-semester/index.html"}
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
      <a href="{mode.url('semester', page_path)}">This semester</a>
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


def schedule_rows():
    rows = []
    for days, times in semester.SCHEDULE:
        if times.startswith("DRAFT:"):
            times = f'<span class="draft-flag">{esc(times[6:])}</span>'
        else:
            times = esc(times)
        rows.append((esc(days), times))
    return rows


def semester_card(mode, page_path):
    """The current-term box on the home page."""
    items = "".join(f"<li><strong>{d}:</strong> {t}</li>" for d, t in schedule_rows())
    return f"""<div class="band term">
<div class="home">
  <section class="term-card" aria-labelledby="term-h">
    <p class="term-badge">This semester <span>{esc(semester.TERM)}</span></p>
    <h2 id="term-h">{esc(semester.PERSON)} in the {esc(semester.PLACE)}</h2>
    <p class="term-what">{esc(semester.HELPS_WITH)}</p>
    <ul>{items}</ul>
    <p class="term-where"><strong>Where:</strong> {esc(semester.LOCATION)}</p>
    <p class="term-more"><a href="{mode.url('semester', page_path)}">See the details for {esc(semester.TERM)}</a> <span class="term-updated">Updated {esc(semester.UPDATED)}</span></p>
  </section>
</div>
</div>"""


def build_semester(mode):
    p = PATHS["semester"]
    rows = "".join(f'<tr><th scope="row">{d}</th><td>{t}</td></tr>' for d, t in schedule_rows())
    tips = "".join(f"<li>{esc(t)}</li>" for t in semester.TIPS)
    tips = f'<div class="note note-tip"><span class="label">Before you go</span><ul>{tips}</ul></div>' if tips else ""
    desc = f"Current-term information for {semester.TERM}: when in-person help is available in the OCTC {semester.PLACE}."
    return f"""{head(f"This Semester: {esc(semester.TERM)} | {SITE}", desc, p, mode)}
<body class="student">
{bar(p, mode)}
<div class="shell solo">
  <main class="reading" id="main">
    <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="{mode.url('home', p)}">Home</a></li><li>This semester</li></ol></nav>
    <div class="term-banner">
      <p class="term-badge">Changes each term</p>
      <h1>This Semester: {esc(semester.TERM)}</h1>
      <p class="term-updated">Updated {esc(semester.UPDATED)}</p>
      <p>The information on this page is for <strong>{esc(semester.TERM)}</strong> only. It changes every term. If the term in the title is not the current term, the times below may be wrong.</p>
    </div>

    <section id="help">
      <h2>In-person help in the {esc(semester.PLACE)}</h2>
      <p>{esc(semester.PERSON)} works in the {esc(semester.PLACE)} (TLC) at these times in {esc(semester.TERM)}.</p>
      <p>{esc(semester.ABOUT)}</p>
      <div class="table-wrap">
        <table class="term-table">
          <caption>{esc(semester.PERSON)}, {esc(semester.TERM)}</caption>
          <thead><tr><th scope="col">Days</th><th scope="col">Times</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
      {tips}
      <p>For what a tutor does and what to say in a session, read <a href="{mode.url('tutor', p)}">Working with a tutor</a>.</p>
    </section>

    <section id="tlc">
      <h2>About the {esc(semester.PLACE)}</h2>
      <p>The TLC is OCTC&rsquo;s free academic support center. It offers tutoring and other services to help you succeed in your classes.</p>
      <div class="note note-tip term-loc"><span class="label">Where to find it in {esc(semester.TERM)}</span><p>{esc(semester.LOCATION_NOTE)}</p></div>
      <ul>
        <li><strong>Hours and appointments:</strong> <a href="{semester.TLC_URL}" target="_blank" rel="noopener">OCTC Teaching and Learning Center<span class="sr-only"> (opens in a new tab)</span></a></li>
        <li><strong>Phone:</strong> {esc(semester.TLC_PHONE)}</li>
        <li><strong>Email:</strong> <a href="mailto:{semester.TLC_EMAIL}">{esc(semester.TLC_EMAIL)}</a></li>
      </ul>
    </section>

    <section id="link">
      <h2>For instructors</h2>
      <p>You can link students to this page. Its address stays the same every term, and the information is replaced when a new term begins.</p>
    </section>
  </main>
</div>
{foot(p, mode)}"""


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
    body = body.replace("<!--SEMESTER-->", semester_card(mode, p))
    body = body.replace("<!--TOC-->", cards).replace("<!--INSTRUCTOR-->", toc_items(INSTRUCTOR, p, mode))
    desc = "Short lessons for the reading, writing, and communication you do in college classes, with an Instructor Companion for faculty."
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
    write("semester", build_semester(mode))
    for section in SECTIONS:
        for key, _title, path in section[3]:
            if path:
                write(key, build_page(key, section, False, mode))
    for key, _title, path in INSTRUCTOR[3]:
        if path:
            write(key, build_page(key, INSTRUCTOR, True, mode))


if __name__ == "__main__":
    main()
