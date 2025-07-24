from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class SchemaField:
    """
    Represents a field in a schema (XSD or JSON Schema) in a normalized, intermediate format.
    """
    name: str
    path: str
    level: int = 0
    type: str = "string"
    cardinality: str = "1"
    restrictions: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    parent_path: str = ""
    is_array: bool = False
    is_complex: bool = False
    required: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    # For Excel export: hierarchical columns (Level1-Level6)
    levels: List[str] = field(default_factory=list) 