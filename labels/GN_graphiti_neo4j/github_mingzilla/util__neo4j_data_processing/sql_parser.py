"""
SQL Parser for Laptop Data

Parses SQL INSERT statements and extracts structured laptop data for Neo4j conversion.
Handles the laptop table schema with columns: name, brand, cpu, video_card, screen_size, ram, hard_drive, price, description.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class LaptopRecord:
    """Represents a single laptop record parsed from SQL INSERT statement."""

    name: str
    brand: str
    cpu: str
    video_card: str
    screen_size: int
    ram: str
    hard_drive: str
    price: float
    description: str
    source_file: str
    source_line: int


class SQLParser:
    """
    Parses SQL INSERT statements for laptop data.

    Handles the schema:
    INSERT INTO laptops (name, brand, cpu, video_card, screen_size, ram, hard_drive, price, description) VALUES (...)
    """

    def __init__(self):
        self.laptop_records: List[LaptopRecord] = []

    def parse_sql_file(self, file_path: str) -> List[LaptopRecord]:
        """
        Parse a single SQL file and extract laptop records.

        Args:
            file_path: Path to SQL file to parse

        Returns:
            List of LaptopRecord objects
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"SQL file not found: {file_path}")

        records = []

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Find all INSERT statements for laptops table
        insert_pattern = r"INSERT INTO laptops \([^)]+\) VALUES\s*([^;]+);"

        for match in re.finditer(insert_pattern, content, re.IGNORECASE | re.DOTALL):
            values_section = match.group(1)

            # Parse individual value tuples
            value_records = self._parse_values_section(values_section, file_path.name)
            records.extend(value_records)

        return records

    def _parse_values_section(self, values_section: str, source_file: str) -> List[LaptopRecord]:
        """
        Parse the VALUES section of an INSERT statement.

        Args:
            values_section: The VALUES (...), (...), ... section
            source_file: Name of source file for tracking

        Returns:
            List of LaptopRecord objects
        """
        records = []

        # Split by tuple boundaries, handling nested quotes and commas
        tuple_pattern = r"\(([^)]+(?:\([^)]*\))?[^)]*)\)"

        line_number = 1
        for match in re.finditer(tuple_pattern, values_section):
            tuple_content = match.group(1)

            try:
                record = self._parse_single_tuple(tuple_content, source_file, line_number)
                if record:
                    records.append(record)
                    line_number += 1
            except Exception as e:
                print(f"Warning: Failed to parse tuple in {source_file} line {line_number}: {e}")
                line_number += 1
                continue

        return records

    def _parse_single_tuple(self, tuple_content: str, source_file: str, line_number: int) -> Optional[LaptopRecord]:
        """
        Parse a single VALUES tuple into a LaptopRecord.

        Args:
            tuple_content: Content between parentheses
            source_file: Source file name
            line_number: Line number for tracking

        Returns:
            LaptopRecord or None if parsing fails
        """
        # Split by commas, respecting quoted strings
        values = self._split_csv_respecting_quotes(tuple_content)

        if len(values) != 9:
            raise ValueError(f"Expected 9 values, got {len(values)}: {values}")

        # Clean and parse each value
        try:
            name = self._clean_string_value(values[0])
            brand = self._clean_string_value(values[1])
            cpu = self._clean_string_value(values[2])
            video_card = self._clean_string_value(values[3])
            screen_size = int(self._clean_numeric_value(values[4]))
            ram = self._clean_string_value(values[5])
            hard_drive = self._clean_string_value(values[6])
            price = float(self._clean_numeric_value(values[7]))
            description = self._clean_string_value(values[8])

            return LaptopRecord(name=name, brand=brand, cpu=cpu, video_card=video_card, screen_size=screen_size, ram=ram, hard_drive=hard_drive, price=price, description=description, source_file=source_file, source_line=line_number)

        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to parse values: {e}")

    def _split_csv_respecting_quotes(self, text: str) -> List[str]:
        """
        Split CSV text by commas while respecting quoted strings.

        Args:
            text: CSV text to split

        Returns:
            List of field values
        """
        values = []
        current_value = ""
        in_quotes = False
        escape_next = False

        i = 0
        while i < len(text):
            char = text[i]

            if escape_next:
                current_value += char
                escape_next = False
            elif char == "\\":
                current_value += char
                escape_next = True
            elif char == "'" and not escape_next:
                in_quotes = not in_quotes
                current_value += char
            elif char == "," and not in_quotes:
                values.append(current_value.strip())
                current_value = ""
            else:
                current_value += char

            i += 1

        # Add the last value
        if current_value.strip():
            values.append(current_value.strip())

        return values

    def _clean_string_value(self, value: str) -> str:
        """
        Clean a string value by removing quotes and handling escapes.

        Args:
            value: Raw string value from SQL

        Returns:
            Cleaned string value
        """
        value = value.strip()

        # Remove surrounding quotes
        if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]

        # Handle escaped quotes
        value = value.replace("\\'", "'").replace('\\"', '"')

        return value

    def _clean_numeric_value(self, value: str) -> str:
        """
        Clean a numeric value by removing quotes and whitespace.

        Args:
            value: Raw numeric value from SQL

        Returns:
            Cleaned numeric string
        """
        value = value.strip()

        # Remove quotes if present
        if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]

        return value.strip()

    def parse_all_sql_files(self, sql_directory: str) -> Dict[str, List[LaptopRecord]]:
        """
        Parse all laptop SQL files in a directory.

        Args:
            sql_directory: Path to directory containing SQL files

        Returns:
            Dictionary mapping filename to list of LaptopRecord objects
        """
        sql_dir = Path(sql_directory)
        if not sql_dir.exists():
            raise FileNotFoundError(f"SQL directory not found: {sql_dir}")

        results = {}

        # Find all laptop-data*.sql files
        laptop_sql_files = list(sql_dir.glob("laptop-data*.sql"))

        if not laptop_sql_files:
            print(f"Warning: No laptop-data*.sql files found in {sql_dir}")

        for sql_file in sorted(laptop_sql_files):
            print(f"Parsing {sql_file.name}...")
            try:
                records = self.parse_sql_file(str(sql_file))
                results[sql_file.name] = records
                print(f"  -> Parsed {len(records)} records")
            except Exception as e:
                print(f"  -> Error parsing {sql_file.name}: {e}")
                results[sql_file.name] = []

        return results

    def get_parsing_summary(self, results: Dict[str, List[LaptopRecord]]) -> Dict[str, Any]:
        """
        Generate a summary of parsing results.

        Args:
            results: Results from parse_all_sql_files

        Returns:
            Summary dictionary with statistics
        """
        total_records = sum(len(records) for records in results.values())

        # Collect unique brands, CPUs, GPUs for analysis
        all_brands = set()
        all_cpus = set()
        all_gpus = set()

        for records in results.values():
            for record in records:
                all_brands.add(record.brand)
                all_cpus.add(record.cpu)
                all_gpus.add(record.video_card)

        return {"total_files": len(results), "total_records": total_records, "files_summary": {filename: len(records) for filename, records in results.items()}, "unique_brands": sorted(all_brands), "unique_cpus": sorted(all_cpus), "unique_gpus": sorted(all_gpus), "data_quality": {"brand_count": len(all_brands), "cpu_variations": len(all_cpus), "gpu_variations": len(all_gpus)}}


def main():
    """Test the SQL parser with the laptop data files."""
    parser = SQLParser()

    # Parse all SQL files in the sql directory
    sql_directory = "sql"
    try:
        results = parser.parse_all_sql_files(sql_directory)
        summary = parser.get_parsing_summary(results)

        print("\n=== SQL Parsing Summary ===")
        print(f"Total files parsed: {summary['total_files']}")
        print(f"Total records extracted: {summary['total_records']}")

        print("\nFiles breakdown:")
        for filename, count in summary["files_summary"].items():
            print(f"  {filename}: {count} records")

        print("\nData quality analysis:")
        print(f"  Unique brands: {summary['data_quality']['brand_count']}")
        print(f"  CPU variations: {summary['data_quality']['cpu_variations']}")
        print(f"  GPU variations: {summary['data_quality']['gpu_variations']}")

        # Show some examples of data variations
        print(f"\nBrand examples: {summary['unique_brands'][:10]}")
        print(f"CPU examples: {summary['unique_cpus'][:10]}")
        print(f"GPU examples: {summary['unique_gpus'][:10]}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
