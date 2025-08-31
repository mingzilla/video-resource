# Component 5 - similarity search - backend

- Purpose of this step - embed user queries and search vectors in Qdrant for similar columns

```text
- 1. Input/Output
- 2. Docker - Embedding + VDB
- 3. Search Pipeline
- 4. Making a Request
```

## 1. Input / Output

### Input - User Query

```text
Query: "company name fields"
Top K: 5
Collection: columns_metadata__2025-08
```

### Output - Ranked Results

```json
{
  "query": "company name fields",
  "collection": "columns_metadata__2025-08",
  "top_k": 5,
  "timing": {
    "embedding_ms": 45.2,
    "search_ms": 12.8,
    "total_ms": 58.0
  },
  "total_results": 5,
  "results": [
    {
      "id": "029af46b-31fb-552c-ad82-d35b6c7ebc00",
      "score": 0.8945,
      "payload": {
        "column_identifier": "ClassifiedCompaniesRelational_Jul2025__ClassifiedCompaniesRelational__CompanyName",
        "column_name": "CompanyName",
        "table_name": "ClassifiedCompaniesRelational",
        "description": "CompanyName - name of a registered company",
        "data_type": "VARCHAR"
      }
    }
  ]
}
```

## 2. Docker - Embedding + VDB

| Name   | Ports     | Image                              | Type      | Purpose             |
|--------|-----------|------------------------------------|-----------|---------------------|
| nomic  | 11435     | mingzilla/ollama-nomic-embed:1.0.2 | embedding | Query vectorization |
| qdrant | 6333,6334 | qdrant/qdrant:v1.15.3              | vdb       | Vector storage      |

## 3. Search Pipeline

### 3.1. Query Embedding

```text
User Query: "company name fields"
    ↓
[Embedding Client] → API Call → "http://localhost:11435/api/embeddings"
    ↓
Query Vector: [0.12, -0.34, 0.56, ...]  # 768 dimensions
```

**Embedding Payload:**

```json
{
  "model": "nomic-embed-text",
  "prompt": "company name fields"
}
```

### 3.2. Vector Search

```text
Query Vector: [0.12, -0.34, 0.56, ...]
    ↓
[Qdrant Client] → Search Request → Collection: columns_metadata__2025-08
    ↓
Ranked Results: Top K by cosine similarity
```

**Search Payload:**

```text
{
  "vector": [0.12, ...],
  "limit": 5,
  "score_threshold": 0.7,  // lowest score
  "with_payload": true,    // include payload in the response
  "with_vector": false     // include vectors in the response
}
```

### 3.3. Response Processing

```text
Qdrant Results
    ↓
[Result Processor] → Format + Score + Metadata
    ↓  
Structured Response: JSON with timing + results
```

## 4. Usage Examples

### CLI Search

```bash
./scripts_sh/015_search.sh "company name fields" 10 columns_metadata__2025-08
./scripts_sh/015_search.sh "financial data" 5 columns_metadata__2025-08 --json
```

### Python API

```python
from similarity_search import SimilaritySearchOrchestrator
from shared_utils.config import get_config, SchemaInfoConfig015

config = SchemaInfoConfig015.from_config(get_config())
orchestrator = SimilaritySearchOrchestrator(config)

results = await orchestrator.search(
    query="company name fields",
    collection_name="columns_metadata__2025-08",
    top_k=5,
    score_threshold=0.7
)
```