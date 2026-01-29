# Verify Generation

- Verifying Quality
- Verifying Structure,Accuracy -> Extraction
- Verify Suitable Input Text Length

## Compare 4 Items - Verifying Quality

- cleaning: Is clean text good or not - does it lose important info?
- generating: Is clean text generating better results or not

```text
Step1:
- Original Text
- Cleaned Text
- Original Text Summary
- Cleaned Text Summary

Step2:
- Give e.g. examples/08219926.md to Deepseek.
```

## Verify Structure

- Verify Structure
- Verify Missing Mandatory Fields
- Verify Reusing Records
- Action: Convert to unpacked structure

```shell
# run__verification.sh
CATEGORIES=("INDUSTRIES" "ACTIVITIES" "PRODUCTS" "MARKETS" "REGIONS" "MODEL" "COMPANY_SUMMARY" "COMPANY_TRADING_NAME")
run_all_verifications "${CATEGORIES[@]}"
```

```text
$./run__verification.sh
=========================================
Verification of generated data
=========================================
Config file: /mnt/e/code/github-release/mvp/work/llm_text_summary/scripts_pipeline_steps/p001__rtic_company_summaries/run__cleaned__extraction__config.json

✓ Config loaded from: /mnt/e/code/github-release/mvp/work/llm_text_summary/scripts_pipeline_steps/p001__rtic_company_summaries/run__cleaned__extraction__config.json
  Output DB: ../__pipelines/2026_01__p001__rtic_companies_webtext_summary/_output/step_04__rtic_company_cleaned_webtext_16k_capabilities__Dec2025.duckdb
  Table: companies
  Summary column: webtext_summary
=========================================
Running verification checks...
=========================================
✓ Output database exists: ../__pipelines/2026_01__p001__rtic_companies_webtext_summary/_output/step_04__rtic_company_cleaned_webtext_16k_capabilities__Dec2025.duckdb

1. STRUCTURE VERIFICATION:
   Checking categories appear in correct order (optional categories are handled)
   Categories: INDUSTRIES ACTIVITIES PRODUCTS MARKETS REGIONS MODEL IS_MANUFACTURING MANUFACTURING_PROCESSES TECHNICAL_CAPABILITIES COMPANY_SUMMARY COMPANY_TRADING_NAME
   Include colon in check: true
   Total rows in table: 43560
   (Checking order of categories if they appear in text)
   Result: 43533/43560 rows have correct structure (99.93%)

2. COMPANY_SUMMARY CHECK:
   Total rows in table: 43560
   Result: 43262/43560 rows have COMPANY_SUMMARY (99.31%)

3. COMPANY_TRADING_NAME CHECK:
   Total rows in table: 43560
   Result: 42727/43560 rows have COMPANY_TRADING_NAME (98.08%)

4. RECORD REUSING STATISTICS:
   Total records: 43560
   Planned records to create: 36025
   Planned records to reuse: 7535
   Actual distinct summaries generated: 35634
   Actual records that reused: 7926

   Planned reuse rate: 17.29%
   Actual reuse rate: 18.19%
```

## Verify Suitable Input Text Length

```text
Total: 8k
- [webtext] - What is the most suitable?
- [prompt] - about 1k
- [output] - about 1k
```

200 Records (character length):

- summary__cleaned__4k.duckdb
- summary__cleaned__8k.duckdb
- summary__cleaned__10k.duckdb
- summary__cleaned__16k.duckdb <-- 4k tokens - best result
- summary__cleaned__24k.duckdb
- summary__cleaned__36k.duckdb
- summary__original__4k.duckdb
- summary__original__8k.duckdb
- summary__original__10k.duckdb
- summary__original__16k.duckdb
- summary__original__24k.duckdb
- summary__original__36k.duckdb

### Best Result (16k)

- Good Order - determined by prompt
- Has Labels - determined by input length

```text
INDUSTRIES: insurance, maritime, shipping, risk management, transport, energy
ACTIVITIES: marine surveying, cargo surveying, engineering, consultancy, salvage, claims adjusting
PRODUCTS: 
MARKETS: UK, international
REGIONS: North West and West of England, Midlands and Wales
MODEL: B2B

COMPANY_SUMMARY: LGSA Marine is an independent company providing a comprehensive range of services to the insurance, maritime, shipping, risk management, transport and energy industries. With offices throughout the UK, they operate internationally and offer expertise in technical, marine, cargo services and general average as well as legal, liability and risk management activities.

COMPANY_TRADING_NAME: LGSA Marine, The Liverpool & Glasgow Salvage Association
```