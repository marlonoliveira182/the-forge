import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
import re


class XSDToJSONSchemaConverter:
    """
    Convert XSD schemas to JSON Schema format.
    """
    
    def __init__(self):
        self.namespace_map = {
            'xs': 'http://www.w3.org/2001/XMLSchema',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }
        self.type_mapping = {
            'string': 'string',
            'integer': 'integer',
            'int': 'integer',
            'long': 'integer',
            'short': 'integer',
            'byte': 'integer',
            'decimal': 'number',
            'float': 'number',
            'double': 'number',
            'boolean': 'boolean',
            'date': 'string',
            'dateTime': 'string',
            'time': 'string',
            'duration': 'string',
            'gYear': 'string',
            'gMonth': 'string',
            'gDay': 'string',
            'gYearMonth': 'string',
            'gMonthDay': 'string',
            'hexBinary': 'string',
            'base64Binary': 'string',
            'anyURI': 'string',
            'QName': 'string',
            'NOTATION': 'string'
        }
        self.format_mapping = {
            'date': 'date',
            'dateTime': 'date-time',
            'time': 'time',
            'anyURI': 'uri',
            'hexBinary': 'hex',
            'base64Binary': 'base64'
        }
    
    def convert_xsd_to_json_schema(self, xsd_content: str, schema_name: str = "GeneratedSchema") -> Dict[str, Any]:
        """
        Convert XSD content to JSON Schema.
        """
        try:
            # Parse XSD
            root = ET.fromstring(xsd_content)
            
            # Find the root element
            root_element = self._find_root_element(root)
            if not root_element:
                raise ValueError("No root element found in XSD")
            
            # Create JSON Schema
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "title": schema_name,
                "properties": {},
                "required": []
            }
            
            # Convert root element
            properties, required = self._convert_element(root_element, root)
            json_schema["properties"] = properties
            json_schema["required"] = required
            
            return json_schema
            
        except Exception as e:
            raise Exception(f"Error converting XSD to JSON Schema: {str(e)}")
    
    def _find_root_element(self, root: ET.Element) -> Optional[ET.Element]:
        """
        Find the root element in the XSD.
        """
        # Look for element definitions
        for element in root.findall('.//xs:element', self.namespace_map):
            if element.get('name'):
                return element
        
        # If no named elements, look for any element
        for element in root.findall('.//xs:element', self.namespace_map):
            return element
        
        return None
    
    def _convert_element(self, element: ET.Element, root: ET.Element) -> tuple[Dict[str, Any], List[str]]:
        """
        Convert an XSD element to JSON Schema properties.
        """
        properties = {}
        required = []
        
        element_name = element.get('name', 'root')
        element_type = element.get('type')
        
        if element_type:
            # Simple type
            prop_def = self._convert_simple_type(element_type, root)
            properties[element_name] = prop_def
            required.append(element_name)
        else:
            # Complex type - look for complexType definition
            complex_type = self._find_complex_type(element, root)
            if complex_type:
                prop_def, req_fields = self._convert_complex_type(complex_type, root)
                properties[element_name] = prop_def
                required.extend(req_fields)
            else:
                # Default to string
                properties[element_name] = {"type": "string"}
                required.append(element_name)
        
        return properties, required
    
    def _find_complex_type(self, element: ET.Element, root: ET.Element) -> Optional[ET.Element]:
        """
        Find the complexType definition for an element.
        """
        # Look for inline complexType
        complex_type = element.find('xs:complexType', self.namespace_map)
        if complex_type is not None:
            return complex_type
        
        # Look for referenced complexType
        type_name = element.get('type')
        if type_name:
            # Remove namespace prefix if present
            if ':' in type_name:
                type_name = type_name.split(':')[-1]
            
            for ct in root.findall('.//xs:complexType', self.namespace_map):
                if ct.get('name') == type_name:
                    return ct
        
        return None
    
    def _convert_complex_type(self, complex_type: ET.Element, root: ET.Element) -> tuple[Dict[str, Any], List[str]]:
        """
        Convert a complexType to JSON Schema object.
        """
        properties = {}
        required = []
        
        # Handle sequence
        sequence = complex_type.find('xs:sequence', self.namespace_map)
        if sequence is not None:
            for child in sequence.findall('xs:element', self.namespace_map):
                child_name = child.get('name')
                child_type = child.get('type')
                min_occurs = int(child.get('minOccurs', '1'))
                max_occurs = child.get('maxOccurs', '1')
                
                if child_type:
                    prop_def = self._convert_simple_type(child_type, root)
                else:
                    # Look for complex type
                    child_complex = self._find_complex_type(child, root)
                    if child_complex:
                        prop_def, _ = self._convert_complex_type(child_complex, root)
                    else:
                        prop_def = {"type": "string"}
                
                # Handle arrays
                if max_occurs == 'unbounded' or (max_occurs != '1' and int(max_occurs) > 1):
                    prop_def = {
                        "type": "array",
                        "items": prop_def,
                        "minItems": min_occurs
                    }
                
                properties[child_name] = prop_def
                if min_occurs > 0:
                    required.append(child_name)
        
        # Handle attributes
        for attr in complex_type.findall('xs:attribute', self.namespace_map):
            attr_name = attr.get('name')
            attr_type = attr.get('type', 'string')
            use = attr.get('use', 'optional')
            
            prop_def = self._convert_simple_type(attr_type, root)
            properties[attr_name] = prop_def
            
            if use == 'required':
                required.append(attr_name)
        
        return {"type": "object", "properties": properties}, required
    
    def _convert_simple_type(self, type_name: str, root: ET.Element) -> Dict[str, Any]:
        """
        Convert a simple type to JSON Schema.
        """
        # Remove namespace prefix if present
        if ':' in type_name:
            type_name = type_name.split(':')[-1]
        
        # Check if it's a built-in type
        if type_name in self.type_mapping:
            json_type = self.type_mapping[type_name]
            prop_def = {"type": json_type}
            
            # Add format if available
            if type_name in self.format_mapping:
                prop_def["format"] = self.format_mapping[type_name]
            
            return prop_def
        
        # Look for simpleType definition
        for simple_type in root.findall('.//xs:simpleType', self.namespace_map):
            if simple_type.get('name') == type_name:
                return self._convert_simple_type_definition(simple_type, root)
        
        # Default to string
        return {"type": "string"}
    
    def _convert_simple_type_definition(self, simple_type: ET.Element, root: ET.Element) -> Dict[str, Any]:
        """
        Convert a simpleType definition to JSON Schema.
        """
        restriction = simple_type.find('xs:restriction', self.namespace_map)
        if restriction is not None:
            base_type = restriction.get('base')
            if base_type:
                prop_def = self._convert_simple_type(base_type, root)
                
                # Add restrictions
                for child in restriction:
                    tag = child.tag.split('}')[-1]  # Remove namespace
                    value = child.get('value')
                    
                    if tag == 'minLength' and value:
                        prop_def['minLength'] = int(value)
                    elif tag == 'maxLength' and value:
                        prop_def['maxLength'] = int(value)
                    elif tag == 'pattern' and value:
                        prop_def['pattern'] = value
                    elif tag == 'minimum' and value:
                        prop_def['minimum'] = float(value)
                    elif tag == 'maximum' and value:
                        prop_def['maximum'] = float(value)
                    elif tag == 'enumeration' and value:
                        if 'enum' not in prop_def:
                            prop_def['enum'] = []
                        prop_def['enum'].append(value)
                
                return prop_def
        
        return {"type": "string"}
    
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