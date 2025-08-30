# Graphiti Knowledge Base System

Graphiti is a `temporal` knowledge graph system that powers RAG (Retrieval-Augmented Generation) capabilities.

```text
- 1. Why - Graphiti - 3 ways
- 2. How - Flow
- 3. Limitation - Graphiti graph search limitation
- 4. What - - Graphiti and Neo4j Relationship
- 5. Terms - Terminology Translation Table
```

## 1. Overview - Why Graphiti: Temporal + 3 ways search

```text
VDB Search:
[client]-----(query)------------------------------------------------------>[vector db]

Graphiti Search:
[client]-----(query)---->[graphiti]-------------3 ways search------------->[neo4j]
                         |                                                 |
                         |                                                 (node:Label)
                         |-- (vectors)          --> semantic search    --> |-- node.vector
                         |-- (text)             --> BM25 text search   --> |-- node.text + `FULLTEXT index`
                         |-- (center_node_uuid) --> BFS graph search   --> |-- node.uuid + `(node)--[:RELATES_TO]->(node2)`

Example:
  results = await client.search(
      query="search text",
      center_node_uuid="xxxxxxxx",  # This triggers graph distance search, only allows 1 center node
      num_results=5
  )

  Graphiti:
  1. Ranks results from each search method separately:
    - Vector search returns ranked list [1, 2, 3, 4, 5...]
    - BM25 search returns ranked list [1, 2, 3, 4, 5...]
    - Graph search returns ranked list [1, 2, 3, 4, 5...]
  2. Combines ranks using RRF formula:
  RRF_score = 1/(k + rank_vector) + 1/(k + rank_bm25) + 1/(k + rank_graph)
  2. Where k is typically 60 (a constant)

  Breadth-First Search (BFS):
  Graph traversal algorithm that explores nodes level by level, starting from one or more origin points
```

## 2. The Search Flow

```text
Your Query: "Lenovo Legend Y9000 i9"
    |
    v
Graphiti Library:
|
|-- Calls Ollama to embed "Lenovo Legend Y9000 i9" → [0.1, -0.3, 0.7, ...]
|
|-- Filter data with Neo4j
|
|-- Runs 3 parallel searches in Neo4j:
|   |
|   |-- Vector similarity: Compare query embedding vs episode vectors
|   |-- BM25 text search: Use FULLTEXT index on episode.content
|   +-- Graph traversal: Find episodes connected to relevant nodes
|
|-- Combines results with weighted scoring
|
+-- Returns ranked hybrid results
    |
    v
Your Application gets unified search results
```

## 3. Limitation - When you need multiple center nodes

What's the relationship between A and B?

```text
  Option 1: Low-level _search() method
  # Multiple BFS (Breadth-First Search) origin nodes
  results = await client._search(
      query,
      search_config_with_bfs_origin_node_uuids=[uuid1, uuid2, uuid3]
  )

  Option 2: Multiple sequential searches
  all_results = []
  for center_uuid in [uuid1, uuid2, uuid3]:
      results = await client.search(query, center_node_uuid=center_uuid)
      all_results.extend(results)
  # Then deduplicate and merge

  Reason: Graphiti's standard API is designed around:
  - One semantic query focus
  - One graph traversal starting point
  - Simplified distance calculations
```

## 4. Graphiti and Neo4j Relationship

**Neo4j Database (Data Storage)**:

- Stores episodes as nodes with `text`, `vector`, `uuid` properties
- Creates FULLTEXT indices for BM25 search capability
- Maintains graph relationships between entities
- All actual data lives in Neo4j

**Graphiti Library (Orchestration Tool)**:

- **Doesn't store data itself** - uses Neo4j as the storage backend
- **Combines searches**: Takes query and runs vector + BM25 + graph searches simultaneously
- **Handles scoring**: Merges results with weighted hybrid scoring
- **Manages embeddings**: Calls embedding service (Ollama), stores vectors in Neo4j properties
- **Provides API**: Simple `client.search()` interface that hides complexity

**Summary**:

- Neo4j = the database
- Graphiti = the smart orchestration tool that makes Neo4j do hybrid RAG effectively

## 5. Terminology Translation Table

Understanding Graphiti is easier when you map its concepts to familiar database terms:

### 5.1. Key Mappings

| Database Terms       | Graphiti Terms    | Neo4j Terms   | Vector DB Terms     | Description                                 |
|----------------------|-------------------|---------------|---------------------|---------------------------------------------|
| **Table**            | Episode Type      | Label         | Collection          | Category of data (TEXT, JSON, MESSAGE)      |
| **Record/Row**       | Episode           | Node          | Document            | Individual data unit with content           |
| **Column**           | Episode Field     | Property      | Metadata Field      | Data attributes (uuid, name, content, etc.) |
| **Primary Key**      | Episode UUID      | Node ID       | Document ID         | Unique identifier                           |
| **Foreign Key**      | Edge              | Relationship  | Reference           | Connection between data units               |
| **Index**            | Embedding         | Index         | Vector Index        | Fast lookup mechanism                       |
| **Schema**           | Episode Structure | Constraints   | Schema              | Data format definition                      |
| **Query**            | Hybrid Search     | Cypher Query  | Similarity Search   | Data retrieval method                       |
| **Join**             | Graph Traversal   | Path/Match    | Multi-vector Search | Multi-table/node queries                    |
| **View**             | Search Result     | Virtual Graph | Query Result        | Processed/filtered data                     |
| **Timestamp**        | reference_time    | Property      | Metadata            | Temporal information                        |
| **INSERT**           | add_episode()     | CREATE        | Add Document        | Adding new data                             |
| **SELECT**           | search()          | MATCH         | Search              | Retrieving data                             |
| **Full-text Search** | BM25 Search       | Text Index    | Keyword Search      | Text-based queries                          |
| **Similarity Join**  | Semantic Search   | N/A           | Vector Search       | Content-based matching                      |

### 5.2. Additional Conceptual Mappings

**Search Operations**:

| Database Terms    | Graphiti Terms  | Neo4j Terms  | Vector DB Terms |
|-------------------|-----------------|--------------|-----------------|
| **WHERE clause**  | Hybrid Search   | Cypher MATCH | Vector Filter   |
| **LIKE '%text%'** | BM25 Search     | Text Index   | Keyword Search  |
| **No equivalent** | Semantic Search | N/A          | Vector Search   |

**Temporal Aspects**:

| Database Terms     | Graphiti Terms | Neo4j Terms | Vector DB Terms |
|--------------------|----------------|-------------|-----------------|
| **created_at**     | created_at     | Property    | Metadata        |
| **effective_date** | reference_time | Property    | Time Filter     |
