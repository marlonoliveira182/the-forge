#!/usr/bin/env python3
"""
JSON Schema Parser Service
Handles parsing of JSON Schema files and converts them to the same format as XSD parser.
"""

import json
from typing import Dict, List, Any, Optional


class JSONSchemaParser:
    def __init__(self, max_level=8):
        self.max_level = max_level

    def parse_json_schema_file(self, json_schema_path: str) -> List[Dict]:
        """
        Parse a JSON Schema file and return rows in the same format as XSD parser.
        
        Args:
            json_schema_path: Path to the JSON Schema file
            
        Returns:
            List of dictionaries with the same structure as XSD parser output
        """
        try:
            with open(json_schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            return self._parse_schema(schema)
        except Exception as e:
            raise Exception(f"Error parsing JSON Schema file: {str(e)}")

    def parse_json_schema_string(self, json_schema_string: str) -> List[Dict]:
        """
        Parse a JSON Schema string and return rows in the same format as XSD parser.
        
        Args:
            json_schema_string: JSON Schema content as string
            
        Returns:
            List of dictionaries with the same structure as XSD parser output
        """
        try:
            schema = json.loads(json_schema_string)
            return self._parse_schema(schema)
        except Exception as e:
            raise Exception(f"Error parsing JSON Schema string: {str(e)}")

    def _parse_schema(self, schema: Dict) -> List[Dict]:
        """
        Parse a JSON Schema dictionary and convert to XSD-like format.
        
        Args:
            schema: JSON Schema as dictionary
            
        Returns:
            List of dictionaries with the same structure as XSD parser output
        """
        rows = []
        
        # Handle root level properties
        if 'properties' in schema:
            for prop_name, prop_def in schema['properties'].items():
                rows.extend(self._parse_property(prop_name, prop_def, ['']))
        
        # Handle root level definitions
        if 'definitions' in schema:
            for def_name, def_def in schema['definitions'].items():
                rows.extend(self._parse_definition(def_name, def_def, ['']))
        
        return rows

    def _parse_property(self, name: str, prop_def: Dict, parent_path: List[str], 
                       level: int = 1, req_param: str = 'Body', category: str = 'element') -> List[Dict]:
        """
        Parse a JSON Schema property and convert to XSD-like format.
        
        Args:
            name: Property name
            prop_def: Property definition
            parent_path: Parent path for hierarchy
            level: Current nesting level
            req_param: Request parameter name
            category: Element category
            
        Returns:
            List of dictionaries with the same structure as XSD parser output
        """
        rows = []
        
        # Create path for this property
        path = parent_path + [name]
        
        # Get JSON Schema type
        json_type = prop_def.get('type', 'string')
        
        # Convert JSON type to XSD-like type
        xsd_type = self._json_type_to_xsd_type(json_type)
        
        # Get cardinality (JSON Schema doesn't have explicit cardinality, default to 1..1)
        cardinality = '1..1'
        
        # Get base type (same as type for JSON Schema)
        base_type = xsd_type
        
        # Get details (constraints, patterns, etc.)
        details = self._extract_details(prop_def)
        
        # Get description
        description = prop_def.get('description', '')
        
        # Create row in XSD parser format
        row = {
            'levels': path[:self.max_level] + [''] * (self.max_level - len(path)),
            'Request Parameter': req_param,
            'GDPR': '',
            'Cardinality': cardinality,
            'Type': xsd_type,
            'Base Type': base_type,
            'Details': details,
            'Description': description,
            'Category': category,
            'Example': prop_def.get('example', '')
        }
        rows.append(row)
        
        # Handle nested objects
        if json_type == 'object' and 'properties' in prop_def:
            for nested_name, nested_def in prop_def['properties'].items():
                rows.extend(self._parse_property(nested_name, nested_def, path, level + 1, req_param, category))
        
        # Handle arrays
        if json_type == 'array' and 'items' in prop_def:
            items_def = prop_def['items']
            if isinstance(items_def, dict):
                # Array of objects
                if items_def.get('type') == 'object' and 'properties' in items_def:
                    for nested_name, nested_def in items_def['properties'].items():
                        rows.extend(self._parse_property(nested_name, nested_def, path, level + 1, req_param, category))
                else:
                    # Array of primitives
                    array_type = items_def.get('type', 'string')
                    xsd_array_type = self._json_type_to_xsd_type(array_type)
                    array_row = {
                        'levels': path[:self.max_level] + [''] * (self.max_level - len(path)),
                        'Request Parameter': req_param,
                        'GDPR': '',
                        'Cardinality': '0..n',  # Arrays are typically 0..n
                        'Type': f'array<{xsd_array_type}>',
                        'Base Type': xsd_array_type,
                        'Details': self._extract_details(items_def),
                        'Description': f'Array of {array_type}',
                        'Category': 'element',
                        'Example': items_def.get('example', '')
                    }
                    rows.append(array_row)
        
        return rows

    def _parse_definition(self, name: str, def_def: Dict, parent_path: List[str]) -> List[Dict]:
        """
        Parse a JSON Schema definition and convert to XSD-like format.
        
        Args:
            name: Definition name
            def_def: Definition definition
            parent_path: Parent path for hierarchy
            
        Returns:
            List of dictionaries with the same structure as XSD parser output
        """
        rows = []
        
        # Create path for this definition
        path = parent_path + [name]
        
        # Get JSON Schema type
        json_type = def_def.get('type', 'string')
        
        # Convert JSON type to XSD-like type
        xsd_type = self._json_type_to_xsd_type(json_type)
        
        # Get cardinality
        cardinality = '1..1'
        
        # Get base type
        base_type = xsd_type
        
        # Get details
        details = self._extract_details(def_def)
        
        # Get description
        description = def_def.get('description', '')
        
        # Create row in XSD parser format
        row = {
            'levels': path[:self.max_level] + [''] * (self.max_level - len(path)),
            'Request Parameter': 'Body',
            'GDPR': '',
            'Cardinality': cardinality,
            'Type': xsd_type,
            'Base Type': base_type,
            'Details': details,
            'Description': description,
            'Category': 'element',
            'Example': def_def.get('example', '')
        }
        rows.append(row)
        
        # Handle nested objects
        if json_type == 'object' and 'properties' in def_def:
            for nested_name, nested_def in def_def['properties'].items():
                rows.extend(self._parse_property(nested_name, nested_def, path, 2, 'Body', 'element'))
        
        return rows

    def _json_type_to_xsd_type(self, json_type: str) -> str:
        """
        Convert JSON Schema type to XSD-like type.
        
        Args:
            json_type: JSON Schema type
            
        Returns:
            XSD-like type string
        """
        type_mapping = {
            'string': 'xs:string',
            'integer': 'xs:integer',
            'number': 'xs:double',
            'boolean': 'xs:boolean',
            'array': 'xs:string',  # Default for arrays
            'object': 'xs:string'   # Default for objects
        }
        
        return type_mapping.get(json_type, 'xs:string')

    def _extract_details(self, prop_def: Dict) -> str:
        """
        Extract constraints and details from JSON Schema property definition.
        
        Args:
            prop_def: Property definition
            
        Returns:
            Comma-separated string of constraints
        """
        details = []
        
        # Length constraints
        if 'minLength' in prop_def:
            details.append(f"minLength={prop_def['minLength']}")
        if 'maxLength' in prop_def:
            details.append(f"maxLength={prop_def['maxLength']}")
        
        # Numeric constraints
        if 'minimum' in prop_def:
            details.append(f"minimum={prop_def['minimum']}")
        if 'maximum' in prop_def:
            details.append(f"maximum={prop_def['maximum']}")
        
        # Pattern constraint
        if 'pattern' in prop_def:
            details.append(f"pattern={prop_def['pattern']}")
        
        # Enum constraint
        if 'enum' in prop_def:
            enum_values = ','.join(str(v) for v in prop_def['enum'])
            details.append(f"enum={enum_values}")
        
        # Format constraint
        if 'format' in prop_def:
            details.append(f"format={prop_def['format']}")
        
        return ', '.join(details) 