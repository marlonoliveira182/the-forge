from .schema_parser import SchemaParser
from .schema_field import SchemaField
from typing import List, Dict, Any
import json
import jsonschema

class JsonSchemaParser(SchemaParser):
    def parse(self, file_path: str) -> List[SchemaField]:
        with open(file_path, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
        jsonschema.Draft7Validator.check_schema(schema_data)
        fields = []
        def walk(properties: dict, parent_path: str = "", level: int = 0, schema: dict = None):
            if parent_path is None:
                parent_path = ""
            if schema is None:
                schema = {}
            for prop_name, prop_data in properties.items():
                field_path = f"{parent_path}.{prop_name}" if parent_path else prop_name
                field_type = prop_data.get('type', 'object' if 'properties' in prop_data else 'string')
                cardinality = '1'
                required = prop_name in schema.get('required', [])
                is_array = field_type == 'array'
                is_complex = field_type in ['object', 'array'] or 'properties' in prop_data
                constraints = {}
                if 'pattern' in prop_data:
                    constraints['pattern'] = prop_data['pattern']
                if 'minLength' in prop_data:
                    constraints['minLength'] = prop_data['minLength']
                if 'maxLength' in prop_data:
                    constraints['maxLength'] = prop_data['maxLength']
                if 'minimum' in prop_data:
                    constraints['minimum'] = prop_data['minimum']
                if 'maximum' in prop_data:
                    constraints['maximum'] = prop_data['maximum']
                if 'enum' in prop_data:
                    constraints['enumeration'] = prop_data['enum']
                if 'format' in prop_data:
                    constraints['format'] = prop_data['format']
                description = prop_data.get('description', '')
                metadata = {}
                if 'title' in prop_data:
                    metadata['title'] = prop_data['title']
                if 'examples' in prop_data:
                    metadata['examples'] = prop_data['examples']
                if 'default' in prop_data:
                    metadata['default'] = prop_data['default']
                if 'additionalProperties' in prop_data:
                    metadata['additionalProperties'] = prop_data['additionalProperties']
                levels = field_path.split('.')
                field = SchemaField(
                    name=prop_name,
                    path=field_path,
                    level=level,
                    type=field_type,
                    cardinality=cardinality,
                    restrictions=constraints,
                    description=description,
                    parent_path=parent_path,
                    is_array=is_array,
                    is_complex=is_complex,
                    required=required,
                    metadata=metadata,
                    levels=levels
                )
                fields.append(field)
                if is_complex and 'properties' in prop_data:
                    walk(prop_data['properties'], field_path, level+1, dict(prop_data))
                if is_array and 'items' in prop_data and isinstance(prop_data['items'], dict) and 'properties' in prop_data['items']:
                    walk(prop_data['items']['properties'], field_path, level+1, dict(prop_data['items']))
        if 'properties' in schema_data:
            walk(schema_data['properties'], "", 0, schema_data)
        return fields 