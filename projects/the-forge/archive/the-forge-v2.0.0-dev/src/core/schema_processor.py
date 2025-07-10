"""
Schema Processor Module

Handles parsing and processing of different schema formats:
- XSD (XML Schema Definition)
- JSON Schema
- XML examples
- JSON examples

Provides unified interface for extracting field information and paths.
"""

import os
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class SchemaType(Enum):
    """Supported schema types."""
    XSD = "xsd"
    JSON_SCHEMA = "json_schema"
    JSON_EXAMPLE = "json_example"
    XML_EXAMPLE = "xml_example"


@dataclass
class SchemaField:
    """Represents a field in a schema with all its metadata."""
    name: str
    path: str
    type: str
    cardinality: str
    description: str = ""
    details: str = ""
    gdpr: str = ""
    required: bool = False
    level: int = 0
    parent: Optional[str] = None


class SchemaProcessor:
    """
    Handles parsing and processing of different schema formats.
    
    Provides unified interface for extracting field information and paths
    from XSD, JSON Schema, XML, and JSON files.
    """
    
    def __init__(self):
        self.supported_extensions = {'.xsd', '.xml', '.json'}
        self.namespace = {'xs': 'http://www.w3.org/2001/XMLSchema'}
    
    def detect_schema_type(self, file_path: str) -> Optional[SchemaType]:
        """
        Detect the type of schema file based on extension and content.
        
        Args:
            file_path: Path to the schema file
            
        Returns:
            SchemaType or None if not supported
        """
        if not os.path.exists(file_path):
            return None
            
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in {'.xsd', '.xml'}:
            return SchemaType.XSD
        elif ext == '.json':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and ('$schema' in data or 'properties' in data):
                        return SchemaType.JSON_SCHEMA
                    else:
                        return SchemaType.JSON_EXAMPLE
            except (json.JSONDecodeError, UnicodeDecodeError):
                return None
        
        return None
    
    def process_schema(self, file_path: str) -> Tuple[List[str], List[List[str]]]:
        """
        Process a schema file and return headers and rows for Excel.
        
        Args:
            file_path: Path to the schema file
            
        Returns:
            Tuple of (headers, rows) for Excel generation
            
        Raises:
            ValueError: If file type is not supported
        """
        schema_type = self.detect_schema_type(file_path)
        
        if schema_type == SchemaType.XSD:
            return self._process_xsd(file_path)
        elif schema_type == SchemaType.JSON_SCHEMA:
            return self._process_json_schema(file_path)
        elif schema_type == SchemaType.JSON_EXAMPLE:
            return self._process_json_example(file_path)
        elif schema_type == SchemaType.XML_EXAMPLE:
            return self._process_xml_example(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
    
    def _process_xsd(self, file_path: str) -> Tuple[List[str], List[List[str]]]:
        """Process XSD file and extract field information."""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Build complex type definitions
        complex_types = {
            ct.get('name'): ct for ct in root.findall('xs:complexType', self.namespace)
        }
        
        fields = []
        max_depth = 0
        
        def walk_element(element, path: List[str], level: int = 0):
            nonlocal max_depth
            
            name = element.get('name', '')
            typ = element.get('type', '')
            min_occurs = element.get('minOccurs', '1')
            max_occurs = element.get('maxOccurs', '1')
            cardinality = f"{min_occurs}..{max_occurs}" if min_occurs != max_occurs else min_occurs
            
            # Extract description from annotation
            description = ""
            annotation = element.find('xs:annotation/xs:documentation', self.namespace)
            if annotation is not None and annotation.text:
                description = annotation.text.strip()
            
            # Determine real type and details
            real_type, details = self._extract_xsd_type_info(element, root, complex_types)
            
            # Build path
            new_path = path + [name]
            path_str = '.'.join(new_path)
            
            if level > max_depth:
                max_depth = level
            
            field = SchemaField(
                name=name,
                path=path_str,
                type=real_type,
                cardinality=cardinality,
                description=description,
                details=details,
                level=level,
                parent='.'.join(path) if path else None
            )
            fields.append(field)
            
            # Process nested elements
            if typ in complex_types:
                self._walk_complex_type(complex_types[typ], new_path, level + 1)
            
            complex_type = element.find('xs:complexType', self.namespace)
            if complex_type is not None:
                self._walk_complex_type(complex_type, new_path, level + 1)
        
        def walk_complex_type(complex_type, path: List[str], level: int = 0):
            sequence = complex_type.find('xs:sequence', self.namespace)
            if sequence is not None:
                for child in sequence.findall('xs:element', self.namespace):
                    walk_element(child, path, level)
        
        # Process all root elements
        for element in root.findall('xs:element', self.namespace):
            walk_element(element, [], 0)
        
        # Convert to Excel format
        headers = [f'Element Level {i+1}' for i in range(max_depth + 1)]
        headers.extend(['Request Parameter', 'GDPR', 'Cardinality', 'Type', 'Details', 'Description'])
        
        rows = self._convert_fields_to_rows(fields, max_depth + 1)
        
        return headers, rows
    
    def _extract_xsd_type_info(self, element, root, complex_types) -> Tuple[str, str]:
        """Extract type information and restrictions from XSD element."""
        typ = element.get('type', '')
        real_type = typ
        details = ""
        
        # Check for inline simpleType
        simple_type = element.find('xs:simpleType', self.namespace)
        if simple_type is not None:
            restriction = simple_type.find('xs:restriction', self.namespace)
            if restriction is not None:
                base = restriction.get('base')
                if base:
                    real_type = base
                details = self._extract_restriction_details(restriction)
        
        # Check for referenced simpleType
        if not details and typ:
            simple_types = {
                st.get('name'): st for st in root.findall('xs:simpleType', self.namespace)
            }
            if typ in simple_types:
                restriction = simple_types[typ].find('xs:restriction', self.namespace)
                if restriction is not None:
                    base = restriction.get('base')
                    if base:
                        real_type = base
                    details = self._extract_restriction_details(restriction)
        
        # Handle complex types
        if typ in complex_types or element.find('xs:complexType', self.namespace) is not None:
            if not real_type or real_type == typ:
                real_type = 'object'
        
        return real_type, details
    
    def _extract_restriction_details(self, restriction) -> str:
        """Extract restriction details from XSD restriction element."""
        details = []
        for r in restriction:
            tag = r.tag.split('}')[-1]
            val = r.get('value')
            if val is not None:
                details.append(f'{tag}="{val}"')
        return '; '.join(details)
    
    def _walk_complex_type(self, complex_type, path: List[str], level: int):
        """Walk through complex type elements."""
        sequence = complex_type.find('xs:sequence', self.namespace)
        if sequence is not None:
            for child in sequence.findall('xs:element', self.namespace):
                self._walk_element(child, path, level)
    
    def _walk_element(self, element, path: List[str], level: int):
        """Walk through element and extract field information."""
        # This method would be similar to walk_element in _process_xsd
        # but adapted for the modular structure
        pass
    
    def _process_json_schema(self, file_path: str) -> Tuple[List[str], List[List[str]]]:
        """Process JSON Schema file and extract field information."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        fields = self._extract_json_schema_fields(data)
        headers = ['Element', 'Request Parameter', 'GDPR', 'Cardinality', 'Type', 'Details', 'Description']
        rows = self._convert_json_fields_to_rows(fields)
        
        return headers, rows
    
    def _extract_json_schema_fields(self, data: Dict, parent: str = '', level: int = 0) -> List[SchemaField]:
        """Extract fields from JSON Schema data."""
        fields = []
        required = set(data.get('required', []))
        properties = data.get('properties', {})
        
        for name, prop in properties.items():
            element_name = ('    ' * level) + name
            cardinality = '1' if name in required else '0..1'
            typ = prop.get('type', '')
            
            details = ""
            if 'enum' in prop:
                details = f"enum: {prop['enum']}"
            elif 'pattern' in prop:
                details = f"pattern: {prop['pattern']}"
            
            description = prop.get('description', '')
            
            field = SchemaField(
                name=name,
                path=f"{parent}.{name}" if parent else name,
                type=typ,
                cardinality=cardinality,
                description=description,
                details=details,
                required=name in required,
                level=level,
                parent=parent
            )
            fields.append(field)
            
            # Process nested objects
            if typ == 'object':
                nested_fields = self._extract_json_schema_fields(
                    prop, f"{parent}.{name}" if parent else name, level + 1
                )
                fields.extend(nested_fields)
            
            # Process arrays
            if typ == 'array' and 'items' in prop:
                item_type = prop['items'].get('type', '')
                array_field = SchemaField(
                    name='[item]',
                    path=f"{parent}.{name}[item]" if parent else f"{name}[item]",
                    type=item_type,
                    cardinality='0..*',
                    level=level + 1,
                    parent=f"{parent}.{name}" if parent else name
                )
                fields.append(array_field)
                
                if item_type == 'object':
                    nested_fields = self._extract_json_schema_fields(
                        prop['items'], 
                        f"{parent}.{name}[item]" if parent else f"{name}[item]", 
                        level + 2
                    )
                    fields.extend(nested_fields)
        
        return fields
    
    def _process_json_example(self, file_path: str) -> Tuple[List[str], List[List[str]]]:
        """Process JSON example file and extract field information."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        fields = self._extract_json_example_fields(data)
        headers = ['Element', 'Request Parameter', 'GDPR', 'Cardinality', 'Type', 'Details', 'Description']
        rows = self._convert_json_fields_to_rows(fields)
        
        return headers, rows
    
    def _extract_json_example_fields(self, data: Any, parent: str = '', level: int = 0) -> List[SchemaField]:
        """Extract fields from JSON example data."""
        fields = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                element_name = ('    ' * level) + key
                typ = type(value).__name__
                
                field = SchemaField(
                    name=key,
                    path=f"{parent}.{key}" if parent else key,
                    type=typ,
                    cardinality='',
                    level=level,
                    parent=parent
                )
                fields.append(field)
                
                # Recursively process nested structures
                nested_fields = self._extract_json_example_fields(
                    value, f"{parent}.{key}" if parent else key, level + 1
                )
                fields.extend(nested_fields)
        
        elif isinstance(data, list):
            element_name = ('    ' * level) + '[item]'
            field = SchemaField(
                name='[item]',
                path=f"{parent}[item]" if parent else '[item]',
                type='array',
                cardinality='',
                level=level,
                parent=parent
            )
            fields.append(field)
            
            if data:
                nested_fields = self._extract_json_example_fields(
                    data[0], f"{parent}[item]" if parent else '[item]', level + 1
                )
                fields.extend(nested_fields)
        
        return fields
    
    def _process_xml_example(self, file_path: str) -> Tuple[List[str], List[List[str]]]:
        """Process XML example file and extract field information."""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        fields = self._extract_xml_fields(root)
        headers = ['Element', 'Request Parameter', 'GDPR', 'Cardinality', 'Type', 'Details', 'Description']
        rows = self._convert_json_fields_to_rows(fields)
        
        return headers, rows
    
    def _extract_xml_fields(self, element, parent: str = '', level: int = 0) -> List[SchemaField]:
        """Extract fields from XML element."""
        fields = []
        
        name = element.tag
        typ = 'object' if list(element) else 'string'
        element_name = ('    ' * level) + name
        
        field = SchemaField(
            name=name,
            path=f"{parent}.{name}" if parent else name,
            type=typ,
            cardinality='',
            level=level,
            parent=parent
        )
        fields.append(field)
        
        # Process child elements
        for child in element:
            nested_fields = self._extract_xml_fields(
                child, f"{parent}.{name}" if parent else name, level + 1
            )
            fields.extend(nested_fields)
        
        return fields
    
    def _convert_fields_to_rows(self, fields: List[SchemaField], max_levels: int) -> List[List[str]]:
        """Convert SchemaField objects to Excel rows with proper level formatting."""
        rows = []
        prev_cells = [''] * max_levels
        
        for field in fields:
            # Create level cells
            level_cells = [''] * max_levels
            path_parts = field.path.split('.')
            
            for i, part in enumerate(path_parts):
                if i < max_levels:
                    level_cells[i] = part
            
            # Hide repeated values
            for i in range(max_levels):
                if level_cells[i] == prev_cells[i]:
                    level_cells[i] = ''
            
            prev_cells = [lc if lc else pc for lc, pc in zip(level_cells, prev_cells)]
            
            # Create row
            row = level_cells + [
                field.name,
                field.gdpr,
                field.cardinality,
                field.type,
                field.details,
                field.description
            ]
            rows.append(row)
        
        return rows
    
    def _convert_json_fields_to_rows(self, fields: List[SchemaField]) -> List[List[str]]:
        """Convert JSON Schema fields to Excel rows."""
        rows = []
        
        for field in fields:
            row = [
                field.name,
                field.name,  # Request Parameter
                field.gdpr,
                field.cardinality,
                field.type,
                field.details,
                field.description
            ]
            rows.append(row)
        
        return rows
    
    def validate_schema(self, headers: List[str], rows: List[List[str]]) -> List[str]:
        """
        Validate schema data and return list of issues.
        
        Args:
            headers: Column headers
            rows: Data rows
            
        Returns:
            List of validation issues
        """
        issues = []
        name_cols = [i for i, col in enumerate(headers) if col.startswith('Element Level')]
        type_col = headers.index('Type') if 'Type' in headers else -1
        card_col = headers.index('Cardinality') if 'Cardinality' in headers else -1
        
        for idx, row in enumerate(rows, 2):  # 2 = header + 1-based
            # Get field name from last non-empty level column
            name = ''
            for i in reversed(name_cols):
                if i < len(row) and row[i]:
                    name = row[i]
                    break
            
            typ = row[type_col] if type_col >= 0 and type_col < len(row) else ''
            card = row[card_col] if card_col >= 0 and card_col < len(row) else ''
            
            if not name:
                issues.append(f"Row {idx}: Field without name.")
            if not typ:
                issues.append(f"Row {idx}: Field '{name}' without type.")
            if not card:
                issues.append(f"Row {idx}: Field '{name}' without cardinality.")
        
        return issues 