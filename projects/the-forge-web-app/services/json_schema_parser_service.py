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
        self.schema_cache = {}  # Cache for resolved references

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
        
        # Clear cache for new schema
        self.schema_cache = {}
        
        # Handle root level properties
        if 'properties' in schema:
            for prop_name, prop_def in schema['properties'].items():
                rows.extend(self._parse_property(prop_name, prop_def, [''], schema))
        
        return rows

    def _parse_property(self, name: str, prop_def: Dict, parent_path: List[str], 
                       root_schema: Dict, level: int = 1, req_param: str = 'Body', 
                       category: str = 'element') -> List[Dict]:
        """
        Parse a JSON Schema property and convert to XSD-like format.
        
        Args:
            name: Property name
            prop_def: Property definition
            parent_path: Parent path for hierarchy
            root_schema: Root schema for reference resolution
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
        
        # Handle arrays - ONLY arrays should be processed here
        if json_type == 'array':
            rows.extend(self._parse_array_property(name, prop_def, path, root_schema, level, req_param, category))
        else:
            # Handle non-array properties
            rows.extend(self._parse_simple_property(name, prop_def, path, root_schema, level, req_param, category))
        
        return rows

    def _parse_array_property(self, name: str, prop_def: Dict, path: List[str], 
                             root_schema: Dict, level: int, req_param: str, category: str) -> List[Dict]:
        """
        Parse an array property specifically.
        """
        rows = []
        items_def = prop_def.get('items', {})
        
        # Determine array item type
        if isinstance(items_def, dict):
            if '$ref' in items_def:
                # Array of referenced objects
                ref_path = items_def['$ref']
                resolved_def = self._resolve_reference(ref_path, root_schema)
                if resolved_def:
                    # Create array entry
                    array_row = {
                        'levels': path[:self.max_level] + [''] * (self.max_level - len(path)),
                        'Request Parameter': req_param,
                        'GDPR': '',
                        'Cardinality': '0..n',
                        'Type': f'array<object>',
                        'Base Type': 'object',
                        'Details': '',
                        'Description': f'Array of {ref_path.split("/")[-1]} objects',
                        'Category': category,
                        'Example': ''
                    }
                    rows.append(array_row)
                    
                    # Parse the referenced object properties
                    if resolved_def.get('type') == 'object' and 'properties' in resolved_def:
                        for nested_name, nested_def in resolved_def['properties'].items():
                            rows.extend(self._parse_property(nested_name, nested_def, path, root_schema, level + 1, req_param, category))
            else:
                # Array of primitives or inline objects
                item_type = items_def.get('type', 'string')
                if item_type == 'object' and 'properties' in items_def:
                    # Array of inline objects
                    array_row = {
                        'levels': path[:self.max_level] + [''] * (self.max_level - len(path)),
                        'Request Parameter': req_param,
                        'GDPR': '',
                        'Cardinality': '0..n',
                        'Type': f'array<object>',
                        'Base Type': 'object',
                        'Details': '',
                        'Description': f'Array of objects',
                        'Category': category,
                        'Example': ''
                    }
                    rows.append(array_row)
                    
                    # Parse the inline object properties
                    for nested_name, nested_def in items_def['properties'].items():
                        rows.extend(self._parse_property(nested_name, nested_def, path, root_schema, level + 1, req_param, category))
                else:
                    # Array of primitives
                    xsd_type = self._json_type_to_xsd_type(item_type)
                    array_row = {
                        'levels': path[:self.max_level] + [''] * (self.max_level - len(path)),
                        'Request Parameter': req_param,
                        'GDPR': '',
                        'Cardinality': '0..n',
                        'Type': f'array<{xsd_type}>',
                        'Base Type': xsd_type,
                        'Details': self._extract_details(items_def),
                        'Description': f'Array of {item_type}',
                        'Category': category,
                        'Example': items_def.get('example', '')
                    }
                    rows.append(array_row)
        
        return rows

    def _parse_simple_property(self, name: str, prop_def: Dict, path: List[str], 
                              root_schema: Dict, level: int, req_param: str, category: str) -> List[Dict]:
        """
        Parse a non-array property.
        """
        rows = []
        
        # Handle $ref references
        if '$ref' in prop_def:
            ref_path = prop_def['$ref']
            resolved_def = self._resolve_reference(ref_path, root_schema)
            if resolved_def:
                # Create reference entry
                ref_name = ref_path.split("/")[-1]
                ref_row = {
                    'levels': path[:self.max_level] + [''] * (self.max_level - len(path)),
                    'Request Parameter': req_param,
                    'GDPR': '',
                    'Cardinality': '1..1',
                    'Type': 'object',
                    'Base Type': 'object',
                    'Details': '',
                    'Description': f'Reference to {ref_name}',
                    'Category': category,
                    'Example': ''
                }
                rows.append(ref_row)
                
                # Parse the referenced object properties
                if resolved_def.get('type') == 'object' and 'properties' in resolved_def:
                    for nested_name, nested_def in resolved_def['properties'].items():
                        rows.extend(self._parse_property(nested_name, nested_def, path, root_schema, level + 1, req_param, category))
        else:
            # Handle regular properties
            json_type = prop_def.get('type', 'string')
            xsd_type = self._json_type_to_xsd_type(json_type)
            
            # Create property row
            row = {
                'levels': path[:self.max_level] + [''] * (self.max_level - len(path)),
                'Request Parameter': req_param,
                'GDPR': '',
                'Cardinality': '1..1',
                'Type': xsd_type,
                'Base Type': xsd_type,
                'Details': self._extract_details(prop_def),
                'Description': prop_def.get('description', ''),
                'Category': category,
                'Example': prop_def.get('example', '')
            }
            rows.append(row)
            
            # Handle nested objects
            if json_type == 'object' and 'properties' in prop_def:
                for nested_name, nested_def in prop_def['properties'].items():
                    rows.extend(self._parse_property(nested_name, nested_def, path, root_schema, level + 1, req_param, category))
        
        return rows

    def _resolve_reference(self, ref_path: str, root_schema: Dict) -> Optional[Dict]:
        """
        Resolve a JSON Schema reference.
        
        Args:
            ref_path: Reference path (e.g., "#/$defs/veggie")
            root_schema: Root schema dictionary
            
        Returns:
            Resolved schema definition or None
        """
        if ref_path in self.schema_cache:
            return self.schema_cache[ref_path]
        
        # Handle different reference formats
        if ref_path.startswith('#/'):
            # Internal reference
            path_parts = ref_path[2:].split('/')
            current = root_schema
            
            for part in path_parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
            
            self.schema_cache[ref_path] = current
            return current
        
        return None

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
            'array': 'array',
            'object': 'object'
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
        
        # Required fields
        if 'required' in prop_def:
            required_fields = ','.join(prop_def['required'])
            details.append(f"required={required_fields}")
        
        return ', '.join(details) 