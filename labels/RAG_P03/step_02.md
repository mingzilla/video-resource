# Step 2: Company Name Vectorization

```text
[Vectorization]
|-- 1. Purpose
|-- 2. System Design & Data Flow
|      |-- 2.1 High-Level Data Flow
|      |-- 2.2 Component Architecture
|      +-- 2.3 Input / Output
|-- 3. Batch Processing and Data Integrity
|      |-- 3.1 Reading
|      |-- 3.2 Processing
|      +-- 3.3 Writing
|-- 4. Embedding Service Interaction
|      |-- 4.1 Health Check
|      +-- 4.2 Vector Generation
|-- 5. Configuration
+-- 6. Error Handling
+-- 7. Output Verification
```

## 1. Purpose

This document outlines Step 2 of the company search pipeline. The primary goal of this step is to populate the `Vector` column of the `CompanyWithVectors` table. It reads company records that have not yet been vectorized, generates a 384-dimensional vector embedding from the `CompanyName` using an external embedding service, and updates the corresponding records in the database.

This process enriches the data from Step 1, making it ready for semantic search and upload to a vector database in subsequent steps.

**Key Challenges Addressed:**

- **Scalability of Embedding:** The core challenge is generating embeddings for over 10 million records, which is an inherently slow, computationally intensive process.
- **Performance Optimization:** The overall speed is heavily dependent on the embedding model's performance. Key optimization strategies include:
    - **Effective Batch Processing:** The embedding service must be able to process batches efficiently. Make sure embedding service can make use of multiple CPUs. e.g. by checking task manager CPU section when performing embedding.
    - **Hardware Acceleration:** Utilizing GPUs for the embedding model can lead to a dramatic (10x or more) improvement in processing speed.
    - **Horizontal Scaling:** Since the embedding process is stateless, it can be parallelized across multiple machines, each running an instance of the embedding model, to significantly reduce the overall processing time.
- **Model Selection & Storage:** The choice of the embedding model has major downstream consequences. A smaller, efficient model (like the chosen 384-dimension `all-MiniLM-L6-v2`) is preferred if it provides acceptable search quality.
    - **Storage** - This decision directly impacts the storage size of the output in the DuckDB file and, subsequently, the memory and storage requirements for the Qdrant vector database.
    - **Sample** - It implies a strategy of testing the end-to-end system with a smaller data sample before committing to the multi-hour process of embedding the full 10 million records.
- **Data Integrity - Row Matching:** Ensuring the generated vector for a company name is correctly written back to that specific company's record without any mismatches, especially in a long-running, batch-oriented process.

## 2. System Design & Data Flow

### 2.1 High-Level Data Flow

The vectorization process is a continuous loop that reads from and writes back to the same database table, interacting with an external service to generate the embeddings.

```text
[Target DuckDB: CompanyWithVectors]
           |
           | 1. Read batch of companies where Vector IS NULL
           V
[Vectorization Service]
           |
           | 2. Extract CompanyName text
           V
[Embedding Service]
           |
           | 3. POST /v1/embeddings with batch of names
           V
[Vectorization Service]
           |
           | 4. Receive 384-dim vectors
           V
[Target DuckDB: CompanyWithVectors]
           |
           | 5. UPDATE Vector column for corresponding companies
           V
[Repeat until no records have NULL vectors]
```

### 2.2 Component Architecture

The process uses a 3-tier architecture, with the `VectorizationService` orchestrating the work between the database and the `EmbeddingService`.

```text
[main.py / py_args.py]
     | (Entry Point & Config)
     V
[VectorizationService]
     | (Orchestrates the process)
     +-----> [EmbeddingService]
     |         (Handles HTTP communication with the embedding model)
     |
     +-----> [TargetDbRepository]
               (Reads records needing vectors and writes vectors back)
```

### 2.3 Input / Output

Unlike Step 1, this step does not have separate input and output files. It operates entirely on the `CompanyWithVectors` table within the target DuckDB file created in the previous step.

- **Input:** Rows from `CompanyWithVectors` where `Vector IS NULL` and `CompanyName IS NOT NULL`.
- **Output:** The same rows in `CompanyWithVectors`, but with the `Vector` column populated with a `FLOAT[384]` array.

## 3. Batch Processing and Data Integrity

The entire vectorization process is a loop (`Read -> Embed -> Write`) designed for efficiency, resumability, and data integrity. The strategy ensures that each vector is correctly matched to its company and that the process can be stopped and restarted safely.

### The Read-Embed-Write Cycle

Here is the step-by-step process for a single batch:

**1. Reading a Batch (The "Read")**

The cycle begins by fetching a batch of records that need to be vectorized. This is achieved with a query that is both efficient and resumable.

- **Finding Work:** - The `WHERE Vector IS NULL` clause ensures that only records that have not yet been processed are selected.
- **Efficient Pagination:** - To avoid re-scanning the entire table for every batch, the query uses a `WHERE CompanyNumber > ?` clause. The service tracks the `CompanyNumber` of the last record from the previous batch and uses it as the starting point for the next, allowing the database to use its index to jump directly to the required data.
- **Deterministic Ordering:** - The `ORDER BY CompanyNumber ASC` clause is critical. It guarantees that the records are always processed in the same, predictable lexicographical order, which is essential for the pagination to work reliably.
- **SQL Order and Code Order** - `last_company_number = batch_companies[-1].company_number` - The code respects DB returned order, because re-sorting in code may not have the same result as `SQL ORDER BY ASC`
- **Resumability:** - Since `last_company_number` is in-memory. When the process restarts, `last_company_number` is "0", it then relies on `Vector IS NULL` to find where to start. It works but just slower.

**Read Query Snippet:**

```sql
SELECT CompanyNumber, CompanyName, Active, City, Vector
FROM CompanyWithVectors
WHERE CompanyNumber > ? AND Vector IS NULL AND CompanyName IS NOT NULL
ORDER BY CompanyNumber ASC
LIMIT ?
```

Efficiency Strategy:

- **Indexing a Value (`CompanyNumber > ?`):** An index on `CompanyNumber` and query `WHERE CompanyNumber > 'value'` - `value` is CONSTANTLY at a specific row, which is indexed
- **Indexing a Condition (`Vector IS NULL`):** An index on `Vector IS NULL` - the first NULL value position is DYNAMIC, an index cannot work out the position without performing a scan
- **Clever Trick:** `WHERE CompanyNumber > ? AND Vector IS NULL` - This allows jumping directly to a specific CompanyNumber, then start scanning `IS NULL`. Since the first item is the expected item, `IS NULL` won't cause slowness

**2. Processing and Embedding (The "Process")**

Once a batch of records is read into memory, the service prepares them for the embedding API.

- It iterates through the records from the database.
- It filters out any records that cannot be vectorized (e.g., those with a `NULL` `CompanyName`).
- It builds two **parallel lists** in memory: one containing the full, valid `CompanyVectorRecord` objects and another containing just the `CompanyName` strings.
- Because these lists are built in the same loop, the record at `valid_companies[i]` is guaranteed to correspond to the name at `company_names[i]`.
- The list of `company_names` is then sent to the embedding service
    - gathers a list of company names and sends that entire list in a single API request to the embedding service.
    - The service then processes all of those names
    - and returns a corresponding list of vectors in a single response - See Section 4.2

**3. Updating the Database (The "Write")**

This is the final and most critical step for data integrity.

- The embedding service returns a list of vectors that is guaranteed to be in the same order as the `company_names` list that was sent.
- The service now has two parallel lists: the `valid_companies` list (containing the `CompanyNumber` for each record) and the `vectors` list.
- The code pairs the `CompanyNumber` from `valid_companies[i]` with the `vector` from `vectors[i]`.
- These pairs are then used in a high-performance **bulk update** operation. Using the unique `CompanyNumber` in the `WHERE` clause for the update guarantees that each vector is written to the correct row.

**Write Query (Conceptual):**

```sql
-- This is a conceptual representation of the bulk update.
UPDATE CompanyWithVectors
SET Vector = temp_updates.Vector
FROM (VALUES (?, ?), (?, ?), ...) AS temp_updates(CompanyNumber, Vector)
WHERE CompanyWithVectors.CompanyNumber = temp_updates.CompanyNumber;
```

## 4. Embedding Service Interaction

### 4.1 Health Check

Before starting the main processing loop, the `VectorizationService` makes a `GET` request to the embedding service's health check endpoint (e.g., `http://localhost:30010/health`). This pre-flight check ensures the external service is available and prevents the system from entering a failure loop if the dependency is down.

### 4.2 Batch Vector Generation

Embeddings are generated by (e.g., `POST` `http://localhost:30010/v1/embeddings`).

- A key performance feature of the system is the use of batch processing when communicating with the embedding service.
- This minimizes the overhead of network latency

**Request Payload Example - Batch:**

```json
{
  "input": [
    "MARINE AND GENERAL MUTUAL LIFE",
    "KENTSTONE PROPERTIES LIMITED"
  ],
  "model": "all-MiniLM-L6-v2"
}
```

**Response Handling:** The embedding service returns data with the same order:

```text
{
  "data": [
    { "embedding": [0.1, 0.2, ...] },
    { "embedding": [0.4, 0.5, ...] }
  ]
}
```

## 5. Configuration

Configuration is handled exclusively through environment variables, as defined in `shared_utils/env_var_defaults.py` and consumed by `py_args.py`.

| Environment Variable           | Default Value                          | Purpose                                                       |
|--------------------------------|----------------------------------------|---------------------------------------------------------------|
| `DB_MOUNT_PATH`                | `.../Databases`                        | Base directory for DuckDB files.                              |
| `COMPANY_TARGET_DB_FILE`       | `..._minilm.duckdb`                    | The database file to read from and write to.                  |
| `COMPANY_BATCH_SIZE`           | `10`                                   | The number of records to read from the database in one go.    |
| `COMPANY_EMBEDDING_BATCH_SIZE` | `10`                                   | The number of names to send to the embedding service at once. |
| `COMPANY_TOTAL_RECORDS`        | `20` (for testing)                     | Limits the total number of records to process in a run.       |
| `COMPANY_EMBEDDING_URL`        | `http://localhost:30010/v1/embeddings` | The API endpoint for generating vectors.                      |
| `COMPANY_EMBEDDING_HEALTH_URL` | `http://localhost:30010/health`        | The health check endpoint for the embedding service.          |
| `COMPANY_EMBEDDING_MODEL`      | `all-MiniLM-L6-v2`                     | The name of the embedding model to use.                       |
| `COMPANY_EMBEDDING_TIMEOUT`    | `30`                                   | Timeout in seconds for the embedding API request.             |

## 6. Error Handling

The system is designed to be robust and handle common failure scenarios gracefully.

| Scenario                          | Handling Mechanism                                                                                                 |
|-----------------------------------|--------------------------------------------------------------------------------------------------------------------|
| **Embedding Service Unavailable** | The initial health check fails, and the process exits gracefully with a clear error message.                       |
| **Invalid `CompanyName`**         | Records with `NULL` or empty `CompanyName` are skipped during the database read (`WHERE CompanyName IS NOT NULL`). |
| **Embedding API Error**           | If the API returns a non-200 status, the batch fails, and the process stops, logging the error message.            |
| **Vector Count Mismatch**         | If the number of vectors returned by the API does not match the number of names sent, the process stops.           |

## 7. Output Verification

After the process runs, you can verify the results by querying the target database.

**1. Count Vectorized vs. Pending Records:**

```sql
SELECT 
    COUNT(CASE WHEN Vector IS NOT NULL THEN 1 END) as vectorized_count,
    COUNT(CASE WHEN Vector IS NULL THEN 1 END) as pending_count
FROM CompanyWithVectors;
```

**2. Inspect a Sample Vector:**

```sql
SELECT CompanyName, Vector FROM CompanyWithVectors WHERE Vector IS NOT NULL LIMIT 1;
```