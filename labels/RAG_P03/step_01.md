# Step 1: Company Data Extraction & Preparation

```text
[Data Extraction]
|-- 1. Purpose
|-- 2. Processing Flow, Input/Output
|-- 3. Data Fetching Process
|      |-- 3.1 Batch Processing
|      |-- 3.2 Performance & Memory Optimization
|      |-- 3.3 Progress Tracking & Resumability
|      +-- 3.4 Performance Monitoring & Tuning
|-- 4. Data Quality & Transformation
|      |-- 4.1 filterable fields
|      +-- 4.2 Avoid duplication
|-- 5. Environment Variables
+-- 6. Output Verification
```

## 1. Purpose

This document outlines the design and implementation of the first step in the company search pipeline: extracting 20 million company records from a source database, transforming them, and loading them into a structured DuckDB table. This process is engineered to be efficient, resumable, and scalable, laying a clean foundation for subsequent vectorization and search stages.

**Key Challenges Addressed:**

- **Large Data Volume:** Processing 20M+ records without high memory consumption.
- **Performance:** Ensuring the extraction completes within a reasonable timeframe.
- **Resumability:** Allowing the process to be stopped and restarted without data loss.
- **Data Integrity:** Guaranteeing data quality and consistency in the target table.

## 2. System Design & Data Flow

### 2.1 High-Level Data Flow

The process reads from two source tables, joins them, processes the data in batches, and inserts it into a new, consolidated target table.

```text
[Source Database]
 |-> [ClassifiedCompaniesRelational]
 +-> [PostcodeDetailRelational]
 |
 V
+------------------------------------+
|         Processing Engine          |
|------------------------------------|
| 1. Join Tables                     |
|    (GROUP BY to de-duplicate)      |
|                 |                  |
|                 V                  |
| 2. Process in Batches (5,000)      |
|    (Uses last ID to resume)        |
|                 |                  |
|                 V                  |
| 3. Normalize City Names            |
+------------------------------------+
 |
 V
[Target Database]
 |-> [CompanyWithVectors Table]
```

### 2.2 Input Data Sources

| Table                           | Key Fields                               | Purpose                                 |
|---------------------------------|------------------------------------------|-----------------------------------------|
| `ClassifiedCompaniesRelational` | `CompanyNumber`, `CompanyName`, `Active` | Provides primary company identity data. |
| `PostcodeDetailRelational`      | `CompanyNumber`, `StandardisedCity`      | Provides geographic (city) information. |

### 2.3 Output Table Structure

A new table, `CompanyWithVectors`, is created in a separate DuckDB file to store the cleaned and structured data.

**SQL Schema:**

```sql
CREATE TABLE IF NOT EXISTS CompanyWithVectors (
    CompanyNumber VARCHAR PRIMARY KEY,
    CompanyName VARCHAR,
    Active BOOLEAN,
    City VARCHAR,
    Vector FLOAT[384]
);

CREATE INDEX IF NOT EXISTS idx_company_number 
ON CompanyWithVectors(CompanyNumber);
```

**Field Specifications:**

| Column          | Type         | Source                                        | Processing Rules                             |
|-----------------|--------------|-----------------------------------------------|----------------------------------------------|
| `CompanyNumber` | `VARCHAR`    | `ClassifiedCompaniesRelational.CompanyNumber` | **Primary Key.** Must not be null.           |
| `CompanyName`   | `VARCHAR`    | `ClassifiedCompaniesRelational.CompanyName`   | Original case and content preserved.         |
| `Active`        | `BOOLEAN`    | `ClassifiedCompaniesRelational.Active`        | Direct mapping. Null if source is null.      |
| `City`          | `VARCHAR`    | `PostcodeDetailRelational.StandardisedCity`   | Normalized: lowercase, special chars to `_`. |
| `Vector`        | `FLOAT[384]` | `NULL` (initially)                            | Populated in Step 02 (Vectorization).        |

## 3. Processing & Performance Strategy

### 3.1 Batch Processing for Scalability

To handle the 20 million records without exhausting memory, the data is processed in managed chunks.

```text
DataExtractionService                       SourceDbRepository      TargetDbRepository
       |                                            |                       |
       |------- Get last processed ID ------------->|                       |
       |<------------------ last_id ----------------|                       |
       |                                            |                       |
       |-- Fetch batch of 5,000 records > last_id ->|                       |
       |<---------------- company_data -------------|                       |
       |                                            |                       |
       | Normalize city names                       |                       |
       |                                            |                       |
       |------- Insert batch via pandas ----------->|---------------------->|
       |<------------------ Success ----------------------------------------|
```

### 3.2 Performance & Memory Optimization

| Technique                 | Implementation Detail                                                   | Benefit                                                      |
|---------------------------|-------------------------------------------------------------------------|--------------------------------------------------------------|
| **Batch Processing**      | Data is read, processed, and written in chunks of 5,000 records.        | Keeps memory usage low and predictable (~10MB per batch).    |
| **Optimized DB Inserts**  | Uses `pandas.DataFrame` and `conn.append()` instead of `executemany()`. | Reduces batch insert time from ~30 seconds to ~2 seconds.    |
| **Target Table Indexing** | A primary key index is created on `CompanyNumber` after table creation. | Ensures fast lookups for progress tracking and future steps. |
| **Ordered Processing**    | Records are consistently processed `ORDER BY CompanyNumber ASC`.        | Guarantees reliable progress tracking and resumability.      |

### 3.3 Progress Tracking & Resumability

The process is designed to be interrupt-safe. If it stops, it can resume exactly where it left off.

| Mechanism            | Implementation                                                                                           |
|----------------------|----------------------------------------------------------------------------------------------------------|
| **State Detection**  | Before starting, the service queries the **target** database (`CompanyWithVectors`) for the highest `CompanyNumber` already processed. |
| **Resumption Logic** | The next batch query uses this number to fetch records from the **source** database (`ClassifiedCompaniesRelational`) that come after it. |
| **Idempotency**      | Since `CompanyNumber` is a primary key in the target table, re-running a completed batch by mistake will not create duplicate records.  |

**Query to find the last processed record:**
```sql
SELECT MAX(CompanyNumber) FROM CompanyWithVectors;
```

**Critical Note on String-Based Resumption:**
The `CompanyNumber` is a `VARCHAR` (text) field. The entire resumability mechanism relies on the `MAX()` function and the `>` operator using the same **lexicographical** (dictionary-style) sorting logic. Because both the source and target databases are DuckDB, this comparison is consistent, making the process reliable. The `ORDER BY CompanyNumber ASC` clause in the source query is also critical to ensure batches are processed in a predictable and repeatable order.

### 3.4 Performance Monitoring & Tuning

Log processing time can help with identifying bottlenecks, this includes e.g. 1) batch processing time, 2) total time.

**Sample Log Output:**

```text
Batch 10 timing (seconds):
- batch_size=5000, sql_read=0.7514, processing=0.2134, db_write=1.5523, total=2.5171

# Note - allow adjusting:
- total_size - test with small dataset, then use big value for actual processing
- batch_size - makes significant differences
```

| Bottleneck Symptom     | Potential Cause                        | Note                                         |
|------------------------|----------------------------------------|----------------------------------------------|
| High `sql_read` time   | Bad indexing, or bad way to read data. | Data order and indexing can affect this      |
| High `processing` time | Bad algorithm.                         | Alignment strategy matters, avoid re-sorting |
| High `db_write` time   | Bad way to write to db.                | Indexes won't cause writing to be slow       |

## 4. Data Quality & Transformation

### 4.1 Attribute Normalization - Use FilterAttributeUtil

To ensure consistent filtering capabilities, text attributes like city names are standardized using a shared utility. This process converts text into a format suitable for database filters (e.g., for Qdrant) by replacing each non-alphanumeric character with an underscore.

| Rule                               | Example Input | Example Output |
|------------------------------------|---------------|----------------|
| Convert to lowercase               | `London`      | `london`       |
| Replace each non-alphanumeric char | `St. Albans`  | `st__albans`   |

### 4.2 Handling Data Duplicates

The `PostcodeDetailRelational` table may contain duplicate `CompanyNumber` entries. This is resolved during the source query with MAX and GROUP BY.

**Query Snippet:**

```sql
SELECT 
    c.CompanyNumber,
    c.CompanyName, 
    c.Active,
    MAX(p.StandardisedCity) AS StandardisedCity       -- Use MAX() to ensure a single city value
FROM ClassifiedCompaniesRelational c
LEFT JOIN PostcodeDetailRelational p ON c.CompanyNumber = p.CompanyNumber  
GROUP BY c.CompanyNumber, c.CompanyName, c.Active     -- Guarantees a unique CompanyNumber in the result set.
WHERE c.CompanyNumber > ?  -- ? is max CompanyNumber from target db, since we get it with SQL, give it to SQL here, `>` for text order is consistent
ORDER BY c.CompanyNumber ASC                          -- Ensures the stream is ordered for reliable pagination.
LIMIT ?;
```

## 5. Configuration & Execution

### 5.1 Configuration Strategy

The application follows a pure environment variable-based configuration strategy. All parameters are loaded from environment variables via the `EnvVarDefaults` class, which serves as the single source of truth for all configuration values.

There are **no command-line arguments** for this step. This unified approach simplifies deployment and ensures consistent behavior across all environments.

### 5.2 Environment Variables

All configuration is managed via environment variables. The `shared_utils/env_var_defaults.py` file defines every parameter used in the data extraction step, along with sensible defaults.

| Environment Variable     | Default Value                                         | Purpose                                                 |
|--------------------------|-------------------------------------------------------|---------------------------------------------------------|
| `DB_MOUNT_PATH`          | `/mnt/d/dev/TDCServerUK/TDCServerUK/Databases`        | Base directory for all DuckDB files.                    |
| `COMPANY_SOURCE_DB_FILE` | `ClassifiedCompaniesRelational_Jul2025.duckdb`        | Filename of the source database.                        |
| `COMPANY_TARGET_DB_FILE` | `ClassifiedCompaniesRelational_Jul2025_minilm.duckdb` | Filename for the output database.                       |
| `COMPANY_BATCH_SIZE`     | `5000`                                                | Number of records to process in a single batch.         |
| `COMPANY_TOTAL_RECORDS`  | `0` (process all)                                     | Limit the number of records to process (for testing).   |
| `SKIP_INVALID_RECORDS`   | `true`                                                | If true, skips records that fail validation.            |
| `CONTAINER_MODE`         | `false`                                               | A flag indicating if running inside a Docker container. |

## 6. Output Verification

After the process completes, run these SQL queries on the target database file to validate the output.

**1. Check for Primary Key Uniqueness:** (Should return 0 rows)

```sql
SELECT CompanyNumber, COUNT(*) 
FROM CompanyWithVectors 
GROUP BY CompanyNumber 
HAVING COUNT(*) > 1;
```

**2. Check for Null Company Numbers:** (Should return 0)

```sql
SELECT COUNT(*) 
FROM CompanyWithVectors 
WHERE CompanyNumber IS NULL;
```

**3. Verify Total Record Count:**

```sql
SELECT COUNT(*) FROM CompanyWithVectors;
```
