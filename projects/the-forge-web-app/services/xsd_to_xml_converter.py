import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
import random
import string


class XSDToXMLConverter:
    """
    Service for converting XSD schemas to XML examples.
    """
    
    def __init__(self):
        self.namespace_map = {}
        self.element_definitions = {}
        self.type_definitions = {}
        self.simple_types = {}
        self.complex_types = {}
    
    def convert_xsd_to_xml_example(self, xsd_content: str, root_element_name: Optional[str] = None) -> str:
        """
        Convert an XSD schema to an XML example.
        
        Args:
            xsd_content: The XSD schema as string
            root_element_name: Optional root element name (if not specified, will be inferred)
            
        Returns:
            String containing the generated XML example
        """
        try:
            # Parse XSD
            root = ET.fromstring(xsd_content)
            
            # Extract namespace information
            self._extract_namespaces(root)
            
            # Parse schema definitions
            self._parse_schema_definitions(root)
            
            # Determine root element
            if not root_element_name:
                root_element_name = self._find_root_element()
            
            if not root_element_name:
                raise ValueError("Could not determine root element from XSD")
            
            # Generate XML example
            xml_example = self._generate_xml_example(root_element_name)
            
            return xml_example
            
        except ET.ParseError as e:
            raise ValueError(f"Invalid XSD: {str(e)}")
    
    def _extract_namespaces(self, root: ET.Element):
        """
        Extract namespace information from XSD.
        """
        # Extract xmlns declarations
        for key, value in root.attrib.items():
            if key.startswith('xmlns'):
                if key == 'xmlns':
                    self.namespace_map[''] = value
                else:
                    prefix = key.split(':')[1]
                    self.namespace_map[prefix] = value
        
        # Extract target namespace
        target_ns = root.get('targetNamespace')
        if target_ns:
            self.namespace_map['tns'] = target_ns
    
    def _parse_schema_definitions(self, root: ET.Element):
        """
        Parse all schema definitions (elements, types, etc.).
        """
        for child in root:
            tag = child.tag
            
            if tag.endswith('element'):
                element_name = child.get('name')
                element_type = child.get('type')
                if element_name and element_type:
                    self.element_definitions[element_name] = {
                        'type': element_type,
                        'element': child
                    }
            
            elif tag.endswith('simpleType'):
                type_name = child.get('name')
                if type_name:
                    self.simple_types[type_name] = child
            
            elif tag.endswith('complexType'):
                type_name = child.get('name')
                if type_name:
                    self.complex_types[type_name] = child
    
    def _find_root_element(self) -> Optional[str]:
        """
        Find the root element in the schema.
        """
        # Look for elements that are not referenced by other elements
        referenced_elements = set()
        
        for element_name, element_info in self.element_definitions.items():
            element_def = element_info['element']
            
            # Check if this element is referenced by other elements
            for other_name, other_info in self.element_definitions.items():
                if other_name != element_name:
                    other_def = other_info['element']
                    # Check if other element contains a reference to this element
                    for child in other_def:
                        if child.tag.endswith('element') and child.get('ref') == element_name:
                            referenced_elements.add(element_name)
                            break
        
        # Return the first unreferenced element
        for element_name in self.element_definitions:
            if element_name not in referenced_elements:
                return element_name
        
        # If all elements are referenced, return the first one
        if self.element_definitions:
            return list(self.element_definitions.keys())[0]
        
        return None
    
    def _generate_xml_example(self, root_element_name: str) -> str:
        """
        Generate XML example starting from root element.
        """
        # Create root element
        root_element = ET.Element(root_element_name)
        
        # Generate content for root element
        self._generate_element_content(root_element, root_element_name)
        
        # Convert to string with proper formatting
        return self._element_to_string(root_element)
    
    def _generate_element_content(self, element: ET.Element, element_name: str):
        """
        Recursively generate content for an element.
        """
        # Get element definition
        element_def = self.element_definitions.get(element_name)
        if not element_def:
            # If no definition found, add some basic content
            element.text = self._generate_sample_value("string")
            return
        
        element_type = element_def['type']
        
        # Handle different type scenarios
        if element_type.startswith('xs:'):
            # Built-in XSD type
            xsd_type = element_type.split(':')[1]
            element.text = self._generate_sample_value(xsd_type)
        
        elif element_type.startswith('tns:'):
            # Custom type in target namespace
            type_name = element_type.split(':')[1]
            self._generate_custom_type_content(element, type_name)
        
        else:
            # Other custom type
            self._generate_custom_type_content(element, element_type)
    
    def _generate_custom_type_content(self, element: ET.Element, type_name: str):
        """
        Generate content for custom types.
        """
        # Check if it's a simple type
        if type_name in self.simple_types:
            simple_type = self.simple_types[type_name]
            base_type = self._get_simple_type_base(simple_type)
            element.text = self._generate_sample_value(base_type)
            return
        
        # Check if it's a complex type
        if type_name in self.complex_types:
            complex_type = self.complex_types[type_name]
            self._generate_complex_type_content(element, complex_type)
            return
        
        # Fallback to string
        element.text = self._generate_sample_value("string")
    
    def _get_simple_type_base(self, simple_type: ET.Element) -> str:
        """
        Get the base type of a simple type.
        """
        for child in simple_type:
            if child.tag.endswith('restriction'):
                base_type = child.get('base')
                if base_type:
                    if base_type.startswith('xs:'):
                        return base_type.split(':')[1]
                    return base_type
        return "string"
    
    def _generate_complex_type_content(self, element: ET.Element, complex_type: ET.Element):
        """
        Generate content for complex types.
        """
        for child in complex_type:
            tag = child.tag
            
            if tag.endswith('sequence'):
                self._generate_sequence_content(element, child)
            
            elif tag.endswith('choice'):
                self._generate_choice_content(element, child)
            
            elif tag.endswith('all'):
                self._generate_all_content(element, child)
            
            elif tag.endswith('simpleContent'):
                self._generate_simple_content(element, child)
    
    def _generate_sequence_content(self, element: ET.Element, sequence: ET.Element):
        """
        Generate content for sequence elements.
        """
        for child in sequence:
            if child.tag.endswith('element'):
                child_name = child.get('name')
                child_type = child.get('type')
                
                if child_name:
                    child_element = ET.SubElement(element, child_name)
                    
                    if child_type:
                        if child_type.startswith('xs:'):
                            xsd_type = child_type.split(':')[1]
                            child_element.text = self._generate_sample_value(xsd_type)
                        else:
                            self._generate_element_content(child_element, child_name)
                    else:
                        # No type specified, use string
                        child_element.text = self._generate_sample_value("string")
    
    def _generate_choice_content(self, element: ET.Element, choice: ET.Element):
        """
        Generate content for choice elements (pick first option).
        """
        for child in choice:
            if child.tag.endswith('element'):
                child_name = child.get('name')
                if child_name:
                    child_element = ET.SubElement(element, child_name)
                    child_element.text = self._generate_sample_value("string")
                    break  # Only generate first choice
    
    def _generate_all_content(self, element: ET.Element, all_elem: ET.Element):
        """
        Generate content for all elements.
        """
        for child in all_elem:
            if child.tag.endswith('element'):
                child_name = child.get('name')
                if child_name:
                    child_element = ET.SubElement(element, child_name)
                    child_element.text = self._generate_sample_value("string")
    
    def _generate_simple_content(self, element: ET.Element, simple_content: ET.Element):
        """
        Generate content for simple content elements.
        """
        for child in simple_content:
            if child.tag.endswith('extension'):
                base_type = child.get('base')
                if base_type and base_type.startswith('xs:'):
                    xsd_type = base_type.split(':')[1]
                    element.text = self._generate_sample_value(xsd_type)
                else:
                    element.text = self._generate_sample_value("string")
    
    def _generate_sample_value(self, xsd_type: str) -> str:
        """
        Generate sample values for XSD types.
        """
        if xsd_type == "string":
            return "Sample String"
        elif xsd_type == "integer":
            return str(random.randint(1, 1000))
        elif xsd_type == "decimal":
            return f"{random.uniform(1.0, 100.0):.2f}"
        elif xsd_type == "boolean":
            return random.choice(["true", "false"])
        elif xsd_type == "date":
            return "2024-01-15"
        elif xsd_type == "dateTime":
            return "2024-01-15T10:30:00"
        elif xsd_type == "time":
            return "10:30:00"
        elif xsd_type == "anyURI":
            return "https://example.com"
        elif xsd_type == "email":
            return "user@example.com"
        else:
            return "Sample Value"
    
    def _element_to_string(self, element: ET.Element) -> str:
        """
        Convert element to properly formatted string.
        """
        # Create a temporary root to get proper formatting
        temp_root = ET.Element("temp")
        temp_root.append(element)
        
        # Convert to string
        xml_str = ET.tostring(temp_root, encoding='unicode')
        
        # Extract the child element (remove temp wrapper)
        start_tag = f"<{element.tag}"
        end_tag = f"</{element.tag}>"
        
        start_pos = xml_str.find(start_tag)
        end_pos = xml_str.rfind(end_tag) + len(end_tag)
        
        return xml_str[start_pos:end_pos]
    
    def validate_xml(self, xml_content: str) -> bool:
        """
        Basic validation of generated XML.
        """
        try:
            ET.fromstring(xml_content)
            return True
        except ET.ParseError:
            return False
    
    def get_example_statistics(self, xml_content: str) -> Dict[str, int]:
        """
        Get statistics about a generated XML example.
        """
        try:
            root = ET.fromstring(xml_content)
            stats = {
                'total_elements': 0,
                'attributes': 0,
                'text_elements': 0,
                'max_depth': 0
            }
            
            self._analyze_xml_example(root, stats, 0)
            return stats
        except ET.ParseError:
            return {
                'total_elements': 0,
                'attributes': 0,
                'text_elements': 0,
                'max_depth': 0
            }
    
    def _analyze_xml_example(self, element: ET.Element, stats: Dict[str, int], depth: int):
        """
        Recursively analyze XML example for statistics.
        """
        stats['max_depth'] = max(stats['max_depth'], depth)
        stats['total_elements'] += 1
        stats['attributes'] += len(element.attrib)
        
        if element.text and element.text.strip():
            stats['text_elements'] += 1
        
        for child in element:
            self._analyze_xml_example(child, stats, depth + 1) 