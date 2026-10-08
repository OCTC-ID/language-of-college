"""THIS SEMESTER

Edit this file at the start of every term. It is the only place the
current-term information lives. The home page box and the "This semester"
page are both built from it.

After you edit it, run:   python3 _src/build.py

Checklist for a new term
  1. Change TERM.
  2. Change UPDATED to today's date.
  3. Replace the rows in SCHEDULE, and check HELPS_WITH and ABOUT.
  4. Check LOCATION and LOCATION_NOTE. The TLC moved temporarily in Fall 2026.
  5. Check that the TLC phone, email, and link are still right.
"""

TERM = "Fall 2026"
UPDATED = "October 8, 2026"

PERSON = "Professor Matt Branham"
PLACE = "Teaching and Learning Center"

# Where the TLC is THIS TERM. In Fall 2026 it is in a temporary location, so check this every term.
# LOCATION is the short form for the home page box. LOCATION_NOTE is one sentence for the page.
LOCATION = "Technical Building, second floor, room TCE 208"
LOCATION_NOTE = ("This term, the TLC is on the second floor of the Technical Building, in room TCE 208. "
                 "This location is temporary.")

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
    "Make an appointment for help with writing. Call or email the TLC.",
    "Bring your assignment, your draft, and your class notes.",
    "Bring your syllabus, your textbook, and any handouts from class.",
    "Know your instructor's name and the name of your class. The tutor writes them on a TLC form.",
    "One session can last as long as two hours.",
]

TLC_URL = "https://owensboro.kctcs.edu/current-students/academic-resources/teaching-and-learning-center.aspx"
TLC_PHONE = "270-852-8964"
TLC_EMAIL = "octc-tlc@kctcs.edu"
