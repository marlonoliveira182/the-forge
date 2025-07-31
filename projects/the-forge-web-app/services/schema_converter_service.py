#!/usr/bin/env python3
"""
Schema Converter Service
Handles conversion between XSD and JSON Schema formats.
"""

import xml.etree.ElementTree as ET
import json
import re
from typing import Dict, List, Any, Optional


class SchemaConverterService:
    """Service for converting between XSD and JSON Schema formats."""
    
    def __init__(self):
        self.xsd_ns = '{http://www.w3.org/2001/XMLSchema}'
        self.json_schema_draft = "http://json-schema.org/draft-07/schema#"
    
    def xsd_to_json_schema(self, xsd_content: str) -> str:
        """
        Convert XSD content to JSON Schema.
        
        Args:
            xsd_content: XSD content as string
            
        Returns:
            JSON Schema as string
        """
        try:
            # Parse XSD
            root = ET.fromstring(xsd_content)
            
            # Create base JSON Schema
            json_schema = {
                "$schema": self.json_schema_draft,
                "type": "object",
                "properties": {},
                "required": [],
                "definitions": {}
            }
            
            # Process elements
            for element in root.findall(f'.//{self.xsd_ns}element'):
                self._process_xsd_element(element, json_schema, root)
            
            # Process complex types
            for complex_type in root.findall(f'.//{self.xsd_ns}complexType'):
                self._process_complex_type(complex_type, json_schema)
            
            # Process simple types
            for simple_type in root.findall(f'.//{self.xsd_ns}simpleType'):
                self._process_simple_type(simple_type, json_schema)
            
            return json.dumps(json_schema, indent=2)
            
        except Exception as e:
            raise Exception(f"Error converting XSD to JSON Schema: {str(e)}")
    
    def json_schema_to_xsd(self, json_schema_content: str) -> str:
        """
        Convert JSON Schema content to XSD.
        
        Args:
            json_schema_content: JSON Schema content as string
            
        Returns:
            XSD as string
        """
        try:
            # Parse JSON Schema
            schema = json.loads(json_schema_content)
            
            # Create base XSD
            xsd_root = ET.Element('schema')
            xsd_root.set('xmlns:xs', 'http://www.w3.org/2001/XMLSchema')
            xsd_root.set('elementFormDefault', 'qualified')
            xsd_root.set('attributeFormDefault', 'unqualified')
            
            # Process properties
            if 'properties' in schema:
                for prop_name, prop_def in schema['properties'].items():
                    self._process_json_property(prop_name, prop_def, xsd_root, schema)
            
            # Create XML string
            return ET.tostring(xsd_root, encoding='unicode', method='xml')
            
        except Exception as e:
            raise Exception(f"Error converting JSON Schema to XSD: {str(e)}")
    
    def _process_xsd_element(self, element: ET.Element, json_schema: Dict, root: ET.Element) -> None:
        """Process an XSD element and add it to JSON Schema."""
        name = element.get('name')
        if not name:
            return
        
        type_name = element.get('type')
        if type_name:
            # Handle built-in types
            json_type = self._xsd_type_to_json_type(type_name)
            json_schema['properties'][name] = {
                "type": json_type,
                "description": f"Converted from XSD element: {name}"
            }
        else:
            # Handle complex types
            complex_type = element.find(f'.//{self.xsd_ns}complexType')
            if complex_type is not None:
                self._process_complex_type(complex_type, json_schema, name)
    
    def _process_complex_type(self, complex_type: ET.Element, json_schema: Dict, element_name: str = None) -> None:
        """Process an XSD complex type."""
        type_name = complex_type.get('name')
        
        # Create property definition
        prop_def = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Process sequence
        sequence = complex_type.find(f'.//{self.xsd_ns}sequence')
        if sequence is not None:
            for child in sequence:
                if child.tag.endswith('element'):
                    child_name = child.get('name')
                    child_type = child.get('type')
                    if child_name and child_type:
                        json_type = self._xsd_type_to_json_type(child_type)
                        prop_def['properties'][child_name] = {
                            "type": json_type,
                            "description": f"Converted from XSD element: {child_name}"
                        }
        
        # Process attributes
        for attr in complex_type.findall(f'.//{self.xsd_ns}attribute'):
            attr_name = attr.get('name')
            attr_type = attr.get('type')
            if attr_name and attr_type:
                json_type = self._xsd_type_to_json_type(attr_type)
                prop_def['properties'][f"@{attr_name}"] = {
                    "type": json_type,
                    "description": f"Converted from XSD attribute: {attr_name}"
                }
        
        if element_name:
            json_schema['properties'][element_name] = prop_def
        elif type_name:
            json_schema['definitions'][type_name] = prop_def
    
    def _process_simple_type(self, simple_type: ET.Element, json_schema: Dict) -> None:
        """Process an XSD simple type."""
        type_name = simple_type.get('name')
        if not type_name:
            return
        
        restriction = simple_type.find(f'.//{self.xsd_ns}restriction')
        if restriction is not None:
            base_type = restriction.get('base')
            json_type = self._xsd_type_to_json_type(base_type)
            
            # Add constraints
            constraints = {}
            for constraint in restriction:
                constraint_name = constraint.tag.split('}')[-1]
                constraint_value = constraint.get('value')
                if constraint_value:
                    if constraint_name == 'minLength':
                        constraints['minLength'] = int(constraint_value)
                    elif constraint_name == 'maxLength':
                        constraints['maxLength'] = int(constraint_value)
                    elif constraint_name == 'pattern':
                        constraints['pattern'] = constraint_value
                    elif constraint_name == 'enumeration':
                        if 'enum' not in constraints:
                            constraints['enum'] = []
                        constraints['enum'].append(constraint_value)
            
            json_schema['definitions'][type_name] = {
                "type": json_type,
                **constraints
            }
    
    def _process_json_property(self, prop_name: str, prop_def: Dict, xsd_root: ET.Element, schema: Dict) -> None:
        """Process a JSON Schema property and add it to XSD."""
        # Create element
        element = ET.SubElement(xsd_root, 'element')
        element.set('name', prop_name)
        
        # Handle different JSON types
        json_type = prop_def.get('type', 'string')
        xsd_type = self._json_type_to_xsd_type(json_type)
        
        if json_type == 'object':
            # Create complex type for object
            complex_type = ET.SubElement(element, 'complexType')
            sequence = ET.SubElement(complex_type, 'sequence')
            
            # Process nested properties
            if 'properties' in prop_def:
                for nested_name, nested_def in prop_def['properties'].items():
                    nested_element = ET.SubElement(sequence, 'element')
                    nested_element.set('name', nested_name)
                    nested_type = nested_def.get('type', 'string')
                    nested_xsd_type = self._json_type_to_xsd_type(nested_type)
                    nested_element.set('type', nested_xsd_type)
        else:
            element.set('type', xsd_type)
    
    def _xsd_type_to_json_type(self, xsd_type: str) -> str:
        """Convert XSD type to JSON Schema type."""
        type_mapping = {
            'xs:string': 'string',
            'xs:integer': 'integer',
            'xs:int': 'integer',
            'xs:long': 'integer',
            'xs:double': 'number',
            'xs:float': 'number',
            'xs:boolean': 'boolean',
            'xs:date': 'string',
            'xs:dateTime': 'string',
            'xs:decimal': 'number',
            'xs:positiveInteger': 'integer',
            'xs:nonNegativeInteger': 'integer'
        }
        
        # Remove namespace prefix if present
        if xsd_type.startswith('xs:'):
            xsd_type = xsd_type[3:]
        
        return type_mapping.get(f'xs:{xsd_type}', 'string')
    
    def _json_type_to_xsd_type(self, json_type: str) -> str:
        """Convert JSON Schema type to XSD type."""
        type_mapping = {
            'string': 'xs:string',
            'integer': 'xs:integer',
            'number': 'xs:double',
            'boolean': 'xs:boolean',
            'array': 'xs:string',  # Default for arrays
            'object': 'xs:string'   # Default for objects
        }
        
        return type_mapping.get(json_type, 'xs:string')
    
    def validate_xsd_content(self, content: str) -> bool:
        """Validate XSD content."""
        try:
            ET.fromstring(content)
            return True
        except ET.ParseError:
            return False
    
    def validate_json_schema_content(self, content: str) -> bool:
        """Validate JSON Schema content."""
        try:
            json.loads(content)
            return True
        except json.JSONDecodeError:
            return False 