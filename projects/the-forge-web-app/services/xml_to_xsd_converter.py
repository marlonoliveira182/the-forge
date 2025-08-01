import xml.etree.ElementTree as ET
from typing import Dict, List, Set, Any, Optional
import re


class XMLToXSDConverter:
    """
    Service for converting XML examples to XSD schemas.
    """
    
    def __init__(self):
        self.processed_elements: Set[str] = set()
        self.element_types: Dict[str, str] = {}
        self.complex_types: Dict[str, Dict[str, Any]] = {}
        self.simple_types: Dict[str, Dict[str, Any]] = {}
    
    def convert_xml_example_to_xsd(self, xml_data: str, schema_name: str = "GeneratedSchema") -> str:
        """
        Convert an XML example to an XSD schema.
        
        Args:
            xml_data: The XML data as string
            schema_name: Name for the generated schema
            
        Returns:
            String containing the generated XSD schema
        """
        self.processed_elements.clear()
        self.element_types.clear()
        self.complex_types.clear()
        self.simple_types.clear()
        
        try:
            # Parse XML
            root = ET.fromstring(xml_data)
            
            # Analyze XML structure
            self._analyze_element(root, "root")
            
            # Generate XSD
            xsd_content = self._generate_xsd_content(schema_name, root.tag)
            
            return xsd_content
            
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML: {str(e)}")
    
    def _analyze_element(self, element: ET.Element, path: str):
        """
        Recursively analyze XML element structure.
        """
        element_name = element.tag
        full_path = f"{path}.{element_name}" if path != "root" else element_name
        
        # Check if we've already processed this element structure
        if full_path in self.processed_elements:
            return
        
        self.processed_elements.add(full_path)
        
        # Analyze attributes
        attributes = {}
        for attr_name, attr_value in element.attrib.items():
            attr_type = self._detect_attribute_type(attr_value)
            attributes[attr_name] = {
                "type": attr_type,
                "value": attr_value
            }
        
        # Analyze child elements
        child_elements = {}
        child_counts = {}
        
        for child in element:
            child_name = child.tag
            if child_name not in child_elements:
                child_elements[child_name] = []
                child_counts[child_name] = 0
            
            child_elements[child_name].append(child)
            child_counts[child_name] += 1
            
            # Recursively analyze child
            self._analyze_element(child, full_path)
        
        # Determine element type
        if len(child_elements) == 0 and not element.text:
            # Empty element
            element_type = "empty"
        elif len(child_elements) == 0 and element.text and element.text.strip():
            # Simple element with text content
            element_type = "simple"
            text_type = self._detect_text_type(element.text.strip())
            self.simple_types[full_path] = {
                "type": text_type,
                "value": element.text.strip()
            }
        else:
            # Complex element with children
            element_type = "complex"
            self.complex_types[full_path] = {
                "attributes": attributes,
                "children": child_elements,
                "counts": child_counts,
                "has_text": bool(element.text and element.text.strip())
            }
        
        self.element_types[full_path] = element_type
    
    def _detect_attribute_type(self, value: str) -> str:
        """
        Detect the XSD type of an attribute value.
        """
        if not value:
            return "string"
        
        # Integer
        if re.match(r"^-?\d+$", value):
            return "integer"
        
        # Decimal
        if re.match(r"^-?\d+\.\d+$", value):
            return "decimal"
        
        # Boolean
        if value.lower() in ["true", "false", "1", "0"]:
            return "boolean"
        
        # Date
        if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            return "date"
        
        # DateTime
        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", value):
            return "dateTime"
        
        # Email
        if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
            return "string"  # XSD doesn't have email type, use string with pattern
        
        # URL
        if re.match(r"^https?://", value):
            return "anyURI"
        
        # Default to string
        return "string"
    
    def _detect_text_type(self, value: str) -> str:
        """
        Detect the XSD type of text content.
        """
        if not value:
            return "string"
        
        # Integer
        if re.match(r"^-?\d+$", value):
            return "integer"
        
        # Decimal
        if re.match(r"^-?\d+\.\d+$", value):
            return "decimal"
        
        # Boolean
        if value.lower() in ["true", "false", "1", "0"]:
            return "boolean"
        
        # Date
        if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            return "date"
        
        # DateTime
        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", value):
            return "dateTime"
        
        # Email
        if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
            return "string"  # XSD doesn't have email type, use string with pattern
        
        # URL
        if re.match(r"^https?://", value):
            return "anyURI"
        
        # Default to string
        return "string"
    
    def _generate_xsd_content(self, schema_name: str, root_element_name: str) -> str:
        """
        Generate the complete XSD content.
        """
        xsd_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"',
            f'           targetNamespace="http://example.com/{schema_name.lower()}"',
            f'           xmlns:tns="http://example.com/{schema_name.lower()}"',
            '           elementFormDefault="qualified">',
            '',
            f'  <!-- Root element -->',
            f'  <xs:element name="{root_element_name}" type="tns:{root_element_name}Type"/>',
            ''
        ]
        
        # Generate complex types
        for element_path, complex_type in self.complex_types.items():
            element_name = element_path.split('.')[-1]
            xsd_lines.extend(self._generate_complex_type(element_name, complex_type))
        
        # Generate simple types
        for element_path, simple_type in self.simple_types.items():
            element_name = element_path.split('.')[-1]
            xsd_lines.extend(self._generate_simple_type(element_name, simple_type))
        
        xsd_lines.append('</xs:schema>')
        
        return '\n'.join(xsd_lines)
    
    def _generate_complex_type(self, element_name: str, complex_type: Dict[str, Any]) -> List[str]:
        """
        Generate XSD complex type definition.
        """
        lines = [
            f'  <xs:complexType name="{element_name}Type">',
            '    <xs:sequence>'
        ]
        
        # Add child elements
        for child_name, children in complex_type["children"].items():
            child_count = complex_type["counts"][child_name]
            
            if child_count == 1:
                # Single occurrence
                lines.append(f'      <xs:element name="{child_name}" type="tns:{child_name}Type"/>')
            else:
                # Multiple occurrences
                lines.append(f'      <xs:element name="{child_name}" type="tns:{child_name}Type" maxOccurs="unbounded"/>')
        
        lines.append('    </xs:sequence>')
        
        # Add attributes
        for attr_name, attr_info in complex_type["attributes"].items():
            lines.append(f'    <xs:attribute name="{attr_name}" type="xs:{attr_info["type"]}"/>')
        
        # Add text content if present
        if complex_type["has_text"]:
            lines.append('    <xs:simpleContent>')
            lines.append('      <xs:extension base="xs:string">')
            for attr_name, attr_info in complex_type["attributes"].items():
                lines.append(f'        <xs:attribute name="{attr_name}" type="xs:{attr_info["type"]}"/>')
            lines.append('      </xs:extension>')
            lines.append('    </xs:simpleContent>')
        
        lines.append('  </xs:complexType>')
        lines.append('')
        
        return lines
    
    def _generate_simple_type(self, element_name: str, simple_type: Dict[str, Any]) -> List[str]:
        """
        Generate XSD simple type definition.
        """
        lines = [
            f'  <xs:simpleType name="{element_name}Type">',
            f'    <xs:restriction base="xs:{simple_type["type"]}">'
        ]
        
        # Add pattern for email if applicable
        if simple_type["type"] == "string" and "@" in simple_type["value"]:
            lines.append(r'      <xs:pattern value="[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"/>')
        
        lines.extend([
            '    </xs:restriction>',
            '  </xs:simpleType>',
            ''
        ])
        
        return lines
    
    def validate_xsd(self, xsd_content: str) -> bool:
        """
        Basic validation of generated XSD.
        """
        try:
            ET.fromstring(xsd_content)
            return True
        except ET.ParseError:
            return False
    
    def get_schema_statistics(self, xsd_content: str) -> Dict[str, int]:
        """
        Get statistics about a generated XSD schema.
        """
        try:
            root = ET.fromstring(xsd_content)
            stats = {
                'total_elements': 0,
                'complex_types': 0,
                'simple_types': 0,
                'attributes': 0,
                'max_depth': 0
            }
            
            self._analyze_xsd_schema(root, stats, 0)
            return stats
        except ET.ParseError:
            return {
                'total_elements': 0,
                'complex_types': 0,
                'simple_types': 0,
                'attributes': 0,
                'max_depth': 0
            }
    
    def _analyze_xsd_schema(self, element: ET.Element, stats: Dict[str, int], depth: int):
        """
        Recursively analyze XSD schema for statistics.
        """
        stats['max_depth'] = max(stats['max_depth'], depth)
        
        tag = element.tag
        if tag.endswith('element'):
            stats['total_elements'] += 1
        elif tag.endswith('complexType'):
            stats['complex_types'] += 1
        elif tag.endswith('simpleType'):
            stats['simple_types'] += 1
        elif tag.endswith('attribute'):
            stats['attributes'] += 1
        
        for child in element:
            self._analyze_xsd_schema(child, stats, depth + 1) 