# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

### Things to Do for FREE as a George Mason student
My domain is about introducing to George Mason student a variety of things they can do and join for free, including exclusive discounts, perks, events, and freebies. George Mason University is a huge commuter university in Fairfax county, VA, where students attend classes and then go home immediately on a daily basis. Thus, they mostly miss any opportunity and privilege as a George Mason, making these pieces of information hard to obtain.

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

**Chunk size:** 256 tokens (default), with a per-source override of **80 tokens** for the Mason Everything Doc.

**Overlap:** 38 tokens (~15%); 12 tokens (~15%) for the 80-token override.

**Reasoning:** 256 tokens is long enough to hold a complete instruction but short enough to keep the embedding vector focused, and `all-MiniLM-L6-v2` accepts at most 256 word-piece tokens and truncates the rest without warning. Most sources are prose guides with many paragraphs, so the chunk size is measured in tokens instead of characters, and ~15% overlap is the standard sweet spot for keeping cross-sentence references intact when a long section gets cut.

**Per-source override (added during implementation):** The Mason Everything Doc is not prose — it is a dense bullet list of many short, independent items (e.g. "Free Play Friday at Corner Pocket... free Fridays 6–11 PM"). At 256 tokens, each chunk lumped ~10 items together and diluted their embeddings, so item-specific queries failed to retrieve the right chunk (the Corner Pocket chunk scored 0.262, below the 0.30 retrieval floor, ranked 14th). Chunking that source at 80 tokens isolates each item; the same chunk then scores 0.519 and ranks 1st. This follows the principle that a list-heavy source warrants finer chunking than a long-form guide. Implemented as `CHUNK_SIZE_OVERRIDES` keyed by `doc_type` in `config.py`.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `sentence-transformers` (`all-MiniLM-L6-v2`).

**Top-k:** 5 chunks per query.

**Production tradeoff reflection:** If cost and resource constraints were not a concern in a real-world deployment, I would weigh in:
* Domain-specific accuracy: my corpus is a blend of official prose and informal, student-made documents ("freebies," building-room codes like "HUB 2300," program names like "Mason Day"). With cost no object, fine-tuning a model on GMU-specific Q&A pairs would likely beat any off-the-shelf choice. 
* Context length: A production model with a 2k+ context window would let me embed an entire program page like Patriot Pantry as one coherent unit, so a query about eligibility and hours and location could be answered from a single vector instead of hoping three chunks all surface. For my prose-heavy sources, this is the upgrade that would matter most.2
* Dimensions/Storage: premium models output 1,024 to 3,072 dimensions, which is far better semantically but bigger in the vector store. 

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
| 4 | How can I travel to GMU by bus for free? | Service Hours:<br> Mon–Fri: 5 a.m.–11 p.m.<br> Sat: 8 a.m.–8 p.m.<br> Sun: 10 a.m.–6 p.m.<br> Note: Times are approximate. |
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
╔══════════════════════════════════════════════════════════════════════════════╗
║  INDEXING PHASE  —  offline, run once (re-run on content refresh)            ║
╚══════════════════════════════════════════════════════════════════════════════╝

                                 10 raw sources
            (Google Doc, Reddit thread, GMU dept pages, Mason360 feed)
                                       |
                                       v
+------------------------------------------------------------------------------+
|                             DOCUMENT INGESTION                               |
|  - Web Scrapers/API Connectors (requests/httpx, BeautifulSoup, Reddit API)   |
|  - Output: clean text + metadata per doc: {source,url,title,doc_type,date}   |
+------------------------------------------------------------------------------+
                                       |
                                       v
+------------------------------------------------------------------------------+
|                                  CHUNKING                                    |
|  - Token-Based Text Splitter: RecursiveCharacterTextSplitter via LangChain   |
|  - Configuration: Chunk Size = 256 Tokens | Overlap = 38 Tokens              |
+------------------------------------------------------------------------------+
                                       |
                                       v
+------------------------------------------------------------------------------+
|                           EMBEDDING + VECTOR STORE                           |
|  - Embedding Model: sentence-transformers (all-MiniLM-L6-v2)                 |
|  - Vector Database: ChromaDB (384 dimensions)                                |
+------------------------------------------------------------------------------+

╔══════════════════════════════════════════════════════════════════════════════╗
║  QUERY PHASE  —  online, per user request                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

                              (Embeded) User query
                                       |
                                       v
+------------------------------------------------------------------------------+
|                                  RETRIEVAL                                   |
|  - Vector Search: Cosine Similarity Matching on User Queries                 |
|  - Configuration: Top-k = 5 Chunks (Fetches highest scoring context pieces)  |
+------------------------------------------------------------------------------+
                                       |
                                       v
+------------------------------------------------------------------------------+
|                                  GENERATION                                  |
|  - LLM Framework: Groq (llama-3.3-70b-versatile)                             |
|  - Grounded prompt: "Answer ONLY from the context below. If absent, say so.  |
|                      Cite each source."                                      |
|  - Output: answer + [source: title/url]                                      |
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
* **AI tool**: Claude
* **Input**: the [Domain](#domain), the [Documents](#documents), and the [Chunking Strategy](#chunking-strategy) sections of this document, along with the system [Architecture](#architecture).
* **Prompt**: I'm building a RAG system to make student-generated knowledge searchable and answerable with the scope as described in the Domain section. Help me to implement both Document Ingestion layer and Chunking layer of the attached system architecture, in Python. Ingestion function should collect texts from sources in document table, clean them, and output a list of dictionaries with the following metadata: `{text, source, url, title, doc_type, date}`. Note that each source type needs its own loader (Google Docs export URL, Reddit `.json` endpoint, BeautifulSoup for GMU dept pages). The chunking function must use `RecursiveCharacterTextSplitter` from LangChain. The chunk size must be 256 tokens, with 38 tokens overlapping. After chunking, the metadata remains the same but with one additional field: `chunk_id`.
* **Expected output**: `ingest.py` consisting of two seperate functions: Document Injection, using appropriate loader per source type and outputing a list of dictionaries with correct metadata, and Document Chunking, using `RecursiveCharacterTextSplitter` with correct chunk size and chunk overlap configuration and outputing a list of chunks with `chunk_id` attached.
* **Verification method**: run on all 10 sources and verify that: *(a)* every chunk has non-empty `text` and all metadata keys present, *(b)* the `doc_type` value belongs to the approved set, *(c)* no chunk exceeds 256 tokens when re-measured with the `all-MiniLM-L6-v2 tokenizer`, *(d)*  consecutive chunks share overlapping text, and *(e)* each chunk is manually reviewed for any remaining navigation, cookie-banner, or menu content (e.g., "Skip to main content"). Any chunk > 256 tokens or missing field or leftover boilerplate should be treated as a failure.

**Milestone 4 — Embedding and retrieval:**
* **AI tool**: Claude
* **Input**: the embedding decision (`all-MiniLM-L6-v2` via `sentence-transformers`, 384-dim), the store decision (ChromaDB), the [Chunking Strategy](#chunking-strategy), and the [Retrieval Approach](#retrieval-approach), along with the system [Architecture](#architecture).
* **Prompt**: After chunking the documents, implement Embedding + Vector Store layer and Retrieval layer. Use `entence-transformers` (`all-MiniLM-L6-v2`) to embed chunks and these embed vectors on ChromaDB. Use Cosine Similarity Matching for vector retrieval. The retrieval function takes raw user query and the variable `k` with the default value of 5. From the user query, embed it using the previous embedding approach. The function outputs top K results, retrieved from ChromaDB.
* **Expected output**: `retriever.py` consisting of two seperate functions: Embedding + Vector Store, embedding input chunks using `entence-transformers` and storing them in ChromaDB, and Retrieval, doing cosine similarity search in ChromaDB and retuning the `k` most relevant chunks for a user query, with similarity score and original metadata.
* **Verification method**: verify that *(a)* `collection.count()` equals number of chunks produced in the Chunking stage, nothing dropped and *(b)* the stored vector dimension is **384**. Additionally, reload the collection from disk in a fresh process and confirm the count stays the same to prove persistence, not just an in-memory store. Finally, use a small set of "golden" queries with a known correct source and verify that *(a)* source appears in the top-k and *(b)* metadata comes back attached (needed downstream for citations). Then, deliberately query something off-domain and confirm the score floor returns few/no chunks instead of 5 weak ones.

**Milestone 5 — Generation and interface:**
* **AI tool**: Claude and ChatGPT
* **Input**: the [Evaluation Plan](#evaluation-plan), the [Anticipated Challenges](#anticipated-challenges), the grounded prompt, along with the system [Architecture](#architecture).
* **Prompt**: Next, implement Generation layer, using Groq's `llama-3.3-70b-versatile` as runtime generation model. This layer takes user query and the retrieved chunks as context, and inject the grounded prompt as provided. Finally, implement a UI for this application, using Gradio UI. This interface receives user prompt and displays LLM's answer. Plus, it should display suggested prompts and sub-topics from the documents. Note that the website must run locally and satisfy all the industry standards.
* **Expected output**: `generate.py` that formats retrieved chunks into a numbered context block, sends the grounded prompt to `llama-3.3-70b-versatile` via the Groq client, and returns the answer. `app.py` exposing `POST /` query (body `{query}` → `{answer, sources, retrieved_chunks}`) and a `GET /` serving one HTML page with a text box, a send button, an answer panel, and a visible suggested prompts and sub-topics. Sources from the LLM messages shown as clickable links (the `url` from metadata).
* **Verification method**: 
  - **Groundedness probe:** use ChatGPT to generate multiple prompts to pressure-test the system prompt against the grounded prompt, including asking a question whose answer is NOT in the corpus (e.g. "what's the free parking policy?") to confirm it triggers the "If absent, say so" path instead of hallucinating.
  - **Citation presence + format:** verify that every non-refusal answer ends with at least one `[source: title/url]`, and every cited source maps to a chunk that was actually retrieved (no fabricated URLs).
  - **No-leakage spot check:** verify a stated fact (a discount %, building name, pantry hours) appears verbatim in a retrieved chunk, proving it came from context, not the Llama model's training data.
  - **User interface check**: run the website locally, submit a query in the browser, and confirm the answer + clickable sources render without touching the terminal. Additionally, submit an empty query and confirm a graceful message, not a 500.