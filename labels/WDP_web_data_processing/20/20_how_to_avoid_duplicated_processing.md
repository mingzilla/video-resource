# Avoid wasting LLM API calls

Avoid wasting LLM API calls (~1s each) on duplicate webtext by reusing previously generated summaries.

## Solution Architecture

```text
[Create mapping_table] -- Create if not present
     |                      |- output.duckdb exists?
     |                      +- mapping_table exists?
     |
[Load chunk] - 10k
     |                 output_max_id = max(id)
     | <--------------------------------------------------------- [output.duckdb]
     |
     |                 WHERE id > output_max_id
     |                 ORDER BY/LIMIT/OFFSET
     | <--[TEMP_TABLE_10k]--------------------------------------- [input.duckdb]
     | <--[mapping_dict_10k: Dict<input_id, same_as_lowest_id>]-- [mapping_table]
     |
   [Read batch] - 1k
     |  Read from [TEMP_TABLE_10k]
     |
   [Process batch] - 1k
     |  Fallback Strategy:
     |  |- in-ram: processed in current batch
     |  |- in mapping_dict_10k: read from output.duckdb
     |  +- LLM API call: 1s
     |
   [Save batch] - 1k
     |
(next trunk ...)

```

### 1. Deduplication Mapping Table

- Table: input_text_duplicate_mappings in output.duckdb
- input_id (mandatory) - include every record in input.duckdb - all using same `ORDER BY/LIMIT/OFFSET`
- same_as_lowest_id (nullable) - lowest ID with identical text
- Domain-agnostic: Uses generic column names from config

| input_id | same_as_lowest_id |
|----------|-------------------|
| 01       | null              |
| 02       | null              |
| 03       | 01                |
| 04       | 01                |

### 2. Table Creation Strategy

- If output.duckdb doesn't exist → create it + mapping table
- If output.duckdb exists but no mapping table → create mapping table (helps half-done runs)

### 3. Usage Flow

For each RAM chunk:

- Query mapping table with same `ORDER BY/LIMIT/OFFSET` as querying input.duckdb
- Load into Dict[str, str] id_mappings in Python memory
- Pass to batch processor

### 4. Batch Processing Fallback Logic

When processing a company with ID in id_mappings:

1. Check current batch's already-processed results (in-memory)
2. If not found, query output.duckdb for same_as_lowest_id's summary
    - same_as_lowest_id can be null if not available. so then if it's null,
    - if null, we don't need to waste effort trying to query output.duckdb to get existing record
3. If still not found, call LLM API
4. Reuse the found summary for current ID

### 5. Key Properties

- Batches process in ASC order (ORDER BY ensures this)
- same_as_lowest_id always references earliest-processed ID
- Mapping lookup order doesn't matter, but DB reads mirror input data reads

## Building the Mapping Table:

### Step 1: Create temp table with ID arrays (no text column to keep it small)

```sql
CREATE TEMP TABLE input_ids_group_by_text AS
SELECT LIST(id_column ORDER BY id_column) as id_list
FROM input_source
GROUP BY text_column
```

### Step 2: Flatten into final mapping

```sql
CREATE TABLE input_text_duplicate_mappings AS
SELECT
    id_elem as input_id,
    CASE
        WHEN id_elem = id_list[1] THEN NULL
        ELSE id_list[1]
    END as same_as_lowest_id
FROM input_ids_group_by_text,
LATERAL UNNEST(id_list) as t(id_elem);
```

Note: Don't skip the first element - creates inconsistent queries!

- If we skip the first element, then:
    - Real data query: WHERE id > ? ORDER BY id LIMIT chunk_size returns [id1, id2, id3, id4, id5]
    - Mapping query: Same WHERE/LIMIT/OFFSET returns [id2, id4, id5] (missing id1, id3)
    - Problem: Queries don't mirror each other! We can't use same WHERE/LIMIT/OFFSET.
- Correct approach: Include ALL IDs, use NULL for first in each group
