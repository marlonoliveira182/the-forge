import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
import re


class JSONToXMLConverter:
    """
    Convert JSON examples to XML format.
    """
    
    def __init__(self):
        self.root_element_name = "root"
        self.array_item_name = "item"
        self.attribute_prefix = "@"
    
    def convert_json_to_xml(self, json_data: Any, root_name: str = "root") -> str:
        """
        Convert JSON data to XML content.
        """
        try:
            # Create root element
            root = ET.Element(root_name)
            
            # Convert JSON to XML
            self._convert_json_element(json_data, root)
            
            # Convert to string with proper formatting
            return ET.tostring(root, encoding='unicode', method='xml')
            
        except Exception as e:
            raise Exception(f"Error converting JSON to XML: {str(e)}")
    
    def _convert_json_element(self, data: Any, parent: ET.Element) -> None:
        """
        Convert a JSON element to XML.
        """
        if isinstance(data, dict):
            # Handle object
            for key, value in data.items():
                if key.startswith(self.attribute_prefix):
                    # This is an attribute
                    attr_name = key[1:]  # Remove @ prefix
                    parent.set(attr_name, str(value))
                else:
                    # This is an element
                    child = ET.SubElement(parent, key)
                    self._convert_json_element(value, child)
        
        elif isinstance(data, list):
            # Handle array
            for item in data:
                child = ET.SubElement(parent, self.array_item_name)
                self._convert_json_element(item, child)
        
        elif isinstance(data, (str, int, float, bool)):
            # Handle primitive types
            if parent.text is None:
                parent.text = str(data)
            else:
                parent.text += str(data)
        
        elif data is None:
            # Handle null values
            parent.set('xsi:nil', 'true')
    
    def convert_json_schema_to_xml(self, schema: Dict[str, Any], root_name: str = "root") -> str:
        """
        Convert JSON Schema to XML example.
        """
        try:
            # Generate sample data from schema
            sample_data = self._generate_sample_from_schema(schema)
            
            # Convert to XML
            return self.convert_json_to_xml(sample_data, root_name)
            
        except Exception as e:
            raise Exception(f"Error converting JSON Schema to XML: {str(e)}")
    
    def _generate_sample_from_schema(self, schema: Dict[str, Any]) -> Any:
        """
        Generate sample data from JSON Schema.
        """
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            result = {}
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            for prop_name, prop_schema in properties.items():
                if prop_name in required:
                    result[prop_name] = self._generate_sample_from_schema(prop_schema)
            
            return result
        
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            min_items = schema.get('minItems', 1)
            max_items = schema.get('maxItems', 3)
            
            # Generate 1-3 items
            num_items = min(min_items, 3)
            return [self._generate_sample_from_schema(items_schema) for _ in range(num_items)]
        
        elif schema_type == 'string':
            format_type = schema.get('format')
            if format_type == 'email':
                return "example@domain.com"
            elif format_type == 'date':
                return "2023-01-01"
            elif format_type == 'date-time':
                return "2023-01-01T00:00:00"
            elif format_type == 'uri':
                return "https://example.com"
            elif format_type == 'uuid':
                return "123e4567-e89b-12d3-a456-426614174000"
            elif format_type == 'ipv4':
                return "192.168.1.1"
            elif format_type == 'ipv6':
                return "2001:db8::1"
            else:
                return "example"
        
        elif schema_type == 'integer':
            minimum = schema.get('minimum', 0)
            maximum = schema.get('maximum', 100)
            return max(minimum, min(maximum, 42))
        
        elif schema_type == 'number':
            minimum = schema.get('minimum', 0.0)
            maximum = schema.get('maximum', 100.0)
            return max(minimum, min(maximum, 42.5))
        
        elif schema_type == 'boolean':
            return True
        
        elif schema_type == 'null':
            return None
        
        else:
            return "example"
    
    def validate_xml(self, xml_content: str) -> bool:
        """
        Validate that the generated XML is well-formed.
        """
        try:
            ET.fromstring(xml_content)
            return True
        except ET.ParseError:
            return False
    
    def get_xml_statistics(self, xml_content: str) -> Dict[str, int]:
        """
        Get statistics about the generated XML.
        """
        try:
            root = ET.fromstring(xml_content)
            
            # Count elements and attributes
            elements = root.findall('.//*')
            attributes = []
            for elem in [root] + elements:
                attributes.extend(elem.attrib.keys())
            
            return {
                'total_elements': len(elements) + 1,  # +1 for root
                'total_attributes': len(attributes),
                'max_depth': self._get_max_depth(root)
            }
        except Exception:
            return {}
    
    def _get_max_depth(self, element: ET.Element, current_depth: int = 0) -> int:
        """
        Get the maximum depth of the XML tree.
        """
        if not element:
            return current_depth
        
        max_depth = current_depth
        for child in element:
            child_depth = self._get_max_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
        
        return max_depth 