## Goal - Take too Long

- too many records -> take too Long

## All Data

| company_id | data_source | doc_id | trust_tier | quality_tier | data | data_type |
|------------|-------------|--------|------------|--------------|------|-----------|
| 1          | A           | 1      | 1          | Q1           |      | json      |
| 1          | B           | 2      | 1          | Q1           |      | csv       |
| 1          | C           | 3      | 2          | Q2           |      | text      |
| 2          | A           | 1      | 1          | Q1           |      | json      |
| 2          | B           | 2      | 1          | Q1           |      | csv       |
| 2          | C           | 3      | 2          | Q2           |      | text      |
| 3          | A           | 1      | 1          | Q1           |      | json      |
| 3          | B           | 2      | 1          | Q1           |      | csv       |
| 3          | C           | 3      | 2          | Q2           |      | text      |

## Providers

| provider    | model            |
|-------------|------------------|
| deepseek    | deepseek 4 flash |
| open router | deepseek 4 flash |
| groq        | deepseek 4 flash |

## Solution

```text
 source data            
 +------+  ->  p1w1  +-+----+ 5min
 |------|  ->  p1w2  +---+----+--+ 8min
 |------|  ->  p2w1  +--+-+----+ 7min
 +------+
```

### Other Consideration

```text
- pause resume       |
- keep track of cost | => 1 duckdb
- timeout            |
```
