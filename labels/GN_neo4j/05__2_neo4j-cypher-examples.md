# Neo4j Examples

## 1. Insert - Sample Script File

### 1.1. **laptop_data.cypher**:

```cypher
// Create laptop nodes
CREATE (hp:Laptop {brand: "HP", model: "Pavilion", price: 999});
CREATE (lenovo:Laptop {brand: "Lenovo", model: "ThinkPad", price: 1299});
CREATE (dell:Laptop {brand: "Dell", model: "XPS", price: 1599});

// Create component nodes
CREATE (i5:CPU {name: "Intel i5", cores: 4});
CREATE (i7:CPU {name: "Intel i7", cores: 8});
CREATE (ram8:RAM {size: "8GB", type: "DDR4"});
CREATE (ram16:RAM {size: "16GB", type: "DDR4"});

// Create relationships
CREATE (hp)-[:HAS_CPU]->(i5);
CREATE (hp)-[:HAS_RAM]->(ram8);
CREATE (lenovo)-[:HAS_CPU]->(i7);
CREATE (lenovo)-[:HAS_RAM]->(ram16);
CREATE (dell)-[:HAS_CPU]->(i7);
CREATE (dell)-[:HAS_RAM]->(ram16);

// Create indexes
CREATE INDEX laptop__brand__idx FOR (l:Laptop) ON (l.brand);
CREATE INDEX cpu__name__idx FOR (c:CPU) ON (c.name);
```

### 1.2. Best Practices

- **Use transactions**: Large scripts should use explicit transactions
- **Handle errors**: Include error handling in production scripts
- **Use parameters**: For dynamic values, use parameterized queries
- **Test incrementally**: Run small portions first to validate logic

## 2. Querying Examples

### 2.1. Basic MATCH Queries

```cypher
-- Find all laptops
MATCH (laptop:Laptop)
RETURN laptop.brand, laptop.model, laptop.price;

-- Find specific laptop by brand
MATCH (laptop:Laptop {brand: "Lenovo"})
RETURN laptop;

-- Find laptops with specific CPU
MATCH (laptop:Laptop)-[:HAS_CPU]->(cpu:CPU {name: "Intel i7"})
RETURN laptop.brand, laptop.model;
```

### 2.2. WHERE Clause Filtering

```cypher
-- Find laptops under $1200
MATCH (laptop:Laptop)
WHERE laptop.price < 1200
RETURN laptop.brand, laptop.model, laptop.price;

-- Find laptops with Intel CPUs
MATCH (laptop:Laptop)-[:HAS_CPU]->(cpu:CPU)
WHERE cpu.name CONTAINS "Intel"
RETURN laptop.brand, laptop.model, cpu.name;

-- Complex filtering
MATCH (laptop:Laptop)-[:HAS_RAM]->(ram:RAM)
WHERE laptop.price > 1000 AND ram.size = "16GB"
RETURN laptop.brand, laptop.model, laptop.price, ram.size;
```

### 2.3. Aggregation and Grouping

```cypher
-- Count laptops by brand
MATCH (laptop:Laptop)
RETURN laptop.brand, count(*) as laptop_count
ORDER BY laptop_count DESC;

-- Average price by brand
MATCH (laptop:Laptop)
RETURN laptop.brand, avg(laptop.price) as avg_price
ORDER BY avg_price DESC;

-- Collect all models per brand
MATCH (laptop:Laptop)
RETURN laptop.brand, collect(laptop.model) as models;
```

### 2.4. Relationship Traversal

```cypher
-- Find all components of a specific laptop
MATCH (laptop:Laptop {brand: "HP"})-[rel]->(component)
RETURN laptop.model, type(rel) as relationship, labels(component) as component_type, component;

-- Find laptops with same CPU (relationship discovery)
MATCH (laptop1:Laptop)-[:HAS_CPU]->(cpu:CPU)<-[:HAS_CPU]-(laptop2:Laptop)
WHERE laptop1 <> laptop2
RETURN laptop1.brand as brand1, laptop2.brand as brand2, cpu.name;

-- Multi-hop traversal (laptops with same CPU and RAM)
MATCH (laptop1:Laptop)-[:HAS_CPU]->(cpu:CPU)<-[:HAS_CPU]-(laptop2:Laptop),
      (laptop1)-[:HAS_RAM]->(ram:RAM)<-[:HAS_RAM]-(laptop2)
WHERE laptop1 <> laptop2
RETURN laptop1.brand, laptop2.brand, cpu.name, ram.size;
```

### 2.5. Optional Matching

```cypher
-- Find all laptops with optional GPU information
MATCH (laptop:Laptop)
OPTIONAL MATCH (laptop)-[:HAS_GPU]->(gpu:GPU)
RETURN laptop.brand, laptop.model, gpu.name as gpu_name;

-- Left join equivalent
MATCH (laptop:Laptop)-[:HAS_CPU]->(cpu:CPU)
OPTIONAL MATCH (laptop)-[:HAS_GPU]->(gpu:GPU)
RETURN laptop.brand, laptop.model, cpu.name,
       CASE WHEN gpu IS NULL THEN "Integrated Graphics" ELSE gpu.name END as graphics;
```

### 2.6. Pattern Matching and Paths

```cypher
-- Find shortest path between two laptops through shared components
MATCH path = shortestPath((laptop1:Laptop {brand: "HP"})-[*]-(laptop2:Laptop {brand: "Dell"}))
RETURN path;

-- Variable length relationships (find all laptops within 2 hops)
MATCH (laptop:Laptop {brand: "HP"})-[*1..2]-(connected)
RETURN laptop.model, connected;

-- Find laptops that share ANY component
MATCH (laptop1:Laptop)-[:HAS_CPU|HAS_RAM|HAS_GPU]->(component)<-[:HAS_CPU|HAS_RAM|HAS_GPU]-(laptop2:Laptop)
WHERE laptop1 <> laptop2
RETURN laptop1.brand, laptop2.brand, labels(component) as shared_component_type, component;
```

### 2.7. Subqueries and Complex Logic

```cypher
-- Find laptops with above-average price in their brand category
MATCH (laptop:Laptop)
WITH laptop.brand as brand, avg(laptop.price) as avg_brand_price
MATCH (laptop:Laptop {brand: brand})
WHERE laptop.price > avg_brand_price
RETURN laptop.brand, laptop.model, laptop.price, avg_brand_price;

-- Find brands that make both budget and premium laptops
MATCH (laptop:Laptop)
WITH laptop.brand as brand, min(laptop.price) as min_price, max(laptop.price) as max_price
WHERE min_price < 1000 AND max_price > 1500
RETURN brand, min_price, max_price;
```

### 2.8. Practical Business Queries

```cypher
-- Recommend similar laptops (same CPU, different brand)
MATCH (target:Laptop {brand: "HP", model: "Pavilion"})-[:HAS_CPU]->(cpu:CPU)
MATCH (similar:Laptop)-[:HAS_CPU]->(cpu)
WHERE similar.brand <> target.brand
RETURN similar.brand, similar.model, similar.price
ORDER BY abs(similar.price - target.price);

-- Find upgrade path (laptops with better specs)
MATCH (current:Laptop {brand: "HP", model: "Pavilion"})-[:HAS_CPU]->(current_cpu:CPU),
      (upgrade:Laptop)-[:HAS_CPU]->(upgrade_cpu:CPU)
WHERE upgrade_cpu.cores > current_cpu.cores
RETURN upgrade.brand, upgrade.model, upgrade.price,
       current_cpu.cores as current_cores, upgrade_cpu.cores as upgrade_cores;

-- Inventory analysis (components used across laptops)
MATCH (component)-[r]-(laptop:Laptop)
RETURN labels(component)[0] as component_type,
       component.name as component_name,
       count(laptop) as used_in_laptops,
       collect(laptop.brand + " " + laptop.model) as laptop_models;
```
