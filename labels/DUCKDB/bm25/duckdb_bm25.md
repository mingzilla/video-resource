## Create bm25 index and testing it

- What is BM25
- create_fts_index - `PRAGMA create_fts_index('table_name', 'primary_key_column', 'text_column');`
    - same as - `PRAGMA create_fts_index('main.table_name', ...);`
- use fts index - fts_main_TABLE_NAME.match_bm25(CompanyNumber, 'test company') IS NOT NULL
- extra example

## What is BM25

BM25 stands for "Best Matching 25".

- BM25 is a ranking algorithm
- Elastic Search uses BM25 by default
- BM25 is a bag-of-words model (no word order) - same score: "Hello World", "World Hello"
- Case Insensitive

**Example with query "hello world":**
BM25 treats the query as individual terms: ["hello", "world"]. It then scores documents based on term frequency, inverse document frequency, and document length.

Given documents:

1. "Hello world!" - High score (both terms, short length)
2. "World, hello!" - Same high score (same terms, same length)
3. "World Hello Ltd" - Slightly lower score (extra term "ltd", longer length)
4. "Hello there" - Lower score (missing "world")
5. "Greetings" - Very low score (no matching terms)

## Creating and Using Index

```shell
PS E:\code\temp-projects> duckdb
D .open companies.duckdb
D PRAGMA create_fts_index('CompaniesWithDescription', 'CompanyNumber', 'CompanyNameWithDescription');
D   SELECT CompanyNumber, CompanyNameWithDescription,
    fts_main_CompaniesWithDescription.match_bm25(CompanyNumber, 'british gas') as scores
    FROM CompaniesWithDescription
    WHERE fts_main_CompaniesWithDescription.match_bm25(CompanyNumber, 'british gas') IS NOT NULL
    ORDER BY scores DESC
    LIMIT 5;
┌───────────────┬────────────────────────────────────────────────────┐
│ CompanyNumber │                    CompanyName                     │
│    varchar    │                      varchar                       │
├───────────────┼────────────────────────────────────────────────────┤
│ 11751181      │ NW COMPANY WORKS LIMITED                           │
│ 09256232      │ QA TESTING CONSULTANCY LIMITED                     │
│ 14354327      │ PHOENIX PARK (THAME) MANAGEMENT COMPANY LIMITED    │
│ 12336983      │ OUSEBURN MUSIC AND ARTS COMMUNITY INTEREST COMPANY │
│ 04927593      │ BROMSGROVE BUS & COACH COMPANY LIMITED             │
└───────────────┴────────────────────────────────────────────────────┘

```

## Using index

### Structure

- `fts_main_ClassifiedCompaniesRelational` breaks down as:
    - **`fts_`** - Prefix indicating it's a full-text search index object
    - **`main`** - The schema name (default schema in DuckDB)
    - **`ClassifiedCompaniesRelational`** - The table name

So `fts_main_ClassifiedCompaniesRelational` is the FTS index object created in the `main` schema for the `ClassifiedCompaniesRelational` table.

### How it works

This offers `WHERE fts_main_ClassifiedCompaniesRelational.match_bm25(CompanyNumber, 'test company') IS NOT NULL`

- Takes the row's `primary key` (CompanyNumber)
- Looks it up in the FTS inverted `index`
- Checks if that row's indexed text (CompanyName) `contains 'test' and 'company'`
    - 'test' relates to company 11751181
    - 'company' relates to company 11751181
    - so 11751181 is high
- Returns a `relevance score (or NULL if no match)`

## Extra Example

```shell
D SELECT
    CompanyNumber,
    fts_main_ClassifiedCompaniesRelational.match_bm25(
        CompanyNumber,
        'british gas'
    ) as keyword_score,
    rank() OVER (ORDER BY fts_main_ClassifiedCompaniesRelational.match_bm25(
        CompanyNumber,
        'british gas'
    ) DESC) as keyword_rank
FROM ClassifiedCompaniesRelational
WHERE fts_main_ClassifiedCompaniesRelational.match_bm25(
    CompanyNumber,
    'british gas'
) IS NOT NULL
ORDER BY keyword_score DESC
LIMIT 1000;
```