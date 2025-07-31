import json
import openpyxl

class JSONSchemaParser:
    def __init__(self, max_level=8):
        self.max_level = max_level

    def flatten_schema(self, schema, parent_key='', sep='.'):
        """Recursively flatten a dict (JSON Schema or XSD structure) into dot notation paths"""
        items = []
        if isinstance(schema, dict):
            for k, v in schema.items():
                new_key = f'{parent_key}{sep}{k}' if parent_key else k
                if isinstance(v, dict):
                    items.extend(self.flatten_schema(v, new_key, sep=sep))
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        items.extend(self.flatten_schema(item, f'{new_key}[{i}]', sep=sep))
                else:
                    items.append(new_key)
        return items

    def parse_json_schema_file(self, file_path):
        """Parse JSON Schema file and return flat structure"""
        with open(file_path, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
        
        paths = self.flatten_schema(schema_data)
        rows = []
        
        for path in paths:
            # Split path into levels
            path_parts = path.split('.')
            levels = path_parts[:self.max_level] + [''] * (self.max_level - len(path_parts))
            
            row = {
                'levels': levels,
                'Request Parameter': 'Body',
                'GDPR': '',
                'Cardinality': '0..1',  # Default for JSON Schema
                'Type': 'string',  # Default type
                'Base Type': 'string',
                'Details': '',
                'Description': '',
                'Category': 'property',
                'Example': ''
            }
            rows.append(row)
        
        return rows

    def parse_json_schema_string(self, schema_string):
        """Parse JSON Schema string and return flat structure"""
        schema_data = json.loads(schema_string)
        
        paths = self.flatten_schema(schema_data)
        rows = []
        
        for path in paths:
            # Split path into levels
            path_parts = path.split('.')
            levels = path_parts[:self.max_level] + [''] * (self.max_level - len(path_parts))
            
            row = {
                'levels': levels,
                'Request Parameter': 'Body',
                'GDPR': '',
                'Cardinality': '0..1',  # Default for JSON Schema
                'Type': 'string',  # Default type
                'Base Type': 'string',
                'Details': '',
                'Description': '',
                'Category': 'property',
                'Example': ''
            }
            rows.append(row)
        
        return rows 