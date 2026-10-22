# Neo4j Relationship Query

## 1. Data

| Attribute    | Possible ids                                               | id Prefix   |
|--------------|------------------------------------------------------------|-------------|
| A_CPUType    | cpu_type_i3, cpu_type_i5, cpu_type_i7, cpu_type_i9         | cpu_type_   |
| A_GPUType    | gpu_type_20xx, gpu_type_30xx, gpu_type_40xx, gpu_type_50xx | gpu_type_   |
| A_RAMType    | ram_type_8gb, ~16gb, ~24gb, ~32gb, ~64G, ~128gb            | ram_type_   |
| V_Brand      | (90 items)                                                 | brand_      |
| E_Laptop     | (545 items)                                                | laptop_     |
| D_LaptopSpec | (545 items)                                                | doc_laptop_ |
| Hard Drive   | 1T, 2T, 4T (No nodes created)                              |             |
| Screen       | 13, 15, 16 (No nodes created)                              |             |

## 2. Basic Queries

### 2.1 Find Laptops with Same CPU and RAM Spec

```cypher
-- Option 1: E/A/V Pattern (Recommended for Scale)
-- Find laptops sharing the same CPU attribute node
-- Also sharing the same RAM attribute node
MATCH (laptop1:E_Laptop)-[:HAS_A_CPU]->(cpu:A_CPUType)<-[:HAS_A_CPU]-(laptop2:E_Laptop)
MATCH (laptop1)-[:HAS_A_RAM]->(ram:A_RAMType)<-[:HAS_A_RAM]-(laptop2)
WHERE laptop1 <> laptop2
RETURN laptop1.id, laptop2.id, cpu.id as cpu_spec, ram.id as ram_spec
LIMIT 25;

-- Example result:
-- laptop_001, laptop_045, cpu_type_i9, ram_type_32gb
-- laptop_023, laptop_067, cpu_type_i7, ram_type_16gb
```

### 2.2 Find Similar to Specific Laptop

```cypher
-- Find laptops with same specs as a reference laptop
MATCH (laptop1:E_Laptop {id: "laptop_yoga_9i_2_in_1"})-[:HAS_A_CPU]->(cpu:A_CPUType)<-[:HAS_A_CPU]-(laptop2:E_Laptop)
MATCH (laptop1)-[:HAS_A_RAM]->(ram:A_RAMType)<-[:HAS_A_RAM]-(laptop2)
WHERE laptop1 <> laptop2
RETURN laptop2
LIMIT 25;

MATCH (laptop1:E_Laptop)-[:HAS_A_CPU]->(cpu:A_CPUType)<-[:HAS_A_CPU]-(laptop2:E_Laptop)
MATCH (laptop1)-[:HAS_A_RAM]->(ram:A_RAMType)<-[:HAS_A_RAM]-(laptop2)
WHERE laptop1 <> laptop2
AND laptop1.id = "laptop_yoga_9i_2_in_1"
RETURN laptop2
LIMIT 25;

-- Example: If laptop_yoga_9i_2_in_1 has cpu_type_i9 + ram_type_32gb
-- Returns all other laptops with same CPU and RAM combination
```

#### 2.2.1. Performance Differences

Performance:

- `SHOW INDEXES` - double check if desired indexes are present
- `PROFILE ~` - add `PROFILE` to the beginning, then you get a plan for the query

### 2.3 Group Laptops by Spec Combinations

```cypher
-- Group laptops by CPU + RAM combination
-- WHERE size(laptop_ids) > 1 -- Only specs with multiple laptops
MATCH (laptop:E_Laptop)-[:HAS_A_CPU]->(cpu:A_CPUType)
MATCH (laptop)-[:HAS_A_RAM]->(ram:A_RAMType)
WITH cpu.id + "_" + ram.id as spec_combo, collect(laptop.id) as laptop_ids
WHERE size(laptop_ids) > 1
RETURN spec_combo, laptop_ids, size(laptop_ids) as count
ORDER BY count DESC
LIMIT 25;

-- Example result:
-- "cpu_type_i7_ram_type_16gb", ["laptop_023", "laptop_067", "laptop_089"], 3
-- "cpu_type_i9_ram_type_32gb", ["laptop_001", "laptop_045"], 2
```

### 2.4 Find Laptops by Multiple Attributes

```cypher
-- Find laptops with specific CPU, RAM, and GPU combination
-- Query 1
MATCH (cpu:A_CPUType {id: "cpu_type_i9"})<-[:HAS_A_CPU]-(laptop:E_Laptop)-[:HAS_A_RAM]->(ram:A_RAMType {id: "ram_type_32gb"})
MATCH (laptop)-[:HAS_A_GPU]->(gpu:A_GPUType {id: "gpu_type_40xx"})
RETURN laptop.id, cpu.id, ram.id, gpu.id
LIMIT 25;

-- Query 2 - Same as Query 1
MATCH (cpu:A_CPUType {id: "cpu_type_i9"})<-[:HAS_A_CPU]-(laptop:E_Laptop)
MATCH (laptop)-[:HAS_A_RAM]->(ram:A_RAMType {id: "ram_type_32gb"})
MATCH (laptop)-[:HAS_A_GPU]->(gpu:A_GPUType {id: "gpu_type_40xx"})
RETURN laptop.id, cpu.id, ram.id, gpu.id
LIMIT 25;

-- Query 3 - Different From Query 1 - They differ in the **direction**
MATCH (laptop:E_Laptop)-[:HAS_A_CPU]->(cpu:A_CPUType {id: "cpu_type_i9"})
MATCH (laptop)-[:HAS_A_RAM]->(ram:A_RAMType {id: "ram_type_32gb"})
MATCH (laptop)-[:HAS_A_GPU]->(gpu:A_GPUType {id: "gpu_type_40xx"})
RETURN laptop.id, cpu.id, ram.id, gpu.id
LIMIT 25;
```

| Query   | CPU Relationship Direction     | Meaning                             |
|---------|--------------------------------|-------------------------------------|
| Query 1 | `(cpu)<-[:HAS_A_CPU]-(laptop)` | CPU ← laptop (incoming to CPU)      |
| Query 3 | `(laptop)-[:HAS_A_CPU]->(cpu)` | laptop → CPU (outgoing from laptop) |

#### Relationship Direction Analysis

```
Query 1: (cpu)<-[:HAS_A_CPU]-(laptop)
         [CPU] <-- HAS_A_CPU -- [Laptop]
         
Query 3: (laptop)-[:HAS_A_CPU]->(cpu)  
         [Laptop] -- HAS_A_CPU --> [CPU]
```

#### Semantic Implications

| Aspect                | Query 1                            | Query 3                              |
|-----------------------|------------------------------------|--------------------------------------|
| **Relationship flow** | CPU receives HAS_A_CPU from laptop | Laptop has HAS_A_CPU pointing to CPU |
| **Graph modeling**    | CPU-centric view                   | Laptop-centric view                  |

- With LIMIT and no ORDER BY: Queries may return different subsets of results due to undefined row ordering.
- Without LIMIT: Queries return identical data (all matching rows), but row order is unspecified and may differ.

#### ORDER BY

```cypher
MATCH (laptop:E_Laptop)-[:HAS_A_CPU]->(cpu:A_CPUType {id: "cpu_type_i9"})
MATCH (laptop)-[:HAS_A_RAM]->(ram:A_RAMType {id: "ram_type_32gb"})
MATCH (laptop)-[:HAS_A_GPU]->(gpu:A_GPUType {id: "gpu_type_40xx"})
RETURN laptop.id, cpu.id, ram.id, gpu.id
ORDER BY laptop.id
LIMIT 25;
```

If order by is used, then the result after using LIMIT CAN be the same:

- because the execution plan works it out
- assuming we order the nodes by laptop.id
- they can still have different results because item 25 may be different items with the same id

#### Indexing

| Scenario                  | Performance Impact   | Memory Requirement                            |
|---------------------------|----------------------|-----------------------------------------------|
| **laptop.id indexed**     | Minimal overhead     | Minimal (streaming possible)                  |
| **laptop.id not indexed** | Significant overhead | High (sorting all matching results in memory) |

**With Index on laptop.id**

```
Neo4j Execution:
1. Pattern matching → Find matching laptops
2. ORDER BY laptop.id → Use index for efficient sort
3. LIMIT 25 → Stop after first 25 sorted results
Performance: O(n log n) where n = matching laptops
```

**Without Index on laptop.id**

```
Neo4j Execution:
1. Pattern matching → Find ALL matching laptops
2. Collect results in memory → Full materialization
3. Sort in memory → O(n log n) sort operation  
4. LIMIT 25 → Return first 25
Performance: Must process entire result set
```
