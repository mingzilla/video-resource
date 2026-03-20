# Data Generation Strategy: Simplified

## Goal

Produce a high-quality labelled dataset for fine-tuning `llama3.2:3b`
as-is (no teacher fine-tuning) with frontier model verification.

---

## Why No Teacher Training

- qwen2.5:32b zero-shot is already capable enough — Kimi's correction rate is expected to be low
- Frontier model verification is required regardless, so teacher training only reduces API cost at scale
- For the volume needed (~2000–3000 records), API cost is negligible vs the effort of Phase 1
- The valuable asset is the verified dataset, not a fine-tuned teacher model

---

## Data Creation

```
   user + system (full template)
        │
        ▼
  ┌─────────────┐     assistent            ┌──────────────────────┐
  │  Kimi K2.5  │ ───────────────────────► │ Claude / Deepseek    │
  │  (corrects) │                          │ (verifies correction)│
  └─────────────┘                          └──────────────────────┘
                                                      | agree?
                                                      +-- yes -> keep training record
                                                      +-- no  -> option 1: important record -> further verification
                                                              -> option 2: says result wrong -> ignore record
```

---

## Student Training Loop

| Cycle | input (created by qwen2.5:32b + verified) | model to fine-tune  | result          | stable? |
|-------|-------------------------------------------|---------------------|-----------------|---------|
| 1     | 500 perfect summaries                     | llama3.2:3b         | llama3.2:3b v+1 | check   |
| 2     | 1000 perfect summaries                    | llama3.2:3b v+1     | llama3.2:3b v+2 | check   |
| 3     | 1500 perfect summaries                    | llama3.2:3b v+2     | llama3.2:3b v+3 | check   |
| ...   | (not enough perfect summaries)            |                     | ...             | ...     |
| n     |                                           | llama3.2:3b v+(n-1) | llama3.2:3b v+n | stop    |

**Not enough perfect summaries:** run more webtexts through qwen2.5:32b + Step 2 verification to grow the dataset.

**Stable:** further training cycles no longer improve output quality. Stop.

The verified dataset is a valuable asset — reusable for future student models.
