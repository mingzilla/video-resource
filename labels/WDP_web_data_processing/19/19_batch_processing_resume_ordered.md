## Big Size Data Processing Resume

- Background: millions of records, each record is big
- Format: parquet, duckdb
- What to achieve: Batch Processing Resume - next time when running a script, it starts from what's left off
- Requirement: Read Data: needs `WHERE id > ? and ORDER BY id` - otherwise cannot guarantee data order
- Problem: `ORDER BY` takes 25s to run, even if index is added, and you just query 5 records

```sql
-- 10 million records, 50GB file size, summary is long
  SELECT id, summary
    FROM companies
   WHERE id > ?
ORDER BY id -- guarantee order
   LIMIT 5  -- does not matter!
```

### **Core Constraints Summary:**
1. **No inherent order** in tables/files without `ORDER BY`
2. **Fresh process each time** — no state between runs except checkpoint ID
3. **Must guarantee order** for correct resume
4. **Must handle huge datasets** (50GB+, millions of records)
5. **Cannot rely on sequential ID ranges** for efficient scanning


## Attempts

### Attempt 1: Limit and Offset ?

```sql
  SELECT id, summary
    FROM companies
   WHERE id > ?
   LIMIT {batch_size} -- e.g. 1000
   OFFSET 100000 -- remove ORDER BY, use raw order and offset
```

- performance: takes 1 second to run query
- problem: no order, cannot guarantee correctness
- result: not possible to stop and resume (open new data connection to continue)


### Attempt 2: Split Files?

- Solution: Split input.parquet into many files with _nnn suffix
- Problem:
  - too many files to clean up
  - cannot remove temp files until all finished
  - stop and restart needs restart the whole small file
  - half done small files: since some records are saved and order is not tracked, this ends up with a broken state 

### Attempt 3: Use CTE?

- Question: Is it possible to run ORDER BY only once?
- Plan: Temp table (ID only) ORDERED -> extract batches -> batch joins and query

```sql
-- 25s upfront cost
  CREATE TEMP TABLE ordered_pks AS
  SELECT id
    FROM companies
   WHERE id > '{resume_from_id}'
ORDER BY id
   LIMIT 20000 -- Total items to process

WITH batch_pks AS (
    SELECT id
      FROM ordered_pks
  ORDER BY id -- add this would increase from 20ms to 60ms for 1k items
     LIMIT {batch_size} -- e.g. 1000
    OFFSET {offset} -- 1000, 2000, ...
)
SELECT a.id, a.summary
  FROM companies a
 INNER JOIN batch_pks b ON a.id = b.id
```

- Does it work? - YES - order guaranteed
- Is it fast? - NO
- Problem: `INNER JOIN` takes 25s to run

### Attempt 4: Use RAM

- Plan: temp_table ORDERED -> read from temp_table limit offset

```sql
-- 25s upfront cost
  CREATE TEMP TABLE ordered_in_ram_data AS
  SELECT id, summary
    FROM companies
   WHERE id > '{resume_from_id}'
ORDER BY id
   LIMIT 20000 -- Total items to process

-- Avoid the file with millions of records
  SELECT id, summary
    FROM ordered_in_ram_data
ORDER BY id -- small cost for safety
   LIMIT {batch_size} -- e.g. 1000
  OFFSET {offset} -- 1000, 2000, ...
```

- Does it work? - YES - order guaranteed
- Is it fast? - YES - each batch takes 10ms to read
- Question: Why not doing 20k in one batch? - problem: 20k read, 20k to process, 20k back in ram, 20k to save
- Problem: extra 200mb ram usage for 20k - what if we need 200 millions?

### Attempt 5: Use RAM - and scaling

- Plan: temp_table ORDERED (ram_data_size) -> read from temp_table limit offset

```sql
-- 25s upfront cost
  CREATE TEMP TABLE ordered_in_ram_data AS
  SELECT id, summary
    FROM companies
   WHERE id > '{resume_from_id}'
ORDER BY id
   LIMIT {ram_data_size} -- Total items to keep in ram
  OFFSET {ram_data_offset} -- 20000, 40000, ...

-- Avoid the file with millions of records
SELECT id, summary
  FROM ordered_in_ram_data
 LIMIT {batch_size} -- e.g. 1000
OFFSET {offset} -- 1000, 2000, ...

-- Next Cycle - drop current - create the next ordered_in_ram_data
DROP TABLE ordered_in_ram_data
```
