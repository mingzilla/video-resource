# Idempotent Data Upload to Qdrant with Progress Tracking

## 1. Problem: Handling Failures in Batch Data Uploads

When uploading large datasets in batches, we need to enable midway failure and resume. If 51/100 of a batch has been uploaded, when resuming,

- How can we track progress? (we cannot iterate qdrant to get progress identifier)
- How does Qdrant identify and handle duplicate records?
- How can we design the pipeline to be recoverable and idempotent?

## 2. Question: How does Qdrant handle duplicate records during an upload?

Qdrant allows `upsert by point_uuid`: exits -> override; missing -> create

## 3. Proposed Solution

- ID: Pre-Generate Qdrant uuid at step 2, batch save as `CompanyWithVectors(CompanyNumber, Vector, QdrantUuid)`
- Tracking: Add a `BatchProgress(ProcedureName, LastProcessedId)` table, after finishing saving a batch, set the last processed id immediately to progress table
    - step 2 LastProcessedId - CompanyWithVectors.CompanyNumber
    - step 3 LastProcessedId - CompanyWithVectors.CompanyNumber
    - Read records: use `ORDER BY CompanyNumber ASC`
    - Write to BatchProgress, use e.g. `batch_companies[-1].company_number` to respect the `SQL ASC` last record
- Resume from LastProcessedId:
    - Step 2 Database: will not start from '0' to find the 1st `NOT NULL` record
    - Step 3 Qdrant Uploading: use batch upsert, so `51/100` would restart the whole batch when uploading
