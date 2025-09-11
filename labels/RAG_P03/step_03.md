# Step 3: Vector Database (VDB) Upload

```text
[VDB Upload]
|-- 1. Purpose
|-- 2. System Design & Data Flow
|-- 3. Qdrant Collection & Point Structure
|-- 4. Processing & Performance Strategy
|-- 5. Qdrant Service Interaction
|-- 6. Configuration
|-- 7. Error Handling
|-- 8. Output Result and Verification
```

## 1. Purpose

This document outlines Step 3 of the company search pipeline. The purpose of this step is to transfer the vectorized company data from the local DuckDB file into a dedicated, high-performance vector database (Qdrant). This makes the vectors and their associated metadata available for fast and scalable similarity searches.

**Key Challenges Addressed:**

- **Performance:** Uploading millions of high-dimensional vectors is a network and database intensive operation that can take hours.
- **Transactional Integrity:** The process involves two separate databases (DuckDB and Qdrant), making it difficult to guarantee that an update is perfectly atomic across both.
- **Resumability:** Tracking the upload progress is complex. A simple failure could mean starting the entire multi-hour process from scratch (see section 6.1).
- **Dependency Management:** The process relies on a healthy and available Qdrant service.

## 2. System Design & Data Flow

The VDB upload process reads from the local database, transforms the data in-memory, and uploads it to the external Qdrant service.

```text
[Target DuckDB: CompanyWithVectors]
           |
           | 1. Read batch of companies where Vector IS NOT NULL
           V
[VDB Upload Service]
           |
           | 2. Transform records to Qdrant Point format
           |    (ID, Vector, Payload)
           V
[Qdrant Client Service]
           |
           | 3. PUT /collections/{name}/points with batch of points
           V
[Qdrant Vector DB]
           |
           | 4. Stores points for searching
           V
[Repeat until all vectorized records are uploaded]
```

## 3. Qdrant Collection & Point Structure

Each company record from DuckDB is transformed into a Qdrant `Point`.

- **`id`**: A deterministic UUID generated from the `CompanyNumber` (point_uuid = uuid.uuid5(namespace, company_number)). Re-uploading the same company will overwrite it, not create a duplicate.
- **`vector`**: The `FLOAT[384]` array from the `Vector` column.
- **`payload`**: A JSON object containing the metadata for filtering and display (`company_number`, `company_name`, `active`, `city`).

## 4. Processing & Performance Strategy

- **Database Batching:** Reads a batch of vectorized records from DuckDB (controlled by `COMPANY_BATCH_SIZE`).
- **Qdrant Upsert Batching:** Uploads a batch of transformed points to the Qdrant API (controlled by `COMPANY_QDRANT_UPSERT_BATCH_SIZE`).
- **Data Transformation:** A static `CompanyPointTransformer` utility converts database records into the Qdrant `Point` format.

## 5. Qdrant Service Interaction

- **Health Check:** Before any upload begins, the service pings the Qdrant service to ensure it is online.
- **Automatic Collection Creation:** If the target collection does not exist, the service creates it with the correct vector size (384), distance metric (Cosine), and keyword indexes on payload fields.
- **Batch Upsert:** Data is uploaded using the `PUT /collections/{name}/points` endpoint.

## 6. Configuration

Configuration is handled exclusively through environment variables.

| Environment Variable               | Default Value           | Purpose                                                       |
|------------------------------------|-------------------------|---------------------------------------------------------------|
| `COMPANY_TARGET_DB_FILE`           | `..._minilm.duckdb`     | The DuckDB file to read vectorized records from.              |
| `COMPANY_BATCH_SIZE`               | `10`                    | The number of records to read from DuckDB in one batch.       |
| `COMPANY_QDRANT_UPSERT_BATCH_SIZE` | `100`                   | The number of points to upload to Qdrant in a single request. |
| `COMPANY_QDRANT_URL`               | `http://localhost:6333` | The root URL of the Qdrant service.                           |
| `COMPANY_COLLECTION_PREFIX`        | `company_search`        | The prefix for the Qdrant collection name.                    |

## 7. Error Handling

| Scenario                       | Handling Mechanism                                                                           |
|--------------------------------|----------------------------------------------------------------------------------------------|
| **Qdrant Service Unavailable** | The initial health check fails, and the process exits gracefully with a clear error message. |
| **Vector Dimension Mismatch**  | The `CompanyPointTransformer` validates vector dimensions. Invalid records are skipped.      |
| **Qdrant API Error**           | If the upsert request fails, the error is logged, and the process stops.                     |

## 8. Output Result and Verification

After the process runs:
- Qdrant status - likely to turn Yellow for indexing, which takes minutes
- Point count accuracy check
- Approx Count - This can be trusted as actual count

Data Verification:
- use small amount of data to test it first
- then verify data order of small batches
- intentional termination to see if it resumes correctly