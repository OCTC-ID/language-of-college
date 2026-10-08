"""THIS SEMESTER

Edit this file at the start of every term. It is the only place the
current-term information lives. The home page box and the "This semester"
page are both built from it.

After you edit it, run:   python3 _src/build.py

Checklist for a new term
  1. Change TERM.
  2. Change UPDATED to today's date.
  3. Replace the rows in SCHEDULE, and check HELPS_WITH and ABOUT.
  4. Check that the TLC phone, email, and link are still right.
"""

TERM = "Fall 2026"
UPDATED = "October 8, 2026"

PERSON = "Professor Matt Branham"
PLACE = "Teaching and Learning Center"

# A few words for the home page box: what this person helps with.
HELPS_WITH = "Help with English and writing"

# One short paragraph for the This Semester page: who this person is and who should come.
ABOUT = ("Professor Branham teaches composition and literature. He helps with English and writing, "
         "and he has experience working with students who use English as an additional language. "
         "Other TLC tutors also help with writing.")

# One row per line: (days, times).
# To mark a time you still need to confirm, start it with "DRAFT:". The words
# after DRAFT: show in a red dashed box on the page until you replace them.
SCHEDULE = [
    ("Mondays and Wednesdays", "9:30 a.m.–12:00 p.m."),
    ("Tuesdays and Thursdays", "11:30 a.m.–2:00 p.m."),
    ("Fridays", "By appointment"),
]

# Short tips shown under the schedule. Leave the list empty to show none.
TIPS = [
    "Bring your assignment prompt, your draft, and your questions.",
]

TLC_URL = "https://owensboro.kctcs.edu/current-students/academic-resources/teaching-and-learning-center.aspx"
TLC_PHONE = "270-852-8964"
TLC_EMAIL = "octc-tlc@kctcs.edu"
