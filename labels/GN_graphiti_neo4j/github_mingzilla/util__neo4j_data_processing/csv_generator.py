"""
CSV Generator for Neo4j Import

Generates Neo4j-compatible CSV files from the graph model with proper headers and formatting.
Creates separate files for nodes and relationships following Neo4j LOAD CSV best practices.
"""

import csv
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from github_mingzilla.util__neo4j_data_processing.graph_model_mapper import GraphModel, GraphNode, GraphRelationship


class CSVGenerator:
    """
    Generates Neo4j-compatible CSV files from graph model.

    Creates separate CSV files for:
    - Each node type (D_LaptopSpec, E_Laptop, A_CPUType, etc.)
    - Each relationship type (CONTAINS_D, HAS_A_CPU, etc.)
    """

    def __init__(self):
        self.output_directory: str = ""
        self.base_filename: str = ""

    def generate_csv_files(self, graph_model: GraphModel, output_path: str, base_filename: str) -> Dict[str, str]:
        """
        Generate all CSV files for the graph model.

        Args:
            graph_model: Graph model to export
            output_path: Directory to write CSV files
            base_filename: Base filename (e.g., "laptop-data" for "laptop-data__neo4j_nodes_E_Laptop.csv")

        Returns:
            Dictionary mapping file type to file path
        """
        self.output_directory = output_path
        self.base_filename = base_filename

        # Ensure output directory exists
        Path(output_path).mkdir(parents=True, exist_ok=True)

        generated_files = {}

        # Generate node CSV files grouped by label
        node_files = self._generate_node_csv_files(graph_model)
        generated_files.update(node_files)

        # Generate relationship CSV files grouped by type
        relationship_files = self._generate_relationship_csv_files(graph_model)
        generated_files.update(relationship_files)

        # Generate master import script
        import_script_path = self._generate_import_script(generated_files)
        generated_files["import_script"] = import_script_path

        return generated_files

    def _generate_node_csv_files(self, graph_model: GraphModel) -> Dict[str, str]:
        """Generate CSV files for nodes, grouped by label."""
        # Group nodes by label
        nodes_by_label = defaultdict(list)
        for node in graph_model.nodes.values():
            nodes_by_label[node.label].append(node)

        generated_files = {}

        for label, nodes in nodes_by_label.items():
            filename = f"{self.base_filename}__neo4j_nodes_{label}.csv"
            file_path = os.path.join(self.output_directory, filename)

            # Generate CSV file for this node type
            self._write_nodes_csv(nodes, file_path, label)
            generated_files[f"nodes_{label}"] = file_path

            print(f"Generated {filename}: {len(nodes)} nodes")

        return generated_files

    def _generate_relationship_csv_files(self, graph_model: GraphModel) -> Dict[str, str]:
        """Generate CSV files for relationships, grouped by type."""
        # Group relationships by type
        rels_by_type = defaultdict(list)
        for rel in graph_model.relationships:
            rels_by_type[rel.relationship_type].append(rel)

        generated_files = {}

        for rel_type, relationships in rels_by_type.items():
            filename = f"{self.base_filename}__neo4j_rels_{rel_type}.csv"
            file_path = os.path.join(self.output_directory, filename)

            # Generate CSV file for this relationship type
            self._write_relationships_csv(relationships, file_path, rel_type)
            generated_files[f"rels_{rel_type}"] = file_path

            print(f"Generated {filename}: {len(relationships)} relationships")

        return generated_files

    def _write_nodes_csv(self, nodes: List[GraphNode], file_path: str, label: str) -> None:
        """Write nodes to CSV file with Neo4j-compatible format."""
        if not nodes:
            return

        # Determine all possible properties across nodes
        all_properties = set()
        for node in nodes:
            all_properties.update(node.properties.keys())

        # Sort properties for consistent ordering
        property_columns = sorted(all_properties)

        # Create CSV header with Neo4j format
        # Format: id:ID,property1,property2,:LABEL
        headers = ["id:ID"] + property_columns + [":LABEL"]

        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

            # Write header
            writer.writerow(headers)

            # Write data rows
            for node in nodes:
                row = [node.id]

                # Add property values
                for prop in property_columns:
                    value = node.properties.get(prop, "")

                    # Handle list properties (convert to semicolon-separated string)
                    if isinstance(value, list):
                        value = ";".join(str(v) for v in value)
                    # Handle complex objects
                    elif isinstance(value, (dict, tuple)):
                        value = str(value)
                    # Handle None values
                    elif value is None:
                        value = ""

                    row.append(value)

                # Add label
                row.append(label)

                writer.writerow(row)

    def _write_relationships_csv(self, relationships: List[GraphRelationship], file_path: str, rel_type: str) -> None:
        """Write relationships to CSV file with Neo4j-compatible format."""
        if not relationships:
            return

        # Determine all possible properties across relationships
        all_properties = set()
        for rel in relationships:
            all_properties.update(rel.properties.keys())

        property_columns = sorted(all_properties)

        # Create CSV header with Neo4j format
        # Format: :START_ID,:END_ID,property1,property2,:TYPE
        headers = [":START_ID", ":END_ID"] + property_columns + [":TYPE"]

        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

            # Write header
            writer.writerow(headers)

            # Write data rows
            for rel in relationships:
                row = [rel.from_node_id, rel.to_node_id]

                # Add property values
                for prop in property_columns:
                    value = rel.properties.get(prop, "")

                    # Handle complex types
                    if isinstance(value, list):
                        value = ";".join(str(v) for v in value)
                    elif isinstance(value, (dict, tuple)):
                        value = str(value)
                    elif value is None:
                        value = ""

                    row.append(value)

                # Add relationship type
                row.append(rel_type)

                writer.writerow(row)

    def _generate_import_script(self, generated_files: Dict[str, str]) -> str:
        """Generate Cypher import script for all CSV files."""
        script_filename = f"{self.base_filename}__neo4j_import.cypher"
        script_path = os.path.join(self.output_directory, script_filename)

        with open(script_path, "w", encoding="utf-8") as script_file:
            script_file.write("// Neo4j CSV Import Script\n")
            script_file.write(f"// Generated for {self.base_filename}\n")
            script_file.write("// Run with: cypher-shell -f <script_name>\n\n")

            # Add constraints first
            script_file.write("// Create constraints for data integrity\n")
            script_file.write("CREATE CONSTRAINT laptop_id IF NOT EXISTS FOR (n:E_Laptop) REQUIRE n.id IS UNIQUE;\n")
            script_file.write("CREATE CONSTRAINT document_id IF NOT EXISTS FOR (n:D_LaptopSpec) REQUIRE n.id IS UNIQUE;\n")
            script_file.write("CREATE CONSTRAINT cpu_id IF NOT EXISTS FOR (n:A_CPUType) REQUIRE n.id IS UNIQUE;\n")
            script_file.write("CREATE CONSTRAINT gpu_id IF NOT EXISTS FOR (n:A_GPUType) REQUIRE n.id IS UNIQUE;\n")
            script_file.write("CREATE CONSTRAINT ram_id IF NOT EXISTS FOR (n:A_RAMType) REQUIRE n.id IS UNIQUE;\n")
            script_file.write("CREATE CONSTRAINT brand_id IF NOT EXISTS FOR (n:V_Brand) REQUIRE n.id IS UNIQUE;\n\n")

            # Add indexes for performance
            script_file.write("// Create indexes for query performance\n")
            script_file.write("CREATE INDEX laptop_name IF NOT EXISTS FOR (n:E_Laptop) ON n.name;\n")
            script_file.write("CREATE INDEX laptop_price IF NOT EXISTS FOR (n:E_Laptop) ON n.price;\n")
            script_file.write("CREATE INDEX cpu_normalized IF NOT EXISTS FOR (n:A_CPUType) ON n.normalized;\n")
            script_file.write("CREATE INDEX gpu_normalized IF NOT EXISTS FOR (n:A_GPUType) ON n.normalized;\n")
            script_file.write("CREATE INDEX ram_normalized IF NOT EXISTS FOR (n:A_RAMType) ON n.normalized;\n")
            script_file.write("CREATE INDEX brand_name IF NOT EXISTS FOR (n:V_Brand) ON n.name;\n")
            script_file.write("CREATE FULLTEXT INDEX laptop_search IF NOT EXISTS FOR (n:E_Laptop) ON EACH [n.name, n.description];\n\n")

            # Import nodes first (in dependency order)
            node_labels = ["D_LaptopSpec", "E_Laptop", "A_CPUType", "A_GPUType", "A_RAMType", "V_Brand"]

            for label in node_labels:
                file_key = f"nodes_{label}"
                if file_key in generated_files:
                    csv_filename = os.path.basename(generated_files[file_key])
                    script_file.write(f"// Import {label} nodes\n")
                    script_file.write(f"LOAD CSV WITH HEADERS FROM 'file:///{csv_filename}' AS row\n")
                    script_file.write(f"CREATE (n:{label})\n")
                    script_file.write("SET n = row, n.id = row.`id:ID`\n")
                    script_file.write("REMOVE n.`id:ID`, n.`:LABEL`;\n\n")

            # Import relationships (in logical order)
            rel_types = ["CONTAINS_D", "HAS_A_CPU", "HAS_A_GPU", "HAS_A_RAM", "HAS_V_BRAND"]

            for rel_type in rel_types:
                file_key = f"rels_{rel_type}"
                if file_key in generated_files:
                    csv_filename = os.path.basename(generated_files[file_key])
                    script_file.write(f"// Import {rel_type} relationships\n")
                    script_file.write(f"LOAD CSV WITH HEADERS FROM 'file:///{csv_filename}' AS row\n")
                    script_file.write("MATCH (from) WHERE from.id = row.`:START_ID`\n")
                    script_file.write("MATCH (to) WHERE to.id = row.`:END_ID`\n")
                    script_file.write(f"CREATE (from)-[r:{rel_type}]->(to);\n\n")

            script_file.write("// Verify import\n")
            script_file.write("MATCH (n) RETURN labels(n), count(n) ORDER BY labels(n);\n")
            script_file.write("MATCH ()-[r]->() RETURN type(r), count(r) ORDER BY type(r);\n")

        print(f"Generated import script: {script_filename}")
        return script_path

    def generate_summary_report(self, graph_model: GraphModel, generated_files: Dict[str, str]) -> str:
        """Generate a summary report of the CSV generation process."""
        report_filename = f"{self.base_filename}__neo4j_summary.txt"
        report_path = os.path.join(self.output_directory, report_filename)

        # Count nodes and relationships by type
        node_counts = defaultdict(int)
        for node in graph_model.nodes.values():
            node_counts[node.label] += 1

        rel_counts = defaultdict(int)
        for rel in graph_model.relationships:
            rel_counts[rel.relationship_type] += 1

        with open(report_path, "w", encoding="utf-8") as report_file:
            report_file.write("Neo4j CSV Generation Summary\n")
            report_file.write(f"{'=' * 40}\n\n")

            report_file.write(f"Base filename: {self.base_filename}\n")
            report_file.write(f"Output directory: {self.output_directory}\n")
            report_file.write(f"Generated at: {__import__('datetime').datetime.now().isoformat()}\n\n")

            report_file.write("Graph Model Statistics:\n")
            report_file.write(f"  Total nodes: {len(graph_model.nodes)}\n")
            report_file.write(f"  Total relationships: {len(graph_model.relationships)}\n\n")

            report_file.write("Node breakdown:\n")
            for label, count in sorted(node_counts.items()):
                report_file.write(f"  {label}: {count}\n")
            report_file.write("\n")

            report_file.write("Relationship breakdown:\n")
            for rel_type, count in sorted(rel_counts.items()):
                report_file.write(f"  {rel_type}: {count}\n")
            report_file.write("\n")

            report_file.write("Generated files:\n")
            for file_type, file_path in sorted(generated_files.items()):
                filename = os.path.basename(file_path)
                report_file.write(f"  {file_type}: {filename}\n")

            report_file.write("\nImport Instructions:\n")
            report_file.write("1. Copy all CSV files to Neo4j import directory\n")
            report_file.write(f"2. Run: cypher-shell -f {self.base_filename}__neo4j_import.cypher\n")
            report_file.write("3. Verify import with summary queries at end of script\n")

        print(f"Generated summary report: {report_filename}")
        return report_path


def main():
    """Test the CSV generator with graph model data."""
    from github_mingzilla.util__neo4j_data_processing.graph_model_mapper import GraphModelMapper
    from github_mingzilla.util__neo4j_data_processing.sql_parser import SQLParser

    # Parse SQL data and create graph model
    parser = SQLParser()
    sql_directory = "sql"

    try:
        results = parser.parse_all_sql_files(sql_directory)

        # Combine all records
        all_records = []
        for records in results.values():
            all_records.extend(records)

        print(f"Loaded {len(all_records)} total laptop records")

        # Map to graph model
        mapper = GraphModelMapper()
        graph_model = mapper.map_laptop_records(all_records)

        # Generate CSV files
        generator = CSVGenerator()
        output_directory = sql_directory  # Same directory as SQL files
        base_filename = "laptop-data-combined"

        print("\nGenerating CSV files...")
        generated_files = generator.generate_csv_files(graph_model, output_directory, base_filename)

        # Generate summary report
        report_path = generator.generate_summary_report(graph_model, generated_files)

        print("\n=== CSV Generation Complete ===")
        print(f"Generated {len(generated_files)} files in {output_directory}")
        print(f"Summary report: {os.path.basename(report_path)}")

        # Show files generated
        print("\nGenerated files:")
        for file_type, file_path in sorted(generated_files.items()):
            filename = os.path.basename(file_path)
            print(f"  {filename}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
