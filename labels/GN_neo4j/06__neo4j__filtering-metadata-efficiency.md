# Neo4j Metadata Filtering and Search Efficiency

```text
[Data Filtering and Search Efficiency]
|
|-- Data Storage:
|   |-- Indexes, Filterable Data  -- 1.3
|   |-- Naming Convention         -- 1.4
|
|-- Searching Strategy
|   |-- Filter then Search?       -- 2.1
|   |-- Neo4j limitations         -- 2.1
|   +-- AND, OR, combined         -- 2.2 - 2.4
|
+-- Performance Considerations    -- 4
```

## 1. Example Data and Storage Format

### 1.1. Laptops Data

| Attribute  | Possible Values                       |
|------------|---------------------------------------|
| CPU        | i5, i7, i9                            |
| Video Card | Nvidia 50xx, Nvidia 40xx, Nvidia 30xx |
| Screen     | 13, 15, 16                            |
| RAM        | 16G, 32G, 64G                         |
| Hard Drive | 1T, 2T                                |

```text
content:
Fantastic Lenovo easy to carry laptop for daily usage and video editing.
Specification: CPU i9, RAM 32G, Video Card Nvidia 30xx, Screen 13", Hard Drive 1T
```

### 1.2. Example Neo4j Laptop Node

Note - Easy to: Find all with `e.filterableAttributes.cpu = "i9"`

```cypher
-- Create indices on filterable attributes
CREATE INDEX laptop__cpu__idx FOR (laptop:Laptop) ON (laptop.filterableAttributes.cpu)
CREATE INDEX laptop__ram__idx FOR (laptop:Laptop) ON (laptop.filterableAttributes.ram)
CREATE INDEX laptop__hdd__idx FOR (laptop:Laptop) ON (laptop.filterableAttributes.hard_drive)
CREATE INDEX laptop__screen__idx FOR (laptop:Laptop) ON (laptop.filterableAttributes.screen)
CREATE TEXT INDEX laptop__video__text FOR (laptop:Laptop) ON (laptop.filterableAttributes.video_card)

-- Create full-text index for BM25 search
CREATE FULLTEXT INDEX laptop__content__fulltext FOR (laptop:Laptop) ON EACH [laptop.content]

-- Create vector index for similarity search
CREATE VECTOR INDEX laptop__vector__vector
FOR (laptop:Laptop)
ON (laptop.vector)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 768,
    `vector.similarity_function`: 'cosine'
  }
};

CREATE (lenovo:Laptop {
  uuid: "laptop_001",
  content: "Fantastic Lenovo easy to carry laptop for daily usage and video editing. Specification: CPU i9, RAM 32G, Video Card Nvidia 30xx, Screen 13, Hard Drive 1T",
  vector: [0.1, 0.2, 0.3, "...", "0.n"],

  "attributeGroups": [
    {
      "groupName": "hardware_specs",
      "attributes": [
        { "name": "CPU", "value": "i9" },
        { "name": "Video Card", "value": "Nvidia 30xx" },
        { "name": "Screen", "value": "13" },
        { "name": "RAM", "value": "32G" },
        { "name": "Hard Drive", "value": "1T" }
      ]
    }
  ],

  filterableAttributes: {
    cpu: "i9",
    video_card: "Nvidia 30xx",
    screen: 13,
    ram: "32G",
    hard_drive: "1T"
  },

  updatedAtMs: 1704067200000
});
```

### 1.3. Indexing

Ensure filterableAttributes are indexed for fast filtering:

- **WHY Index**: Unindexed filters scan all laptops, indexed filters use optimized lookups
- **RESULT**: 10x-100x faster filtering performance

**Index Types:**

- **Exact match properties** (cpu, ram, hard_drive): Use standard INDEX
- **Numeric range properties** (screen): Use standard INDEX
- **Text search properties** (video_card with CONTAINS): Use standard INDEX
- **Content search**: Use FULLTEXT INDEX for BM25
- **Vector search**: Use VECTOR INDEX for Vector Search

### 1.4. Naming Convention

- "vector" - vectors for the user query - singular for attribute/db-field
- "filterableAttributes.hard_drive" - recommendation: change "Hard Drive" to "hard_drive"
    - convert all non-alphanumeric characters into "_", then lower case text
    - treat "Hard Drive" and "hard+Drive" the same in filters

```text
  # Examples:
  "Video Card" -> "video_card"
  "Video+Card" -> "video_card"
  "video Card" -> "video_card"
  "RAM/Memory" -> "ram_memory"
  "Screen-Size" -> "screen_size"
```

## 2. Filter Strategy: Vector First, Then Filter

### 2.1. How Neo4j works:

#### How you expect things to work:

- 1st: Apply Filters (e.g. i9 only)
- 2nd: Limit count (e.g. 5 - top 5 i9 laptops)
- 3rd: Search (since filter first, top 5 is a lot more relevant, and faster to query)

#### How Neo4j actually works:

- 1st: Vector search scans entire vector space (unavoidable in Neo4j)
- 2nd: Apply filters to vector results
- 3rd: Return filtered subset

**Note**: Unlike Qdrant, Neo4j cannot filter BEFORE vector search - it always scans the full vector space first.

CALL...YIELD behaves like MATCH - it has to be the first line in Neo4j - **Result**:

- Neo4j's vector search is less efficient than databases like Qdrant that support true filter-first approaches.
- Currently, Neo4j does not have a filter first efficient alternative solution

```cypher
// ✅ CORRECT - CALL at the start
CALL db.index.vector.queryNodes('index', 10, $embedding)
YIELD node, score
WHERE score > 0.5
RETURN node;

// ✅ CORRECT - MATCH at the start
MATCH (laptop:Laptop)
WHERE laptop.cpu = "i9"
RETURN laptop;

// ❌ WRONG - Can't put CALL after WHERE
MATCH (laptop:Laptop)
WHERE laptop.cpu = "i9"
CALL db.index.vector.queryNodes('index', 10, $embedding)  -- Error!

Exception: Subqueries

You can use CALL inside subqueries with CALL {}:

// ✅ CORRECT Syntax but slow - CALL in subquery - However, this approach still scans the whole vector space. So this returns "10 laptops", not "10 i9 laptops"
MATCH (laptop:Laptop)
WHERE laptop.cpu = "i9"
WITH laptop
CALL {
    WITH laptop
    CALL db.index.vector.queryNodes('index', 10, $embedding)
    YIELD node, score
    WHERE node = laptop
    RETURN score
}
RETURN laptop, score;

// ✅ CORRECT - Alternative. This correctly returns 10 most relevant items
CALL db.index.vector.queryNodes('laptop__vector__vector', 1000, $embedding)  -- Get 1000 items instead
YIELD node as laptop, score
WHERE laptop.cpu = "i9"          -- Filter the 1000 results
LIMIT 10                         -- Get top 10 i9 laptops by vector similarity
```

### 2.2. Use `AND`

```cypher
// Step 1: Get vector similarity candidates
CALL db.index.vector.queryNodes('laptop__vector__vector', 50, $query_embedding)
YIELD node as e, score as similarity_score

// Step 2: Apply metadata filters to vector candidates
WHERE e.filterableAttributes.cpu = "i9"
  AND e.filterableAttributes.ram = "32G"
  AND e.filterableAttributes.hard_drive = "1T"
  AND similarity_score > 0.7

RETURN e.uuid, e.content, similarity_score
ORDER BY similarity_score DESC
LIMIT 5
```

### 2.3. Use `OR`

```cypher
// Step 1: Get vector similarity candidates
CALL db.index.vector.queryNodes('laptop__vector__vector', 50, $query_embedding)
YIELD node as e, score as similarity_score

// Step 2: Apply OR filter to vector candidates
WHERE e.filterableAttributes.cpu IN ["i7", "i9"]
  AND similarity_score > 0.5

RETURN e.uuid, e.content, similarity_score
ORDER BY similarity_score DESC
LIMIT 5
```

### 2.4. Combine `AND` and `OR`

```cypher
// Step 1: Get vector similarity candidates
CALL db.index.vector.queryNodes('laptop__vector__vector', 100, $query_embedding)
YIELD node as e, score as similarity_score

// Step 2: Apply complex filters to vector candidates
WHERE e.filterableAttributes.cpu IN ["i7", "i9"]
  AND e.filterableAttributes.ram IN ["16G", "32G"]
  AND e.filterableAttributes.video_card CONTAINS "Nvidia"
  AND similarity_score > 0.5

// Step 3: Optional BM25 text search on filtered subset
WITH e, similarity_score
CALL {
  WITH e
  CALL db.index.fulltext.queryNodes("laptop__content__fulltext", $query_text)
  YIELD node, score as bm25_score
  WHERE node = e
  RETURN bm25_score
}

// Step 4: Hybrid scoring
WITH e, similarity_score, bm25_score,
     (0.6 * similarity_score + 0.4 * bm25_score) as final_score

RETURN e.uuid, e.content, e.filterableAttributes, final_score
ORDER BY final_score DESC
LIMIT 5
```

### 2.5. Range Filters

```cypher
// Step 1: Get vector similarity candidates
CALL db.index.vector.queryNodes('laptop__vector__vector', 50, $query_embedding)
YIELD node as e, score as similarity_score

// Step 2: Apply range filter to vector candidates
WHERE e.filterableAttributes.screen >= 13
  AND e.filterableAttributes.screen <= 15
  AND similarity_score > 0.5

RETURN e.uuid, e.content, similarity_score
ORDER BY similarity_score DESC
LIMIT 5
```

## 3. Complete Hybrid Search Query

```cypher
// Complete hybrid search with metadata filtering
// Parameters: $query_embedding (vector), $query_text (string), $cpu_filter, $ram_filters, $min_screen, $max_screen

// Step 1: Get vector similarity candidates
CALL db.index.vector.queryNodes('laptop__vector__vector', 200, $query_embedding)
YIELD node as e, score as vec_score

// Step 2: Apply metadata filters to vector candidates
WHERE e.filterableAttributes.cpu = $cpu_filter
  AND e.filterableAttributes.ram IN $ram_filters  // ['16G', '32G']
  AND e.filterableAttributes.screen >= $min_screen
  AND e.filterableAttributes.screen <= $max_screen
  AND vec_score > 0.3

// Step 3: BM25 text search on filtered subset
WITH e, vec_score
CALL {
  WITH e
  CALL db.index.fulltext.queryNodes("laptop__content__fulltext", $query_text)
  YIELD node, score as bm25_score
  WHERE node = e
  RETURN bm25_score
}

// Step 4: Hybrid scoring
WITH e, vec_score, bm25_score,
     (0.4 * vec_score + 0.3 * bm25_score) as hybrid_score

// Step 5: Optional graph context boost
OPTIONAL MATCH (e)-[:HAS_CPU|HAS_RAM|HAS_GPU]->(component)
WITH e, hybrid_score, count(component) as component_count,
     hybrid_score + (component_count * 0.1) as final_score

RETURN e.uuid, e.content, e.filterableAttributes,
       vec_score, bm25_score, final_score
ORDER BY final_score DESC
LIMIT 5
```

### 4. Query Performance Strategy

**Vector-First Approach** (Neo4j Limitation):

1. **Run vector similarity** -> Scans entire vector space (always slow at scale)
2. **Apply metadata filters** -> Filter vector candidates by attributes
3. **Run BM25 search** -> Only on filtered laptops (fast)
4. **Combine scores** -> Hybrid ranking

**Performance Reality**:

- Vector search cannot be optimized with pre-filtering in Neo4j
- Always scans full vector space regardless of metadata filters
- Metadata filtering only reduces post-vector-search processing
- At billion-scale, vector step becomes the bottleneck (50-500ms)

## Summary

This Neo4j approach provides **hybrid search capabilities** but with important limitations compared to Qdrant:

- ✅ **Metadata filtering** using nested `filterableAttributes` structure
- ✅ **Complex filter logic** (AND/OR/ranges) using Cypher
- ✅ **Hybrid search** combining vector + BM25 + graph context
- ❌ **No filter-first strategy** - vector search always scans full space
- ❌ **No performance optimization** for vector search via pre-filtering
- **Reality**: At billion-scale, use dedicated vector databases for semantic search, Neo4j for graph relationships
