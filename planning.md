# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

### Things to Do for FREE as a George Mason student
My domain is about introducing to George Mason student a variety of things they can do and join for free, including exclusive discounts, perks, events, and freebies. George Mason University is a huge commuting university in Fairfax county, VA, as students attend classes and then go home immediately on a daily basis. Thus, they mostly miss any opportunity and priviledge as a George Mason, making these pieces of information hard to obtain.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
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

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 500 tokens.

**Overlap:** 50 tokens.

**Reasoning:** It is long enough to hold a complete instruction but short enough to keep the embedding vector focused. Since the documents contains long guides with many paragraphs, the chunk size will be measured in tokens instead of characters.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `sentence-transformers` (`all-MiniLM-L6-v2`).

**Top-k:** 5 chunks per query.

**Production tradeoff reflection:** If cost and resource constraints were not a concern in a real-world deployment, I would weigh in accuracy, context length, semantic capability, and latency.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What is Mason Day and what will it feature in 2027? | Mason Day is a end-of-year Spring Carnival that combines amusements, rides, games, food, music, and more at GMU. Mason students can join for free with active and valid student ID. Mason Day 2027 will feature a HUGE carnival with rides, games, delicious treats, food trucks, inflatables, novelties, student performances all day. |
| 2 | How can I enter Corner Pocket for free? | Free Play Friday at Corner Pocket: Mason’s mini arcade and games area is free on Fridays from 6-11 PM. |
| 3 | Where and how can I get free food at GMU? | You can get free food support from the Patriot Pantry. In order to utilize the Patriot Pantry, a student must be a degree-seeking George Mason student enrolled in at least one (1) credit hour in the current/present term. If you are interested in receiving services from the Patriot Pantry, please visit the Patriot Pantry at Fairfax or Patriot Pantry at Mason Square pages depending on the campus you primarily attend to learn more and submit an order form. |
| 4 | What is the service hour of CUE bus? | Service Hours:<br> Mon–Fri: 5 a.m.–11 p.m.<br> Sat: 8 a.m.–8 p.m.<br> Sun: 10 a.m.–6 p.m.<br> Note: Times are approximate. |
| 5 | How can I claim free tickets for any athletic events at GMU? | Tickets can be claimed with these simple steps:<br>1) Open Mason360 App<br>2) Select Events Tab from bottom<br>3) Select Filter Option in Top Right<br>4) Filter by group, "Mason Athletics"<br>5) Select on the game you wish to get your ticket<br>6) Select “Register”<br>7) Hit the back arrow and click on “1 ticket” to get your ticket QR code<br>NOTE: QR Code WILL BE required for entry. No paper tickets will be accpeted. EagleBank Arena or George Mason Athletics staff can deny anyone trying to enter with a paper QR Code |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Some information contains important notes or notice. The model could fail to mention those when user wants to query these pieces of information.

2. Some sources contain embedded citations or references to other sources, which the model may fail to attribute properly.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
```
+------------------------------------------------------------------------------+
|                          1. DOCUMENT INGESTION                               |
|  - Web Scrapers / API Connectors (Requests, BeautifulSoup, Reddit API)       |
|  - Ingests: GMU Domain Sites, Reddit Threads, City Transit Data, Google Docs |
+------------------------------------------------------------------------------+
                                       |
                                       v
+------------------------------------------------------------------------------+
|                               2. CHUNKING                                    |
|  - Token-Based Text Splitter (RecursiveCharacterTextSplitter via LangChain)  |
|  - Configuration: Chunk Size = 500 Tokens | Overlap = 50 Tokens              |
+------------------------------------------------------------------------------+
                                       |
                                       v
+------------------------------------------------------------------------------+
|                        3. EMBEDDING + VECTOR STORE                           |
|  - Embedding Model: sentence-transformers (all-MiniLM-L6-v2)                 |
|  - Vector Database: ChromaDB                                                 |
+------------------------------------------------------------------------------+
                                       |
                                       v
+------------------------------------------------------------------------------+
|                               4. RETRIEVAL                                   |
|  - Vector Search: Cosine Similarity Matching on User Queries                 |
|  - Configuration: Top-k = 5 Chunks (Fetches highest scoring context pieces)  |
+------------------------------------------------------------------------------+
                                       |
                                       v
+------------------------------------------------------------------------------+
|                               5. GENERATION                                  |
|  - LLM Framework: Groq (llama-3.3-70b-versatile)                             |
|  - Generation Model: Anthropic Claude 3.5 Sonnet                             |
|  - Output: Accurately synthesis of free student perks, transit, and events   |
+------------------------------------------------------------------------------+

```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
