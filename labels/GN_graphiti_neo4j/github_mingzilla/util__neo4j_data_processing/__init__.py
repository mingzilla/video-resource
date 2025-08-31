"""
Neo4j Data Processing Utilities

This package provides utilities for converting SQL data to Neo4j graph database format,
following the 4-level abstraction pattern (D_, E_, A_, V_) and established naming conventions.

Modules:
- sql_parser: Parse SQL INSERT statements and extract structured data
- graph_model_mapper: Convert laptop data to 4-level graph model
- csv_generator: Generate Neo4j-compatible CSV files
- cypher_script_generator: Create Cypher CREATE/MERGE statements
- neo4j_bulk_importer: Execute bulk import into Neo4j
"""
