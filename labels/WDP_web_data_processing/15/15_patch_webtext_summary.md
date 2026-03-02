# Patch Updated Companies Webtext Summary

Applies a patch to the previous pipeline outputs whenever a new Archive release is available.
Frequency is not fixed - can be monthly, fortnightly, or ad hoc.

## Challenges and Solution

```text
   old.parquet           new.parquet  
 +---------------+     +---------------+
 | text          | --- |               |  # deleted
 |               | --- | text          |  # added
 | text < 1.5k   | -?- | text < 1.5k   |  # check length
 | text > 50k    | -?- | text > 50k    |  # compare content
 +---------------+     +---------------+

Challenge:
- compare content is slow
- ram limitation -- need to copy to wsl directory
- content may not affect summary - e.g. news

Tips:
- make sure file names are consistent, use scripts to set up input and output
```

## Prerequisites

Everything below must be in place before starting the pipeline.

### Data files

| Action                                                                    | Detail                                             |
|---------------------------------------------------------------------------|----------------------------------------------------|
| Rename `_release/_app_data/Archive.parquet` → `Archive__previous.parquet` | Preserves previous archive for diff comparison     |
| Place new release as `_release/_app_data/Archive.parquet`                 | This is what the pipeline reads as the new version |
| Confirm `_release/_app_data/Companies.duckdb` is up to date               | Used in step2 to filter active companies           |

### _previous/ directory

Run one of these scripts to populate `_output/_previous/` before step6:

| Script                                    | When to use                                             |
|-------------------------------------------|---------------------------------------------------------|
| `prepare_previous__from_p001__initial.sh` | First time only — copies from p001 output               |
| `prepare_previous__from_p002__update.sh`  | Every subsequent run — copies from p002 step_06 outputs |

### Services

| Service                            | Required for        | How to start       |
|------------------------------------|---------------------|--------------------|
| Ollama + llama3.2:3b on port 40201 | step3 LLM summaries | start before step3 |
| Docker with GPU                    | step5 embeddings    | start before step5 |

## Inputs

| File                                           | Description                                                 |
|------------------------------------------------|-------------------------------------------------------------|
| `_release/_app_data/Archive__previous.parquet` | Previous archive (2 columns: CompanyNumber, CompanyWebText) |
| `_release/_app_data/Archive.parquet`           | New archive release (same schema)                           |
| `_release/_app_data/Companies.duckdb`          | Source of `Active` flag                                     |

## Copy Files to /tmp

To make sure ram and space is enough, make sure files in WSL, not mixing WSL and Windows

```shell
    echo "Copying source parquets to Linux filesystem..."
    TMP_OLD_ARCHIVE="/tmp/duckdb_work/old_archive_$$.parquet"
    TMP_NEW_ARCHIVE="/tmp/duckdb_work/new_archive_$$.parquet"
    cp "${OLD_ARCHIVE_PATH}" "${TMP_OLD_ARCHIVE}"
    cp "${NEW_ARCHIVE_PATH}" "${TMP_NEW_ARCHIVE}"
    echo "Copy complete."

    cleanup() {
        rm -f "${TMP_OLD_ARCHIVE}" "${TMP_NEW_ARCHIVE}" "${TEMP_SQL}"
    }
    trap cleanup EXIT
```

## Pipeline Flow

```
Archive__previous.parquet  ──┐
                             ├──► step0 run1: classify by length
          Archive.parquet  ──┘              | + output: step_00a__archive_diff.duckdb (4 tables)
                                            |
                                            ▼
                                  step0 run2: text compare on unknown set (~278k, not full 1M+)
                                            | + output: step_00a__archive_diff.duckdb (+2 tables)
                                            | + output: step_00a__archive_diff__full__summary.csv
                                            |
                                            ▼
                                  step0 run3: create parquet input (added + updated companies only)
                                            | + output: step_00b__archive_diff.parquet
                                            |
                                            ▼
                                  step1: clean web text
                                            | + output: step_01__cleaned_web_text__parallel.duckdb
                                            |
                                            ▼
ClassifiedCompaniesRelational ──► step2: filter active companies
                                            | + output: step_02__companies__clean_text.parquet
                                            |
                                            ▼
                                  step3: LLM summaries
                                            | + output: step_03__companies__16k_chars__llama3pt2_3b.duckdb
                                            |
                                            ▼
                                  step4: feature extraction
                                            | + output: step_04__companies__16k_chars__llama3pt2_3b__features__diffs.duckdb
                                            |
                                            ▼
                                  step5: embeddings (full/s/m/l)
                                            | + output: step_05__companies__{variant}__nomic_64d_embeddings__diffs.duckdb
                                            |
          _previous/ ───────────────────────+
                                            ▼
                                  step6: merge with previous
                                            | + output: step_06__companies__{variant}__nomic_64d_embeddings.duckdb
                                            |           step_06__companies__16k_chars__llama3pt2_3b__features.duckdb
```

## step0 - Archive Diff Logic

### Why truncation at `truncation_chars__stable_content`?

`Archive.parquet` contains web text derived from `company_description + first_50k_chars` of scraped pages.
Most of this text is dynamic — blog posts, news, seasonal content — and changes frequently without affecting
what a company actually does. Only the first portion of the text (company description, core services, trading
name) is stable enough to indicate a genuine website change worth regenerating a summary for.

`truncation_chars__stable_content` (default: 3000) defines this stable content boundary. "Truncated" in all
table names means "text reaches or exceeds this boundary" — not the 50k archive limit. Companies whose text
is fully within this boundary can be compared by length alone. Companies whose text extends beyond it require
an explicit text compare on `LEFT(text, truncation_chars__stable_content)` to avoid treating dynamic content
changes as meaningful updates.

**SQL run 1 — classify by length** (reads CompanyNumber + LENGTH only, no text in memory):

| old_len            | new_len            | Table                                            | LLM reprocess?   |
|--------------------|--------------------|--------------------------------------------------|------------------|
| not in old         | —                  | `companies__added`                               | YES              |
| —                  | not in new         | `companies__deleted`                             | NO — delete only |
| below N, **same**  | below N, **same**  | `companies__untruncated__unchanged__same_length` | NO               |
| below N or differs | below N or differs | `companies__untruncated__updated__diff_length`   | YES              |
| **at or above N**  | **at or above N**  | `companies__truncated__text_diff_required`       | see run 2        |

_N = `truncation_chars__stable_content`_

**SQL run 2 — text compare on `companies__truncated__text_diff_required` only:**

Both texts extend into dynamic content territory, so length alone is unreliable. Compare only the stable
content portion: `LEFT(text, N)`.

| `LEFT(old, N)` == `LEFT(new, N)` | Table                                               | LLM reprocess? |
|----------------------------------|-----------------------------------------------------|----------------|
| NO — stable content differs      | `companies__truncated__text_diff_result__updated`   | YES            |
| YES — stable content identical   | `companies__truncated__text_diff_result__unchanged` | NO             |

### Tables in step_00a__archive_diff.duckdb

| Table                                               | Columns                       | Description                                                   |
|-----------------------------------------------------|-------------------------------|---------------------------------------------------------------|
| `companies__added`                                  | CompanyNumber, CompanyWebText | In new archive, not in old                                    |
| `companies__deleted`                                | CompanyNumber                 | In old archive, not in new                                    |
| `companies__untruncated__unchanged__same_length`    | CompanyNumber                 | Same length, both below N — stable content unchanged          |
| `companies__untruncated__updated__diff_length`      | CompanyNumber, CompanyWebText | Length differs or one side crosses N — stable content changed |
| `companies__truncated__text_diff_required`          | CompanyNumber                 | Both at or beyond N — input for run 2                         |
| `companies__truncated__text_diff_result__updated`   | CompanyNumber, CompanyWebText | Confirmed stable content changed via LEFT(text, N) compare    |
| `companies__truncated__text_diff_result__unchanged` | CompanyNumber                 | Confirmed stable content identical via LEFT(text, N) compare  |

`step_00b__archive_diff.parquet` = `companies__added` + `companies__untruncated__updated__diff_length` + `companies__truncated__text_diff_result__updated`

## step6 - Merge Logic (per output file)

```
_previous/step_04__...__previous.duckdb  ──┐
                                           ├──► exclude deleted + exclude already-in-diffs
step_04__...__diffs.duckdb  ───────────────┤
                                           ├──► UNION ALL diffs
step_00a__archive_diff.duckdb (deleted) ───┘
                                           │
                                           ▼
                              step_06__*.duckdb  (final)
```

Applied to: step_04 features + step_05 embeddings (full, s, m, l) = 5 merged output files.

## Cleanup

The `_previous/` directory is not auto-deleted. Clean up manually after confirming the merged step_06 outputs are correct.
