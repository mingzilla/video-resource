# Component 4 - vdb

- Purpose of this step - create vdb collection, store data to vdb

```text
- 1. Collection Creation
- 2. Indexes
- 3. Upload - Data Format
- 4. Docker - Volume Out?
```

```yaml
  qdrant:
    image: qdrant/qdrant:latest
    container_name: schema-info-qdrant-2025-08-v01
    ports:
      - "18012:6333"
      - "18013:6334"
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: no
```

## 1. Collection Creation

- Share one db - Different Collections for Different Months - Month suffix

### 1.1. Explanation

```text
Fields
|-- vectors
|   |-- "vectors": {size, distance}               - default field name is `vector`
|   +-- "vectors": {embedding: {size, distance}}  - to use e.g. "embedding" - need nested structure
|
|-- "size": 768          - 768 should match embedding
|-- "distance": "Cosine" - search algorithm
|
|-- default_segment_number
|   |-- default - means it scales up and down based on number of documents
|   +-- segments - allows parallel searching, but it has additional resource cost
|
+-- replication_factor - JUST SET TO 1 -- why replication_factor this pointless:
    |-- it does not enable high availability
    +-- if you want parallel reading, you already define it on segments
```

Collection Creation:

```shell
curl -X PUT "$QDRANT_URL/collections/$COLLECTION_NAME" \
    -H "Content-Type: application/json" \
    -d '{
        "vectors": {
            "size": 768,
            "distance": "Cosine"
        },
        "optimizers_config": {
            "default_segment_number": 2
        },
        "replication_factor": 1
    }'
```

Store:

```json
{
  "points": [
    {
      "id": 1,
      "vector": [],
      "payload": {
        "text": "The quick brown fox jumps over the lazy dog."
      }
    }
  ]
}
```

Query

```shell
curl -X POST "$QDRANT_URL/collections/$COLLECTION_NAME/points/search" \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, 0.3],
    "limit": 10
  }'
```

### 1.2. Good Solution

Can just use model name as the key to store vectors.

- Vectors for model1 cannot be used by model2
- Enables multi-models comparison

Collection Creation:

```json
{
  "vectors": {
    "all-MiniLM-L6-v2": {
      "size": 384,
      "distance": "Cosine"
    },
    "nomic-embed-text": {
      "size": 768,
      "distance": "Cosine"
    }
  }
}
```

Store:

```json
{
  "points": [
    {
      "id": 1,
      "vector": {
        "all-MiniLM-L6-v2": [],
        "nomic-embed-text": []
      },
      "payload": {
        "text": "The quick brown fox jumps over the lazy dog."
      }
    }
  ]
}
```

Query

```shell
curl -X POST "$QDRANT_URL/collections/$COLLECTION_NAME/points/search" \
  -H "Content-Type: application/json" \
  -d '{
    "vector": {
      "name": "nomic-embed-text",
      "vector": [0.1, 0.2, 0.3]
    },
    "limit": 10
  }'
```

## 2. Indexes

- Why Index - Can be used for filtering
- Why Scripts - Use scripts to run python anyway
- Indexes on the `vector` field? - Not necessary, this is vdb's core feature

| column          | index type |
|-----------------|------------|
| column_name     | keyword    |
| data_type       | keyword    |
| table_name      | keyword    |
| null_percentage | float      |
| unique_count    | integer    |
| total_rows      | integer    |

```shell
curl -X PUT "$QDRANT_URL/collections/$COLLECTION_NAME/index" \
    -H "Content-Type: application/json" \
    -d '{
        "field_name": "column_name",
        "field_schema": "keyword"
    }'
```

## 3. Upload - Data Format

V3 Data Format and Qdrant data format are different - just convert to qdrant format, works if we use another vdb.

### 3.1. V3 Data Format

```json
{
  "ClassifiedCompaniesRelational_Jul2025__ClassifiedCompaniesRelational__CompanyName": {
    "column_name": "CompanyName",
    "data_type": "VARCHAR",
    "database_name": "ClassifiedCompaniesRelational_Jul2025",
    "null_percentage": 0.0,
    "sample_data": [
      "HOUSE OF MIAHS LIMITED",
      "KONSTNAR LIMITED",
      "B-SPOKE AUTOMOTIVE LIMITED",
      "CLARITY ULTRASOUND LIMITED",
      "FUNLINX UK LTD"
    ],
    "table_name": "ClassifiedCompaniesRelational",
    "total_rows": 10204100,
    "unique_count": 10026123,
    "description": "CompanyName - name of a registered company",
    "vector": [
      0.12
    ]
  }
}
```

### 3.2. Qdrant Data Format

- id: standard format for qdrant
- column_identifier: the key - unique in our system, but cannot use that as id

```json
{
  "id": "029af46b-31fb-552c-ad82-d35b6c7ebc00",
  "vector": [
    0.12
  ],
  "payload": {
    "column_identifier": "ClassifiedCompaniesRelational_Jul2025__ClassifiedCompaniesRelational__CompanyName",
    "column_name": "CompanyName",
    "data_type": "VARCHAR",
    "database_name": "ClassifiedCompaniesRelational_Jul2025",
    "table_name": "ClassifiedCompaniesRelational",
    "null_percentage": 0.0,
    "total_rows": 10204100,
    "unique_count": 10026123,
    "description": "CompanyName - name of a registered company",
    "sample_data": [
      "HOUSE OF MIAHS LIMITED",
      "KONSTNAR LIMITED",
      "B-SPOKE AUTOMOTIVE LIMITED",
      "CLARITY ULTRASOUND LIMITED",
      "FUNLINX UK LTD"
    ],
    "metadata_type": "column_metadata"
  }
}
```

## 4. Docker - Volume Out?

Stateless docker? - Can keep it stateless

- No volumes out, no maintenance
- Small data size, single source of truth - v3 data
- Version controlled v3 data - clear visibility about changes
- Multiple Months - just upload many months data
