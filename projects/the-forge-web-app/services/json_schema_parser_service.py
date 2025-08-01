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
        
        # Get required fields from schema
        required_fields = set(schema.get('required', []))
        
        # Handle root level properties
        if 'properties' in schema:
            for prop_name, prop_def in schema['properties'].items():
                is_required = prop_name in required_fields
                rows.extend(self._parse_property(prop_name, prop_def, [], schema, is_required=is_required))
        
        return rows

    def _parse_property(self, name: str, prop_def: Dict, parent_path: List[str], 
                       root_schema: Dict, level: int = 1, req_param: str = 'Body', 
                       category: str = 'element', is_required: bool = False) -> List[Dict]:
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
            rows.extend(self._parse_array_property(name, prop_def, path, root_schema, level, req_param, category, is_required))
        else:
            # Handle non-array properties
            rows.extend(self._parse_simple_property(name, prop_def, path, root_schema, level, req_param, category, is_required))
        
        return rows

    def _parse_array_property(self, name: str, prop_def: Dict, path: List[str], 
                             root_schema: Dict, level: int, req_param: str, category: str, is_required: bool = False) -> List[Dict]:
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
                        'Cardinality': self._determine_cardinality(prop_def),
                        'Type': f'array<object>',
                        'Base Type': 'object',
                        'Details': self._extract_details(prop_def),
                        'Description': f'Array of {ref_path.split("/")[-1]} objects',
                        'Category': category,
                        'Example': ''
                    }
                    rows.append(array_row)
                    
                    # Parse the referenced object properties
                    if resolved_def.get('type') == 'object' and 'properties' in resolved_def:
                        # Get required fields for referenced object
                        ref_required_fields = set(resolved_def.get('required', []))
                        for nested_name, nested_def in resolved_def['properties'].items():
                            ref_is_required = nested_name in ref_required_fields
                            rows.extend(self._parse_property(nested_name, nested_def, path, root_schema, level + 1, req_param, category, ref_is_required))
            else:
                # Array of primitives or inline objects
                item_type = items_def.get('type', 'string')
                if item_type == 'object' and 'properties' in items_def:
                    # Array of inline objects
                    array_row = {
                        'levels': path[:self.max_level] + [''] * (self.max_level - len(path)),
                        'Request Parameter': req_param,
                        'GDPR': '',
                        'Cardinality': self._determine_cardinality(prop_def),
                        'Type': f'array<object>',
                        'Base Type': 'object',
                        'Details': self._extract_details(prop_def),
                        'Description': f'Array of objects',
                        'Category': category,
                        'Example': ''
                    }
                    rows.append(array_row)
                    
                    # Parse the inline object properties
                    # Get required fields for inline object
                    inline_required_fields = set(items_def.get('required', []))
                    for nested_name, nested_def in items_def['properties'].items():
                        inline_is_required = nested_name in inline_required_fields
                        rows.extend(self._parse_property(nested_name, nested_def, path, root_schema, level + 1, req_param, category, inline_is_required))
                else:
                    # Array of primitives
                    xsd_type = self._json_type_to_xsd_type(item_type)
                    array_row = {
                        'levels': path[:self.max_level] + [''] * (self.max_level - len(path)),
                        'Request Parameter': req_param,
                        'GDPR': '',
                        'Cardinality': self._determine_cardinality(prop_def),
                        'Type': f'array<{xsd_type}>',
                        'Base Type': xsd_type,
                        'Details': self._extract_details(prop_def),
                        'Description': f'Array of {item_type}',
                        'Category': category,
                        'Example': items_def.get('example', '')
                    }
                    rows.append(array_row)
        
        return rows

    def _parse_simple_property(self, name: str, prop_def: Dict, path: List[str], 
                              root_schema: Dict, level: int, req_param: str, category: str, is_required: bool = False) -> List[Dict]:
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
                    'Cardinality': self._determine_cardinality(prop_def, True),  # References are typically required
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
                'Cardinality': self._determine_cardinality(prop_def, is_required),
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
                # Get required fields for nested object
                nested_required_fields = set(prop_def.get('required', []))
                for nested_name, nested_def in prop_def['properties'].items():
                    nested_is_required = nested_name in nested_required_fields
                    rows.extend(self._parse_property(nested_name, nested_def, path, root_schema, level + 1, req_param, category, nested_is_required))
        
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

    def _determine_cardinality(self, prop_def: Dict, is_required: bool = False) -> str:
        """
        Determine cardinality based on JSON Schema constraints.
        
        Args:
            prop_def: Property definition
            is_required: Whether the property is required
            
        Returns:
            Cardinality string (e.g., "1..1", "0..1", "0..n", "1..n")
        """
        # Check if it's an array
        if prop_def.get('type') == 'array':
            min_items = prop_def.get('minItems', 0)
            max_items = prop_def.get('maxItems')
            
            if min_items == 0 and max_items is None:
                return "0..n"
            elif min_items == 1 and max_items is None:
                return "1..n"
            elif min_items == 0 and max_items == 1:
                return "0..1"
            elif min_items == 1 and max_items == 1:
                return "1..1"
            elif max_items is not None:
                return f"{min_items}..{max_items}"
            else:
                return f"{min_items}..n"
        
        # For non-array properties
        if is_required:
            return "1..1"
        else:
            return "0..1"

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
        
        # Additional JSON Schema constraints
        if 'multipleOf' in prop_def:
            details.append(f"multipleOf={prop_def['multipleOf']}")
        
        if 'exclusiveMinimum' in prop_def:
            details.append(f"exclusiveMinimum={prop_def['exclusiveMinimum']}")
        
        if 'exclusiveMaximum' in prop_def:
            details.append(f"exclusiveMaximum={prop_def['exclusiveMaximum']}")
        
        if 'uniqueItems' in prop_def:
            details.append(f"uniqueItems={prop_def['uniqueItems']}")
        
        if 'minItems' in prop_def:
            details.append(f"minItems={prop_def['minItems']}")
        
        if 'maxItems' in prop_def:
            details.append(f"maxItems={prop_def['maxItems']}")
        
        if 'minProperties' in prop_def:
            details.append(f"minProperties={prop_def['minProperties']}")
        
        if 'maxProperties' in prop_def:
            details.append(f"maxProperties={prop_def['maxProperties']}")
        
        if 'additionalProperties' in prop_def:
            details.append(f"additionalProperties={prop_def['additionalProperties']}")
        
        if 'allOf' in prop_def:
            details.append("allOf=composite")
        
        if 'anyOf' in prop_def:
            details.append("anyOf=union")
        
        if 'oneOf' in prop_def:
            details.append("oneOf=choice")
        
        if 'not' in prop_def:
            details.append("not=exclusion")
        
        return ', '.join(details) 