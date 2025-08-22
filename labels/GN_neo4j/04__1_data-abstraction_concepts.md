# Data Normalization / Abstraction

```text
- WHAT - 1. The 4-Level Graph Abstraction Pyramid
- WHY  - 1. Key Differentiators Between Levels
```

## 1. The 4-Level Graph Abstraction Pyramid (WHAT)

```text
Data Abstraction Levels
|-- D_ (Documents) - Raw Data                    -- different sellers having different descriptions about the same laptop
|-- E_ (Entities) - lenovo_y9000, hp_350: Laptop -- an actual laptop, each record represents a thing
|-- A_ (Attributes) - intel_i9, intel_i7: CPU    -- domain-specific enums (naturally scoped to computing devices) - typically used by one type of entity - e.g. laptop
+-- V_ (Values) - red, blue: Color               -- universal enums (naturally cross-domain) - typically shared by different types of entities - e.g. car and laptop
```

### 1.1. D_ Documents (Root Level)

- **Purpose**: Store raw, unprocessed data
- **Example**:
  ```cypher
  CREATE (d:D_ProductPage {
    url: "https://example.com/laptop123",
    htmlRaw: "<div>Intel i9-13900HX...</div>",
    scrapedAt: datetime()
  }
  ```
- **When to Use**:
    - Need to retain original sources
    - Legal/compliance requirements
    - Full-text search over raw content

### 1.2. E_ Entities (Core Level)

- **Purpose**: Represent domain objects with identity
- **Example**:
  ```cypher
  CREATE (e:E_Laptop {
    id: "lenovo_legion_7i",
    sku: "82RU000DUS",
    releaseYear: 2023
  })
  ```
- **When to Use**:
    - Main actors in your domain (users, products, etc.)
    - Objects with lifecycle and relationships

### 1.3. A_ Attributes (Domain-Specific Level)

- **Purpose**: Model variable characteristics with potential variations
- **Example**:
  ```cypher
  CREATE (a:A_CPUType {
    normalized: "i9",
    variations: ["i9-13900HX", "Intel Core i9"],
    tdp: 55,
    benchmarkScore: 1524
  }
  ```
- **When to Use**:
    - Attributes needing normalization ("i9" vs "I9")
    - Properties requiring their own metadata (e.g., CPU benchmark scores)
    - Frequently filtered/searchable traits

### 1.4. V_ Values (Universal Level)

- **Purpose**: Represent constrained, enumerable values
- **Example**:
  ```cypher
  CREATE (v:V_Color {
    hex: "#000000",
    names: ["black", "onyx", "jet black"],
    pantone: "Black C"
  })
  ```
- **When to Use**:
    - Small fixed sets (colors, countries, status codes)
    - Values needing industry-standard mappings
    - When the concept is stable across domains

---

## 2. Key Differentiators Between Node Levels (WHY)

| Criteria                 | D_ Documents              | E_ Entities       | A_ Attributes (Scoped)                            | V_ Values (Universal)                                   |
|--------------------------|---------------------------|-------------------|---------------------------------------------------|---------------------------------------------------------|
| **Frequency of Changes** | High (raw changes)        | Low               | Very Low                                          | Very Low                                                |
| **Query Use**            | Full-text/search          | Traversal anchors | Filtering + Relationship traversal (domain joins) | Filtering + Relationship traversal (cross-domain joins) |
| **Example**              | hp_gaming, hp_gamer: Spec | hp_530: Laptop    | intel_i9: CPU                                     | black: Color                                            |

Differentiation:

- Attributes: similar to a (scoped) Enum - It's context related - e.g. You want 32gb_ram to join different laptops
- Values: similar to a (universal) Enum - It's generic - The Values Level Nodes creates the ability to join different concepts - e.g. You want color to join car and laptop

Abilities:

- A_ and V_ nodes provide both traditional filtering capabilities (on node properties) AND relationship traversal capabilities (for discovering connections between entities).
- This dual functionality is a key advantage of the node-based approach over property-based modeling.

```text
The scope isn't an enforced property - it's a conceptual distinction that emerges from usage patterns:

A_ (Attributes) - Naturally scoped:
- intel_i9: CPU - naturally only applies to computing devices
- 32gb: RAM - naturally only applies to devices with memory
- No need to explicitly store scope, it's implicit in the domain
- 32gb: RAM - can be applied to phone or laptop, if there is a need to build phone and laptop relationship, then a V_ is needed, otherwise create scoped A_

V_ (Values) - Naturally universal:
- red: Color - naturally applies to anything that can have color
- large: Size - naturally applies across domains

The Evolution Pattern:
1. Start with A_ attributes for domain-specific needs
2. When cross-domain requirements emerge ("same color as my laptop" for phones)
3. Then promote/refactor to V_ values

So the distinction is more about:
- A_: allows building relationship between same type of entities - e.g. hp laptop and lenovo laptop - both relate to `32gb: LaptopRam`
- V_: allows building relationship between different types of entities - e.g. car color and laptop color - both relate to `red: Color`

The system can evolve from A_ → V_ when business requirements demand cross-domain relationships, rather than trying to predict universality upfront.
```

### Real-World Modeling Example

```cypher
// Document (raw source)
CREATE (d:D_ProductSpec {
  content: "Lenovo Legion 7i (2023) - Intel® Core™ i9-13900HX - 32GB DDR5 - NVIDIA RTX 4090"
})

// Entity (core object)
CREATE (e:E_Laptop {
  id: "legion_7i_2023",
  model: "Legion 7i Gen 8"
})

// Attributes (variable traits)
CREATE (a_cpu:A_CPUType {
  normalized: "i9",
  generation: "13th"
})

CREATE (a_gpu:A_GPUType {
  normalized: "RTX 4090",
  vram: "16GB GDDR6X"
})

// Values (fixed enums)
CREATE (v_color:V_Color {
  names: ["Storm Grey"],
  hex: "#5F5F5F"
})

// Connect everything
CREATE (e)-[:CONTAINS_D]->(d)
CREATE (e)-[:HAS_A_CPU]->(a_cpu)
CREATE (e)-[:HAS_A_GPU]->(a_gpu)
CREATE (e)-[:HAS_V_COLOR]->(v_color)

// Add timestamp properties to demonstrate temporal aspects
CREATE (a_cpu:A_CPUType {
  normalized: "i9",
  createdAt: datetime(),
  source: "Intel ARK Database"
})
```

### Technical Notes:

- In Neo4j, relationships must be explicitly created
- there are no "automatic" or "implicit" relationships

---

## 3. Implementation Details

### Naming Convention

For label and property naming rules, see: [04__2_neo4j-naming-convention.md]

### Implementation Strategies

See companion guide [04__3_data-normalization-decisions.md] for:

- When to process data at creation vs runtime
- Tradeoffs between node proliferation and property simplicity
- Frequency-based decision framework
