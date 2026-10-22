# Embedding Generation

## 1. Text to Vector Conversion

### Overview
**WHAT**: Transform text chunks into numerical vectors that capture semantic meaning
**WHY**: Vector databases need numerical data to perform similarity calculations
**HOW**: Use embedding models to convert text into fixed-size numerical arrays

### 1.1. Conversion Process

```
[Text Input] ----> [Embedding Model] -> [Vector Output] -> [Vector Database]
     |               |                    |                   |
     |               |                    |                   |
"Fantastic         [nomic-embed-text]   [0.1, -0.3, 0.7,    [Storage]
Lenovo laptop      [Model Processing]   ..., 0.2]           [Indexing]
for daily usage"   [768 dimensions]     [Similarity Ready]  [Querying]
```

### 1.2. Cloud or Local

| Model Type | Example                       | Dimensions | Use Case                       |
|------------|-------------------------------|------------|--------------------------------|
| **Local**  | nomic-embed-text              | 768        | Development, Privacy           |
| **Cloud**  | OpenAI text-embedding-3-small | 1536       | Production, Performance        |
| **Hybrid** | Local + Cloud fallback        | Variable   | Reliability, Cost optimization |

### 1.3. LLM Usage Types and Session State

**WHAT**: LLM models serve 3 distinct purposes with different session requirements
**WHY**: Understanding session state helps choose appropriate models and optimization strategies
**HOW**: Match model capabilities to usage patterns and caching needs

```
LLM Model Usage Types:
|
|-- Chat Completion (STATEFUL)
|   |-- Requires session management
|   |-- Conversation history tracking
|   |-- Prompt caching possible
|   +-- Context window optimization
|
|-- Embedding (STATELESS)
|   |-- Pure text -> vector conversion
|   |-- No session state needed
|   |-- No prompt caching benefit
|   +-- Simple local models work well (Ollama)
|
+-- Reranking (STATELESS)
    |-- Query + chunks -> relevance scores
    |-- No conversation context needed
    |-- No session mixing concerns
    +-- Can use basic models without caching
```

### 1.4. Ollama Advantage for Stateless Operations

| Operation           | Session State | Caching Benefit       | Ollama Suitability       |
|---------------------|---------------|-----------------------|--------------------------|
| **Chat Completion** | Required      | High (prompt caching) | Good (but no caching)    |
| **Embedding**       | None          | None (deterministic)  | Excellent (no drawbacks) |
| **Reranking**       | None          | Low (simple scoring)  | Excellent (no drawbacks) |

## 2. Model Selection Considerations

### 2.1. Choosing Models and Dimensions

**WHAT**: Different models produce vectors of different dimensions and quality
**WHY**: Dimension count affects storage size and computational requirements
**HOW**: Balance accuracy needs with performance and storage constraints

| Model      | Dimensions | Quality | Storage Impact | Speed  |
|------------|------------|---------|----------------|--------|
| **Small**  | 384        | Good    | Low            | Fast   |
| **Medium** | 768        | Better  | Medium         | Medium |
| **Large**  | 1536+      | Best    | High           | Slow   |

### 2.2. Model Consistency Requirement

**WHAT**: Cannot mix different embedding models for the same vector database
**WHY**: Different models produce completely different vectors for identical text
**HOW**: Choose one model and use it consistently across all documents

```
Problem Scenario:
|
|-- Document A: "Laptop review" -> [Model X] -> [0.1, 0.3, -0.2, ...]
|-- Document B: "Laptop review" -> [Model Y] -> [0.7, -0.1, 0.5, ...]
|
+-- Result: Same text = Different vectors = No similarity match
```

## 3. Performance and System Caching Strategy

### 3.1. Embedding Performance Impact

**WHAT**: Local embedding generation is significantly slower than vector storage
**WHY**: Complex neural network processing takes more time than simple database inserts
**HOW**: Plan for embedding bottlenecks and consider batch processing

```
Performance Comparison:
|
|-- Embedding Generation: ~1 second per text chunk
|-- Vector DB Storage: ~10 milliseconds per vector
|-- Performance Ratio: 100:1 (embedding is the bottleneck)
```

### 3.2. Relational Database Caching

**WHAT**: Store generated embeddings in relational database for reuse
**WHY**: Avoid re-generating expensive embeddings when rebuilding vector collections
**HOW**: Cache text-to-vector mappings with model version tracking

```
Caching Strategy:
|
|-- [Text Input] -> [Check Cache] -> [Cache Hit?]
|                        |              |
|                        |              v
|                        |        [Return Cached Vector]
|                        |
|                        v
|                   [Generate New] -> [Store in Cache] -> [Store in Vector DB]
|                        |                 |                    |
|                        v                 v                    v
|                   [1s processing]   [DB Insert]         [Rebuild Ready]
```

Specific choice:

- VectorDB as docker - not volumed out, free to destroy
- Embedded Vectors - store in mysql, allow single-db vector out-of-date check

## 4. Example Usage

### 4.1. Ollama Embedding API

```bash
curl -X POST http://localhost:11434/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nomic-embed-text",
    "prompt": "Fantastic Lenovo laptop for daily usage"
  }'
```

### 4.2. OpenAI Embedding API

```bash
curl -X POST https://api.openai.com/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "text-embedding-3-small",
    "input": "Fantastic Lenovo laptop for daily usage"
  }'
```
