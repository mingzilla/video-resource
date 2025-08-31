# Component 6 - similarity search - api+ui

- Purpose of this step - provide web interface and REST API for schema similarity search

```text
- 1. Input/Output  
- 2. Web Architecture
- 3. API Endpoints
- 4. UI Interface
```

## 1. Input / Output

### Input - HTTP Requests

**Search Request:**

```
POST /api/search
{
  "query": "company name fields",
  "top_k": 5,
  "collection_name": "columns_metadata__2025-08",
  "score_threshold": 0.7
}
```

**Health Check:**

```http
GET /api/health
```

### Output - HTTP Responses

**Search Response:**

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
      "score": 0.8945,
      "payload": {
        "column_name": "CompanyName",
        "table_name": "ClassifiedCompaniesRelational",
        "description": "CompanyName - name of a registered company",
        "data_type": "VARCHAR",
        "sample_data": [
          "HOUSE OF MIAHS LIMITED",
          "KONSTNAR LIMITED"
        ]
      }
    }
  ]
}
```

## 2. API Endpoints

### 2.1. Core Endpoints

| Method | Endpoint         | Purpose                    | Auth |
|--------|------------------|----------------------------|------|
| GET    | /                | Web UI homepage            | -    |
| GET    | /api/health      | Service health check       | -    |
| POST   | /api/search      | Similarity search          | -    |
| GET    | /api/collections | List available collections | -    |
| GET    | /docs            | OpenAPI documentation      | -    |

### 2.2. Search API Details

**Endpoint:** `POST /api/search`

**Request Model:**

```python
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(5, ge=1, le=100)
    collection_name: str = Field("schema_info")
    score_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
```

**Response Model:**

```python
class SearchResponse(BaseModel):
    query: str
    collection: str
    top_k: int
    timing: Dict[str, float]
    total_results: int
    results: List[Dict[str, Any]]
```

### 2.3. Health Check API

**Endpoint:** `GET /api/health`

**Response:**

```json
{
  "status": "healthy",
  "services": {
    "embedding_service": true,
    "qdrant_service": true,
    "collections": [
      "columns_metadata__2025-08",
      "columns_metadata__2025-07"
    ]
  },
  "timestamp": 1703123456.789
}
```

### 2.4. Error Responses

```json
{
  "detail": {
    "error": "embedding_service_unavailable",
    "message": "Cannot connect to embedding service at http://localhost:11435",
    "timestamp": 1703123456.789,
    "suggestions": [
      "Check if Ollama is running: ollama serve",
      "Verify embedding service configuration"
    ]
  }
}
```

## 3. UI Interface

### 3.1. Web UI Features

```text
[Search Interface]
|-- Query Input     ← Text field for user queries
|-- Collection      ← Dropdown for time periods  
|-- Top K           ← Slider for result count
|-- Score Filter    ← Threshold for quality
+-- Results Display ← Formatted search results
```

### 3.2. Collection Selection

```html
<select id="collection">
    <option value="columns_metadata__2025-08">2025-08</option>
    <option value="columns_metadata__2025-07">2025-07</option>
</select>
```

### 3.3. Server Startup

```bash
./scripts_sh/016_start_web_server.sh 18000

# Output:
🚀 Starting FastAPI server...
   Web Interface: http://localhost:18000  
   API Documentation: http://localhost:18000/docs
   Health Check: http://localhost:18000/api/health
```

## Usage Examples

### Start Web Server

```bash
# Default port 18000
./scripts_sh/016_start_web_server.sh

# Custom port  
./scripts_sh/016_start_web_server.sh 8080
```

### API Calls

```bash
# Health check
curl http://localhost:18000/api/health

# Search request
curl -X POST http://localhost:18000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "company name fields",
    "top_k": 5,
    "collection_name": "columns_metadata__2025-08"
  }'
```

### Web Interface

```text
Open browser → http://localhost:18000
    ↓
Enter query → "financial data columns"
    ↓
Select collection → 2025-08
    ↓ 
Click Search → View ranked results
```