## Goal

```text
 source data            desired data
 +------+               +------+
 |------|  ->  LLM  ->  |------|
 |------|               +------+
 +------+
```

## All Data

| company_id | data_source | doc_id | trust_tier | quality_tier | data | data_type |
|------------|-------------|--------|------------|--------------|------|-----------|
|            |             |        |            |              |      |           |

## Quality Tier

| id | quality_tier | type | status |
|----|--------------|------|--------|
| Q1 |              |      | raw    |
| Q2 |              |      | clean  |
| Q3 |              |      | clean  |
| Q4 |              |      | raw    |

## Input Output Data

| id | date | value | investor |
|----|------|-------|----------|
|    |      |       |          |
|    |      |       |          |

## 1 item many records

| company_id | data_source | doc_id | trust_tier | quality_tier | data | data_type |
|------------|-------------|--------|------------|--------------|------|-----------|
|            |             |        |            |              |      |           |
