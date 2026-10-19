# The Language of College

**A Reading, Writing & Communication Toolkit** for students at Owensboro Community & Technical College, with an Instructor Companion for faculty and staff.

**Live site:** <https://octc-instructional-design.github.io/language-of-college/>

Each page teaches one skill and can be linked directly from a course. Blackboard holds assignments, due dates, and grades. This site holds the lessons.

To link students to one page, use its full address, for example:

```
https://octc-instructional-design.github.io/language-of-college/assignments/writing-prompt.html
```

> The repository name in the link is all lowercase, with hyphens.

## Structure

```
index.html              Home: This semester box, how to use, College Classes, College Life, Companion band
this-semester/          Current-term information (built from _src/semester.py)
css/styles.css          One stylesheet for every page
js/site.js              Menu behavior, copy buttons, and the prompt builder
images/                 OCTC logos and tab icons (from the official logo files)
words/                  Student pages: College words
assignments/            Student pages: Understand the assignment
participate/            Student pages: Take part in class
reading/                Student pages: Read college texts
writing/                Student pages: Write
grammar/                Student pages: Grammar for college writing
sources/                Student pages: Use sources
feedback/               Student pages: Revise and use feedback
help/                   Student pages: Ask for help
tools/                  Student pages: Tools and AI
life/                   Student pages: College Life
instructors/            Instructor Companion: landing page (index.html), pages, and the prompt builder
_src/build.py           Table of contents and page shell; builds every page
_src/pages/*.html       The body of each page (edit these)
_src/semester.py        Current-term information (edit each term)
_src/export.py          Builds the PDF and EPUB downloads
_src/export.css         Styles for the downloads
downloads/              The PDF and EPUB (generated)
```

The top bar on every page links to This semester, College Classes, College Life, and the Instructor Companion landing page ("For instructors").

## Rules

1. **Never rename or move a published file or folder.** Course links point to these exact paths.
2. **Lowercase file names, with hyphens instead of spaces.**
3. **No dates, deadlines, or point values in page content.** Those live in Blackboard. The two exceptions are This semester and the automatic "Updated" date in the footer.
4. **Colors come from the [KCTCS brand palette](https://kctcs.edu/newsroom/marketing/brand-guide/color-palette.aspx).** Text and background pairs must meet the contrast ratios in the [KCTCS color combinations](https://kctcs.edu/newsroom/marketing/brand-guide/color-combinations.aspx) guide (4.5:1 for body text). Gold is never used for text on white, and white is never used on gold. Neutral tints and status colors are listed at the top of `css/styles.css`.
5. **Links that leave the site open in a new tab,** with `target="_blank" rel="noopener"` and a screen-reader note.
6. **Mark English example sentences with `translate="no"`** so browser translation leaves them in English.
7. **After any change to `css/styles.css` or `js/site.js`,** raise `V` in `_src/build.py` and rebuild.

## At the start of every term

One page holds information that changes each term: who is working in the Teaching and Learning Center, and when. It appears in a gold box at the top of the home page and on its own page at `this-semester/`.

All of it lives in one file: **`_src/semester.py`**. To update it:

1. Open `_src/semester.py` and follow the checklist at the top (term, date, schedule rows).
2. Run `python3 _src/build.py`.
3. Commit and push.

To mark a time you still need to confirm, start it with `DRAFT:`. It shows in a red dashed box until you replace it.

This is the only page with dates on it. It is left out of the PDF and EPUB downloads on purpose, so an old download never shows an old schedule.

## Edition and updated date

Every page footer shows an edition and a date, for example "Fall 2026 edition · Updated October 18, 2026."

- **Edition:** set `EDITION` near the top of `_src/build.py`. Change it when you release a new version, for example to `"Spring 2027"`. The PDF footer uses the same setting.
- **Updated:** filled in automatically when you build. Each page shows the date its source file in `_src/pages/` last changed (unsaved or uncommitted edits count as today). The home page shows the newest change anywhere in `_src/`. This semester uses `_src/semester.py`. Dates are in Central time.

## Editing and building

The pages in the site folders are generated. Edit the source, then rebuild:

1. Edit a page body in `_src/pages/`, or the table of contents in `_src/build.py`.
2. Run `python3 _src/build.py`.
3. Commit the source and the rebuilt pages together.

To add a page:

1. Create `_src/pages/<key>.html`.
2. In `_src/build.py`, give the page a path in `SECTIONS` (College Classes), `LIFE` (College Life, which also has a goal line for its tile), or `INSTRUCTOR` (Instructor Companion). A page with no path shows as "Coming soon."
3. Add its title, "Use this page when" line, reading time, and description to `PAGES`.
4. Link it from related pages. Replace any "Coming soon" mention of it with `{{url:<key>}}`.

The Instructor Companion landing page (`_src/pages/instructors-home.html`) lists every Companion page automatically. Its table of student and instructor pairs is written by hand, so add new pairs there.

`python3 _src/build.py --preview <folder>` writes single-file copies for review. Do not publish those.

## Offline editions (PDF and EPUB)

The home page links to two downloads for students without steady internet access:

- `downloads/language-of-college.pdf`: a tagged PDF with bookmarks, a document title, and a language setting.
- `downloads/language-of-college.epub`: an EPUB 3 file with accessibility metadata. Text resizes and reflows on a phone.

After you change any page, rebuild them so the downloads match the site:

```
python3 _src/build.py
python3 _src/export.py
```

`export.py` needs Playwright (Chromium), beautifulsoup4, pikepdf, and lxml. Interactive parts, such as the prompt builder form, are replaced in the downloads with a pointer to the website. Styles for the downloads are in `_src/export.css`.

Before a major release, check the PDF with an accessibility checker (Acrobat or PAC) and the EPUB with EPUBCheck.

## Page patterns

- **College Classes (student):** "Use this page when" line, explanation, annotated example, language focus, sentence starters, practice with suggested answers and reasoning, next step, related pages. Grammar pages add a Purdue OWL "More practice" link.
- **College Life (student):** what many students notice, what helps, annotated example, a short language focus, sentence starters, where to start at OCTC, next step. No graded practice.
- **Instructor Companion:** what students experience, practices, before and after, wording to copy, link for students, sources.

## Writing conventions

- **Student pages use no labels** such as ESL or ELL. They describe skills and tasks, so any student can use them without identifying as a language learner. Instructor pages use "multilingual learners."
- **Student pages are written for an intermediate English reader:** short sentences, no idioms, literal wording. Instructor pages are written for faculty.
- **AI guidance uses OCTC's AI use labels** (No AI, AI-supported, AI-integrated) from the AI Literacy Faculty Playbook. "Levels" means phases of AI literacy, not these labels. Translation, dictionaries, and grammar checkers are addressed separately, in a Tools line. Name Microsoft Copilot, which students and faculty have through OCTC's Microsoft 365.
- **Never present AI detection as proof,** or language differences as evidence of AI use.
- **Cite only verified sources.** Main sources so far: the CCCC statement on second language writing (2020), Winkelmes et al. (2016), the MLA-CCCC working paper (2023), the CCCC 2021 State of the Art of OWI report, and NCTE's terminology glossary (2017). Label anything else as practitioner advice.
- **OCTC services:** describe only what OCTC's own pages state. Do not claim a service is free or confidential unless its page says so.
- **Describe U.S. college expectations openly,** without describing any student's home culture.
- **Check every page at desktop width and at phone width (390 px)** before publishing.
