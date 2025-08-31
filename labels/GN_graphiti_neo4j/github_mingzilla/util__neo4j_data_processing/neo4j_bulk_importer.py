"""
Neo4j Bulk Importer

Command-line interface for converting SQL laptop data to Neo4j CSV format.
Provides end-to-end pipeline from SQL files to Neo4j-ready CSV files and import scripts.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from github_mingzilla.util__neo4j_data_processing.csv_generator import CSVGenerator
from github_mingzilla.util__neo4j_data_processing.graph_model_mapper import GraphModelMapper
from github_mingzilla.util__neo4j_data_processing.sql_parser import SQLParser


class Neo4jBulkImporter:
    """
    Main class for SQL to Neo4j conversion pipeline.

    Coordinates parsing, mapping, and CSV generation for bulk import.
    """

    def __init__(self):
        self.parser = SQLParser()
        self.mapper = GraphModelMapper()
        self.csv_generator = CSVGenerator()

    def convert_sql_to_csv(self, sql_files: List[str] = None, sql_directory: str = None, output_directory: str = None, base_filename: str = "laptop-data") -> Dict[str, Any]:
        """
        Convert SQL files to Neo4j CSV format.

        Args:
            sql_files: List of specific SQL files to process
            sql_directory: Directory containing SQL files (processes all laptop-data*.sql)
            output_directory: Where to write CSV files (defaults to same as SQL directory)
            base_filename: Base name for output files

        Returns:
            Results dictionary with statistics and file paths
        """
        print("=== Neo4j Bulk Import Pipeline ===")

        # Determine input files
        if sql_files:
            # Process specific files
            records_by_file = {}
            for sql_file in sql_files:
                if not os.path.exists(sql_file):
                    print(f"Warning: SQL file not found: {sql_file}")
                    continue
                records = self.parser.parse_sql_file(sql_file)
                filename = os.path.basename(sql_file)
                records_by_file[filename] = records
                print(f"Parsed {filename}: {len(records)} records")
        elif sql_directory:
            # Process directory
            records_by_file = self.parser.parse_all_sql_files(sql_directory)
        else:
            raise ValueError("Must specify either sql_files or sql_directory")

        # Combine all records
        all_records = []
        for records in records_by_file.values():
            all_records.extend(records)

        if not all_records:
            raise ValueError("No laptop records found in input files")

        print(f"\nTotal records loaded: {len(all_records)}")

        # Map to graph model
        print("\nMapping to graph model...")
        graph_model = self.mapper.map_laptop_records(all_records)

        # Generate normalization summary
        normalization_summary = self.mapper.get_normalization_summary()
        print("\nData normalization summary:")
        print(f"  CPU: {normalization_summary['cpu_normalizations']} variations -> {normalization_summary['unique_cpu_types']} types")
        print(f"  GPU: {normalization_summary['gpu_normalizations']} variations -> {normalization_summary['unique_gpu_types']} types")
        print(f"  RAM: {normalization_summary['ram_normalizations']} variations -> {normalization_summary['unique_ram_types']} types")
        print(f"  Brands: {normalization_summary['unique_brands']} unique brands")

        # Determine output directory
        if not output_directory:
            if sql_directory:
                output_directory = sql_directory
            elif sql_files:
                output_directory = os.path.dirname(sql_files[0]) or "."
            else:
                output_directory = "."

        # Generate CSV files
        print("\nGenerating CSV files...")
        generated_files = self.csv_generator.generate_csv_files(graph_model, output_directory, base_filename)

        # Generate summary report
        summary_report = self.csv_generator.generate_summary_report(graph_model, generated_files)

        print("\n=== Conversion Complete ===")
        print(f"Generated {len(generated_files)} files in {output_directory}")
        print(f"Summary report: {os.path.basename(summary_report)}")

        return {"input_files": list(records_by_file.keys()), "total_records": len(all_records), "graph_model_stats": {"nodes": len(graph_model.nodes), "relationships": len(graph_model.relationships)}, "normalization_summary": normalization_summary, "generated_files": generated_files, "summary_report": summary_report, "output_directory": output_directory}

    def process_individual_sql_files(self, sql_directory: str) -> None:
        """
        Process each SQL file individually to create separate CSV sets.

        Args:
            sql_directory: Directory containing SQL files
        """
        sql_dir = Path(sql_directory)
        laptop_sql_files = list(sql_dir.glob("laptop-data*.sql"))

        if not laptop_sql_files:
            print(f"No laptop-data*.sql files found in {sql_directory}")
            return

        print(f"Processing {len(laptop_sql_files)} SQL files individually...")

        for sql_file in sorted(laptop_sql_files):
            base_name = sql_file.stem  # filename without extension
            print(f"\n--- Processing {sql_file.name} ---")

            try:
                results = self.convert_sql_to_csv(sql_files=[str(sql_file)], output_directory=str(sql_dir), base_filename=base_name)

                print(f"Success: {results['total_records']} records -> {len(results['generated_files'])} files")

            except Exception as e:
                print(f"Error processing {sql_file.name}: {e}")


def main():
    """Command-line interface for Neo4j bulk import."""
    parser = argparse.ArgumentParser(
        description="Convert SQL laptop data to Neo4j CSV format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all SQL files in directory (combined)
  python -m src.github_mingzilla.util__neo4j_data_processing.neo4j_bulk_importer --sql-dir sql

  # Process individual files separately
  python -m src.github_mingzilla.util__neo4j_data_processing.neo4j_bulk_importer --sql-dir sql --individual

  # Process specific files
  python -m src.github_mingzilla.util__neo4j_data_processing.neo4j_bulk_importer --sql-files sql/laptop-data.sql sql/laptop-data-1.sql

  # Custom output settings
  python -m src.github_mingzilla.util__neo4j_data_processing.neo4j_bulk_importer --sql-dir sql --output-dir output --base-name my-laptops
        """,
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--sql-dir", help="Directory containing laptop-data*.sql files")
    input_group.add_argument("--sql-files", nargs="+", help="Specific SQL files to process")

    # Output options
    parser.add_argument("--output-dir", help="Output directory for CSV files (defaults to SQL directory)")
    parser.add_argument("--base-name", default="laptop-data", help="Base filename for output files")

    # Processing options
    parser.add_argument("--individual", action="store_true", help="Process each SQL file individually (only with --sql-dir)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Validate arguments
    if args.individual and not args.sql_dir:
        parser.error("--individual can only be used with --sql-dir")

    try:
        importer = Neo4jBulkImporter()

        if args.individual:
            # Process each file individually
            importer.process_individual_sql_files(args.sql_dir)
        else:
            # Process all files together
            results = importer.convert_sql_to_csv(sql_files=args.sql_files, sql_directory=args.sql_dir, output_directory=args.output_dir, base_filename=args.base_name)

            if args.verbose:
                print("\nDetailed Results:")
                print(f"  Input files: {results['input_files']}")
                print(f"  Total records processed: {results['total_records']}")
                print(f"  Graph nodes created: {results['graph_model_stats']['nodes']}")
                print(f"  Graph relationships created: {results['graph_model_stats']['relationships']}")
                print(f"  Output directory: {results['output_directory']}")

        print("\n✓ Import preparation complete!")
        print("  Next steps:")
        print("  1. Copy CSV files to Neo4j import directory")
        print(f"  2. Run: cypher-shell -f {args.base_name}__neo4j_import.cypher")
        print("  3. Verify with queries in the import script")

    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
