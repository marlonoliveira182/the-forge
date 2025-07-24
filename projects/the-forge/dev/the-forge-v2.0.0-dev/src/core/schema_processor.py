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
try:
    import xmlschema  # type: ignore  # NEW: for robust XSD parsing
except ImportError:
    xmlschema = None  # type: ignore
import jsonschema  # NEW: for robust JSON Schema validation

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
        """Extract fields from XSD file using xmlschema for robust parsing, with robust recursion and debug output."""
        try:
            if xmlschema is None:
                raise ImportError("xmlschema library is not installed.")
            schema = xmlschema.XMLSchema(xsd_path)
            fields = []
            def walk(element, parent_path: str, parent_required: bool = True):
                name = element.name or element.local_name or ""
                field_path = f"{parent_path}.{name}" if parent_path else name
                is_complex = element.type.is_complex() if hasattr(element.type, 'is_complex') else False
                is_array = (getattr(element, 'max_occurs', 1) not in (1, 0, None))
                cardinality = str(getattr(element, 'max_occurs', 1))
                required = getattr(element, 'min_occurs', 1) != 0 and parent_required
                # Constraints
                constraints = {}
                if hasattr(element.type, 'facets'):
                    for facet_name, facet in element.type.facets.items():
                        if facet_name == 'enumeration':
                            constraints['enumeration'] = [v for v in facet.enumeration]
                        elif facet_name == 'pattern':
                            constraints['pattern'] = facet.patterns[0].pattern if facet.patterns else ''
                        elif facet_name in ('minLength', 'maxLength', 'length'):
                            constraints[facet_name] = facet.value
                        elif facet_name in ('fractionDigits', 'totalDigits'):
                            constraints[facet_name] = facet.value
                # Annotations
                description = ""
                metadata = {}
                if element.annotation is not None:
                    # xmlschema's XsdAnnotation has .documentation and .appinfo lists
                    docs = []
                    if hasattr(element.annotation, 'documentation'):
                        docs = [d for d in element.annotation.documentation if hasattr(d, 'text') and d.text] or [d for d in element.annotation.documentation if isinstance(d, str) and d]
                    if docs:
                        description = docs[0].text if hasattr(docs[0], 'text') else str(docs[0])
                        metadata['documentation'] = description
                    # Optionally extract appinfo
                    if hasattr(element.annotation, 'appinfo') and element.annotation.appinfo:
                        metadata['appinfo'] = [a.text if hasattr(a, 'text') else str(a) for a in element.annotation.appinfo if a]
                # Guarantee type safety for all code paths (always run this)
                description = description or ""
                metadata = metadata or {}
                # Compose field
                field = SchemaField(
                    path=field_path,
                    name=name,
                    type=str(element.type.name) if element.type is not None else 'string',
                    description=description,
                    cardinality=cardinality,
                    required=required,
                    parent_path=parent_path,
                    is_array=is_array,
                    is_complex=is_complex,
                    constraints=constraints,
                    metadata=metadata
                )
                fields.append(field)
                print(f"[DEBUG] XSD Field: {field.path} | {field.type} | {field.cardinality} | {field.required} | {field.constraints} | {field.description}")
                # Recurse into children if complex
                if is_complex and hasattr(element.type, 'content') and element.type.content:
                    for child in element.type.content.iter_elements():
                        walk(child, field_path, required)
            # Start from all global elements
            for elem in schema.elements.values():
                walk(elem, "")
            print(f"[DEBUG] Extracted {len(fields)} fields from XSD")
            return fields
        except Exception as e:
            print(f"[ERROR] Failed to extract fields from XSD: {e}")
            return []
    
    def extract_fields_from_json_schema(self, json_path: str) -> List[SchemaField]:
        """Extract fields from JSON Schema file using jsonschema for robust parsing"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
            # Validate schema structure
            jsonschema.Draft7Validator.check_schema(schema_data)
            fields = []
            def walk(properties: dict, parent_path: str, schema: dict):
                if parent_path is None:
                    parent_path = ""
                if schema is None:
                    schema = {}
                for prop_name, prop_data in properties.items():
                    field_path = f"{parent_path}.{prop_name}" if parent_path else prop_name
                    field_type = prop_data.get('type', 'object' if 'properties' in prop_data else 'string')
                    cardinality = '1'
                    required = prop_name in schema.get('required', [])
                    is_array = field_type == 'array'
                    is_complex = field_type in ['object', 'array'] or 'properties' in prop_data
                    constraints = {}
                    if 'pattern' in prop_data:
                        constraints['pattern'] = prop_data['pattern']
                    if 'minLength' in prop_data:
                        constraints['minLength'] = prop_data['minLength']
                    if 'maxLength' in prop_data:
                        constraints['maxLength'] = prop_data['maxLength']
                    if 'minimum' in prop_data:
                        constraints['minimum'] = prop_data['minimum']
                    if 'maximum' in prop_data:
                        constraints['maximum'] = prop_data['maximum']
                    if 'enum' in prop_data:
                        constraints['enumeration'] = prop_data['enum']
                    if 'format' in prop_data:
                        constraints['format'] = prop_data['format']
                    description = prop_data.get('description', '')
                    metadata = {}
                    if 'title' in prop_data:
                        metadata['title'] = prop_data['title']
                    if 'examples' in prop_data:
                        metadata['examples'] = prop_data['examples']
                    if 'default' in prop_data:
                        metadata['default'] = prop_data['default']
                    if 'additionalProperties' in prop_data:
                        metadata['additionalProperties'] = prop_data['additionalProperties']
                    field = SchemaField(
                        path=field_path,
                        name=prop_name,
                        type=field_type,
                        description=description,
                        cardinality=cardinality,
                        required=required,
                        parent_path=parent_path,
                        is_array=is_array,
                        is_complex=is_complex,
                        constraints=constraints,
                        metadata=metadata
                    )
                    fields.append(field)
                    # Recurse into nested properties
                    if is_complex and 'properties' in prop_data:
                        walk(prop_data['properties'], str(field_path), dict(prop_data))
                    if is_array and 'items' in prop_data and isinstance(prop_data['items'], dict) and 'properties' in prop_data['items']:
                        walk(prop_data['items']['properties'], str(field_path), dict(prop_data['items']))
            if 'properties' in schema_data:
                walk(schema_data['properties'], "", schema_data)
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
        
        # Create the field first (whether it's complex or simple)
        is_complex = element_type in self.complex_types if element_type else any(child.tag.endswith('complexType') for child in element)
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
        
        # If the element has a type attribute and it's a named complex type, expand its children
        if element_type and element_type in self.complex_types:
            # Prevent infinite recursion
            visit_key = (field_path, element_type)
            if visit_key in visited:
                return fields
            visited.add(visit_key)
            
            # Debug: print the XML structure of the complex type being expanded
            import xml.etree.ElementTree as ET
            print(f"[DEBUG] Expanding complex type {element_type}:")
            print(ET.tostring(self.complex_types[element_type], encoding='unicode'))
            
            # Recursively process children inside xs:sequence, xs:all, xs:choice
            for container_tag in ['xs:sequence', 'xs:all', 'xs:choice']:
                for container in self.complex_types[element_type].findall(container_tag, self.namespace_map):
                    for child in container.findall('xs:element', self.namespace_map):
                        fields.extend(self._process_element(child, field_path, root, visited))
        
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
        
        if element is None:
            return constraints
        
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
    
    def _determine_json_cardinality(self, prop_data: Dict[str, Any], prop_name: str = None, parent_schema: Dict[str, Any] = None) -> str:
        """Determine JSON Schema field cardinality"""
        if prop_data.get('type') == 'array':
            min_items = prop_data.get('minItems')
            max_items = prop_data.get('maxItems')
            min_str = str(min_items) if min_items is not None else '0'
            max_str = str(max_items) if max_items is not None else '*'
            return f"{min_str}..{max_str}"
        else:
            # For objects/fields, use parent's required list if available
            if prop_name and parent_schema and 'required' in parent_schema:
                return '1' if prop_name in parent_schema['required'] else '0..1'
            return '1'

    def _process_json_properties(self, properties: Dict[str, Any], parent_path: str, schema: Dict[str, Any]) -> List[SchemaField]:
        """Process JSON Schema properties with exact name preservation"""
        fields = []
        for prop_name, prop_data in properties.items():
            field_path = f"{parent_path}.{prop_name}" if parent_path else prop_name
            field_type = self._determine_json_field_type(prop_data)
            # Defensive: ensure prop_name and schema are not None
            safe_prop_name = prop_name if prop_name is not None else ""
            safe_schema = schema if schema is not None else {}
            cardinality = self._determine_json_cardinality(prop_data, safe_prop_name, safe_schema)
            required = prop_name in schema.get('required', [])
            is_array = field_type == 'array'
            is_complex = self._is_json_complex_type(prop_data)
            constraints = self._extract_json_constraints(prop_data)
            metadata = self._extract_json_metadata(prop_data)
            field = SchemaField(
                path=field_path,
                name=prop_name,
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
            if is_complex and 'properties' in prop_data:
                nested_fields = self._process_json_properties(prop_data['properties'], field_path, prop_data)
                fields.extend(nested_fields)
            if is_array and 'items' in prop_data:
                if isinstance(prop_data['items'], dict) and 'properties' in prop_data['items']:
                    nested_fields = self._process_json_properties(prop_data['items']['properties'], field_path, prop_data['items'])
                    fields.extend(nested_fields)
        return fields
    
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

    def _is_json_complex_type(self, prop_data: Dict[str, Any]) -> bool:
        """Check if JSON Schema field is complex"""
        return prop_data.get('type') in ['object', 'array'] or 'properties' in prop_data 