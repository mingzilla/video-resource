# Batch Completion Strategy for 2M LLM Records

## Table of Contents

- [Problem](#problem)
- [Priority Batch Order](#priority-batch-order)
- [Pipeline Flow](#pipeline-flow)
- [Merge Pattern](#merge-pattern)

---

## Problem

```text
2M company records
  |
  +-- LLM: ~0.75s/item local
  |
  +-- Full run: ~17 days end-to-end
  |
  +-- Cannot prioritise without a batch strategy
```

- Not all companies have equal business value
- Cannot wait 17 days for highest-value companies
- Solution: process in priority order, accumulate into one merged output

---

## Priority Batch Order

```text
RTIC companies (~100k)
  |-- highest business value
  |-- ~3 days processing
  |
Group Structure companies (~100k)
  |-- from remaining (excl. already processed)
  |
Top 100k by employee count
  |-- from remaining (excl. already processed)
  |-- repeatable: run again for next 100k until coverage is sufficient
  |
Sanity check + fill gaps
  |-- verify coverage, patch missing records
```

---

## Pipeline Flow

```text
MySQL/rtic.duckdb ──► step1a: copy rtic companies
                              |
Archive.parquet   ──► step1b: clean web text
                              |
                              v
ClassifiedCompanies ──► step2_a: filter rtic           ──► step3_a: LLM (rtic)  ────────────────────────+
ClassifiedCompanies ──► step2_b: filter group          ──► step3_b: LLM (group) ────────────────────────+──► step3_z: merged
ClassifiedCompanies ──► step2_c: filter top 100k [rep] ──► step3_c_01: LLM (top 100k) [__in_progress]   |      |
                          ^                                        |                                    |      |
                          |                                step3_c_02: merge ───────────────────────────+      |
                          |                                        |                                           |
                          +── step3_c_03: rename __in_progress → __01/__02/…                                   |
                                                                                                               |
                                                                                                   step4: feature extraction
                                                                                                               |
                                                                                                   step5: embeddings
```

- Each step2 filter **excludes** companies already in step3_z
- step2_c + step3_c are repeatable — run again for the next 100k batch
- Only step2_c/step3_c outputs use `__in_progress` naming; step3_c_03 renames them to `__01`, `__02`, … before the next loop

---

## Merge Pattern

```text
step3_a ──+
step3_b ──+──► step3_z  (accumulated merge, grows with each batch run)
step3_c ──+
```

| Run | What gets added to step3_z                                    |
|-----|---------------------------------------------------------------|
| 1   | RTIC companies (~100k)                                        |
| 2   | Group structure (~100k)                                       |
| 3+  | Top 100k by employee count (repeat until sufficient coverage) |
