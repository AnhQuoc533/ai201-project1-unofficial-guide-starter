# The Unofficial Guide

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
My domain is about introducing to George Mason student a variety of things they can do and join for free, including exclusive discounts, perks, events, and freebies. George Mason University is a huge commuter university in Fairfax county, VA, where students attend classes and then go home immediately on a daily basis. Thus, they mostly miss any opportunity and privilege as a George Mason, making these pieces of information hard to obtain.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | <div style="width: 230px;">Description | URL |
|---|--------|-------------|---|
| 1 | the mason everything doc - Google Docs| Free things to do around George Mason University (what you are paying with with your tuition) | https://docs.google.com/document/d/11A-QRB7bBZ3XX3F3WJ8U0ZRLrEipKoB-9JLFMPf-oKU/ |
| 2 | r/EngineeringStudents | Free things you can get with student email | https://www.reddit.com/r/EngineeringStudents/comments/1rphp2z/free_stuff_you_can_claim_with_your_student_email/ |
| 3 | First-Gen+ Center - GMU | Perks and Discounts for GMU students | https://firstgen.gmu.edu/resources-information/resource-guide-2/perks-discounts/ |
| 4 | Student Support and Advocacy Center (SSAC) | Get food support for free from GMU Food Pantry| https://ssac.gmu.edu/patriot-pantry |
| 5 | First-Year Connections - GMU | Free Social Events for First-Year and Transfer students | https://fyc.gmu.edu/first-year-programs |
| 6 | Student Involvement - GMU | Mason Day is the biggest student fair in GMU and Mason students can attend for free | https://si.gmu.edu/mason-day/ |
| 7 | George Mason University Athletics | Free Admission to all George Mason athletic events | https://gomason.com/sports/2013/8/1/205056605.aspx |
| 8 | The University Network | Affordable and Free Activities for GMU students in Fairfax, VA | https://www.tun.com/schools/discover-affordable-and-free-activities-for-george-mason-university-students-in-fairfax-va |
| 9 | City of Fairfax Virginia | Fare-free rides from CUE Bus for GMU students | https://www.fairfaxva.gov/Services/CUE-Bus |
| 10 | Mason360 | All free events offered by George Mason community. Some events have limited spots | https://mason360.gmu.edu/events |


---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 256 tokens (default), with a per-source override of **80 tokens** for the Mason Everything Doc.

**Overlap:** 38 tokens (~15%); 12 tokens (~15%) for the 80-token override.

**Reasoning:** 256 tokens is long enough to hold a complete instruction but short enough to keep the embedding vector focused, and `all-MiniLM-L6-v2` accepts at most 256 word-piece tokens and truncates the rest without warning. Most sources are prose guides with many paragraphs, so the chunk size is measured in tokens instead of characters, and ~15% overlap is the standard sweet spot for keeping cross-sentence references intact when a long section gets cut.

**Final chunk count:** **149** across 10 documents.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `sentence-transformers` (`all-MiniLM-L6-v2`)

**Production tradeoff reflection:** If cost and resource constraints were not a concern in a real-world deployment, I would weigh in:
* Domain-specific accuracy: my corpus is a blend of official prose and informal, student-made documents ("freebies," building-room codes like "HUB 2300," program names like "Mason Day"). With cost no object, fine-tuning a model on GMU-specific Q&A pairs would likely beat any off-the-shelf choice. 
* Context length: A production model with a 2k+ context window would let me embed an entire program page like Patriot Pantry as one coherent unit, so a query about eligibility and hours and location could be answered from a single vector instead of hoping three chunks all surface. For my prose-heavy sources, this is the upgrade that would matter most.2
* Dimensions/Storage: premium models output 1,024 to 3,072 dimensions, which is far better semantically but bigger in the vector store. 

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
> *You are a George Mason University's information assistant, helping other GMU students find free things, perks, events, and resources.*\
> *Answer the question using ONLY the numbered context provided. Rules:*\
> *- Be specific: include hours, locations, eligibility, costs, and step-by-step instructions when they appear in the context.*\
> *- Preserve important notes, conditions, and warnings (e.g. ID required, limited spots, approximate times).*\
> *- Do not use outside knowledge or guess. If the answer is not contained in the context, reply with exactly "NO_ANSWER" and nothing else.*\
> *- If your answer is not "NO_ANSWER", cite every source you drew from and do not cite a source unless you used it in your answer. Strictly use the below format for your citation:*\
> *Source:*\
> *- `[source 1 title](url)`*\
> *- `[source 2 title](url)`*\
> *- etc.*

**How source attribution is surfaced in the response:** the model is instructed to append `[source: Title](URL)` after each claim it makes. The interface then renders them as a clickable link list. Only sources that appear in the answer text are included, so the list reflects what the model actually drew from, not everything that was retrieved.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | <div style="width: 280px;">Expected answer</div> | <div style="width: 280px;">System response (summarized)</div> | Retrieval quality | Response accuracy |
|---|---|---|---|---|---|
| 1 | What is Mason Day and what will it feature in 2027? | Mason Day is a end-of-year Spring Carnival that combines amusements, rides, games, food, music, and more at GMU. Mason students can join for free with active and valid student ID. Mason Day 2027 will feature a HUGE carnival with rides, games, delicious treats, food trucks, inflatables, novelties, student performances all day. | Mason Day is George Mason's largest and longest-standing tradition, an end-of-year Spring Carnival. In 2027, it will feature a HUGE carnival with rides, games, delicious treats, food trucks, inflatables, novelties, student performances all day, and Mason Day T-shirts and goodies (while supplies last). All events are FREE. The 2027 headliner has not been announced yet. <br>Source:<br>- Mason Day \| https://si.gmu.edu/mason-day/|Relevant|Partially accurate
| 2 | How can I enter Corner Pocket for free? | Free Play Friday at Corner Pocket: Mason’s mini arcade and games area is free on Fridays from 6-11 PM. | To enter Corner Pocket for free, you can go on Fridays from 6-11 PM, as it is free on Fridays during this time. Corner Pocket is Mason's mini arcade and games area.<br>Source:<br>- [The Mason Everything Doc](https://docs.google.com/document/d/11A-QRB7bBZ3XX3F3WJ8U0ZRLrEipKoB-9JLFMPf-oKU/)|Relevant|Accurate
| 3 | Where and how can I get free food at GMU? | You can get free food support from the Patriot Pantry. In order to utilize the Patriot Pantry, a student must be a degree-seeking George Mason student enrolled in at least one (1) credit hour in the current/present term. If you are interested in receiving services from the Patriot Pantry, please visit the Patriot Pantry at Fairfax or Patriot Pantry at Mason Square pages depending on the campus you primarily attend to learn more and submit an order form. | You can get free food at the Patriot Pantry, which is located in SUB I on the Fairfax Campus. You can also contact them at [email protected] for questions about services, donating, or volunteering. Additionally, you can check out the Virginia Supplemental Nutrition Assistance Program (SNAP) if the Patriot Pantry is not enough. <br>Source:<br>- [4] (source: Patriot Pantry \| https://ssac.gmu.edu/patriot-pantry)|Relevant|Accurate
| 4 | How can I travel to GMU by bus for free? | You can travel to GMU by bus for free using the CUE Bus.<br>Service Hours:<br> Mon–Fri: 5 a.m.–11 p.m.<br> Sat: 8 a.m.–8 p.m.<br> Sun: 10 a.m.–6 p.m.<br> Note: Times are approximate. | You can travel to GMU by bus for free using the CUE Bus, which offers fare-free service throughout the City of Fairfax, connecting riders to George Mason University. The service hours are:<br>- Mon–Fri: 5 a.m.–11 p.m.<br>- Sat: 8 a.m.–8 p.m.<br>- Sun: 10 a.m.–6 p.m.<br>Note: Times are approximate.<br>Source:<br>- [CUE Bus](https://www.fairfaxva.gov/Services/CUE-Bus)|Relevant|Accurate
| 5 | How can I claim free tickets for any athletic events at GMU? | Tickets can be claimed with these simple steps:<br>1) Open Mason360 App<br>2) Select Events Tab from bottom<br>3) Select Filter Option in Top Right<br>4) Filter by group, "Mason Athletics"<br>5) Select on the game you wish to get your ticket<br>6) Select “Register”<br>7) Hit the back arrow and click on “1 ticket” to get your ticket QR code<br>NOTE: QR Code WILL BE required for entry. No paper tickets will be accpeted. EagleBank Arena or George Mason Athletics staff can deny anyone trying to enter with a paper QR Code | To claim free tickets for GMU athletic events, follow these steps:<br>1) Open the Mason360 App<br>2) Select the Events Tab from the bottom<br>3) Select the Filter Option in the Top Right<br>4) Filter by group, "Mason Athletics"<br>5) Select the game you wish to get your ticket for<br>6) Select "Register"<br>7) Hit the back arrow and click on "1 ticket" to get your ticket QR code.<br>Note: A QR Code is required for entry, and no paper tickets will be accepted.<br>Source:<br>- Free Admission to George Mason athletic events (https://gomason.com/sports/2013/8/1/205056605.aspx)|Relevant|Accurate

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** Can I get attend a class at GMU for free?

**What the system returned:**
>NO_ANSWER\
>Source:
>- Perks and Discounts for GMU students | https://firstgen.gmu.edu/resources-information/resource-guide-2/perks-discounts/
>- Affordable and Free Activities for GMU students in Fairfax, VA | https://www.tun.com/schools/discover-affordable-and-free-activities-for-george-mason-university-students-in-fairfax-va
>- Free stuff you can claim with your student email | https://www.reddit.com/r/EngineeringStudents/comments/1rphp2z/free_stuff_you_can_claim_with_your_student_email/
>- The Mason Everything Doc | https://docs.google.com/document/d/11A-QRB7bBZ3XX3F3WJ8U0ZRLrEipKoB-9JLFMPf-oKU/ 
>- The Mason Everything Doc | https://docs.google.com/document/d/11A-QRB7bBZ3XX3F3WJ8U0ZRLrEipKoB-9JLFMPf-oKU/

**Root cause (tied to a specific pipeline stage):** The grounded system prompt poorly explains how the LLM should cite sources.

**What you would change to fix it:** Instead of saying *"After you answer, cite every source [...],"* this portion of the system prompt should say *"If your answer is not "NO_ANSWER", cite every source [...]."*

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**\
The metadata contract defined in planning.md that requires every document to carry
`{source, url, title, doc_type, date}` from ingestion through to generation and acts
as a concrete checklist at every stage boundary. Instead of asking "does this work?"
at each handoff, I could ask the narrower, testable question: "does this chunk still
have all fields?" That made integration bugs surface immediately rather than
silently propagating. Specifically, it was the reason source attribution in the
`generate.py` worked on the first attempt: the `title` and `url` needed for
citations were already guaranteed to be present on every chunk object because the spec
had enforced them since Stage 1. Without that explicit contract, the most likely
failure mode would have been a KeyError or a missing citation discovered late, during
the demo.

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* I gave Claude Code the Evaluation Plan, the Anticipated Challenges, the grounded prompt, along with the system Architecture. Then, I ask it to implement Generation layer, using Groq's `llama-3.3-70b-versatile` as runtime generation model.
- *What it produced:* `generate.py` that formats retrieved chunks into a numbered context block, sends the grounded prompt, context, and user query to `llama-3.3-70b-versatile` via the Groq client, then returns the answer
- *What I changed or overrode:* I noticed that the grounded prompt written by Claude was flawed and missing some impportant rules. So I made a few changes to clarify the prompt for better results. 

**Instance 2**

- *What I gave the AI:* At the final step, I told Claude Code to implement a UI for this application, using Gradio UI and following industry standards for a website.
- *What it produced:* `app.py` that uses `POST /` query (body `{query}` → `{answer, sources, retrieved_chunks}`) and a `GET /` serving one HTML page with a text box, a send button, an answer panel, and a visible suggested prompts and sub-topics.
- *What I changed or overrode:* The application website looked odd and unaesthetic. So I used the code example from lab 1 to restructure the UI and further added some features.
