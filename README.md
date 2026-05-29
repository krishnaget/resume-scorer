# Day 5 — Résumé Scorer Streamlit

**Live URL:** https://resume-scorer-dckby23cf4nthpc7ehz4c3.streamlit.app/  
**Code:** [app.py](app.py)  
**Acceptance Log:** [acceptance_log.md](acceptance_log.md)

## Tools Used

- Continue.dev
- Gemini 2.5 Flash
- Streamlit
- GitHub
- Streamlit Community Cloud

## Features

- Résumé vs JD fit score
- Rationale
- Missing skills
- Suggestions
- 4-axis score breakdown chart
- Free learning resources for missing skills

## Reflection

- This is an AI-assisted prototype built using Continue.dev and Gemini.
- To productionise, I would add better error handling, caching, rate limits, and authentication.
- Continue.dev helped scaffold the UI quickly, but manual review was needed for prompt correctness and deployment fixes.

---

## Day 5 Lab 5B — Hugging Face Pulls

### Models tested
- `facebook/bart-large-mnli` — zero-shot classification
- `distilbert-base-uncased-finetuned-sst-2-english` — sentiment

### Timing comparison

| | min | avg | Notes |
|---|-----|-----|-------|
| Local in Colab | 0.85s | 0.89s | Download: 90s on first run |

### When to use each

1. **API:** for low-volume, occasional calls. Avoids download. Cold-start risk on first call after idle.
2. **Local:** for batch processing 100+ items, where you want predictable latency and don't pay per call.
3. **Production rule of thumb:** if your usage exceeds the API free tier, self-host. Otherwise API.




---

## Day 6 Lab 6A — Gemini Structured Output

### What it does
Extracts structured JSON from raw resume text using Gemini + Pydantic schema validation.

### Models used
- `gemini-2.5-flash` — structured JSON extraction with response_schema

### Errors handled

1. **Markdown fence wrapping** — retry prompt forces raw JSON output.
2. **Missing optional fields** — `Optional[str] = None` in Pydantic handles null phone numbers.
3. **Empty / whitespace input** — input validation blocks requests shorter than 50 chars.

### Hallucination finding
Gemini invented a complete fake resume "John Doe" from an empty string input. Fix: validate input before sending to LLM — minimum length and email pattern check.

### Result
5/5 resumes extracted successfully with correct name, skills, education and experience fields.





---

## Day 6 — Capstone Sprint 1: PlacementDataProcessor

### Engineer Answer

1. **PROBLEM** — JDs from company websites are messy text — placement cells need structured data to filter ("which JDs want Java + CGPA 7+?"). Manual extraction is unscalable for 50+ JDs.

2. **ARCHITECTURE** — JD URL → BeautifulSoup scraper (extract clean text) → Gemini structured-output call (response_schema=JD Pydantic) → JSON Lines file. Validation at each step; retry on schema fail.

3. **TRADE-OFFS** —
   - Cost: free Gemini ~1 JD/sec on average; ~30K tokens/day quota → ~5K JDs/day.
   - Accuracy: Pydantic catches schema violations but not semantic errors.
   - Latency: ~2-5s per JD (Gemini call dominant).
   - Complexity: scraping fragile — some Amazon URLs returned 404 or encoding errors. Fallback to alternate URLs was needed.

4. **SCALE** —
   - 10 JDs/day: trivial. Today's lab.
   - 100 JDs/day: still in free quota. Add overnight batch + sleep between calls.
   - 10K JDs/day: free tier breaks. Move to paid Gemini OR self-host an open model.

5. **INTERVIEW ANSWER** — "I built a structured-output pipeline that turns scraped Amazon JDs into clean filterable JSON, using free Gemini and Pydantic. Schema-first design with retry-on-failure made it production-shaped on a free-tier API."

### Files
- `Day6_PlacementProcessor.ipynb` — the notebook
- `jds.jsonl` — output of this sprint, input for Day 7 RAG

### Pair: Naveen




---

## Day 7 Lab 7A — ChromaDB Hello-World

- Embedded 7 CSE Sem 5 paragraphs with all-MiniLM-L6-v2 (384-dim, free, local)
- Indexed in persistent ChromaDB collection `hello_syllabus`
- Ran 3 semantic queries — observed:
  - "operating system processes" → dist 0.713 → correct match (topic in corpus)
  - "dynamic programming" → dist 1.464 → wrong match (topic NOT in corpus)
  - "machine learning topics" → dist 1.300 → wrong match (topic NOT in corpus)
- Plotted PCA 2D — visible clusters by subject area
- Added food outlier (butter chicken) — landed visibly far from all syllabus paragraphs

**Reflection:** Semantic search returns nearest, not exact. High distance = low relevance. RAG must enforce citations to catch out-of-corpus queries — if the answer isn't in the corpus, the system should say "I don't know" not hallucinate.





---

## Day 7 — Capstone Sprint 2: PlacementKnowledgeRAG

### Engineer Answer

1. **PROBLEM** — Frontier LLMs do not know your private data (JDs, syllabi). Students need a chatbot that answers from YOUR placement corpus, with citations they can verify.

2. **ARCHITECTURE** — 5-box RAG: embed (MiniLM 384-dim) → index (ChromaDB persistent collection with metadata) → retrieve (top-4 cosine similarity) → augment (citation-enforcing prompt) → generate (Gemini 2.5 Flash).

3. **TRADE-OFFS** —
   - Cost: free (MiniLM local + Gemini quota).
   - Accuracy: top-4 retrieval works well for in-corpus queries.
   - Latency: ~1-2s retrieval + 2-5s Gemini.
   - Complexity: chunking strategy needs tuning per corpus.
   - Caveat: refuses out-of-corpus queries only when prompt strictly enforces "do not guess".

4. **SCALE** —
   - 9 docs (today): trivial. ChromaDB returns in <100ms.
   - 5K docs: still fine on one machine.
   - 1M docs: need HNSW indexing or move to Pinecone/Weaviate.

5. **INTERVIEW ANSWER** — "I built a citation-enforcing RAG over placement docs (JDs + syllabi) using free MiniLM embeddings, ChromaDB, and Gemini. The system either cites a specific chunk or refuses — no hallucinated answers."

### 5 cited Q&A pairs

| # | Question | Answer (excerpt) | Sources cited |
|---|----------|------------------|---------------|
| 1 | Which companies want Python skills? | Razorpay, Accenture, Tech Mahindra, Cognizant | jd_extra, jd_final |
| 2 | What are the Sem 5 OS topics? | Process management, threads, scheduling, deadlocks... | cse_sem5_0 |
| 3 | Which jobs are in Hyderabad? | Amazon, TCS, Deloitte, Accenture | jd_1, jd_2, jd_3, jd_4 |
| 4 | Which companies have highest package? | PayTM — highest package | jd_3 |
| 5 | What is TCS Codevita? | I do not know | (not in corpus) |

### Collection stats
- Total documents: 50
- JDs indexed: 25 (5 Amazon + 20 extra companies)
- Syllabus chunks: 25 (CSE, Mech, ECE, Civil, IT, AIDS, Math, Physics, Management)







---

## Day 10 Lab 10A — Hello-CrewAI

### Goal
Built a 2-agent CrewAI system that generates a 1-page TCS Digital placement preparation brief.

### Agents
1. **Placement Researcher** — prepares factual placement notes with 5 sections.
2. **Placement Brief Writer** — converts notes into a student-friendly markdown brief.

### Workflow
Researcher Agent → Writer Agent → Final Markdown Brief

### Files Generated
- `Day10_MultiAgent.ipynb` — the notebook
- `tcs_digital_brief.md` — the generated TCS Digital placement brief
- `day10_lab10a_transcript.txt` — full agent execution transcript

### Reflection
1. The handoff between agents is the design quality — Researcher output becomes Writer input.
2. `expected_output` is the contract between agents — vague output means poor next agent input.
3. Verbose mode helps debug multi-agent workflows — you can see exactly what each agent did.
4. 503 error from Gemini is not code failure — it is cloud-resource limitation. Retry fixes it.





---

## Day 10 Sprint 5 — Placement Prep Crew (4-agent)

### Goal
Built a 4-agent CrewAI placement preparation workflow processing 3 student profiles.

### Agents
1. **Placement Researcher** — searches RAG knowledge base for company requirements
2. **Mock Interviewer** — generates 10 personalized interview questions
3. **Answer Coach** — creates strong sample answer for question 3
4. **Progress Tracker** — generates JSON progress summary

### Workflow
Researcher → Interviewer → Coach → Tracker → JSON Summary

### Students Processed
| Student | Target | Status |
|---------|--------|--------|
| Ravi Kumar (CSE) | TCS Digital | ✅ Completed |
| Sneha Reddy (ECE) | Cognizant | ✅ Completed |
| Arun Pillai (IT) | Amazon | ⚠️ Quota hit |

### Files Generated
- `Day10_MultiAgent.ipynb` — the notebook
- `day10_sprint5_transcripts.json` — JSON transcripts for all 3 students
- `day10_sprint5_report.md` — markdown report

### Reflection
1. 4-agent sequential pipeline works — each agent passes output to next.
2. RAG tool integrated into Researcher agent — searches real placement data.
3. Quota error on 3rd student — free tier limit is 5 requests/minute. Fix: add sleep() between crew runs.
4. Transcript IS the architecture — read it to understand what each agent did.






## Day 11 Lab 11A — Ollama Offline + Hybrid Fallback

### Completed
- ✅ Ollama installed locally
- ✅ llama3.2 model downloaded
- ✅ Offline AI tested after Wi-Fi disconnect
- ✅ Gemini → Groq → Ollama fallback chain implemented
- ✅ Force-failure testing completed
- ✅ Local fallback verified

### Demo Proof
- Wi-Fi disconnect demo recorded
- Fallback chain outputs captured

### Reflection
1. First inference is slow because the model loads into RAM.
2. Ollama is useful for privacy, offline access, and zero per-call cost.
3. Production AI systems should not depend on a single provider.

### Architecture

Gemini Cloud → Groq Cloud → Ollama Local