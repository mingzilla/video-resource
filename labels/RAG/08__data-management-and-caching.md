# Vector DB Data Management, Data Read-Write, Caching Strategy

## 1. Context: MySQL to Vector DB Pipeline

Enable semantic similarity search on business data

```text
[Data Flow Context]

[Business Domain]           [Vector Search Domain]
       │                            │
┌──────▼──────┐              ┌──────▼───────┐
│   MySQL     │              │   Qdrant     │
│ • laptops   │─── embed ───▶│ • vectors    │
│ • specs     │              │ • metadata   │
│ • reviews   │              │ • similarity │
└─────────────┘              └──────────────┘
       │                            │
       ▼                            ▼
[Transactional]              [Search & AI]
```

## 2. Specific Design with Prerequisite: Small Data Scale

### Decision - No Persistent Volumes

Prerequisite - Small data size (<5000 records) enables fast rebuilds (<10 seconds)

- **Vector Database**: Qdrant runs without persistent volumes
- **Fast Rebuilds**: <10 seconds for <5000 records from MySQL cache
- **Cloud Friendly**: No data migration needed for deployments
- **Recovery Capability**: System can rebuild if vector database fails

### Decision - Cache Embeddings

- Computed embeddings stored in relational database
- Reason - Takes e.g. 0.5s to embed text per record

## 3. Decision: Clean Rebuild Strategy & MySQL Cache

```text
Stateless Container Recovery Sequence:

[User Query]    [Application]      [MySQL Cache]   [Embedding Service]  [Qdrant VDB]
     |              |                    |                    |            |
     |--Query------>|                    |                    |            |
     |              |------Check VDB-------------------------------------->|
     |              |<-----Empty VDB ? ------------------------------------|
     |              |                    |                    |            |
     |              |                    |                    |            |
     |              | (If VDB Empty)     |                    |            |
     |              |---+                |                    |            |
     |              |   | (every item)   |                    |            |
     |              |   |--Get Vectors-->| (if not present)   |            |
     |              |   |                |---+                |            |
     |              |   |                |   |--Embed Text--->|            |
     |              |   |                |   |<-Vectors-------|            |
     |              |   |                |<--+                |            |
     |              |   |                |(store)             |            |
     |              |   |<-Vectors-------|                    |            |
     |              |   |                |                    |            |
     |              |   |                |                    |            |
     |              |   |--Rebuild VDB------------------------------------>|
     |              |   |<-Ready in 10s------------------------------------|
     |              |   |                |                    |            |
     |              |<--+                |                    |            |
     |              |                    |                    |            |
     |      (handle user query)          |                    |            |
     |              |                    |                    |            |
     |<-Response----|                    |                    |            |
     |              |                    |                    |            |
```

## 4. Database Design: Two-Tables

| Component                | **Primary Table**        | **Vector Cache Table**                         |
|--------------------------|--------------------------|------------------------------------------------|
| **Name**                 | `laptops`                | `laptop_vectors`                               |
| **Purpose**              | Business data storage    | Embedding cache                                |
| **Key Fields**           | `id`, `updated_at_ms`    | `source_id`, `source_updated_at_ms`, `vectors` |
| **Update updated_at_ms** | Sub-domain table changes |                                                |
| **Update Embedding**     |                          | Embedding generation                           |
| **Transaction**          | ACID compliant           | Asynchronous                                   |
| **Consistency**          | Immediate                | Eventual                                       |

Note:

- `laptops.updated_at_ms`: `laptops` table has associated sub-domain tables. a change to sub-domain tables should trigger a change of `laptops.updated_at_ms`
- `laptop_vectors.source_updated_at_ms`: used to decide if data is out of date

```text
[Table Relationship]

┌─────────────────┐      ┌─────────────────┐
│    laptops      │      │ laptop_vectors  │
│                 │      │                 │
│ id (PK)         │<─────│ source_id (FK)  │
│ updated_at_ms   │      │ source_upd_at_ms│
│ name            │      │ vectors (BLOB)  │
│ specs           │      │                 │
└─────────────────┘      └─────────────────┘
         │                         │
         ▼                         ▼
 [Business Logic]         [Vector Search]
```

### Why Separate Embedding Table

- **Timing Difference**: Business data creation/update is transactional, embedding generation takes ~0.5 seconds later
- **Transactional Completeness**: Maintains ACID properties for laptops and related sub-domain tables
- **Asynchronous Processing**: Allows upsert of single record or wholesale insert when laptop_vectors is empty
- **Source Isolation**: Business table `updated_at_ms` should not be affected by updating laptop_vectors

## 5. Read-Write Operations

**Remove Vector Record**:

- When laptop record deleted from MySQL (immediate consistency)

**Upsert Vector Record**:

- When laptop record added/updated in MySQL
- When vector database is empty (full rebuild)

**Create All Vector Records**:

- System startup with empty vector database
- Explicit rebuild requests
- Collection corruption detection
