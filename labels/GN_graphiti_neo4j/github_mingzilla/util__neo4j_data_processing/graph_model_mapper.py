"""
Graph Model Mapper for Laptop Data

Maps laptop data to 4-level Neo4j graph abstraction (D_, E_, A_, V_) following established conventions.
Handles data normalization and relationship creation according to the abstraction guide.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Set

from github_mingzilla.util__neo4j_data_processing.sql_parser import LaptopRecord


@dataclass
class GraphNode:
    """Represents a Neo4j node with label, properties, and unique ID."""

    id: str
    label: str
    properties: Dict[str, Any]

    def __post_init__(self):
        # Ensure all nodes have creation timestamp
        if "createdAt" not in self.properties:
            self.properties["createdAt"] = datetime.now().isoformat()


@dataclass
class GraphRelationship:
    """Represents a Neo4j relationship between two nodes."""

    from_node_id: str
    to_node_id: str
    relationship_type: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphModel:
    """Complete graph model with all nodes and relationships."""

    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    relationships: List[GraphRelationship] = field(default_factory=list)

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph model."""
        self.nodes[node.id] = node

    def add_relationship(self, relationship: GraphRelationship) -> None:
        """Add a relationship to the graph model."""
        self.relationships.append(relationship)


class GraphModelMapper:
    """
    Maps laptop records to 4-level Neo4j graph model following established patterns:

    D_ (Document): Raw SQL data
    E_ (Entity): Core laptop objects
    A_ (Attribute): Normalized specifications (CPU, GPU, RAM)
    V_ (Value): Fixed enumerated values (Brand, Color)
    """

    def __init__(self):
        self.graph_model = GraphModel()

        # Track normalization mappings for consistency
        self._cpu_normalizations: Dict[str, str] = {}
        self._gpu_normalizations: Dict[str, str] = {}
        self._ram_normalizations: Dict[str, str] = {}
        self._brand_normalizations: Dict[str, str] = {}

        # Track created nodes to avoid duplicates
        self._created_attribute_nodes: Set[str] = set()
        self._created_value_nodes: Set[str] = set()

    def map_laptop_records(self, records: List[LaptopRecord]) -> GraphModel:
        """
        Map a list of laptop records to the 4-level graph model.

        Args:
            records: List of parsed laptop records

        Returns:
            GraphModel with nodes and relationships
        """
        print(f"Mapping {len(records)} laptop records to graph model...")

        for record in records:
            self._process_single_laptop(record)

        print("Created graph model:")
        print(f"  Total nodes: {len(self.graph_model.nodes)}")
        print(f"  Total relationships: {len(self.graph_model.relationships)}")

        # Print breakdown by node type
        node_counts = {}
        for node in self.graph_model.nodes.values():
            label = node.label
            node_counts[label] = node_counts.get(label, 0) + 1

        for label, count in sorted(node_counts.items()):
            print(f"    {label}: {count}")

        return self.graph_model

    def _process_single_laptop(self, record: LaptopRecord) -> None:
        """
        Process a single laptop record into the 4-level graph model.

        Args:
            record: Laptop record to process
        """
        # Generate unique IDs
        laptop_id = f"laptop_{self._generate_safe_id(record.name)}"
        document_id = f"doc_{laptop_id}"

        # 1. Create D_LaptopSpec (Document level - raw SQL data)
        document_node = GraphNode(
            id=document_id,
            label="D_LaptopSpec",
            properties={
                "contentRaw": self._serialize_record_as_text(record),
                "sourceFile": record.source_file,
                "sourceLine": record.source_line,
                "originalName": record.name,
                "originalBrand": record.brand,
                "originalCpu": record.cpu,
                "originalVideoCard": record.video_card,
                "originalRam": record.ram,
                "originalHardDrive": record.hard_drive,
            },
        )
        self.graph_model.add_node(document_node)

        # 2. Create E_Laptop (Entity level - core laptop object)
        laptop_node = GraphNode(
            id=laptop_id,
            label="E_Laptop",
            properties={
                "name": record.name,
                "screenSize": record.screen_size,
                "price": record.price,
                "description": record.description,
                # Keep some normalized properties for quick access
                "cpuNormalized": self._normalize_cpu(record.cpu),
                "gpuNormalized": self._normalize_gpu(record.video_card),
                "ramNormalized": self._normalize_ram(record.ram),
                "brandNormalized": self._normalize_brand(record.brand),
            },
        )
        self.graph_model.add_node(laptop_node)

        # 3. Create A_ Attribute nodes (normalized specifications)
        cpu_node_id = self._create_cpu_attribute_node(record.cpu)
        gpu_node_id = self._create_gpu_attribute_node(record.video_card)
        ram_node_id = self._create_ram_attribute_node(record.ram)

        # 4. Create V_ Value nodes (fixed enumerated values)
        brand_node_id = self._create_brand_value_node(record.brand)

        # 5. Create relationships following naming convention
        # Document relationship
        self.graph_model.add_relationship(GraphRelationship(from_node_id=laptop_id, to_node_id=document_id, relationship_type="CONTAINS_D"))

        # Attribute relationships
        self.graph_model.add_relationship(GraphRelationship(from_node_id=laptop_id, to_node_id=cpu_node_id, relationship_type="HAS_A_CPU"))

        self.graph_model.add_relationship(GraphRelationship(from_node_id=laptop_id, to_node_id=gpu_node_id, relationship_type="HAS_A_GPU"))

        self.graph_model.add_relationship(GraphRelationship(from_node_id=laptop_id, to_node_id=ram_node_id, relationship_type="HAS_A_RAM"))

        # Value relationships
        self.graph_model.add_relationship(GraphRelationship(from_node_id=laptop_id, to_node_id=brand_node_id, relationship_type="HAS_V_BRAND"))

    def _serialize_record_as_text(self, record: LaptopRecord) -> str:
        """Serialize laptop record as raw text for document storage."""
        return f"INSERT INTO laptops VALUES ('{record.name}', '{record.brand}', '{record.cpu}', '{record.video_card}', {record.screen_size}, '{record.ram}', '{record.hard_drive}', {record.price}, '{record.description}');"

    def _generate_safe_id(self, text: str) -> str:
        """Generate a safe ID from text for Neo4j."""
        # Remove special characters and spaces, convert to lowercase
        safe_id = re.sub(r"[^a-zA-Z0-9_]", "_", text.lower())
        # Remove multiple underscores and leading/trailing underscores
        safe_id = re.sub(r"_+", "_", safe_id)
        safe_id = safe_id.strip("_")
        # Ensure it's not too long
        if len(safe_id) > 50:
            safe_id = safe_id[:47] + str(hash(text) % 1000)
        return safe_id

    def _normalize_cpu(self, cpu_raw: str) -> str:
        """Normalize CPU string to standard format."""
        if cpu_raw in self._cpu_normalizations:
            return self._cpu_normalizations[cpu_raw]

        # Clean up common variations
        cpu_clean = cpu_raw.upper().strip()

        # Handle Intel Core variations
        cpu_clean = re.sub(r"INTEL\s+(CORE\s+)?", "", cpu_clean)

        # Normalize i3, i5, i7, i9 variations
        if re.search(r"I\s*3", cpu_clean):
            normalized = "i3"
        elif re.search(r"I\s*5", cpu_clean):
            normalized = "i5"
        elif re.search(r"I\s*7", cpu_clean):
            normalized = "i7"
        elif re.search(r"I\s*9", cpu_clean):
            normalized = "i9"
        else:
            # Keep original if no standard pattern found
            normalized = cpu_raw.strip()

        self._cpu_normalizations[cpu_raw] = normalized
        return normalized

    def _normalize_gpu(self, gpu_raw: str) -> str:
        """Normalize GPU string to standard format."""
        if gpu_raw in self._gpu_normalizations:
            return self._gpu_normalizations[gpu_raw]

        gpu_clean = gpu_raw.upper().strip()

        # Remove brand prefixes
        gpu_clean = re.sub(r"(NVIDIA|GEFORCE|RTX)\s*", "", gpu_clean)

        # Normalize series patterns
        if re.search(r"20\s*XX", gpu_clean):
            normalized = "20xx"
        elif re.search(r"30\s*XX", gpu_clean):
            normalized = "30xx"
        elif re.search(r"40\s*XX", gpu_clean):
            normalized = "40xx"
        elif re.search(r"50\s*XX", gpu_clean):
            normalized = "50xx"
        else:
            normalized = gpu_raw.strip()

        self._gpu_normalizations[gpu_raw] = normalized
        return normalized

    def _normalize_ram(self, ram_raw: str) -> str:
        """Normalize RAM string to standard format."""
        if ram_raw in self._ram_normalizations:
            return self._ram_normalizations[ram_raw]

        ram_clean = ram_raw.upper().strip()

        # Extract numeric value
        numbers = re.findall(r"(\d+)", ram_clean)
        if numbers:
            ram_gb = numbers[0]
            normalized = f"{ram_gb}GB"
        else:
            normalized = ram_raw.strip()

        self._ram_normalizations[ram_raw] = normalized
        return normalized

    def _normalize_brand(self, brand_raw: str) -> str:
        """Normalize brand string to standard format."""
        if brand_raw in self._brand_normalizations:
            return self._brand_normalizations[brand_raw]

        # Brand normalization is simpler - just clean whitespace
        normalized = brand_raw.strip()
        self._brand_normalizations[brand_raw] = normalized
        return normalized

    def _create_cpu_attribute_node(self, cpu_raw: str) -> str:
        """Create or reuse A_CPUType attribute node."""
        normalized = self._normalize_cpu(cpu_raw)
        node_id = f"cpu_type_{self._generate_safe_id(normalized)}"

        if node_id not in self._created_attribute_nodes:
            # Collect all variations for this normalized CPU
            variations = [raw for raw, norm in self._cpu_normalizations.items() if norm == normalized]
            if cpu_raw not in variations:
                variations.append(cpu_raw)

            cpu_node = GraphNode(id=node_id, label="A_CPUType", properties={"normalized": normalized, "variations": variations, "originalRaw": cpu_raw})
            self.graph_model.add_node(cpu_node)
            self._created_attribute_nodes.add(node_id)
        else:
            # Update variations list for existing node
            existing_node = self.graph_model.nodes[node_id]
            variations = existing_node.properties.get("variations", [])
            if cpu_raw not in variations:
                variations.append(cpu_raw)
                existing_node.properties["variations"] = variations

        return node_id

    def _create_gpu_attribute_node(self, gpu_raw: str) -> str:
        """Create or reuse A_GPUType attribute node."""
        normalized = self._normalize_gpu(gpu_raw)
        node_id = f"gpu_type_{self._generate_safe_id(normalized)}"

        if node_id not in self._created_attribute_nodes:
            variations = [raw for raw, norm in self._gpu_normalizations.items() if norm == normalized]
            if gpu_raw not in variations:
                variations.append(gpu_raw)

            gpu_node = GraphNode(id=node_id, label="A_GPUType", properties={"normalized": normalized, "variations": variations, "originalRaw": gpu_raw})
            self.graph_model.add_node(gpu_node)
            self._created_attribute_nodes.add(node_id)
        else:
            existing_node = self.graph_model.nodes[node_id]
            variations = existing_node.properties.get("variations", [])
            if gpu_raw not in variations:
                variations.append(gpu_raw)
                existing_node.properties["variations"] = variations

        return node_id

    def _create_ram_attribute_node(self, ram_raw: str) -> str:
        """Create or reuse A_RAMType attribute node."""
        normalized = self._normalize_ram(ram_raw)
        node_id = f"ram_type_{self._generate_safe_id(normalized)}"

        if node_id not in self._created_attribute_nodes:
            variations = [raw for raw, norm in self._ram_normalizations.items() if norm == normalized]
            if ram_raw not in variations:
                variations.append(ram_raw)

            ram_node = GraphNode(id=node_id, label="A_RAMType", properties={"normalized": normalized, "variations": variations, "originalRaw": ram_raw, "capacityGB": int(re.findall(r"(\d+)", normalized)[0]) if re.findall(r"(\d+)", normalized) else 0})
            self.graph_model.add_node(ram_node)
            self._created_attribute_nodes.add(node_id)
        else:
            existing_node = self.graph_model.nodes[node_id]
            variations = existing_node.properties.get("variations", [])
            if ram_raw not in variations:
                variations.append(ram_raw)
                existing_node.properties["variations"] = variations

        return node_id

    def _create_brand_value_node(self, brand_raw: str) -> str:
        """Create or reuse V_Brand value node."""
        normalized = self._normalize_brand(brand_raw)
        node_id = f"brand_{self._generate_safe_id(normalized)}"

        if node_id not in self._created_value_nodes:
            brand_node = GraphNode(id=node_id, label="V_Brand", properties={"name": normalized, "originalRaw": brand_raw})
            self.graph_model.add_node(brand_node)
            self._created_value_nodes.add(node_id)

        return node_id

    def get_normalization_summary(self) -> Dict[str, Any]:
        """Get summary of data normalization performed."""
        return {"cpu_normalizations": len(self._cpu_normalizations), "gpu_normalizations": len(self._gpu_normalizations), "ram_normalizations": len(self._ram_normalizations), "brand_normalizations": len(self._brand_normalizations), "unique_cpu_types": len(set(self._cpu_normalizations.values())), "unique_gpu_types": len(set(self._gpu_normalizations.values())), "unique_ram_types": len(set(self._ram_normalizations.values())), "unique_brands": len(set(self._brand_normalizations.values())), "cpu_mapping_examples": dict(list(self._cpu_normalizations.items())[:5]), "gpu_mapping_examples": dict(list(self._gpu_normalizations.items())[:5])}


def main():
    """Test the graph model mapper with parsed laptop data."""
    from github_mingzilla.util__neo4j_data_processing.sql_parser import SQLParser

    # Parse SQL data first
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
        mapper.map_laptop_records(all_records)

        # Print normalization summary
        print("\n=== Data Normalization Summary ===")
        summary = mapper.get_normalization_summary()

        print(f"CPU normalizations: {summary['cpu_normalizations']} -> {summary['unique_cpu_types']} unique")
        print(f"GPU normalizations: {summary['gpu_normalizations']} -> {summary['unique_gpu_types']} unique")
        print(f"RAM normalizations: {summary['ram_normalizations']} -> {summary['unique_ram_types']} unique")
        print(f"Brand normalizations: {summary['brand_normalizations']} -> {summary['unique_brands']} unique")

        print("\nCPU mapping examples:")
        for raw, normalized in summary["cpu_mapping_examples"].items():
            print(f"  '{raw}' -> '{normalized}'")

        print("\nGPU mapping examples:")
        for raw, normalized in summary["gpu_mapping_examples"].items():
            print(f"  '{raw}' -> '{normalized}'")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
