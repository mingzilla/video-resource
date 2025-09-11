# Similarity Search API

```text
[Similarity Search API]
|-- 1. Purpose
|-- 2. System Design & Architecture
|      |-- 2.1 High-Level Flow
|      +-- 2.2 Component Architecture
|-- 3. API Endpoints
|-- 4. Search Request & Response Format
|      |-- 4.1 Request Body
|      +-- 4.2 Response Body
|-- 5. Key Implementation Details
|      |-- 5.1 OllamaQdrantClient Utility
|      |-- 5.2 Payload Filtering
|      +-- 5.3 Web UI
|-- 6. Execution & Scripts
|      |-- 6.1 API Server
|      +-- 6.2 Command-Line Search Tool
|-- 7. Configuration
+-- 8. Output Verification
```

## 1. Purpose

This document outlines Step 4 of the company search pipeline. The purpose of this step is to expose the search functionality via a FastAPI web server. It provides a REST API for performing semantic similarity searches on the company data stored in Qdrant and includes a basic web interface for interactive testing.

**Key Challenges Addressed:**

- **Real-time Performance:** The API must provide low-latency responses, which involves two network-bound steps: generating an embedding for the user's query and then searching the Qdrant database.
- **Dependency Health:** The API acts as a facade over two other critical services (the embedding model and Qdrant). It must be resilient to their potential failures and report health status accurately.
- **Search Relevance:** The system must effectively translate user queries and filter parameters into a valid Qdrant search request that returns meaningful, relevant results.
- **Scalability:** The API server needs to be able to handle multiple concurrent user requests efficiently.

## 2. System Design & Architecture

### 2.1 High-Level Flow

A user's search query is sent to the API, which then orchestrates communication with the embedding service and the Qdrant database to return a ranked list of similar companies.

```text
[User / Client]
      |
      | 1. POST /api/v1/search with JSON query
      V
[FastAPI Server (main.py)]
      |
      | 2. Forwards request to OllamaQdrantClient
      V
[OllamaQdrantClient Utility]
      |
      | 3. Get embedding for query text --> [Embedding Service]
      |
      | 4. Search Qdrant with vector ---> [Qdrant Vector DB]
      |
      | 5. Receive ranked results
      V
[FastAPI Server (main.py)]
      |
      | 6. Format and return JSON response
      V
[User / Client]
```

### 2.2 Component Architecture

The architecture for this step is simplified, relying on a reusable client to handle interactions with the other services. This is a notable simplification from earlier design documents.

- **`main.py`**: The main FastAPI application. It defines the API endpoints, handles HTTP requests and responses, and serves the static web UI.
- **`shared_utils/ollama_qdrant_client.py`**: A reusable utility that encapsulates the core logic. It takes a search query, gets the vector embedding from the embedding service, and then executes the search against the Qdrant database.
- **`py_args.py`**: Consumes the `EnvVarDefaults` to provide configuration to the application.

## 3. API Endpoints

The application exposes the following endpoints:

| Method | Path                   | Description                                              |
|--------|------------------------|----------------------------------------------------------|
| `POST` | `/api/v1/search`       | The primary endpoint for performing similarity searches. |
| `GET`  | `/api/v1/health`       | Checks the health of the API and its dependencies.       |
| `GET`  | `/api/v1/search/stats` | Provides basic statistics about the service.             |
| `GET`  | `/`                    | Serves the static HTML web UI for interactive searches.  |

## 4. Search Request & Response Format

### 4.1 Request Body

The `POST /api/v1/search` endpoint accepts a JSON body with the following structure:

```json
{
  "query": "text to search for",
  "limit": 10,
  "filters": {
    "city": "london",
    "active": true
  }
}
```

### 4.2 Response Body

A successful search returns a JSON object containing the ranked results.

```json
{
  "success": true,
  "results": [
    {
      "id": "...",
      "score": 0.895,
      "payload": {
        "company_name": "LONDON CONSTRUCTION LTD",
        "company_number": "01234567",
        "active": true,
        "city": "london"
      }
    }
  ]
}
```

## 5. Key Implementation Details

### 5.1 OllamaQdrantClient Utility

Instead of building a complex service layer within Step 4, the logic was consolidated into a reusable `OllamaQdrantClient` located in `shared_utils`. This client is responsible for the two-step search process:

1. **Get Embedding:** It takes the user\'s query text and makes a `POST` request to the embedding service to get the corresponding vector.
2. **Search Qdrant:** It uses the vector from the first step to perform a similarity search in the Qdrant database.

### 5.2 Payload Filtering

The API supports filtering on the metadata stored in the Qdrant point payloads. The `004_search.sh` script contains a Python snippet that demonstrates how simple key-value strings (e.g., `status:active,city:leeds`) are parsed and converted into the structured JSON format that Qdrant\'s filter queries require.

### 5.3 Web UI

The application serves a simple, static web page from the `src/company_search__004__similarity_search/static/` directory. This `index.html` file provides a user-friendly interface for making search requests to the API without needing a separate client.

## 6. Execution & Scripts

Two shell scripts are provided for interacting with this step.

### 6.1 API Server

- **`work/company_search/scripts_sh/004_similarity_search_api.sh`**: This is the primary script for running the application. It validates dependencies, checks for available ports, and starts the FastAPI server using `uvicorn`.

### 6.2 Command-Line Search Tool

- **`work/company_search/scripts_sh/004_search.sh`**: This is a powerful command-line utility for developers. It allows you to perform searches directly from your terminal without needing to run the full API server. It handles the process of getting an embedding for your query text and then sending the search request to Qdrant.

## 7. Configuration

Key configuration is handled via environment variables.

| Environment Variable           | Default Value                          | Purpose                                                     |
|--------------------------------|----------------------------------------|-------------------------------------------------------------|
| `COMPANY_API_HOST`             | `0.0.0.0`                              | The host address for the FastAPI server to bind to.         |
| `COMPANY_API_PORT`             | `19000`                                | The port for the FastAPI server.                            |
| `COMPANY_API_WORKERS`          | `1`                                    | The number of Uvicorn worker processes.                     |
| `COMPANY_API_RELOAD`           | `false`                                | Set to `true` for auto-reloading in development.            |
| `COMPANY_EMBEDDING_URL`        | `http://localhost:30010/v1/embeddings` | The URL of the embedding service.                           |
| `COMPANY_QDRANT_URL`           | `http://localhost:6333`                | The URL of the Qdrant service.                              |
| `COMPANY_SEARCH_DEFAULT_LIMIT` | `10`                                   | The default number of search results to return.             |
| `COMPANY_SEARCH_MAX_LIMIT`     | `100`                                  | The maximum number of search results that can be requested. |

## 8. Output Verification

You can test the API endpoints using `curl` or by accessing the web UI.

**1. Health Check:**

```bash
curl http://localhost:19000/api/v1/health
```

**2. Search Request:**

```bash
curl -X POST http://localhost:19000/api/v1/search \
-H "Content-Type: application/json" \
-d '{"query": "construction in london"}'
```

**3. Web UI:**
Open a web browser and navigate to `http://localhost:19000`.

```
