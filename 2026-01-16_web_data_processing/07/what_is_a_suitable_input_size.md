## Creating a Summary - What Length to Use

- Find a suitable length
- Verify length
- Performance Consideration

## Check the DB - What Length to Use

```shell
$.show_data_distribution.sh

--- Text Length Distribution Report (Column: webtext_cleaned) ---

100% ▕██████████████████████████████████████▏ (00:00:25.71 elapsed)
┌─────────────┬─────────────────┬────────────────────────┐
│ text_length │ %_vs_max_length │ %_records_below_length │
│    int64    │  decimal(5,2)   │         int64          │
├─────────────┼─────────────────┼────────────────────────┤
│        3349 │            6.70 │                     10 │
│        6320 │           12.64 │                     20 │
│        9418 │           18.84 │                     30 │
│       12769 │           25.54 │                     40 │
│       16291 │           32.58 │                     50 │
│       20076 │           40.15 │                     60 │
│       24119 │           48.24 │                     70 │
│       28660 │           57.32 │                     80 │
│       34285 │           68.57 │                     90 │
│       50001 │          100.00 │                    100 │
├─────────────┴─────────────────┴────────────────────────┤
│ 10 rows                                      3 columns │
└────────────────────────────────────────────────────────┘

Columns:
- text_length - characters of the text field to check
- %_vs_max_length - text_length / max_length_value_length * 100
- %_records_below_length - count of records shorter than this length

```

## Verify Length

24k & 36k have different results: means it takes >24k

- 24k: Original=35279 chars, Truncated=24000 chars, Summary=1191 chars
- 36k: Original=35279 chars, Truncated=35279 chars, Summary=653 chars

```shell
.show_cleaned_summary.sh 09505554

Initialized CompanyTextGenerator
Generating summary for company 09505554...

================================================================================
Company Number: 09505554
================================================================================
INDUSTRIES: Heritage, Industrial Heritage
ACTIVITIES: Archaeological consultancy, Conservation management, Cultural heritage management, Environmental impact assessment, Historical building recording, Industrial archaeology, Landscape management, Planning and development
PRODUCTS: Heritage advice, Conservation reports, Archaeological surveys, Building surveys, Environmental assessments
MARKETS: UK, International (no specific countries mentioned)
REGIONS: England, South Yorkshire, Peak District National Park
MODEL: B2B

COMPANY_SUMMARY:
TJC Heritage Ltd is a specialist heritage consultancy providing expert advice and services to clients across the UK and internationally. The company offers a range of services including archaeological consultancy, conservation management, cultural heritage management, environmental impact assessment, historical building recording, industrial archaeology, landscape management, and planning and development. With expertise in heritage and environmental issues, TJC Heritage Ltd helps clients navigate complex regulatory frameworks and develop sustainable solutions for their projects.

COMPANY_TRADING_NAME: The Jessop Consultancy, TJC Heritage Ltd
================================================================================

Stats: Original=35279 chars, Truncated=24000 chars, Summary=1191 chars
```

```shell
.show_cleaned_summary.sh 09505554

Initialized CompanyTextGenerator
Generating summary for company 09505554...

================================================================================
Company Number: 09505554
================================================================================
INDUSTRIES: Heritage Consultancy, Archaeology, Conservation, Restoration
ACTIVITIES: Building surveys, Historical research, Digital heritage projects, Photographic services
PRODUCTS:
MARKETS: UK, International
REGIONS: England, Wales, Scotland, Northern Ireland
MODEL: B2B
COMPANY_SUMMARY:
The JESSOP Consultancy is a heritage consultancy and archaeological service provider offering a range of services including building surveys, historical research, digital heritage projects, and photographic services. The company provides expert advice on heritage and archaeology to clients across the UK and internationally.

COMPANY_TRADING_NAME:
TJC Heritage
================================================================================

Stats: Original=35279 chars, Truncated=35279 chars, Summary=653 chars
```

## Time Differences - 60 items

| Defined Input Length | Actual Input Length | Time |
|----------------------|---------------------|------|
| 24k                  | 19k                 | 93s  |
| 16k                  | 14k                 | 88s  |
| 6k                   | 5k                  | 68s  |
