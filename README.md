# The Language of College

**A Reading, Writing & Communication Toolkit** for students at Owensboro Community & Technical College, with an Instructor Companion for faculty and staff.

**Live site:** <https://octc-id.github.io/language-of-college/>

Each page teaches one skill and can be linked directly from a course. Blackboard holds assignments, due dates, and grades. This site holds the lessons.

To link students to one page, use its full address, for example:

```
https://octc-id.github.io/language-of-college/assignments/writing-prompt.html
```

> The repository name in the link is all lowercase, with hyphens.

## Structure

```
index.html              Home: how to use the toolkit, contents, Instructor Companion
css/styles.css          One stylesheet for every page
js/site.js              Menu behavior, copy buttons, and the prompt builder
images/                 OCTC logos and tab icons (from the official logo files)
assignments/            Student pages: Understand the assignment
participate/            Student pages: Take part in class
instructors/            Instructor Companion pages and tools
_src/build.py           Table of contents and page shell; builds every page
_src/pages/*.html       The body of each page (edit these)
```

## Rules

1. **Never rename or move a published file or folder.** Course links point to these exact paths.
2. **Lowercase file names, with hyphens instead of spaces.**
3. **No dates, deadlines, or point values.** Those live in Blackboard.
4. **Colors come from the KCTCS brand palette.** See the notes at the top of `css/styles.css`.
5. **Links that leave the site open in a new tab,** with `target="_blank" rel="noopener"` and a screen-reader note.
6. **Mark English example sentences with `translate="no"`** so browser translation leaves them in English.
7. **After any change to `css/styles.css` or `js/site.js`,** raise `V` in `_src/build.py` and rebuild.

## Editing and building

The pages in the site folders are generated. Edit the source, then rebuild:

1. Edit a page body in `_src/pages/`, or the table of contents in `_src/build.py`.
2. Run `python3 _src/build.py`.
3. Commit the source and the rebuilt pages together.

To add a page, give it a path in `SECTIONS` (or `INSTRUCTOR`), add its details to `PAGES`, and create `_src/pages/<key>.html`. A page with no path shows as "Coming soon."

`python3 _src/build.py --preview <folder>` writes single-file copies for review. Do not publish those.

## Page pattern

Student pages: explanation, annotated example, language focus, sentence starters, practice with answers, next step, related pages.

Instructor pages: what students experience, practices, before and after, wording to copy, link for students, sources.
