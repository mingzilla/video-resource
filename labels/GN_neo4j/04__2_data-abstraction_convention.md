# Data Abstraction Related Naming Convention System

For Neo4j graph modeling, a consistent naming convention is crucial for maintainability and clarity. Here's a comprehensive prefix-based system aligned with your abstraction levels:

```text
- 1. WHAT - Naming Conventions
- 2. WHY  - For Neo4j
- 3. Additional
- 4. Examples
```

## 1. Recommended Naming Convention System - WHAT

```text
Graph System Concepts
|
|-- Nodes / Labels
|   |-- Node Properties
|   +-- Constraints
|
+-- Relationships
```

### 1.1. Node Labels (PascalCase)

| Prefix | Category      | Example         | When to Use                         |
|--------|---------------|-----------------|-------------------------------------|
| **D_** | **Document**  | `D_ProductSpec` | Raw, unstructured data (PDFs, JSON) |
| **E_** | **Entity**    | `E_Laptop`      | Core domain objects with identity   |
| **A_** | **Attribute** | `A_CPUType`     | Domain-scoped attribute nodes (naturally limited to specific contexts) |
| **V_** | **Value**     | `V_Color`       | Universal value nodes (cross-domain, evolutionarily promoted from A_) |

### 1.2. Node Properties (camelCase)

| Suffix       | Purpose               | Example                 |
|--------------|-----------------------|-------------------------|
| `Raw`        | Unprocessed raw value | `cpuRaw: "Intel i9"`    |
| `Normalized` | Cleaned value         | `cpuNormalized: "i9"`   |
| `At`         | Timestamps            | `createdAt: datetime()` |
| `Count`      | Quantities            | `errorCount: 3`         |

### 1.3. Constraints/Indexes (Suffixes)

```cypher
// Unique constraints
CREATE CONSTRAINT e_laptop_id__unique FOR (n:E_Laptop) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT a_cpu_type__unique FOR (n:A_CPUType) REQUIRE n.normalized IS UNIQUE;

// Indexes (non-unique)
CREATE INDEX d_product_spec_title__index FOR (n:D_ProductSpec) ON n.title;
CREATE FULLTEXT INDEX a_searchable_terms__bm25_index FOR (n:A_CPUType|A_GPUType) ON n.normalized;
```

### 1.4. Relationships (SCREAMING_SNAKE_CASE)

| Pattern           | Example           | Usage                               |
|-------------------|-------------------|-------------------------------------|
| `HAS_[A/V]`       | `HAS_A_CPU`       | Entity → Attribute/Value connection |
| `CONTAINS_D`      | `CONTAINS_D_SPEC` | Entity/Doc contains raw data        |
| `LINKED_TO_[E/A]` | `LINKS_TO_E_USER` | Generic associations                |

---

## 2. Why This Works Well in Neo4j - WHY

1. **Visual Scanning**
    - Prefixes make node types instantly recognizable in Cypher results:
      `MATCH (n) RETURN labels(n)` → `["E_Laptop", "A_CPUType"]`

2. **Query Clarity**
   ```cypher
   // Intent is obvious
   MATCH (e:E_Laptop)-[:HAS_A_CPU]->(a:A_CPUType)
   WHERE a.normalized = "i9"
   RETURN e;
   ```

3. **Schema Management**
    - Easily list all entities:
      `SHOW CONSTRAINTS YIELD name WHERE name STARTS WITH 'e_'`

4. **APOC/GraphQL Friendly**
    - Compatible with tools expecting naming patterns

---

## 3. Additional Consideration - Special Cases

1. **Cross-Domain Evolution**
   When A_ attributes need cross-domain relationships, promote to V_ nodes (e.g., `A_LaptopColor` → `V_Color` when cars also need color relationships)

2. **Temporal Data**
   ```cypher
   CREATE (t:T_2025_07)-[:SNAPSHOT_OF]->(e:E_Laptop)
   ```

3. **Metadata Nodes**
   ```text
   M_UserTracking, M_AuditLog
   ```

---

## 4. Implementation Example

```cypher
// Document node (raw data)
CREATE (d:D_ProductPage {
  id: "doc123",
  contentRaw: "Lenovo laptop with Intel i9...",
  scrapedAt: datetime()
})

// Entity node
CREATE (e:E_Laptop {
  id: "lenovo_legion_7i",
  modelRaw: "Legion 7i Gen 8",
  priceNormalized: 1999.99
})

// Attribute node
CREATE (a:A_CPUType {
  normalized: "i9",
  variations: ["i9", "I9", "Intel Core i9"]
})

// Relationships
CREATE (e)-[:CONTAINS_D]->(d)
CREATE (e)-[:HAS_A_CPU]->(a)
```
