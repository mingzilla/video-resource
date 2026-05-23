## Goal

```text
 source data            desired data
 +------+      200k     +------+
 |------|  ->  LLM  ->  |------|
 |------|               +------+
 +------+
```

## All Data

| company_id | data_source | doc_id | trust_tier | quality_tier | data | data_type |
|------------|-------------|--------|------------|--------------|------|-----------|
| 1          | A           | 1      | 1          | Q1           |      | json      |
| 1          | B           | 2      | 1          | Q1           |      | csv       |
| 1          | C           | 3      | 2          | Q2           |      | text      |
| 2          | A           | 1      | 1          | Q1           |      | json      |
| 2          | B           | 2      | 1          | Q1           |      | csv       |
| 2          | C           | 3      | 2          | Q2           |      | text      |

## Input Output Data

| company_id | date     | value | investor |
|------------|----------|-------|----------|
| 1          | 5/3/2026 | 10m   | Andy     |
| 1          | 3/4/2026 | 23m   | Bob      |
| 1          | 3/3/2026 | 13m   | Chris    |

## Quality Tier

| id | quality_tier | type        | status |
|----|--------------|-------------|--------|
| Q1 | official     | csv,json    | raw    |
| Q2 | official     | pdf to text | clean  |
| Q3 | official     | ocr         | clean  |
| Q4 | 3rd party    | csv,json    | raw    |

## 1 item many records

| company_id | data_source | doc_id | trust_tier | quality_tier | data | data_type |
|------------|-------------|--------|------------|--------------|------|-----------|
| 1          | A           | 1      | 1          | Q1           |      | json      |
| 1          | B           | 2      | 1          | Q1           |      | csv       |
| 1          | C           | 3      | 2          | Q2           |      | text      |
| 1          | C           | 4      | 2          | Q2           |      | text      |
| 1          | C           | 5      | 2          | Q2           |      | text      |
