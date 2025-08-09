# RAG Basic Theory and Overview

## 1. What is RAG?

```text
|-- **WHAT**:
|   |-- Retrieval (from Vector DB)
|   |-- Augmented (context added to prompt)
|   +-- Generation (by LLM)
|
+-- **WHY** - Knowledge Gap:
    |-- Time Gap: data cut 2025-01-01
    |-- Internal Data
    +-- Vector DB: semantic search - e.g. hello ~= Hi
```

## 2. RAG System Overview

### 2.1. Vectors

```
Text:

Man -> Male + Age Group
       1      3


Vectors:

       |
30:  3 |-          Man
       |
20:  2 |-
       |
10:  1 |-
       |---+-------+--
        F: 0    M: 1
```

### 2.2. Services

| Service             | Function                    |
|---------------------|-----------------------------|
| [System]            | orchestration               |
| [Text Splitter]     | text -> chunks              |
| [Embedding Service] | chunk -> vectors            |
| [Vector DB]         | storage                     |
| [Reranking Service] | reorder chunks by relevance |
| [LLM Service]       | response generation         |

## 3. RAG Workflow Sequence

### 3.1. Vector DB Data Storage

```
[System]   [Text Splitter]   [Embedding Service]   [Vector DB]
   |             |                  |                 |
   |---text----->|                  |                 |
   |<--chunks----|                  |                 |
   |             |                  |                 |
   |             |                  |                 |
   |(chunk + metadata) * x          |                 |
   |-- (chunk + metadata) * 1 ----->|                 |
   |<--vectors----------------------|                 |
   |             |                  |                 |
   |             |                  |                 |
   |(chunk + metadata + vectors) = document           |
   |---document-------------------------------------->|
   |             |                  |                 |
```

### 3.2. RAG Query

```
[User]    [System]  [Embedding Service]  [Vector DB]  [Reranking Service]  [LLM Service]
  |          |           |                  |            |                   |
  |---query->|           |                  |            |                   |
  |          |           |                  |            |                   |
  |          |           |                  |            |                   |
  |          |---query-->|                  |            |                   |
  |          |<--vectors-|                  |            |                   |
  |          |           |                  |            |                   |
  |          |           |                  |            |                   |
  |          |---vectors + metadata-------->|            |                   |
  |        R |<--chunks-(always > 0)--------|            |                   |
  |          |           |                  |            |                   |
  |          |           |                  |            |                   |
  |          |---chunks + query------------------------->|                   |
  |          |<--reranked chunks-(can return 0)----------|                   |
  |          |           |                  |            |                   |
  |          |           |                  |            |                   |
  |        A | (query + reranked chunks + template = prompt)                 |
  |          |---prompt----------------------------------------------------->|
  |        G |<--answer------------------------------------------------------|
  |          |           |                  |            |                   |
  |          |           |                  |            |                   |
  |<--answer-|           |                  |            |                   |
  |          |           |                  |            |                   |
```

## 4. Common Use Cases

| Use Case               | Document Type      | Query Example                    |
|------------------------|--------------------|----------------------------------|
| **Knowledge Base**     | FAQs, Manuals      | "How do I reset my password?"    |
| **Research Assistant** | Papers, Reports    | "What are recent findings on X?" |
| **Customer Support**   | Tickets, Solutions | "Similar issues to this error?"  |
| **Code Helper**        | Documentation      | "How to use this API?"           |
