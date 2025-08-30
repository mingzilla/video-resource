# Data Normalization Decisions Framework: Creation Time vs Runtime Processing

**Core Insight - Graph modeling is choosing when to do work: creation time (pre-processing) or runtime (on-demand).**

```text
[Creation Time vs Runtime Processing - Decisions Framework]
|
|-- 1. Levels: Document, Entities, Attributes, Values
|
|-- 2. Challenges: Data Cleaning and Labeling
|
|-- 3. Considerations: Speed, Quality, Maintenance
|
|-- 4. Implementation Patterns - Create Time and Runtime
|
|-- 5. Implementation and Maintenance Strategies
|
+-- Summary - Decisions: Store un-cleaned data (no work) or structured data (hard work)
    |
    +-- Decision: Creation Time or Runtime Processing
        |-- Considerations: Speed, Quality, Maintenance
        +-- Key Criteria: Frequency of Usage, Rate of Change
```

## 1. Abstraction Level <--> Processing Strategy

| Level       | Typical Processing | Example Use Case                                                           |
|-------------|--------------------|----------------------------------------------------------------------------|
| D_Document  | Runtime            | Full-text search                                                           |
| E_Entity    | Either             | Core business objects                                                      |
| A_Attribute | Creation-time      | Domain-scoped attributes (evolve to V_ when cross-domain needs emerge)     |
| V_Value     | Creation-time      | Universal values (promoted from A_ when cross-domain relationships needed) |

---

## 2. Typical Data Challenge

- A **typical challenge** about data is **data cleaning and data labeling** - e.g.:
- handling variations like "i9" vs "I9" vs "Intel i9".
- We are deciding about taking the challenge at: create time vs. runtime

---

## 3. Key Considerations

| Aspect           | Creation Time Processing | Runtime Processing        |
|------------------|--------------------------|---------------------------|
| **Performance**  | ✅ Do Once                | ❌ Per Request             |
| **Data Quality** | ✅ Enforced consistency   | ❌ Validation required     |
| **Maintenance**  | ❌ High (schema updates)  | ✅ Low (code changes only) |
| **Flexibility**  | ❌ Rigid schema           | ✅ Dynamic handling        |

- ✅ Win, ❌ Lose
- Creation Time Processing - Clean data and turn into concrete `nodes` (enables both filtering on node properties AND relationship traversal for discovering connections)
- Runtime Processing - Leave text as `properties` (filtering only, no relationship discovery capabilities)

---

## 3. Key Decision Criteria

**Core Insight - handle each concept separately. DO NOT develop a one-for-all solution.**

```text
Create Time or Runtime
|-- Frequency of Usage
|-- Data Change Rate
+-- V_ (Values) - Universal Enums (cross-domain)
```

### 3.1. Frequency of Usage

```text
Query Frequency Decision Tree:
|-- Always    -> Creation-time (A_* nodes with indexes)
|-- Sometimes -> Hybrid approach (both property + node)
|-- Rarely    -> Runtime properties only
+-- Unknown   -> Full-text search indexes
```

### 3.2. Rate of Change

- Low Rate -- Creation-time (`A_CPUType`) -> Node
- High Rate -- Runtime (`price` property) -> property

## 4. Implementation Patterns

### Creation-Time Normalization

```cypher
// 1. Create normalized node
CREATE (cpu:A_CPUType {
  normalized: "i9",
  variations: ["i9", "I9", "Intel i9"],
  benchmark: 2100,
  createdAt: datetime()
})

// 2. Link to entity
MATCH (l:E_Laptop {id: "lenovo_legion_7i"})
CREATE (l)-[:HAS_A_CPU]->(cpu)
```

### Runtime Processing

```cypher
// Store raw value
CREATE (:E_Laptop {
  id: "thinkpad_x1_gen9",
  cpuRaw: "Intel Core i9-13900H",
  updatedAt: datetime()
})

// Query with logic
MATCH (l:E_Laptop)
WHERE toLower(l.cpuRaw) CONTAINS "i9"
AND l.updatedAt > date("2023-06-01")
RETURN l
```

## 5. Implementation and Maintenance Strategies

### Implementation Strategy

1. Start with runtime properties
2. Monitor query patterns
3. Convert hot properties to nodes:

```cypher
MATCH (l:E_Laptop)
WHERE l.cpuRaw IS NOT NULL
MERGE (cpu:A_CPUType {normalized: normalizeCPU(l.cpuRaw)})
CREATE (l)-[:HAS_A_CPU]->(cpu)
```

### Optimisation Strategy - Add Indexing

```cypher
// For creation-time nodes
CREATE INDEX a_cpu_type_normalized FOR (n:A_CPUType) ON n.normalized;

// For runtime properties
CREATE FULLTEXT INDEX e_laptop_search FOR (n:E_Laptop) ON [n.cpuRaw, n.model]
```

## Maintenance Strategy - Procedures

- Add: If you repeatedly need to use an attribute and data quality is not reliable, consider creating a node for it, which encapsulates e.g. 'i9' and 'I9' confusion
- Remove: If you create a node and it's never used, then you can delete the node

1. **Audit Unused Nodes**
   ```cypher
   MATCH (a:A_CPUType)
   WHERE NOT ()-[:HAS_A_CPU]->(a)
   AND a.createdAt < date().subtract('P6M')
   DETACH DELETE a;
   ```

2. **Migration Strategy**
    - Start with runtime properties
    - Convert to nodes when usage frequency justifies it

3. **Versioning**
   ```cypher
   CREATE (v:V_Color_V2 {
     hex: "#000000",
     createdAt: datetime()
   })
   ```

## A_ → V_ Evolution Pattern

When cross-domain business requirements emerge, promote A_ attributes to V_ values:

```cypher
// 1. Create V_ node for cross-domain use
CREATE (v:V_Color {
  hex: "#FF0000",
  names: ["red", "rouge", "rojo"]
})

// 2. Migrate existing A_ relationships
MATCH (laptop:E_Laptop)-[:HAS_A_COLOR]->(a:A_LaptopColor {normalized: "red"})
MATCH (v:V_Color {names: ["red"]})
CREATE (laptop)-[:HAS_V_COLOR]->(v)

// 3. Enable cross-domain relationships
MATCH (car:E_Car)-[:HAS_V_COLOR]->(v:V_Color)<-[:HAS_V_COLOR]-(laptop:E_Laptop)
RETURN car, laptop // Cars and laptops with same color
```

**Trigger**: Business requirement like "find phones with same color as my laptop"

## Anti-Patterns

| Anti-Pattern               | Solution                            |
|----------------------------|-------------------------------------|
| Over-normalized attributes | Convert to properties               |
| Premature V_ promotion     | Start with A_, evolve when needed   |
| Unindexed hot queries      | Add specific indexes                |
| Mixed naming               | Enforce `Raw`/`Normalized` suffixes |
| Zombie nodes               | Quarterly cleanup scripts           |
