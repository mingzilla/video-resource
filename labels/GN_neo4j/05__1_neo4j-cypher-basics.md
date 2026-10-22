# Understand Neo4j Cypher

```text
[cypher is similar to sql]
|
|-- operations - similar to SQL
|   |-- insert          - 1.1. CREATE
|   |-- relationships   - 3.   similar to sql join, but different
|   |-- constraints     - 4.   unique, composite, required
|   |-- index           - 5.   range, text, fulltext (BM25), vector (similarity), point
|   +-- query           - 1.2. MATCH ... WHERE x=y RETURN ...
|
|-- cypher statements and scripts
|   |-- statement       - similar to a sql statement
|   +-- script          - separated by ;
|
+-- concepts
    |-- Operators       - 2.4
    |-- Performance:    - 5.8. EXPLAIN, PROFILE
    +-- Running Scripts - 6. UI, cypher-shell, code
```

## 1. Simple Example Breakdown

### 1.1. Creation

```cypher
-- Nodes
CREATE (lenovoY90:Laptop {
  uuid: "laptop-123",                                 -- central node reference
  content: "Lenovo Y70 feature Intel i9 processors",  -- actual text - with FULLTEXT INDEX, this enables BM25 search
  vector: [0.1, -0.3, 0.7, ...]                       -- singular for attribute/db-field e.g. 768-dimensional vectors
})

CREATE (i9   :CPU {name: "Intel i9"})
CREATE (32gb :RAM {name: "Kinsinton 32gb"})

-- Relationships
CREATE (lenovoY90)-[:HAS]->(i9)
CREATE (lenovoY90)-[:HAS]->(32gb)

-- Enables BM25 for `lenovoY90.content`
CREATE FULLTEXT INDEX laptop__content__fulltext FOR (lenovoY90:Laptop) ON EACH [lenovoY90.content]
```

Explanation:

- `uuid`, `content`, `vector` are just common attribute names for different data formats.
    - They are not keywords
    - When used, you get a particular attribute and use it for whatever purpose programmatically
- Relationships
    - Nodes can have many-to-many relationships. e.g. "Lenovo Y70 feature Intel i9 processors".
- FULLTEXT INDEX - enables BM25
    - **With FULLTEXT INDEX**: You get proper BM25 search with term frequency scoring, document length normalization, etc.
    - **Without FULLTEXT INDEX**: You can only do basic string matching like `CONTAINS` or `STARTS WITH`, but not true BM25 algorithm.
- Variable
    - The variable `lenovoY90` is just a way to refer to this node in the same script (variable scope).
    - So it does not matter if you call it something else in another script.

### 1.2. Query

```cypher
MATCH (laptop:Laptop)-[:HAS]->(component:CPU)
WHERE laptop.brand = "Lenovo"
RETURN component.name
```

| **Cypher Part**                                 | **SQL Equivalent**                                                                                    | **Explanation**                |
|-------------------------------------------------|-------------------------------------------------------------------------------------------------------|--------------------------------|
| `MATCH (laptop:Laptop)-[:HAS]->(component:CPU)` | `FROM Laptop l JOIN laptop_components lc ON l.id = lc.laptop_id JOIN CPU c ON lc.component_id = c.id` | Graph traversal vs table joins |
| `WHERE laptop.brand = "Lenovo"`                 | `WHERE l.brand = "Lenovo"`                                                                            | Identical filtering syntax     |
| `RETURN component.name`                         | `SELECT c.name`                                                                                       | Output specification           |

## 2. Cypher vs SQL Comparison

### 2.1. **Reading/Querying Operations**

#### 2.1.1. Basic

| **Cypher Concept** | **SQL Equivalent** | **Description**                          |
|--------------------|--------------------|------------------------------------------|
| **MATCH**          | FROM + JOIN        | Pattern matching nodes and relationships |
| **WHERE**          | WHERE              | Filtering conditions                     |
| **RETURN**         | SELECT             | Specifying output columns                |
| **ORDER BY**       | ORDER BY           | Sorting results                          |
| **LIMIT**          | LIMIT/TOP          | Restricting result count                 |
| **SKIP**           | OFFSET             | Skipping rows                            |

#### 2.1.2 Advanced

| **Cypher Concept** | **SQL Equivalent**       | **Description**                     |
|--------------------|--------------------------|-------------------------------------|
| **COUNT()**        | COUNT()                  | Counting records                    |
| **DISTINCT**       | DISTINCT                 | Removing duplicates                 |
| **WITH**           | Subquery/CTE             | Intermediate processing             |
| **UNWIND**         | UNNEST/CROSS APPLY       | Expanding arrays/lists              |
| **COLLECT()**      | STRING_AGG()/ARRAY_AGG() | Aggregating values into collections |
| **OPTIONAL MATCH** | LEFT JOIN                | Optional pattern matching           |
| **EXISTS**         | EXISTS                   | Subquery existence check            |
| **CASE**           | CASE                     | Conditional expressions             |

### 2.2. **Writing/Modification Operations**

| **Cypher Concept** | **SQL Equivalent**                          | **Description**                       |
|--------------------|---------------------------------------------|---------------------------------------|
| **CREATE**         | INSERT                                      | Creating new nodes/relationships      |
| **MERGE**          | INSERT ... ON DUPLICATE KEY UPDATE / UPSERT | Create if not exists, otherwise match |
| **SET**            | UPDATE                                      | Modifying existing properties         |
| **REMOVE**         | UPDATE (set to NULL) / ALTER TABLE DROP     | Removing properties or labels         |
| **DELETE**         | DELETE                                      | Removing nodes/relationships          |
| **DETACH DELETE**  | DELETE CASCADE                              | Remove node and all its relationships |
| **ON CREATE SET**  | INSERT with specific values                 | Set properties only when creating     |
| **ON MATCH SET**   | UPDATE with WHERE condition                 | Set properties only when matching     |

### 2.3. **Key Writing Patterns**

```
Creating Data:
Cypher: CREATE (laptop:Laptop {brand: "Lenovo", model: "Legion 7i"})
SQL:    INSERT INTO Laptop (brand, model) VALUES ("Lenovo", "Legion 7i")

Updating Data:
Cypher: MATCH (laptop:Laptop {brand: "Lenovo"}) SET laptop.price = 1999
SQL:    UPDATE Laptop SET price = 1999 WHERE brand = "Lenovo"

Upserting Data:
Cypher: MERGE (cpu:CPU {name: "Intel i9"}) ON CREATE SET cpu.created = timestamp()
SQL:    INSERT INTO CPU (name, created) VALUES ("Intel i9", NOW())
        ON DUPLICATE KEY UPDATE name = name
```

### 2.4. Operators

| **Cypher**           | **SQL**              | **Purpose**                 |
|----------------------|----------------------|-----------------------------|
| `=`                  | `=`                  | Equality                    |
| `<>`                 | `!=` or `<>`         | Not equal                   |
| `<`, `<=`, `>`, `>=` | `<`, `<=`, `>`, `>=` | Numerical comparisons       |
| `IS NULL`            | `IS NULL`            | Null checking               |
| `IS NOT NULL`        | `IS NOT NULL`        | Non-null checking           |
| `STARTS WITH`        | `LIKE 'value%'`      | String prefix matching      |
| `ENDS WITH`          | `LIKE '%value'`      | String suffix matching      |
| `CONTAINS`           | `LIKE '%value%'`     | String substring matching   |
| `=~`                 | `REGEXP`             | Regular expression matching |
| `IN [list]`          | `IN (list)`          | List membership             |

## 3. Relationships

Relationships in Neo4j connect nodes and have direction, type, and properties.

### 3.1. Basic Relationship Creation

```cypher
-- Create nodes and relationships in one statement
CREATE (laptop:Laptop {brand: "HP", model: "Pavilion"})
CREATE (cpu:CPU {name: "Intel i7", cores: 8})
CREATE (ram:RAM {size: "16GB", type: "DDR4"})
CREATE (gpu:GPU {name: "NVIDIA RTX 3060", vram: "6GB"})

-- Create relationships
CREATE (laptop)-[:HAS_CPU]->(cpu)
CREATE (laptop)-[:HAS_RAM]->(ram)
CREATE (laptop)-[:HAS_GPU]->(gpu)
```

### 3.2. Relationship with Properties

```cypher
-- Relationships can have properties too
CREATE (laptop)-[:MANUFACTURED_BY {year: 2023, country: "China"}]->(brand:Brand {name: "HP"})
```

### 3.3. Direction Matters

```cypher
-- Different directions mean different things
CREATE (user:User {name: "John"})
CREATE (laptop:Laptop {model: "ThinkPad"})

-- User owns laptop
CREATE (user)-[:OWNS]->(laptop)

-- Laptop belongs to user (conceptually different)
CREATE (laptop)-[:BELONGS_TO]->(user)
```

### 3.4. Querying Relationships

```cypher
-- Find all laptops with Intel CPUs
MATCH (laptop:Laptop)-[:HAS_CPU]->(cpu:CPU)
WHERE cpu.name CONTAINS "Intel"
RETURN laptop.brand, laptop.model, cpu.name

-- Find laptops with same CPU (relationship traversal)
MATCH (laptop1:Laptop)-[:HAS_CPU]->(cpu:CPU)<-[:HAS_CPU]-(laptop2:Laptop)
WHERE laptop1 <> laptop2
RETURN laptop1.brand, laptop2.brand, cpu.name
```

### 3.5. Cypher vs SQL for Relationships

| **Operation**                    | **Cypher**                               | **SQL Equivalent**                                                                   |
|----------------------------------|------------------------------------------|--------------------------------------------------------------------------------------|
| **Create relationship**          | `CREATE (a)-[:REL]->(b)`                 | `INSERT INTO relationship_table (a_id, b_id) VALUES (1, 2)`                          |
| **Query relationship**           | `MATCH (a)-[:REL]->(b)`                  | `SELECT * FROM a JOIN relationship_table r ON a.id = r.a_id JOIN b ON r.b_id = b.id` |
| **Relationship with properties** | `CREATE (a)-[:REL {prop: "value"}]->(b)` | `INSERT INTO relationship_table (a_id, b_id, prop) VALUES (1, 2, "value")`           |

## 4. Constraints

Constraints ensure data integrity by enforcing rules on nodes and relationships.

### 4.1. Unique Constraints

```cypher
-- Ensure laptop serial numbers are unique
CREATE CONSTRAINT laptop__serial__unique
FOR (laptop:Laptop)
REQUIRE laptop.serialNumber IS UNIQUE;

-- Ensure CPU model names are unique
CREATE CONSTRAINT cpu__model__unique
FOR (cpu:CPU)
REQUIRE cpu.model IS UNIQUE;
```

### 4.2. Node Key Constraints (Composite Unique)

```cypher
-- Combination of brand + model must be unique
CREATE CONSTRAINT laptop__brand__model__key
FOR (laptop:Laptop)
REQUIRE (laptop.brand, laptop.model) IS NODE KEY;
```

### 4.3. Property Existence Constraints

```cypher
-- Every laptop must have a brand
CREATE CONSTRAINT laptop__brand__exists
FOR (laptop:Laptop)
REQUIRE laptop.brand IS NOT NULL;

-- Every CPU must have a name
CREATE CONSTRAINT cpu__name__exists
FOR (cpu:CPU)
REQUIRE cpu.name IS NOT NULL;
```

### 4.4. Relationship Property Constraints

```cypher
-- Manufacturing relationships must have a year
CREATE CONSTRAINT manufactured__year__exists
FOR ()-[r:MANUFACTURED_IN]-()
REQUIRE r.year IS NOT NULL;
```

### 4.5. Managing Constraints

```cypher
-- List all constraints
SHOW CONSTRAINTS;

-- Drop a constraint
DROP CONSTRAINT laptop__serial__unique;
```

### 4.6. Cypher vs SQL Constraints Comparison

| **Constraint Type**  | **Cypher**                                                               | **SQL Equivalent**                                          |
|----------------------|--------------------------------------------------------------------------|-------------------------------------------------------------|
| **Unique**           | `CREATE CONSTRAINT FOR (n:Label) REQUIRE n.prop IS UNIQUE`               | `ALTER TABLE table ADD CONSTRAINT UNIQUE (column)`          |
| **Not Null**         | `CREATE CONSTRAINT FOR (n:Label) REQUIRE n.prop IS NOT NULL`             | `ALTER TABLE table ALTER COLUMN column SET NOT NULL`        |
| **Composite Key**    | `CREATE CONSTRAINT FOR (n:Label) REQUIRE (n.prop1, n.prop2) IS NODE KEY` | `ALTER TABLE table ADD CONSTRAINT PRIMARY KEY (col1, col2)` |
| **List Constraints** | `SHOW CONSTRAINTS`                                                       | `SHOW CREATE TABLE table` or `DESCRIBE table`               |
| **Drop Constraint**  | `DROP CONSTRAINT constraint_name`                                        | `ALTER TABLE table DROP CONSTRAINT constraint_name`         |

## 5. Indexes

Indexes speed up queries by creating optimized lookup structures for node properties.

| Index Type     | Required for? | Purpose                            |
|----------------|---------------|------------------------------------|
| Regular Index  | ❌ Optional    | Performance optimization           |
| Fulltext Index | ✅ Required    | BM25 search (no alternative)       |
| Vector Index   | ✅ Required    | Similarity search (no alternative) |

### 5.1. Range Indexes (Standard)

```cypher
-- Index for laptop brand queries
CREATE INDEX laptop__brand__index
FOR (laptop:Laptop)
ON (laptop.brand);

-- Index for CPU name searches
CREATE INDEX cpu__name__index
FOR (cpu:CPU)
ON (cpu.name);

-- Composite index for brand + model
CREATE INDEX laptop__brand__model__index
FOR (laptop:Laptop)
ON (laptop.brand, laptop.model);
```

### 5.2. Text Indexes (String Search)

```cypher
-- Text index for laptop descriptions
CREATE TEXT INDEX laptop__description__text
FOR (laptop:Laptop)
ON (laptop.description);

-- Query using text index
MATCH (laptop:Laptop)
WHERE laptop.description CONTAINS "gaming"
RETURN laptop.brand, laptop.model;
```

### 5.3. Fulltext Indexes (BM25 Search)

```cypher
-- Fulltext index for comprehensive search across multiple properties
CREATE FULLTEXT INDEX laptop__search__fulltext
FOR (laptop:Laptop)
ON EACH [laptop.brand, laptop.model, laptop.description];

-- Query using fulltext search with scoring
CALL db.index.fulltext.queryNodes("laptop__search__fulltext", "gaming Intel")
YIELD node, score
RETURN node.brand, node.model, score
ORDER BY score DESC;
```

```text
Neo4j Fulltext Indexes:
1. Create a search index (with BM25 capabilities)
2. Query FROM the index (not the nodes directly)

MySQL Traditional Indexes:
1. Create index ON a table (optimization structure)
2. Query FROM the table (index speeds up the query behind the scenes)

The Key Difference

-- Neo4j: Query the INDEX directly
CALL db.index.fulltext.queryNodes("laptop__search__fulltext", "gaming Intel")
YIELD node, score

vs

-- MySQL: Query the TABLE (index used automatically)
SELECT * FROM laptop WHERE ...;

What Actually Happens

Neo4j Fulltext Index:
- The index IS the search engine
- BM25 scoring happens within the index
- Index returns: {node, score} pairs
- You're literally asking the index: "give me your top matches"

MySQL Index:
- Index is a helper structure
- MySQL optimizer decides whether to use it
- You still query the table
- Index speeds up the WHERE clause execution
```

### 5.4. Vector Indexes (Similarity Search)

```cypher
-- Vector index for semantic similarity (embeddings)
CREATE VECTOR INDEX laptop__embedding__vector
FOR (laptop:Laptop)
ON (laptop.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 768,
    `vector.similarity_function`: 'cosine'
  }
};

-- Query using vector similarity
CALL db.index.vector.queryNodes('laptop__embedding__vector', 5, $queryEmbedding)
YIELD node, score
RETURN node.brand, node.model, score;
```

```text
- laptop.embedding - the property `embedding` stores [1.1, 1.2, ...]. Property name is flexible e.g. `embedding` or `vector`
- Vector indexes are REQUIRED for similarity search - they're not just for performance, they're mandatory
```

### 5.5. Point Indexes (Geospatial)

```cypher
-- Point index for store locations
CREATE POINT INDEX store__location__point
FOR (store:Store)
ON (store.location);

-- Find stores within 10km of a point
MATCH (store:Store)
WHERE point.distance(store.location, point({latitude: 40.7128, longitude: -74.0060})) < 10000
RETURN store.name, store.location;
```

### 5.6. Managing Indexes

```cypher
-- List all indexes
SHOW INDEXES;

-- Show index usage statistics
CALL db.stats.retrieve('INDEX');

-- Drop an index
DROP INDEX laptop__brand__index;
```

### 5.7. Cypher vs SQL Indexes Comparison

| **Index Type**      | **Cypher**                                                       | **SQL Equivalent**                                                         |
|---------------------|------------------------------------------------------------------|----------------------------------------------------------------------------|
| **Simple Index**    | `CREATE INDEX FOR (n:Label) ON (n.property)`                     | `CREATE INDEX idx_name ON table (column)`                                  |
| **Composite Index** | `CREATE INDEX FOR (n:Label) ON (n.prop1, n.prop2)`               | `CREATE INDEX idx_name ON table (col1, col2)`                              |
| **Text Index**      | `CREATE TEXT INDEX FOR (n:Label) ON (n.property)`                | `CREATE INDEX idx_name ON table (column) USING gin(to_tsvector(column))`   |
| **Fulltext Index**  | `CREATE FULLTEXT INDEX FOR (n:Label) ON EACH [n.prop1, n.prop2]` | `CREATE FULLTEXT INDEX idx_name ON table (col1, col2)`                     |
| **List Indexes**    | `SHOW INDEXES`                                                   | `SHOW INDEXES FROM table` or `SELECT * FROM information_schema.statistics` |
| **Drop Index**      | `DROP INDEX index_name`                                          | `DROP INDEX idx_name`                                                      |

### 5.8. Performance Tips

```cypher
-- Use EXPLAIN to see index usage
EXPLAIN MATCH (laptop:Laptop {brand: "Lenovo"}) RETURN laptop;

-- Use PROFILE to see actual execution statistics
PROFILE MATCH (laptop:Laptop {brand: "Lenovo"}) RETURN laptop;
```

## 6. Cypher Scripts and How to Run Them

A Cypher script is a file (typically `*.cypher`) containing multiple Cypher statements, similar to SQL scripts.

### 4.1. Neo4j Browser (Web Interface or Neo4j Desktop)

**Access**: `http://localhost:7474` (default Neo4j Browser)

**Single Statement Execution**:

```cypher
CREATE (laptop:Laptop {brand: "HP", model: "Pavilion"});
```

**Multiple Statements** (separate with semicolons):

```cypher
CREATE (laptop111111:Laptop {brand: "HP", model: "Pavilion 111111"});
CREATE (cpu:CPU {name: "Intel i7"});
CREATE (laptop)-[:HAS_CPU]->(cpu);
```

**Script File Import**:

- Copy and paste script contents into the browser
- Use `:play` commands for guided scripts

### 4.2. Cypher Shell (Command Line)

**Installation**: Comes with Neo4j or install separately

**Basic Usage**:

```bash
# Connect interactively
cypher-shell -u neo4j -p password

# Execute single command
cypher-shell -u neo4j -p password "MATCH (n) RETURN count(n);"

# Execute script file
cypher-shell -u neo4j -p password -f laptop_data.cypher

# Execute with different format
cypher-shell -u neo4j -p password --format plain -f script.cypher
```

**Docker Usage**:

```bash
# If Neo4j is in Docker, access the container
docker exec -it neo4j-container cypher-shell -u neo4j -p password

# Or mount script and execute
docker run --rm -v /path/to/script:/script neo4j:latest \
  cypher-shell -u neo4j -p password -f /script/laptop_data.cypher
```

### 4.3. Programming Language Drivers

**Python Example**:

```python
from neo4j import GraphDatabase


def run_script(script_path):
    driver = GraphDatabase.driver("bolt://localhost:7687",
                                  auth=("neo4j", "password"))

    with open(script_path, 'r') as file:
        script = file.read()

    with driver.session() as session:
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in script.split(';') if s.strip()]
        for statement in statements:
            session.run(statement)

    driver.close()


# Usage
run_script('laptop_data.cypher')
```
