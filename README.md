# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

Student reviews of CS professors at Florida International University, sourced from Rate My Professors. This knowledge is valuable because official FIU channels provide no student feedback on teaching quality, grading style, exam difficulty, or workload. The university website lists professors but gives no indication of how they actually teach. Students rely on scattered word-of-mouth that is hard to search systematically. This system makes that informal knowledge queryable.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors | Text reviews | data/solis_reviews.txt |
| 2 | Rate My Professors | Text reviews | data/xie_reviews.txt |
| 3 | Rate My Professors | Text reviews | data/malik_reviews.txt |
| 4 | Rate My Professors | Text reviews | data/rahn_reviews.txt |
| 5 | Rate My Professors | Text reviews | data/hernandez_reviews.txt |
| 6 | Rate My Professors | Text reviews | data/he_reviews.txt |
| 7 | Rate My Professors | Text reviews | data/boroojeni_reviews.txt |
| 8 | Rate My Professors | Text reviews | data/jweiss_reviews.txt |
| 9 | Rate My Professors | Text reviews | data/mcdermott_wells_reviews.txt |
| 10 | Rate My Professors | Text reviews | data/whittaker_reviews.txt |
---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** One review per chunk (~100-250 characters of review text plus metadata including course number, date, quality/difficulty scores, and tags.

**Overlap:** None. Each review is self-contained and does not depend on adjacent reviews for meaning.

**Why these choices fit your documents:** The documents are structured with --- delimiters separating individual reviews. Splitting on this delimiter is the natural unit of meaning for this corpus. Fixed-character chunking would split review text mid-sentence and discard the professor and course context attached to each review. No overlap is needed because reviews are independent opinions, not continuous prose where a fact might span a chunk boundary.

**Final chunk count:** 60 chunks across 10 documents.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2 via sentence-transformers. Runs locally with no API key and no rate limits.

**Production tradeoff reflection:** In a production deployment I would evaluate OpenAI text-embedding-3-small for higher accuracy at low cost per token. Multilingual support would matter if serving non-English-speaking FIU students. Latency would be a concern with a local model at scale, making an API-based embedding service preferable. Context length is not a limiting factor here since reviews are short, but would matter if the corpus included longer documents like syllabi. For this corpus all-MiniLM-L6-v2 is sufficient.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
"You are an assistant that helps FIU students learn about CS professors based on student reviews. Answer the question using ONLY the information provided in the documents below. Do not use any outside knowledge. If the documents do not contain enough information to answer the question, say 'I don't have enough information in the reviews to answer that.'"

**How source attribution is surfaced in the response:** Each retrieved chunk is labeled with its source filename before being passed to the LLM as context. After generation, the unique source filenames from all retrieved chunks are collected programmatically and displayed in the UI under "Retrieved from." Attribution is guaranteed by the pipeline structure, not left to the LLM.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Is Professor Whittaker a good professor? | Yes, 4.8/5, 96% would take again, caring and passionate | Confirmed positive with 4.8/5 and 96%, noted some negative outliers | Relevant | Accurate |
| 2 | What do students say about Professor Rahn's grading? | Very negative, capricious, unfair, 26% would take again | Described as mixed — capricious in one review, forgiving in another | Relevant | Accurate |
| 3 | Does Professor Boroojeni give extra credit? | Yes, multiple reviews mention generous extra credit | Confirmed yes, cited two specific COP3337 reviews | Relevant | Accurate |
| 4 | What courses does Professor Hernandez teach? | COP3530, COP4534, CAP5738 | Only identified CAP5738, missed COP3530 and COP4534 | Partially relevant | Partially accurate |
| 5 | Which FIU CS professors are known for being easy graders? | Jill Weiss (1.7 difficulty) and Whittaker (2.3 difficulty) | Identified Whittaker but did not surface Jill Weiss | Partially relevant | Partially accurate |
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

**Question that failed:** What courses does Professor Hernandez teach?

**What the system returned:** Only identified CAP5738 and said it did not have enough information about other courses. COP3530 and COP4534 are in the data but were not retrieved.

**Root cause (tied to a specific pipeline stage):** This is a retrieval failure. The query is semantically focused on course names. The top-k=5 results did not include the COP3530 or COP4534 chunks because those reviews focused on teaching style and workload rather than course identity, so they ranked lower in semantic similarity. Only one Hernandez chunk that mentioned CAP5738 explicitly made it into the top 5.

**What you would change to fix it:** Increase top-k from 5 to 8-10 for queries asking about factual attributes like course lists. Alternatively, add a metadata filter that forces retrieval to only return chunks from a specific professor's file when that professor's name appears in the query.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Writing the chunking strategy in planning.md before touching any code forced a deliberate decision about chunk boundaries. Because the spec identified the --- delimiter as the natural split point, the chunking implementation was straightforward and produced clean self-contained chunks on the first try. Without the spec, a default character-based chunker would have been the path of least resistance and would have produced worse retrieval results.

**One way your implementation diverged from the spec, and why:** The spec anticipated chunk sizes of 100-250 characters. In practice some chunks are much shorter — a few reviews are only one or two sentences like "Just don't. Save yourself." These very short chunks carry little semantic signal. This was identified as an anticipated challenge in planning.md but not pre-solved. A future fix would filter out chunks shorter than 50 characters or merge them with a neighboring review.

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

**Instance 1**
- *What I gave the AI:* The Chunking Strategy section from planning.md and a sample .txt file showing the --- delimiter structure
- *What it produced:* A complete ingest.py with load_documents() and chunk_documents() functions that split on the delimiter and attached source metadata to each chunk
- *What I changed or overrode:* The generated code used a minimum chunk length filter of 0 characters. I changed this to 50 characters to filter out empty strings and near-empty chunks that would embed poorly

**Instance 2**
- *What I gave the AI:* The full planning.md including the grounding requirement and Retrieval Approach section
- *What it produced:* A complete query.py with a grounded prompt template, Groq API integration, and source attribution logic
- *What I changed or overrode:* The original prompt said "try to use only the provided documents." I directed Claude to strengthen the grounding instruction to "answer using ONLY the information provided" and added the explicit fallback instruction to say "I don't have enough information" rather than guessing
