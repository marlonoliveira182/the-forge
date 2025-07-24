from .xsd_parser import XsdSchemaParser
from .json_parser import JsonSchemaParser
from .schema_field import SchemaField
from typing import List

def load_schema(file_path: str) -> List[SchemaField]:
    if file_path.lower().endswith('.xsd'):
        return XsdSchemaParser().parse(file_path)
    elif file_path.lower().endswith('.json'):
        return JsonSchemaParser().parse(file_path)
    else:
        raise ValueError(f"Unsupported schema file type: {file_path}") 