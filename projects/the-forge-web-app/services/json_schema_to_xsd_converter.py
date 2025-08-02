import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
import re


class JSONSchemaToXSDConverter:
    """
    Convert JSON Schema to XSD format.
    """
    
    def __init__(self):
        self.type_mapping = {
            'string': 'xs:string',
            'integer': 'xs:integer',
            'number': 'xs:decimal',
            'boolean': 'xs:boolean',
            'array': 'xs:anyType',
            'object': 'xs:anyType',
            'null': 'xs:string'
        }
        self.format_mapping = {
            'date': 'xs:date',
            'date-time': 'xs:dateTime',
            'time': 'xs:time',
            'uri': 'xs:anyURI',
            'email': 'xs:string',
            'uuid': 'xs:string',
            'ipv4': 'xs:string',
            'ipv6': 'xs:string'
        }
        self.element_counter = 0
    
    def convert_json_schema_to_xsd(self, schema: Dict[str, Any], schema_name: str = "GeneratedSchema") -> str:
        """
        Convert JSON Schema to XSD content.
        """
        try:
            # Create root schema element
            root = ET.Element('xs:schema')
            root.set('xmlns:xs', 'http://www.w3.org/2001/XMLSchema')
            root.set('elementFormDefault', 'qualified')
            
            # Create root element
            root_element = ET.SubElement(root, 'xs:element')
            root_element.set('name', schema_name)
            
            # Convert schema to complex type
            complex_type = ET.SubElement(root_element, 'xs:complexType')
            
            # Convert properties
            properties = schema.get('properties', {})
            required_fields = schema.get('required', [])
            
            if properties:
                sequence = ET.SubElement(complex_type, 'xs:sequence')
                self._convert_properties_to_elements(properties, required_fields, sequence, root)
            else:
                # Empty object
                any_element = ET.SubElement(complex_type, 'xs:any')
                any_element.set('minOccurs', '0')
                any_element.set('maxOccurs', 'unbounded')
            
            # Convert to string
            return ET.tostring(root, encoding='unicode', method='xml')
            
        except Exception as e:
            raise Exception(f"Error converting JSON Schema to XSD: {str(e)}")
    
    def _convert_properties_to_elements(self, properties: Dict[str, Any], required_fields: List[str], 
                                      parent: ET.Element, root: ET.Element) -> None:
        """
        Convert JSON Schema properties to XSD elements.
        """
        for prop_name, prop_schema in properties.items():
            element = ET.SubElement(parent, 'xs:element')
            element.set('name', prop_name)
            
            # Set occurrence
            is_required = prop_name in required_fields
            if not is_required:
                element.set('minOccurs', '0')
            
            # Convert property type
            self._convert_property_type(prop_schema, element, root)
    
    def _convert_property_type(self, prop_schema: Dict[str, Any], element: ET.Element, root: ET.Element) -> None:
        """
        Convert a JSON Schema property type to XSD type.
        """
        prop_type = prop_schema.get('type', 'string')
        
        if prop_type == 'array':
            # Handle arrays
            self._convert_array_type(prop_schema, element, root)
        elif prop_type == 'object':
            # Handle objects
            self._convert_object_type(prop_schema, element, root)
        else:
            # Handle simple types
            self._convert_simple_type(prop_schema, element)
    
    def _convert_array_type(self, prop_schema: Dict[str, Any], element: ET.Element, root: ET.Element) -> None:
        """
        Convert JSON Schema array to XSD sequence.
        """
        # Create complex type for array
        complex_type = ET.SubElement(element, 'xs:complexType')
        sequence = ET.SubElement(complex_type, 'xs:sequence')
        
        # Create array item element
        item_element = ET.SubElement(sequence, 'xs:element')
        item_element.set('name', 'item')
        item_element.set('maxOccurs', 'unbounded')
        
        # Convert array items
        items_schema = prop_schema.get('items', {})
        if items_schema.get('type') == 'object':
            self._convert_object_type(items_schema, item_element, root)
        else:
            self._convert_simple_type(items_schema, item_element)
    
    def _convert_object_type(self, prop_schema: Dict[str, Any], element: ET.Element, root: ET.Element) -> None:
        """
        Convert JSON Schema object to XSD complex type.
        """
        properties = prop_schema.get('properties', {})
        required_fields = prop_schema.get('required', [])
        
        if properties:
            # Create complex type
            complex_type = ET.SubElement(element, 'xs:complexType')
            sequence = ET.SubElement(complex_type, 'xs:sequence')
            
            # Convert nested properties
            self._convert_properties_to_elements(properties, required_fields, sequence, root)
        else:
            # Empty object - use anyType
            element.set('type', 'xs:anyType')
    
    def _convert_simple_type(self, prop_schema: Dict[str, Any], element: ET.Element) -> None:
        """
        Convert JSON Schema simple type to XSD type.
        """
        prop_type = prop_schema.get('type', 'string')
        format_type = prop_schema.get('format')
        
        # Handle format-specific types
        if format_type and format_type in self.format_mapping:
            element.set('type', self.format_mapping[format_type])
        else:
            # Use basic type mapping
            xsd_type = self.type_mapping.get(prop_type, 'xs:string')
            element.set('type', xsd_type)
        
        # Add restrictions if present
        restrictions = []
        
        if 'minLength' in prop_schema:
            restrictions.append(('minLength', str(prop_schema['minLength'])))
        
        if 'maxLength' in prop_schema:
            restrictions.append(('maxLength', str(prop_schema['maxLength'])))
        
        if 'minimum' in prop_schema:
            restrictions.append(('minimum', str(prop_schema['minimum'])))
        
        if 'maximum' in prop_schema:
            restrictions.append(('maximum', str(prop_schema['maximum'])))
        
        if 'pattern' in prop_schema:
            restrictions.append(('pattern', prop_schema['pattern']))
        
        if 'enum' in prop_schema:
            for enum_value in prop_schema['enum']:
                restrictions.append(('enumeration', str(enum_value)))
        
        # Apply restrictions if any
        if restrictions:
            # Create simple type with restrictions
            simple_type = ET.SubElement(element, 'xs:simpleType')
            restriction = ET.SubElement(simple_type, 'xs:restriction')
            restriction.set('base', element.get('type'))
            
            # Remove the type attribute since we're using restriction
            element.attrib.pop('type', None)
            
            # Add restriction facets
            for facet_name, facet_value in restrictions:
                facet = ET.SubElement(restriction, f'xs:{facet_name}')
                facet.set('value', facet_value)
    
    def validate_xsd(self, xsd_content: str) -> bool:
        """
        Validate that the generated XSD is well-formed.
        """
        try:
            ET.fromstring(xsd_content)
            return True
        except ET.ParseError:
            return False
    
    def get_schema_statistics(self, xsd_content: str) -> Dict[str, int]:
        """
        Get statistics about the generated XSD.
        """
        try:
            root = ET.fromstring(xsd_content)
            
            # Count elements
            elements = root.findall('.//xs:element')
            complex_types = root.findall('.//xs:complexType')
            simple_types = root.findall('.//xs:simpleType')
            
            return {
                'total_elements': len(elements),
                'complex_types': len(complex_types),
                'simple_types': len(simple_types)
            }
        except Exception:
            return {} 