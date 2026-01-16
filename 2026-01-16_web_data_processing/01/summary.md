"data cleaning" solution inspired by huggingface. This is how people clean webtext and prepare data for LLM training.

### This solution does the below: 
- steps: 1) markup cleaning, 2) Paragraph deduplication, 3) Sentence deduplication, 4) N-gram phrase removal, 5) Quality filters
- performance: it takes ~5ms per domain, so <15 hours to do 10 million websites
- result: The avg text size of a web domain is 30k characters, this clean procedure typically removes nearly 15k chars - about 50%
- indication: 15k chars ~= 5k tokens, it means we can use llama3.2 to convert this into 2k tokens consistent website description

### To visualize it, the below can be a good pipeline:

```text
+-------------------+               +-------------------+               +-------------------+            +----------------------+
| 30k chars webtext | -[cleaning]-> | 15k chars webtext | -[gemma3.2]-> | 2k tokens summary | -[nomic]-> | full content vectors |
+-------------------+    | (1)      +-------------------+     | (2)     +-------------------+     | (3)  +----------------------+
         |               |- ~ 15hours         |               |- 3b 8k context                    |- 8k context - 8k ~= 4days
         |                                    |               |                                   |
 Archive_MonthYear.parquet            ~ 4k tokens     5k input, 2k output                      2k input
```

### This step (1) enables the rest.
- we can put the `2k tokens summary` on the platform
- we can make use of the FULL interpretation of a website for similar company lookup (vector similarity search)
- (current solution: using minilm with about 5% of the FULL interpretation. a short description is prepended to get around this)


### Here's an example of how step (1) works

```text
INPUT TEXT:

    <style>body { margin: 0; }</style>
    <script>console.log('test');</script>

    Home About Products Contact Privacy Terms.
    <div class="content">Welcome to TechCorp Solutions</div>
    We are a leading provider of innovative software solutions.
    Home About Products Contact Privacy Terms.

    Our products include cloud computing, data analytics, and AI services.
    <p>We have been in business for 15 years.</p>
    Home About Products Contact Privacy Terms.

    Customer satisfaction is our top priority. We serve clients worldwide.
    We are a leading provider of innovative software solutions.

    Copyright 2024 TechCorp All Rights Reserved Privacy Policy Terms of Service.
    Contact us at info@techcorp.com for more information.
    Copyright 2024 TechCorp All Rights Reserved Privacy Policy Terms of Service.


Length: 840 chars

--------------------------------------------------------------------------------
OUTPUT TEXT:
Welcome to TechCorp Solutions
We are a leading provider of innovative software solutions. Our products include cloud computing, data analytics, and AI services. We have been in business for 15 years. Customer satisfaction is our top priority. We serve clients worldwide. We are a leading provider of innovative software solutions. Copyright 2024 TechCorp All Rights Reserved Privacy Policy Terms of Service. Contact us at info@techcorp.com for more information. Copyright 2024 TechCorp All Rights Reserved Privacy Policy Terms of Service..

--------------------------------------------------------------------------------
STATISTICS:
  Original length:     840 chars
  Cleaned length:      539 chars
  Reduction:           35.8%
  Sentences removed:   3
  Paragraphs removed:  0
  Quality passed:      True

💡 What happened (in order):
  1. Removed: <style>, <script>, <div>, <p> tags (boilerplate)
  2. Deduplicated paragraphs (removed large duplicate blocks first)
  3. Removed: 'Home About Products Contact Privacy Terms' (sentence appeared 3x)
  4. Removed: 'Copyright 2024 TechCorp...' phrase (n-gram removal)
  5. Passed quality checks (length, word count, etc.)
```

### Output of this clean procedure

- output.duckdb -- an example file attached, with 50 rows
- output_summary.csv -- a summary of a different run, this run processes 20k rows

### meaning of csv columns

1. batch - Range (e.g., "0-5") or "TOTAL"
2. rows_processed - How many rows in batch
3. rows_kept - Passed quality filters
4. rows_rejected - Failed quality filters
5. avg_chars_before - Average original text length
6. avg_chars_after - Average cleaned text length
7. percent_reduction - (before - after) / before * 100
8. paragraphs_removed - Total in batch
9. sentences_removed - Total in batch
10. processing_time_ms - Batch processing time