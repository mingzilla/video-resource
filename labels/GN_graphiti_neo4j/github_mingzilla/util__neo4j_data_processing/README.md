# Neo4j Data Processing Utilities

- Prerequisite: Docker
- SQL File with Test Data
- Convert SQL into Neo4j data
- Import Neo4j data

## Usage - Convert SQL into Neo4j Content

Converting SQL laptop data to Neo4j graph database format, following the established 4-level abstraction pattern (D_, E_, A_, V_) and naming conventions.

```bash
uv venv
source .venv/Scripts/activate
uv run python -m github_mingzilla.util__neo4j_data_processing.neo4j_bulk_importer --sql-files github_mingzilla/util__neo4j_data_processing/sql/laptop-data.sql
```

## Dependencies

None. Just use Python 3.11.

## Implementation Details

### 4-Level Graph Abstraction

Following the established documentation patterns:

- **D_LaptopSpec** (Document): Raw SQL data and source tracking
- **E_Laptop** (Entity): Core laptop objects with normalized properties
- **A_CPUType, A_GPUType, A_RAMType** (Attribute): Normalized specifications handling data variations
- **V_Brand** (Value): Fixed enumerated values for brands

### Data Normalization

Handles common data quality issues:

- CPU variations: "i9", "I9", "Intel i9", "Intel Core i9" → "i9"
- GPU variations: "Nvidia 20xx", "NVIDIA RTX 20xx", "GeForce RTX 20xx" → "20xx"
- RAM variations: "32GB", "32G", "32 GB" → "32GB"
- Brand consistency: Preserves exact brand names

### Relationship Model

```cypher
(E_Laptop)-[:CONTAINS_D]->(D_LaptopSpec)
(E_Laptop)-[:HAS_A_CPU]->(A_CPUType)
(E_Laptop)-[:HAS_A_GPU]->(A_GPUType)
(E_Laptop)-[:HAS_A_RAM]->(A_RAMType)
(E_Laptop)-[:HAS_V_BRAND]->(V_Brand)
```
