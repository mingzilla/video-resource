# PDF Processing Pipeline: PDF to JSON

- extract -> transform
- e: txt, img
- t: llm, code

```text
Final Pipeline:
                                                        EXTRACT | TRANSFORM
                                                                |
[PDF] -> [pdftotext] -> [validate] --+-> [valid] ------------------> [sh01_txt_parser.py] ----> [json]
         (CPU)                       |                          |
                                     +-> [invalid] -> [Marker] ----> [sh01_marker_parser.py] -> [json]       
                                                      (GPU)     |
                                                                |
```

## Table of Contents

1. Process: [PDF Text Extraction (Step 1)](#1-pdf-text-extraction-step-1)
2. Process: [Fallback Pipeline Design](#2-fallback-pipeline-design)
3. Process: [Cloud Parallel Processing](#3-cloud-parallel-processing)
4. Marker: [Marker Optimization & GPU Utilization](#4-marker-optimization--gpu-utilization)
5. Marker: [Gemini Flash + --use_llm](#5-gemini-flash---use_llm)
6. Transformation: [Text Transformation (Step 2)](#6-text-transformation-step-2)
7. [Final Architecture](#7-final-architecture)

---

## 1. PDF Text Extraction (Step 1)

### What

Tools and strategies for extracting text from SH01 PDFs (digital + scanned).

### Options

```text
(A) pdftotext (Poppler)   -> validate -> [END]
(B) Marker (GPU)          -> output   -> [END]
(C) pdftotext             -> validate -> if fail -> Marker -> [END]
(D) Tesseract (pdf2image) -> validate -> [END]
```

### Decisions

| #   | Pros                          | Cons                              | Win |
|-----|-------------------------------|-----------------------------------|-----|
| (A) | Fast (ms), free               | Fails on scanned/complex          |     |
| (B) | Handles complex, accurate     | Slow (15s/doc), GPU heavy         |     |
| (C) | Fast path + accurate fallback | Two tools to maintain             | Y   |
| (D) | Simple, CPU-only              | Lower accuracy for financial data |     |

**Why (C):** `pdftotext` is fast and sufficient for ~80% of SH01s (digital). Marker catches the rest (scanned, complex layouts). No pre-detection step needed — validation alone determines fallback.

### Reminder

- No need to pre-detect "text vs image" — just run `pdftotext` and validate output
- Marker fallback only triggers when validation fails
- For investment data (penny accuracy), Tesseract is too risky (1-5% error rate)

---

## 2. Fallback Pipeline Design

### What

The specific flow of extraction without pre-detection.

### Options

```text
(A) [pdftotext] -> [END]

(B) [detect text?] -> YES -> [pdftotext] -> [END]
                       |
                      NO  -> [Marker]    -> [END]

(C) [pdftotext] -> [validate] -> [valid?] -> [END]
                       |              |
                    [invalid]         |
                       |              |
                    [Marker] ---------+
```

### Decisions

| #   | Pros                                     | Cons                                       | Win |
|-----|------------------------------------------|--------------------------------------------|-----|
| (A) | Simple                                   | Fails silently on scanned PDFs             |     |
| (B) | Explicit detection                       | Detection step is guesswork, adds overhead |     |
| (C) | One validation rule catches all failures | Requires good validation logic             | Y   |

**Why (C):** Validation is the only signal that matters — output quality, not source format. Detection upfront adds complexity without benefit.

### Reminder

- Validation rules already exist (sanity checks for numbers, keywords)
- If `pdftotext` output passes validation, keep it
- If validation fails, route to Marker — regardless of whether PDF was "text" or "image"

---

## 3. Cloud Parallel Processing

### What

Running Marker across multiple cloud GPUs to reduce batch processing time (120k docs, ~20 days locally).

### Options

```text
(A) Single beast machine (4x A100) -> [run] -> [END]

(B) Multiple single-GPU instances -> [split files] -> [run parallel] -> [merge] -> [END]

(C) Serverless GPU (Modal, RunPod) -> [auto-scale] -> [END]
```

### Decisions

| #   | Pros                                | Cons                                    | Win |
|-----|-------------------------------------|-----------------------------------------|-----|
| (A) | One machine to manage               | 10x more expensive than slower machines |     |
| (B) | Cost-effective, near-linear speedup | Manual file splitting, orchestration    | Y   |
| (C) | Hands-off scaling                   | Setup complexity, vendor lock-in        |     |

**Why (B):** Cheaper than one beast machine. Achieves same throughput with many cheaper GPUs. Simple to implement with folder splitting.

### Reminder

- 10x slower machines can be 10x cheaper — cost/performance favors many small GPUs
- Use shared storage (EFS) to avoid manual file splitting: `--chunk_idx 0 --num_chunks 4`
- Expected: 120k docs -> ~4-5 days with 4 cloud GPUs, ~1-2 days with 10

---

## 4. Marker Optimization & GPU Utilization

**Marker processing steps :**

| Step                 | What Marker Does Locally                                         | Why It Matters                      |
|----------------------|------------------------------------------------------------------|-------------------------------------|
| **Layout detection** | Runs Surya layout model to identify text blocks, tables, figures | GPU intensive                       |
| **OCR fallback**     | Uses Tesseract/Surya OCR for image-only pages                    | CPU/GPU intensive                   |
| **Table extraction** | Identifies table boundaries and structure                        | Must be done locally                |
| **Chunking for LLM** | Splits large tables into `max_rows_per_batch: 60`                | Each chunk becomes a Gemini request |
| **Postprocessing**   | Merges Gemini responses back into coherent markdown              | CPU work                            |

### What

Tuning Marker for maximum throughput on an RTX 5090 laptop (150W power limit).

### Options

```text
(A) --workers 1 (current)

(B) --workers 4

(C) --workers 8

(D) --workers 4 --batch_multiplier 2
```

### Decisions

| #   | Pros                                | Cons                                         | Win            |
|-----|-------------------------------------|----------------------------------------------|----------------|
| (A) | Stable, 79% GPU util, power-limited | Single-threaded                              | Y (for laptop) |
| (B) | More parallelism                    | Power divided, no throughput gain            |                |
| (C) | Even more parallel                  | Contention, likely slower                    |                |
| (D) | Larger batches                      | VRAM headroom exists, but power still capped |                |

**Why (A):** `nvidia-smi` shows power at 146W/150W — the laptop's power limit is the real bottleneck, not compute. Adding workers doesn't increase total power budget; it just divides same power among more tasks. Cloud GPU (unlimited power) is the only path to speedup.

### Reminder

- Current: 79% GPU-Util, 8.7GB/24GB VRAM, 146W/150W
- Power limit = ceiling. More workers = more context switching = lower per-worker efficiency
- Cloud GPU (e.g., A100) with 300-575W = 3-5x speedup
- For laptop: keep `--workers 1`

---

## 5. Gemini Flash + --use_llm

### What

Using Marker's `--use_llm` flag with Gemini Flash to improve accuracy (at cost of speed).

### Options

```text
(A) Marker alone (no LLM)

(B) Marker --use_llm with Gemini

(C) Marker + separate Gemini API parser (sh01_marker_with_llm_parser.py)
```

### Decisions

| #   | Pros                                   | Cons                                                | Win           |
|-----|----------------------------------------|-----------------------------------------------------|---------------|
| (A) | Fast, deterministic, free              | Accuracy ceiling                                    | Y (for speed) |
| (B) | Higher accuracy (tables, forms)        | Rate limits (429 errors), slower, non-deterministic |               |
| (C) | Decoupled, can scale Gemini separately | Two parsers to maintain                             |               |

**Why (A) for speed, (B) only if accuracy issues:** Marker's `--use_llm` still does layout/OCR locally — only table refinement hits Gemini. Rate limits (15-60 RPM) mean even with parallel workers, throughput drops. Your parser `sh01_marker_parser.py` expects deterministic output; Gemini output would break it (would need separate parser).

### Reminder

- Marker sends PDF pages as WEBP images to Gemini internally — no Files API needed
- Each Gemini call adds latency (seconds per table chunk)
- `--use_llm` does NOT speed up processing — it slows it down (adds API wait time)
- Only use if current accuracy is unacceptable
- If used, write `sh01_marker_with_llm_parser.py` and route based on situation

---

## 6. Text Transformation (Step 2)

### What

Converting extracted text into structured `SH01Parsed` dataclass.

### Options

```text
(A) Existing sh01_marker_parser.py (deterministic, regex-based)

(B) DeepSeek API (LLM)

(C) Local LLM (Ollama, Llama)

(D) Hybrid: parser for fields + LLM for fuzzy correction
```

### Decisions

| #   | Pros                                           | Cons                                       | Win |
|-----|------------------------------------------------|--------------------------------------------|-----|
| (A) | Deterministic, auditable, free, penny-accurate | Only works for SH01                        | Y   |
| (B) | Flexible, handles variants                     | Cost, latency, non-deterministic, overkill |     |
| (C) | Offline, private                               | Slower, setup complexity                   |     |
| (D) | Best of both                                   | Two systems to maintain                    |     |

**Why (A):** For SH01-only processing, deterministic parser is faster, cheaper, and more reliable than LLM. No "hallucination" risk for penny data.

### Reminder

- Parser already handles: wrapped class names, value-before-label, inline blobs, split words
- Validation against Section 4 totals could be added (medium priority)
- Do NOT use LLM for Step 2 unless processing novel/unseen document types

---

## 7. Final Architecture

### What

Complete end-to-end pipeline for SH01 processing (120k docs, investment data, penny accuracy).

### Options

```text
(1) Local laptop (RTX 5090, 150W) -> 20 days

(2) Cloud GPUs (4 instances) -> 4-5 days

(3) Cloud GPUs (10 instances) -> 1-2 days

(4) Cloud GPUs + --use_llm -> slower, more accurate
```

### Decisions

| #   | Pros                         | Cons                           | Win                  |
|-----|------------------------------|--------------------------------|----------------------|
| (1) | Free, already running        | 20 days                        |                      |
| (2) | Cost-effective, 4-5x speedup | $                              | Y (if budget allows) |
| (3) | Fastest (1-2 days)           | $$                             |                      |
| (4) | Highest accuracy             | Slower, API costs, rate limits |                      |

**Why (2) as recommended next step:** Multiple smaller cloud GPUs is cheaper than one beast machine. Your laptop is power-limited — cloud removes that bottleneck. No code changes needed (just upload zip, run batch). Avoid `--use_llm` unless accuracy issues emerge.
