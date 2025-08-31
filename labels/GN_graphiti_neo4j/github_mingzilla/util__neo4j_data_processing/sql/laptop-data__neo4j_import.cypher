// Neo4j CSV Import Script
// Generated for laptop-data
// Run with: cypher-shell -f <script_name>

// Create constraints for data integrity
CREATE CONSTRAINT laptop_id IF NOT EXISTS FOR (n:E_Laptop) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT document_id IF NOT EXISTS FOR (n:D_LaptopSpec) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT cpu_id IF NOT EXISTS FOR (n:A_CPUType) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT gpu_id IF NOT EXISTS FOR (n:A_GPUType) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT ram_id IF NOT EXISTS FOR (n:A_RAMType) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT brand_id IF NOT EXISTS FOR (n:V_Brand) REQUIRE n.id IS UNIQUE;

// Create indexes for query performance
CREATE INDEX laptop_name IF NOT EXISTS FOR (n:E_Laptop) ON n.name;
CREATE INDEX laptop_price IF NOT EXISTS FOR (n:E_Laptop) ON n.price;
CREATE INDEX cpu_normalized IF NOT EXISTS FOR (n:A_CPUType) ON n.normalized;
CREATE INDEX gpu_normalized IF NOT EXISTS FOR (n:A_GPUType) ON n.normalized;
CREATE INDEX ram_normalized IF NOT EXISTS FOR (n:A_RAMType) ON n.normalized;
CREATE INDEX brand_name IF NOT EXISTS FOR (n:V_Brand) ON n.name;
CREATE FULLTEXT INDEX laptop_search IF NOT EXISTS FOR (n:E_Laptop) ON EACH [n.name, n.description];

// Import D_LaptopSpec nodes
LOAD CSV WITH HEADERS FROM 'file:///laptop-data__neo4j_nodes_D_LaptopSpec.csv' AS row
CREATE (n:D_LaptopSpec)
SET n = row, n.id = row.`id:ID`
REMOVE n.`id:ID`, n.`:LABEL`;

// Import E_Laptop nodes
LOAD CSV WITH HEADERS FROM 'file:///laptop-data__neo4j_nodes_E_Laptop.csv' AS row
CREATE (n:E_Laptop)
SET n = row, n.id = row.`id:ID`
REMOVE n.`id:ID`, n.`:LABEL`;

// Import A_CPUType nodes
LOAD CSV WITH HEADERS FROM 'file:///laptop-data__neo4j_nodes_A_CPUType.csv' AS row
CREATE (n:A_CPUType)
SET n = row, n.id = row.`id:ID`
REMOVE n.`id:ID`, n.`:LABEL`;

// Import A_GPUType nodes
LOAD CSV WITH HEADERS FROM 'file:///laptop-data__neo4j_nodes_A_GPUType.csv' AS row
CREATE (n:A_GPUType)
SET n = row, n.id = row.`id:ID`
REMOVE n.`id:ID`, n.`:LABEL`;

// Import A_RAMType nodes
LOAD CSV WITH HEADERS FROM 'file:///laptop-data__neo4j_nodes_A_RAMType.csv' AS row
CREATE (n:A_RAMType)
SET n = row, n.id = row.`id:ID`
REMOVE n.`id:ID`, n.`:LABEL`;

// Import V_Brand nodes
LOAD CSV WITH HEADERS FROM 'file:///laptop-data__neo4j_nodes_V_Brand.csv' AS row
CREATE (n:V_Brand)
SET n = row, n.id = row.`id:ID`
REMOVE n.`id:ID`, n.`:LABEL`;

// Import CONTAINS_D relationships
LOAD CSV WITH HEADERS FROM 'file:///laptop-data__neo4j_rels_CONTAINS_D.csv' AS row
MATCH (from) WHERE from.id = row.`:START_ID`
MATCH (to) WHERE to.id = row.`:END_ID`
CREATE (from)-[r:CONTAINS_D]->(to);

// Import HAS_A_CPU relationships
LOAD CSV WITH HEADERS FROM 'file:///laptop-data__neo4j_rels_HAS_A_CPU.csv' AS row
MATCH (from) WHERE from.id = row.`:START_ID`
MATCH (to) WHERE to.id = row.`:END_ID`
CREATE (from)-[r:HAS_A_CPU]->(to);

// Import HAS_A_GPU relationships
LOAD CSV WITH HEADERS FROM 'file:///laptop-data__neo4j_rels_HAS_A_GPU.csv' AS row
MATCH (from) WHERE from.id = row.`:START_ID`
MATCH (to) WHERE to.id = row.`:END_ID`
CREATE (from)-[r:HAS_A_GPU]->(to);

// Import HAS_A_RAM relationships
LOAD CSV WITH HEADERS FROM 'file:///laptop-data__neo4j_rels_HAS_A_RAM.csv' AS row
MATCH (from) WHERE from.id = row.`:START_ID`
MATCH (to) WHERE to.id = row.`:END_ID`
CREATE (from)-[r:HAS_A_RAM]->(to);

// Import HAS_V_BRAND relationships
LOAD CSV WITH HEADERS FROM 'file:///laptop-data__neo4j_rels_HAS_V_BRAND.csv' AS row
MATCH (from) WHERE from.id = row.`:START_ID`
MATCH (to) WHERE to.id = row.`:END_ID`
CREATE (from)-[r:HAS_V_BRAND]->(to);

// Verify import
MATCH (n) RETURN labels(n), count(n) ORDER BY labels(n);
MATCH ()-[r]->() RETURN type(r), count(r) ORDER BY type(r);
