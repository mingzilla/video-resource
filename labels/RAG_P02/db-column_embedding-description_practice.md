# RAG Embedding Best Practices: Database Column Disambiguation

## 1. The Problem

When implementing RAG (Retrieval-Augmented Generation) systems, we need to embed database columns as vector documents for similarity search. The challenge: how should we craft the text that gets converted into vectors?

Should the description (to be used to convert into vectors) of a column be:

| Approach      | Explanation                                                                   | Intent, Query, Concern                                                                  |
|---------------|-------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| clarification | a short explanation to clarify which meaning it is related to the column name | emphasises on removing ambiguity meaning of a word                                      |
| explain       | an explanation about this name                                                | emphasises on explanation                                                               |
| attributes    | list attributes of this thing                                                 | because embedding is all about many characteristic dimensions                           |
| example       | an explanation with examples data                                             | would the example hallucinate the meaning?                                              |
| hybrid        | explanation plus metadata attributes plus example data                        | then how would the embedding model know what is the important part we try to emphasise? |

Consider a database column called "bat". Should the embedding description be:

- `"bat - Noun (animal): A nocturnal flying mammal"`
- `"bat - Nocturnal, flying, mammal, echolocating, winged, insect-eating, fruit-eating, roosting, social, agile, silent, warm-blooded, fur-covered, upside-down hanger, colony-dwelling"`
- A one-sentence story about bats?

## 2. The Goal

- **User Intent**: "Does the database store info related to what they ask about?"
- **Example Query**: A user wants to know if the database has info about "sports they can play with their pet that eats fruits."
- **Expectation**: This query should **NOT** match a "bat" column containing animal data, even though bats eat fruit. The user is asking about sports, not animals.

## 3. Key Principles

### 3.1. Ambiguity Removal is Critical

The primary goal of embedding text is **disambiguation**, not comprehensive description. Modern embedding models already understand semantic concepts - they just need to know **which meaning** you're referring to.

### 3.2. Parenthetical Disambiguation Has Weight Issues

Formats like `"bat (animal)"` or `"bat (sports equipment)"` are problematic because embedding models don't clearly understand the hierarchy:

- Is "bat" the main concept with "animal" as context?
- Or is "animal" the main concept with "bat" as an example?

### 3.3. Negative Examples Cause Hallucination

❌ **Bad**: `"Bat here means the animal, not sports equipment"`

**Problem**: Embeddings aren't logical reasoners. They see: `[bat] + [animal] + [sports] + [equipment]`

**Result**: Actually **increases** similarity to sports queries!

### 3.4. Example Data Causes Hallucination

❌ **Bad**: `"Bat - animal. Examples: vampire bat, fruit bat, baseball bat"`

**Problem**: The "baseball bat" example would cause false matches with sports queries, defeating the disambiguation purpose.

### 3.5. Attribute Lists Create Noise

❌ **Bad**: `"bat - Nocturnal, flying, mammal, echolocating, winged, insect-eating, fruit-eating..."`

**Problem**: Too many attributes increase chances of false positive matches. A user searching "fruit-eating pets" might incorrectly match this animal data.

## 4. Recommended Approach: Three-Stage Architecture

### 4.1. Stage 1: Embedding (Retrieval)

**Purpose**: Clean semantic retrieval with clear disambiguation

**Format**: `{Primary_Term} - {brief_unambiguous_definition}`

**Examples**:

- `"Bat - a nocturnal flying mammal"`
- `"Python - a programming language for software development"`
- `"Bank - a financial institution for money services"`

**Output**: Top 50 candidates based on semantic similarity

### 4.2. Stage 2: Reranking (Relevance Ranking)

**Purpose**: Rank candidates by actual relevance to the query, not just semantic similarity

**Input**: User query + top 50 candidates from embedding stage

**Process**: Reranking models are specifically trained to understand query-document relevance better than embeddings alone

**Output**: Top 5 most relevant candidates

**Why Needed**: Embedding similarity ≠ query relevance. A column might be semantically similar but not actually relevant to the user's intent.

### 4.3. Stage 3: LLM Verification

**Purpose**: Intent validation with full context

**Content**: Include description + example data + user query for LLM to verify the match

```
verification_context = {
    "column": "bat",
    "description": "Bat - a nocturnal flying mammal", 
    "sample_values": ["fruit bat", "vampire bat", "little brown bat"],
    "user_query": "sports they can play with their pet that eats fruits"
}
```

## 5. Justification

### 5.1. Why This Works

```
Query: "sports they can play with their pet that eats fruits"
    ↓
Embedding Retrieval: Clean disambiguation enables wide semantic net (50 candidates)
    ↓
Reranking: Identifies that sports-related columns are more relevant than animal columns
    ↓
LLM Verification: "This is about sports activities, not animal data"
    ↓
Result: Correctly rejects the bat (animal) column
```

Note - if column name is completely wrong, it would be rejected by verification stage. The description is not to be used to correct the column name

### 5.2. Implementation Pattern

| Stage           | Content                             | Purpose            | Output     |
|-----------------|-------------------------------------|--------------------|------------|
| **Embedding**   | `"Bat - a nocturnal flying mammal"` | Semantic retrieval | Top 50     |
| **Reranking**   | Query + candidate descriptions      | Relevance ranking  | Top 5      |
| **LLM Context** | Description + examples + user query | Intent validation  | Final list |

### 5.3. Key Questions to Consider

When creating embedding text for database columns, ask:

- **Disambiguation**: Does this remove ambiguity about which meaning of the term I'm referring to?
- **Weight Clarity**: Is the primary concept clearly the main subject?
- **Noise Avoidance**: Am I introducing irrelevant semantic dimensions?
- **Negative Pollution**: Am I accidentally including concepts I want to exclude?
- **Example Contamination**: Will example data create false positive matches?

The goal is **precise retrieval** followed by **relevance ranking** and **contextual verification**, not comprehensive description in the embedding stage.