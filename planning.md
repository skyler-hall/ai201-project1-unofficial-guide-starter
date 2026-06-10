# Project 1 Planning: The Unofficial Guide

---

## Domain

FIU Computer Science professor reviews sourced from Rate My Professors. This knowledge is valuable because students making course registration decisions cannot find honest, student-generated opinions through official FIU channels. The university website lists professors but provides no feedback on teaching quality, grading style, or workload. Students rely on informal word-of-mouth that is hard to search systematically.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors | Tiana Solis reviews (53 ratings) | data/solis_reviews.txt |
| 2 | Rate My Professors | Ning Xie reviews (37 ratings) | data/xie_reviews.txt |
| 3 | Rate My Professors | Hafiz Mahmood Malik reviews (16 ratings) | data/malik_reviews.txt |
| 4 | Rate My Professors | Caryl Rahn reviews (179 ratings) | data/rahn_reviews.txt |
| 5 | Rate My Professors | Antonio Hernandez reviews (79 ratings) | data/hernandez_reviews.txt |
| 6 | Rate My Professors | Xudong He reviews (21 ratings) | data/he_reviews.txt |
| 7 | Rate My Professors | Kianoosh Boroojeni reviews (68 ratings) | data/boroojeni_reviews.txt |
| 8 | Rate My Professors | Jill Weiss reviews (354 ratings) | data/jweiss_reviews.txt |
| 9 | Rate My Professors | Patricia McDermott Wells reviews (149 ratings) | data/mcdermott_wells_reviews.txt |
| 10 | Rate My Professors | Richard Whittaker reviews (354 ratings) | data/whittaker_reviews.txt |

---

## Chunking Strategy

**Chunk size:** One review per chunk (approximately 100-250 characters of review text plus metadata). Each chunk includes the course number, date, quality/difficulty scores, review text, and tags.

**Overlap:** None. Each review is fully self-contained and does not depend on adjacent reviews for meaning.

**Reasoning:** The documents are structured with "---" delimiters separating individual student reviews. Splitting on this delimiter is the natural unit of meaning for this corpus. A single student review about a specific professor in a specific course is exactly the granularity a user query needs. Fixed-character chunking would be wrong here because it would split review text mid-sentence and lose the course/professor context attached to each review. No overlap is needed because reviews are independent opinions, not continuous prose where a fact might span a boundary.

---

## Retrieval Approach

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers. Runs locally with no API key and no rate limits.

**Top-k:** 5. Enough to surface opinions from multiple students about the same professor without flooding the LLM context with loosely related reviews.

**Production tradeoff reflection:** In a production deployment I would evaluate OpenAI text-embedding-3-small for higher accuracy at low cost per token, and consider a larger context window model if reviews were longer. Multilingual support would matter if serving non-English-speaking FIU students. Latency would be a concern with a local model at scale, making an API-based embedding service preferable. For this corpus, all-MiniLM-L6-v2 is sufficient since reviews are short and in English.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Is Professor Whittaker a good professor? | Yes, highly rated 4.8/5, 96% would take again, described as caring and passionate by multiple students |
| 2 | What do students say about Professor Rahn's grading? | Very negative overall, described as capricious and unfair, arbitrary point deductions, only 26% would take again |
| 3 | Does Professor Boroojeni give extra credit? | Yes, multiple reviews mention generous extra credit opportunities in COP3337 and CDA courses |
| 4 | What courses does Professor Hernandez teach? | COP3530, COP4534, CAP5738 are mentioned across reviews |
| 5 | Which professors at FIU CS are known for being easy graders? | Jill Weiss (1.7 difficulty, 97% would take again) and Whittaker (2.3 difficulty) are mentioned most as easy or manageable |

---

## Anticipated Challenges

1. Thin documents: Malik has only 16 reviews and He has 21. Queries specifically about these professors may return weak matches because there is less text for the embedding to match against, potentially pulling in reviews from other professors instead.

2. Short review chunks: Some reviews are only one or two sentences (e.g., "Just don't. Save yourself."). These extremely short chunks carry very little semantic signal and may not embed meaningfully, causing them to be retrieved for unrelated queries or missed for relevant ones.

---

## Architecture

```
Document Ingestion       Chunking                Embedding + Vector Store
(load .txt files   →    (split on "---"    →    (all-MiniLM-L6-v2 via
 from data/ folder)      one review =            sentence-transformers,
                         one chunk,              stored in ChromaDB
                         attach source           with source metadata)
                         metadata)                       ↓
                                                     Retrieval
                                                 (semantic search,
                                                  top-k=5, returns
                                                  chunks + sources)
                                                         ↓
                                                     Generation
                                                 (Groq llama-3.3-70b,
                                                  grounded prompt,
                                                  source attribution)
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
I will give Claude the Chunking Strategy section and a sample .txt file and ask it to implement load_documents() that reads all .txt files from data/ and chunk_documents() that splits on "---" delimiters and tags each chunk with its source filename. I will verify by printing 5 random chunks and confirming they are complete reviews with course metadata intact.

**Milestone 4 — Embedding and retrieval:**
I will give Claude the Retrieval Approach section and Architecture diagram and ask it to implement embed_and_store() using all-MiniLM-L6-v2 and ChromaDB, and retrieve(query, k=5) that returns top-k chunks with source filenames. I will verify by running 3 evaluation questions and checking returned chunks are visibly relevant.

**Milestone 5 — Generation and interface:**
I will give Claude the full planning.md and ask it to implement generate_answer(query) that calls retrieve(), builds a grounded prompt, calls Groq, and returns the answer with source attribution. I will also ask it to wrap this in a Gradio UI with question input, answer output, and sources output fields.