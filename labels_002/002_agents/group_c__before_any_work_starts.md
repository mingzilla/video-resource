# C. Before Any Work Starts

- [7. Upfront prompt verification — one call, multiple validations]
- [8. Dynamic results schema — output adapts to prompt changes]
- [9. PK from data, not synthetic row_id]
- [10. Upfront optimisation — skip invalid websites]
- [11. Distinguishing failure reasons — _source tracking]

---

## The Problem

Before a single company is classified, a lot can go wrong. The user
might upload the wrong file in the wrong box. The prompt might not define
an output schema. The CSV might have columns Claude doesn't expect.
16% of companies might not even have a website.

Every mistake found later costs tokens. Every mistake found now costs nothing.

```text
20,000 companies to process.
Each costs ~$0.003 in tokens.
Total: ~$60.

What if the prompt has no output schema?
  $60 wasted. 20,000 results with wrong columns.

What if 3,200 companies have no website?
  $9.60 wasted. Claude returns "Data Quality Issue" for all of them.
  We could have detected this in milliseconds.

What if Alex uploaded the taxonomy as the prompt?
  $60 wasted. All results are nonsense.

The question: how much can we catch for free before spending $60?
```

---

## Decision 7: Upfront prompt verification

> You thought: regex-parse the prompt for column names.
> But actually: Claude reads the prompt semantically — catches file-swap errors regex can't.

```text
REGEX (rejected):

  Read prompt.md
  Find lines matching: "Column_Name | description"
  Extract column names

  Problems:
  - Alex changes the format? Regex breaks.
  - Taxonomy uploaded as prompt? Regex finds nothing, returns error.
    But the error says "no schema found" — not "this is a taxonomy."
  - CSV columns don't map to output? Regex can't check semantics.


ONE CLAUDE CALL (chosen):

  Reads ALL 5 input files + CSV header.
  Returns JSON:

  {
    "output_columns": [
      {"name": "Company_Number", "description": "as provided"},
      {"name": "Verdict", "description": "one of five verdicts"},
      ...
    ],
    "input_to_output_mapping": {
      "Companynumber": "Company_Number",
      "Companyname": "Company_Name",
      "Website": "Website"
    },
    "primary_key": "Company_Number",
    "validation_errors": [],
    "input_file_issues": [
      "taxonomy.md appears to contain classification instructions"  <-- caught!
    ]
  }

  Cost: ~$0.10, 30-60 seconds.
  Amortised over 20,000 companies: negligible.
  Catches: wrong files, missing schema, unmapped columns, missing PK.
```

- **Q:** how do we validate inputs before spending tokens on 20,000 companies?
- **Options:** (a) regex-parse for schema, (b) one Claude call for everything
- **Chose:** one upfront Claude call. Reads all files, returns structured JSON.
- **Why:** regex breaks on format changes. Claude understands semantics — "this file looks like a taxonomy, not a prompt." Cost amortised over the entire job.
- **Cascade:** the JSON response creates the DuckDB output_records table dynamically

---

## Decision 8: Dynamic results schema

> You thought: hardcode the output columns.
> But actually: Alex changes the prompt weekly. Dynamic schema adapts without code changes.

```text
HARDCODED (rejected):

  CREATE TABLE output_records (
      Company_Number VARCHAR,
      Company_Name VARCHAR,
      Website VARCHAR,
      Verdict VARCHAR,
      Activity_Flag VARCHAR,
      ...12 columns...
  );

  Alex adds "Sector_Confidence" to the prompt.
  --> Code change needed.
  --> Deploy new Docker image.
  --> For one column.


DYNAMIC (chosen):

  Upfront Claude call returns:
    output_columns: ["Company_Number", "Company_Name", ..., "Sector_Confidence"]

  Python builds:
    CREATE TABLE output_records (
        "Company_Number" VARCHAR PRIMARY KEY,
        "Company_Name" VARCHAR,
        ...
        "Sector_Confidence" VARCHAR,       <-- new column, no code change
        "_source" VARCHAR,
        "_instance_workspace" VARCHAR,
        "_created_at" TIMESTAMP
    );

  Alex adds a column? The system adapts automatically.
  The UI adapts too — table shows all columns, charts show known ones.
```

- **Q:** prompt defines output columns. Alex changes them. Do we update code?
- **Options:** (a) hardcode, (b) read from first result CSV, (c) detect from upfront Claude call
- **Chose:** upfront call extracts schema, Python creates table dynamically
- **Why:** Alex changes the prompt frequently. The upfront call already reads the prompt — schema extraction costs nothing extra.
- **Cascade:** UI (system3 dashboard) handles dynamic columns — charts for known columns, table for everything

---

## Decision 9: PK from data, not synthetic row_id

> You thought: use row numbers as primary keys.
> But actually: the data has a real PK (company number). Use it — queries make sense.

```text
SYNTHETIC ROW_ID (rejected):

  input_records:           output_records:        processing_records:
  | row_id | Companynumber  | row_id | Verdict    | row_id | workspace
  |--------|--------------- |--------|----------- |--------|----------
  | 1      | 09688671       | 1      | Valid      | 47     | ws_003
  | 2      | 11689731       | 2      | FP         | 48     | ws_003
  | 47     | 08458210       |        |            | 49     | ws_003

  "What's row_id 47?"
  --> Look up input_records.
  --> It's company 08458210.
  --> Extra mental step every time.


REAL PK (chosen):

  input_records:               output_records:          processing_records:
  | Companynumber | Name       | Company_Number | Verdict | Companynumber | workspace
  |---------------|----------- |----------------|---------|---------------|----------
  | 09688671      | SUM & SUB  | 09688671       | Valid   | 08458210      | ws_003
  | 11689731      | CRASSULA   | 11689731       | FP      | 10137834      | ws_003

  "What's being processed?"
  --> 08458210 and 10137834.
  --> Immediately meaningful.

  Unclaimed = input - output - processing:
  SELECT Companynumber FROM input_records
  WHERE Companynumber NOT IN (SELECT Company_Number FROM output_records)
    AND Companynumber NOT IN (SELECT Companynumber FROM processing_records)
```

- **Q:** synthetic row_id or actual PK?
- **Options:** (a) row_id (1-based row number), (b) actual PK from data
- **Chose:** actual PK, identified by the upfront Claude call
- **Why:** queries on real business keys are immediately meaningful. No extra lookup.
- **Cascade:** processing_records uses input PK, output_records uses output PK (may differ via column mapping). Python builds queries dynamically.

---

## Decision 10: Skip invalid websites before Claude

> You thought: let Claude handle "no website" companies.
> But actually: 16% waste. DNS check in milliseconds, zero tokens.

```text
100 companies from test run:

  +------------------+-------+---------------------------+
  | Category         | Count | What Claude did           |
  +------------------+-------+---------------------------+
  | No website       | 16    | Spent tokens --> "DQI"    |
  | Website, Claude  | 78    | Classified normally       |
  | Website, Claude  | 6     | Spent tokens --> "DQI"    |
  |   failed         |       | (valid URLs, Claude flaky)|
  +------------------+-------+---------------------------+

  16 companies: zero value from Claude. Pure waste.
  6 companies: Claude failed on valid URLs. We can't prevent this,
               but we can label it differently.


THREE-TIER PRE-FILTER (chosen):

  20,000 companies
       |
  Tier 1: no website URL?
       |-- YES --> output_records (_source: 'no_website')    0 tokens
       |-- NO
       v
  Tier 2: DNS check fails?
       |-- YES --> output_records (_source: 'dns_failed')    0 tokens
       |-- NO                     (aiodns, 1000 concurrent,
       v                           milliseconds)
  Tier 3: send to Claude
       --> output_records (_source: 'claude')                $$ tokens

  Result for 20,000 companies:
    ~3,200 no website    --> free
    ~200 DNS failed      --> free
    ~16,600 to Claude    --> $$
    Saved: ~$10 and hours of processing time
```

- **Q:** 16% of companies had no website. Claude spent tokens to return "Data Quality Issue."
- **Options:** (a) let Claude handle it, (b) pre-filter in Python
- **Chose:** three-tier: no website → skip, DNS fails → skip, DNS passes → Claude
- **Why:** zero tokens on companies identifiable as unclassifiable in milliseconds
- **Cascade:** pre-filtered records go into output_records with distinct `_source` values

---

## Decision 11: Distinguishing failure reasons

> You thought: all results look the same.
> But actually: _source column — was it Claude, no website, or DNS fail? Users need to know.

```text
WITHOUT _source:

  | Company_Number | Verdict     |
  |----------------|-------------|
  | 09688671       | Valid       |
  | 03166744       | DQI         |  <-- why? no website? DNS? Claude failed?
  | 09903923       | FP          |
  | 06493819       | DQI         |  <-- same verdict, completely different reason

  User can't tell what was researched vs what was skipped.


WITH _source:

  | Company_Number | Verdict | _source    |
  |----------------|---------|------------|
  | 09688671       | Valid   | claude     |  <-- researched, classified
  | 03166744       |         | no_website |  <-- skipped, no URL provided
  | 09903923       | FP      | claude     |  <-- researched, false positive
  | 06493819       |         | dns_failed |  <-- skipped, domain doesn't resolve

  Progress endpoint shows:
    classified: 16,600
    no_website: 3,200
    dns_failed: 200
    total: 20,000

  User knows exactly what happened and what needs attention.
```

Metadata columns prefixed with `_` to avoid collision with prompt-defined output columns.
`_source`, `_instance_workspace`, `_created_at` — always present regardless of prompt schema.

- **Q:** how do we know if Claude classified a company or Python pre-filtered it?
- **Options:** (a) don't track, (b) `_source` metadata column
- **Chose:** `_source`: 'claude', 'no_website', 'dns_failed'
- **Why:** users need to know what was researched vs skipped. Progress shows the breakdown.
