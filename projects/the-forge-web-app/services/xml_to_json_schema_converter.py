import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
import re


class XMLToJSONSchemaConverter:
    """
    Convert XML examples to JSON Schema format.
    """
    
    def __init__(self):
        self.type_patterns = {
            'integer': r'^-?\d+$',
            'number': r'^-?\d+(\.\d+)?$',
            'boolean': r'^(true|false|0|1)$',
            'date': r'^\d{4}-\d{2}-\d{2}$',
            'date-time': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'uri': r'^https?://',
            'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            'ipv4': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',
            'ipv6': r'^[0-9a-fA-F:]+$'
        }
    
    def convert_xml_to_json_schema(self, xml_content: str, schema_name: str = "GeneratedSchema") -> Dict[str, Any]:
        """
        Convert XML content to JSON Schema.
        """
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Create JSON Schema
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "title": schema_name,
                "properties": {},
                "required": []
            }
            
            # Convert root element
            properties, required = self._convert_element(root)
            json_schema["properties"] = properties
            json_schema["required"] = required
            
            return json_schema
            
        except Exception as e:
            raise Exception(f"Error converting XML to JSON Schema: {str(e)}")
    
    def _convert_element(self, element: ET.Element) -> tuple[Dict[str, Any], List[str]]:
        """
        Convert an XML element to JSON Schema properties.
        """
        properties = {}
        required = []
        
        # Handle attributes
        for attr_name, attr_value in element.attrib.items():
            attr_type = self._infer_type(attr_value)
            properties[attr_name] = {"type": attr_type}
            required.append(attr_name)
        
        # Handle child elements
        children = list(element)
        if children:
            # Group children by name to handle arrays
            child_groups = {}
            for child in children:
                child_name = child.tag
                if child_name not in child_groups:
                    child_groups[child_name] = []
                child_groups[child_name].append(child)
            
            # Convert each group
            for child_name, child_list in child_groups.items():
                if len(child_list) == 1:
                    # Single element
                    child_prop, child_req = self._convert_element(child_list[0])
                    properties[child_name] = child_prop
                    required.extend(child_req)
                else:
                    # Array of elements
                    # Check if all children have the same structure
                    first_child_prop, first_child_req = self._convert_element(child_list[0])
                    
                    # Verify all children have similar structure
                    is_similar = all(
                        self._compare_element_structures(child_list[0], child)
                        for child in child_list[1:]
                    )
                    
                    if is_similar:
                        properties[child_name] = {
                            "type": "array",
                            "items": first_child_prop,
                            "minItems": 1,
                            "uniqueItems": True
                        }
                        required.append(child_name)
                    else:
                        # Different structures - use anyOf
                        item_schemas = []
                        for child in child_list:
                            child_prop, _ = self._convert_element(child)
                            item_schemas.append(child_prop)
                        
                        properties[child_name] = {
                            "type": "array",
                            "items": {
                                "anyOf": item_schemas
                            },
                            "minItems": 1
                        }
                        required.append(child_name)
        else:
            # Leaf element - infer type from text content
            if element.text and element.text.strip():
                text_content = element.text.strip()
                inferred_type = self._infer_type(text_content)
                properties["value"] = {"type": inferred_type}
                required.append("value")
        
        return properties, required
    
    def _compare_element_structures(self, elem1: ET.Element, elem2: ET.Element) -> bool:
        """
        Compare if two elements have similar structure.
        """
        # Compare attributes
        if set(elem1.attrib.keys()) != set(elem2.attrib.keys()):
            return False
        
        # Compare child elements
        children1 = [child.tag for child in elem1]
        children2 = [child.tag for child in elem2]
        
        return children1 == children2
    
    def _infer_type(self, value: str) -> str:
        """
        Infer JSON Schema type from a value.
        """
        if not value:
            return "string"
        
        # Check each type pattern
        for type_name, pattern in self.type_patterns.items():
            if re.match(pattern, value, re.IGNORECASE):
                return type_name
        
        # Check for boolean values
        if value.lower() in ['true', 'false', '0', '1']:
            return "boolean"
        
        # Check for numbers
        try:
            float(value)
            if '.' in value:
                return "number"
            else:
                return "integer"
        except ValueError:
            pass
        
        # Default to string
        return "string"
    
    def _infer_format(self, value: str, type_name: str) -> Optional[str]:
        """
        Infer format from value and type.
        """
        if type_name == "string":
            if re.match(self.type_patterns['email'], value):
                return "email"
            elif re.match(self.type_patterns['date'], value):
                return "date"
            elif re.match(self.type_patterns['date-time'], value):
                return "date-time"
            elif re.match(self.type_patterns['uri'], value):
                return "uri"
            elif re.match(self.type_patterns['uuid'], value):
                return "uuid"
            elif re.match(self.type_patterns['ipv4'], value):
                return "ipv4"
            elif re.match(self.type_patterns['ipv6'], value):
                return "ipv6"
        
        return None
    
    def validate_json_schema(self, schema: Dict[str, Any]) -> bool:
        """
        Validate that the generated JSON Schema is valid.
        """
        try:
            # Basic validation
            required_fields = ['$schema', 'type', 'properties']
            for field in required_fields:
                if field not in schema:
                    return False
            
            if schema['type'] != 'object':
                return False
            
            if not isinstance(schema.get('properties', {}), dict):
                return False
            
            return True
        except Exception:
            return False
    
    def get_schema_statistics(self, schema: Dict[str, Any]) -> Dict[str, int]:
        """
        Get statistics about the generated JSON Schema.
        """
        try:
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            return {
                'total_properties': len(properties),
                'required_properties': len(required),
                'optional_properties': len(properties) - len(required)
            }
        except Exception:
            return {} 