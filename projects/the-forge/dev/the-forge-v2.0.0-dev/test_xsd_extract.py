import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.schema_processor import SchemaProcessor

if len(sys.argv) < 2:
    print("Usage: python test_xsd_extract.py <path-to-xsd>")
    sys.exit(1)

xsd_path = sys.argv[1]
fields = SchemaProcessor().extract_fields_from_xsd(xsd_path)
print(f"Extracted {len(fields)} fields from {xsd_path}")
for f in fields:
    print(f"{f.path} | {f.type} | {f.cardinality} | {f.required} | {f.constraints} | {f.description}") 