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