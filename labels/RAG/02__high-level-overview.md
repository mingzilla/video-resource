# RAG System: High-Level Component Overview

```text
0. Services Included
1. Text Split Content Metadata
2. Embedding
3. Vector DB Qdrant
4. Filtering Metadata Efficiency
5. Reranking
6. Augmented Generation
7. Data Management & Caching
8. Rate Limiting & Locking
```

## 0. Services Included

| Service             | Function                    |
|---------------------|-----------------------------|
| [System]            | orchestration               |
| [Text Splitter]     | text -> chunks              |
| [Embedding Service] | chunk -> vectors            |
| [Vector DB]         | storage                     |
| [Reranking Service] | reorder chunks by relevance |
| [LLM Service]       | response generation         |

## 1. Text Split Content Metadata

Breaking documents into searchable chunks with structured metadata for efficient filtering.

- **Core Process**: Document -> Extract Structure -> Content Splitting + Metadata Generation -> Store in Vector DB
- **Metadata Strategy**: Group related attributes (CPU, RAM, Video Card) for optimal query performance
- **Filtering Advantage**: Pre-filter by metadata before vector search (1000 -> 25 chunks) then semantic matching

```text
[Document] -> [Smart Splitting] -> [Chunks + Metadata] -> [Vector DB Storage]
     |              |                      |                    |
     |              |                      |                    |
"Manual         [Structure         metadata: CPU=i9,        [Storage]
50 pages"       Based Split]       Video Card=Nvidia         [Indexing]
                [Overlap 10-20%]   Text: "Fantastic..."      [Querying]
```

## 2. Embedding

Converting text chunks to numerical vectors with model consistency and MySQL caching strategy.

- **Conversion**: Text -> Embedding Model -> Fixed-size Vector Array (768 or 1536 dimensions)
- **Model Choice**: Local (Ollama) excellent for stateless operations, Cloud (OpenAI) for production performance
- **Performance Bottleneck**: Embedding ~1s per chunk vs Vector DB storage ~10ms (100:1 ratio)
- **Caching Strategy**: Store embeddings in MySQL to avoid re-generation during vector database rebuilds

```text
[Text Input] -> [Embedding Model] -> [MySQL Cache] -> [Vector Database]
     |               |                    |              |
"Fantastic      [nomic-embed-text]    [Cache Hit?]    [Storage]
Lenovo laptop   [768 dimensions]      [1s -> 10ms]    [Ready for Search]
daily usage"    [Consistency Req]     [Rebuild Fast]  [Similarity Calc]
```

## 3. Vector DB Qdrant

Database selection focused on cost, performance, and deployment flexibility for RAG systems.

- **Selection Criteria**: Qdrant chosen for free OSS, excellent performance, Docker deployment, REST API
- **Multi-Node Challenge**: In-memory databases need complex synchronization, centralized VDB simpler
- **Authentication**: Nginx proxy provides consistent Bearer token format across all RAG components
- **Read-Only Strategy**: Immutable updates through URL swapping eliminates locking concerns

```text
Database Comparison Matrix:
                Cost    Performance   Deployment   Scalability
Qdrant          Free    High          Docker       Excellent
Pinecone        $$$$    High          Cloud        Excellent
Chroma          Free    Medium        Simple       Good
```

## 4. Filtering Metadata Efficiency

AND/OR filtering strategy before vector search with performance optimization through indexing.

- **Filter-First Strategy**: Apply metadata filters -> Limit count -> Vector search for relevance
- **Boolean Logic**: Support AND (must), OR (should), and combined filtering for precise results
- **Performance Impact**: Indexed filters provide 10x-100x faster performance vs unindexed scans
- **Field Types**: keyword (exact match), text (partial match), integer (range queries)

```bash
# Example: Find gaming laptops with (i7 OR i9) AND Nvidia graphics
curl -X POST "localhost:6333/collections/laptops/points/search" \
-d '{
  "vector": [0.1, 0.2, 0.3],
  "filter": {
    "must": [
      {"should": [{"cpu": "i7"}, {"cpu": "i9"}]},
      {"video_card": {"text": "Nvidia"}}
    ]
  },
  "limit": 5
}'
```

## 5. Reranking

Post-processing step to reorder search results by relevance using specialized models.

- **Purpose**: Reorder vector search results for improved relevance ranking
- **Stateless Operation**: No session state needed, suitable for simple local models
- **Integration Point**: After vector search, before final result presentation

```bash
# Simple reranking curl command
curl -X POST "http://localhost:11434/api/rerank" \
-H "Content-Type: application/json" \
-d '{
  "model": "rerank-model",
  "query": "best gaming laptop",
  "documents": ["doc1", "doc2", "doc3"]
}'
```

## 6. Augmented Generation

Prompt templates and context window management for LLM response generation with cost optimization.

- **Standard Template**: "Use the following context to answer: Context: {chunks} Query: {query}"
- **Context Window**: Fixed limits require chunk size control, character limits simpler than token counting
- **Token Economics**: Input tokens (cheaper) vs Output tokens (expensive), max_tokens reserves response space
- **Streaming**: SSE format with "data: {...}\n\n" and final "data: [DONE]" chunk

```text
Context Management Flow:
[Vector Search] -> [Size Check] -> [Template Fill] -> [LLM Request] -> [Response]
     |                |               |                |               |
[Relevant Chunks]  [Truncate if]   [Standard or]    [Stream or]    [Format]
[Metadata Filter]  [Too Large]     [Truncated]      [Complete]     [Output]
```

```text
Use the following context to answer the query:
Context: {chunks}
Query: {query}
```

The latter, the more important.

## 7. Data Management & Caching

Two-table MySQL design with stateless container recovery and fast rebuild capability.

- **Architecture**: Business data (laptops) + Vector cache (laptop_vectors) for transaction separation
- **Stateless Design**: No persistent volumes, <10s rebuild from MySQL cache for <5000 records
- **Consistency Model**: Business table (ACID), Vector cache (eventual consistency)
- **Recovery Strategy**: Empty VDB triggers automatic rebuild from cached embeddings

```text
Stateless Recovery Sequence:
[User Query] -> [Check VDB] -> [Empty?] -> [Rebuild from Cache] -> [Ready]
     |             |            |              |                    |
     |             |            |              |                    |
[New Request]  [No Data]    [Triggers]    [MySQL Vectors]      [10s Later]
```

## 8. Rate Limiting & Locking

Dual-layer coordination system preventing conflicts during expensive rebuild operations.

- **Problem**: 10s rebuild conflicts when multiple instances detect empty VDB simultaneously
- **Solution**: Single unified lock (5s local + 5min distributed) affects both embedding AND VDB operations
- **Implementation**: VDB-based remote locking using dedicated lock collections for coordination
- **Namespace Concept**: Each topic gets paired data + lock collections for complete isolation

```text
Coordinated Rebuild with Load Balancing:
[Load Balancer] -> [App Instances] -> [Local Lock 5s] -> [VDB Lock 5min] -> [Rebuild]
     |                   |               |                   |               |
[Query Request]      [Check VDB]     [Acquire Lock]     [Coordinate]     [10s Process]
[Distribution]       [Empty State]   [Block Others]     [Cross-Instance]  [Ready State]
```
