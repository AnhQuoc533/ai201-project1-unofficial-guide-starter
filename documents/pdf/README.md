# PDF copies of un-scrapable sources

Some sources can't be fetched programmatically from every network:
JavaScript-only pages (Mason360, gomason athletics) and bot-blocked hosts
(Reddit, fairfaxva.gov). For those, open the URL in your browser, **print to
PDF**, and save it here with the exact filename below. `ingest.py` extracts the
text with `pdfplumber` (a PDF takes priority over a `.txt` snapshot).

| Source # | URL | Save as |
|----------|-----|---------|
| 2 | https://www.reddit.com/r/EngineeringStudents/comments/1rphp2z/free_stuff_you_can_claim_with_your_student_email/ | `02-reddit.pdf` |
| 7 | https://gomason.com/sports/2013/8/1/205056605.aspx | `07-athletics.pdf` *(optional; snapshot already exists)* |
| 9 | https://www.fairfaxva.gov/Services/CUE-Bus | `09-cue-bus.pdf` |
| 10 | https://mason360.gmu.edu/events | `10-mason360.pdf` |

After adding files, re-run:  `python ingest.py`  (or `python verify_ingest.py`).
