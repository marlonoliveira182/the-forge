"""
Enhanced Schema Processor for The Forge v2.0.0
Processes XSD and JSON Schema files with exact field name preservation
"""

import xml.etree.ElementTree as ET
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SchemaField:
    """Represents a field in a schema with exact name preservation"""
    path: str
    name: str
    type: str
    description: str
    cardinality: str
    required: bool
    parent_path: str
    is_array: bool
    is_complex: bool
    constraints: Dict[str, Any]
    metadata: Dict[str, Any]

class SchemaProcessor:
    """Enhanced schema processor that preserves exact field names and structures"""
    
    def __init__(self):
        self.namespace_map = {}
        self.complex_types = {}
        self.simple_types = {}
    
    def extract_fields_from_xsd(self, xsd_path: str) -> List[SchemaField]:
        """Extract fields from XSD file with exact name preservation (no global type flattening, only true hierarchy)"""
        try:
            tree = ET.parse(xsd_path)
            root = tree.getroot()
            self._extract_namespaces(root)
            self._extract_types(root)
            visited = set()
            fields = []
            # Only process direct <xs:element> children of <xs:schema> as roots
            for element in root.findall('xs:element', self.namespace_map):
                fields.extend(self._process_element(element, parent_path="", root=root, visited=visited))
            # Debug: print all field paths
            print("[DEBUG] Extracted field paths:")
            for f in fields:
                print(f"  path={f.path}, name={f.name}, type={f.type}, parent_path={f.parent_path}")
            return fields
        except Exception as e:
            print(f"[ERROR] Failed to extract fields from XSD: {e}")
            return []
    
    def extract_fields_from_json_schema(self, json_path: str) -> List[SchemaField]:
        """Extract fields from JSON Schema file with exact name preservation"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
            
            fields = []
            if 'properties' in schema_data:
                fields = self._process_json_properties(schema_data['properties'], "", schema_data)
            
            return fields
            
        except Exception as e:
            raise Exception(f"Error processing JSON Schema file: {str(e)}")
    
    def _extract_namespaces(self, root: ET.Element):
        """Extract namespace information from XSD root"""
        # Initialize with default XSD namespace
        self.namespace_map = {'xs': 'http://www.w3.org/2001/XMLSchema'}
        
        # Extract namespace declarations from attributes
        for key, value in root.attrib.items():
            if key.startswith('xmlns:'):
                prefix = key.split(':')[1]
                self.namespace_map[prefix] = value
            elif key == 'xmlns':
                # Default namespace
                self.namespace_map[''] = value
        
        # Also check for namespace declarations in the root element
        for key, value in root.attrib.items():
            if key == 'xmlns:xs':
                self.namespace_map['xs'] = value
            elif key == 'xmlns':
                # This is the default namespace
                pass
        
        print(f"  [DEBUG] Namespace map: {self.namespace_map}")
    
    def _extract_types(self, root: ET.Element):
        """Extract complex and simple type definitions"""
        try:
            # Extract complex types
            for complex_type in root.findall('.//xs:complexType', self.namespace_map):
                name = complex_type.get('name')
                if name:
                    self.complex_types[name] = complex_type
            
            # Extract simple types
            for simple_type in root.findall('.//xs:simpleType', self.namespace_map):
                name = simple_type.get('name')
                if name:
                    self.simple_types[name] = simple_type
        except Exception as e:
            print(f"  [WARNING] Error extracting types: {e}")
            # Continue without type extraction
    
    def _is_root_element(self, element: ET.Element) -> bool:
        """No longer used: root elements are now detected as direct children of root <xs:schema>."""
        return True
    
    def _process_element(self, element: ET.Element, parent_path: str, root: ET.Element, visited=None) -> List[SchemaField]:
        """Process an XSD element and extract field information, expanding referenced complex types as children"""
        if visited is None:
            visited = set()
        fields = []
        element_name = element.get('name', '')
        element_type = element.get('type', '')
        if not element_name:
            return fields
        field_path = f"{parent_path}.{element_name}" if parent_path else element_name
        if element_type:
            print(f"[DEBUG] Processing element: {element_name}, type: {element_type}")
            print(f"[DEBUG] Available complex_types: {list(self.complex_types.keys())}")
        # If the element has a type attribute and it's a named complex type, expand its children
        if element_type and element_type in self.complex_types:
            # Prevent infinite recursion
            visit_key = (field_path, element_type)
            if visit_key in visited:
                return fields
            visited.add(visit_key)
            # Create the parent field
            field = SchemaField(
                name=element_name,
                type=element_type,
                path=field_path,
                parent_path=parent_path,
                is_complex=True,
                is_array=element.get('maxOccurs', '1') not in ('1', '0', None),
                description=element.findtext('xs:annotation/xs:documentation', default='', namespaces=self.namespace_map),
                cardinality=element.get('maxOccurs', '1'),
                required=element.get('minOccurs', '1') != '0',
                constraints={},
                metadata={}
            )
            fields.append(field)
            # Debug: print the XML structure of the complex type being expanded
            import xml.etree.ElementTree as ET
            print(f"[DEBUG] Expanding complex type {element_type}:")
            print(ET.tostring(self.complex_types[element_type], encoding='unicode'))
            # Recursively process children inside xs:sequence, xs:all, xs:choice
            for container_tag in ['xs:sequence', 'xs:all', 'xs:choice']:
                for container in self.complex_types[element_type].findall(container_tag, self.namespace_map):
                    for child in container.findall('xs:element', self.namespace_map):
                        fields.extend(self._process_element(child, field_path, root, visited))
            return fields
        # Otherwise, process as a simple or inline complex element
        is_complex = any(child.tag.endswith('complexType') for child in element)
        field = SchemaField(
            name=element_name,
            type=element_type or element.get('type', 'string'),
            path=field_path,
            parent_path=parent_path,
            is_complex=is_complex,
            is_array=element.get('maxOccurs', '1') not in ('1', '0', None),
            description=element.findtext('xs:annotation/xs:documentation', default='', namespaces=self.namespace_map),
            cardinality=element.get('maxOccurs', '1'),
            required=element.get('minOccurs', '1') != '0',
            constraints=self._extract_constraints(element),
            metadata={}
        )
        print(f"[DEBUG] Field: {field.path}, Constraints: {field.constraints}")
        fields.append(field)
        # If inline complexType, process its children
        for child in element.findall('.//xs:element', self.namespace_map):
            fields.extend(self._process_element(child, field_path, root, visited))
        return fields
    
    def _determine_field_type(self, element: ET.Element, element_type: str, root: ET.Element) -> str:
        """Determine the field type with exact preservation"""
        if element_type:
            # Remove namespace prefix if present
            if ':' in element_type:
                element_type = element_type.split(':')[-1]
            return element_type
        
        # Check for inline type definition
        for child in element:
            if 'simpleType' in child.tag:
                return 'string'  # Default for simple types
            elif 'complexType' in child.tag:
                return 'complex'
        
        return 'string'  # Default type
    
    def _determine_cardinality(self, element: ET.Element) -> str:
        """Determine field cardinality"""
        if element is None or not hasattr(element, 'get'):
            print("[WARNING] _determine_cardinality called with invalid element; returning '1'")
            return '1'
        min_occurs = element.get('minOccurs', '1')
        max_occurs = element.get('maxOccurs', '1')
        
        if max_occurs == 'unbounded':
            if min_occurs == '0':
                return '0..*'
            else:
                return '1..*'
        elif min_occurs == '0' and max_occurs == '1':
            return '0..1'
        elif min_occurs == '1' and max_occurs == '1':
            return '1'
        else:
            return f"{min_occurs}..{max_occurs}"
    
    def _is_complex_type(self, element: ET.Element, element_type: str, root: ET.Element) -> bool:
        """Check if element is a complex type"""
        if element_type:
            # Check if type is complex
            if element_type in self.complex_types:
                return True
            # Check for common complex types
            if element_type in ['complexType', 'object', 'array']:
                return True
        
        # Check for inline complex type
        for child in element:
            if 'complexType' in child.tag:
                return True
        
        return False
    
    def _extract_constraints(self, element: ET.Element) -> Dict[str, Any]:
        """Extract field constraints"""
        constraints = {}
        
        try:
            # Extract pattern constraints
            for pattern in element.findall('.//xs:pattern', self.namespace_map):
                constraints['pattern'] = pattern.get('value', '')
            
            # Extract length constraints
            for length in element.findall('.//xs:length', self.namespace_map):
                constraints['length'] = length.get('value', '')
            
            # Extract min/max length
            for min_length in element.findall('.//xs:minLength', self.namespace_map):
                constraints['minLength'] = min_length.get('value', '')
            
            for max_length in element.findall('.//xs:maxLength', self.namespace_map):
                constraints['maxLength'] = max_length.get('value', '')
            
            # Extract enumeration
            enum_values = []
            for enum in element.findall('.//xs:enumeration', self.namespace_map):
                enum_values.append(enum.get('value', ''))
            if enum_values:
                constraints['enumeration'] = enum_values
        except Exception as e:
            print(f"  [WARNING] Error extracting constraints: {e}")
        
        return constraints
    
    def _extract_metadata(self, element: ET.Element) -> Dict[str, Any]:
        """Extract field metadata"""
        metadata = {}
        
        try:
            # Extract documentation
            for doc in element.findall('.//xs:documentation', self.namespace_map):
                metadata['documentation'] = doc.text or ''
            
            # Extract annotations
            for annotation in element.findall('.//xs:annotation', self.namespace_map):
                metadata['annotation'] = annotation.text or ''
            
            # Extract attributes
            for attr in element.findall('.//xs:attribute', self.namespace_map):
                attr_name = attr.get('name', '')
                attr_type = attr.get('type', '')
                if attr_name and attr_type:
                    if 'attributes' not in metadata:
                        metadata['attributes'] = {}
                    metadata['attributes'][attr_name] = attr_type
        except Exception as e:
            print(f"  [WARNING] Error extracting metadata: {e}")
        
        return metadata
    
    def _extract_description(self, element: ET.Element) -> str:
        """Extract field description from documentation"""
        try:
            for doc in element.findall('.//xs:documentation', self.namespace_map):
                if doc.text:
                    return doc.text.strip()
        except Exception as e:
            print(f"  [WARNING] Error extracting description: {e}")
        return ""
    
    def _process_complex_content(self, element: ET.Element, parent_path: str, root: ET.Element, visited=None) -> List[SchemaField]:
        """Process complex content (nested elements), avoiding duplicate expansions"""
        if visited is None:
            visited = set()
        fields = []
        
        try:
            # Process sequence
            for sequence in element.findall('.//xs:sequence', self.namespace_map):
                for child_element in sequence.findall('xs:element', self.namespace_map):
                    child_fields = self._process_element(child_element, parent_path, root, visited)
                    fields.extend(child_fields)
            
            # Process choice
            for choice in element.findall('.//xs:choice', self.namespace_map):
                for child_element in choice.findall('xs:element', self.namespace_map):
                    child_fields = self._process_element(child_element, parent_path, root, visited)
                    fields.extend(child_fields)
            
            # Process all
            for all_elem in element.findall('.//xs:all', self.namespace_map):
                for child_element in all_elem.findall('xs:element', self.namespace_map):
                    child_fields = self._process_element(child_element, parent_path, root, visited)
                    fields.extend(child_fields)
        except Exception as e:
            print(f"  [WARNING] Error processing complex content: {e}")
        
        return fields
    
    def _process_json_properties(self, properties: Dict[str, Any], parent_path: str, schema: Dict[str, Any]) -> List[SchemaField]:
        """Process JSON Schema properties with exact name preservation"""
        fields = []
        
        for prop_name, prop_data in properties.items():
            # Build field path
            field_path = f"{parent_path}.{prop_name}" if parent_path else prop_name
            
            # Determine field type
            field_type = self._determine_json_field_type(prop_data)
            
            # Determine cardinality
            cardinality = self._determine_json_cardinality(prop_data)
            
            # Check if required
            required = prop_name in schema.get('required', [])
            
            # Check if array
            is_array = field_type == 'array'
            
            # Check if complex
            is_complex = self._is_json_complex_type(prop_data)
            
            # Extract constraints
            constraints = self._extract_json_constraints(prop_data)
            
            # Extract metadata
            metadata = self._extract_json_metadata(prop_data)
            
            # Create field
            field = SchemaField(
                path=field_path,
                name=prop_name,  # Preserve exact name
                            type=field_type,
                description=prop_data.get('description', ''),
                            cardinality=cardinality,
                required=required,
                parent_path=parent_path,
                is_array=is_array,
                is_complex=is_complex,
                constraints=constraints,
                metadata=metadata
            )
            
            fields.append(field)
            
            # Process nested properties if complex
            if is_complex and 'properties' in prop_data:
                nested_fields = self._process_json_properties(prop_data['properties'], field_path, prop_data)
                fields.extend(nested_fields)
            
            # Process array items if array
            if is_array and 'items' in prop_data:
                if isinstance(prop_data['items'], dict) and 'properties' in prop_data['items']:
                    nested_fields = self._process_json_properties(prop_data['items']['properties'], field_path, prop_data['items'])
                    fields.extend(nested_fields)
        
        return fields
    
    def _determine_json_field_type(self, prop_data: Dict[str, Any]) -> str:
        """Determine JSON Schema field type"""
        if 'type' in prop_data:
            return prop_data['type']
        elif 'oneOf' in prop_data or 'anyOf' in prop_data:
            return 'union'
        elif 'properties' in prop_data:
            return 'object'
        else:
            return 'string'  # Default type
    
    def _determine_json_cardinality(self, prop_data: Dict[str, Any]) -> str:
        """Determine JSON Schema field cardinality"""
        if prop_data.get('type') == 'array':
            return '0..*'  # Arrays are typically unbounded
        else:
            return '1'  # Default cardinality
    
    def _is_json_complex_type(self, prop_data: Dict[str, Any]) -> bool:
        """Check if JSON Schema field is complex"""
        return prop_data.get('type') in ['object', 'array'] or 'properties' in prop_data
    
    def _extract_json_constraints(self, prop_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract JSON Schema field constraints"""
        constraints = {}
        
        # Extract pattern
        if 'pattern' in prop_data:
            constraints['pattern'] = prop_data['pattern']
        
        # Extract min/max length
        if 'minLength' in prop_data:
            constraints['minLength'] = prop_data['minLength']
        
        if 'maxLength' in prop_data:
            constraints['maxLength'] = prop_data['maxLength']
        
        # Extract min/max value
        if 'minimum' in prop_data:
            constraints['minimum'] = prop_data['minimum']
        
        if 'maximum' in prop_data:
            constraints['maximum'] = prop_data['maximum']
        
        # Extract enumeration
        if 'enum' in prop_data:
            constraints['enumeration'] = prop_data['enum']
        
        # Extract format
        if 'format' in prop_data:
            constraints['format'] = prop_data['format']
        
        return constraints
    
    def _extract_json_metadata(self, prop_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract JSON Schema field metadata"""
        metadata = {}
        
        # Extract title
        if 'title' in prop_data:
            metadata['title'] = prop_data['title']
        
        # Extract examples
        if 'examples' in prop_data:
            metadata['examples'] = prop_data['examples']
        
        # Extract default value
        if 'default' in prop_data:
            metadata['default'] = prop_data['default']
        
        # Extract additional properties
        if 'additionalProperties' in prop_data:
            metadata['additionalProperties'] = prop_data['additionalProperties']
        
        return metadata 