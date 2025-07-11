"""
Schema processor for extracting and analyzing XSD and JSON Schema structures.
"""

import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SchemaField:
    """Represents a field in a schema with its metadata."""
    levels: List[str]
    type: str
    description: str
    cardinality: str
    details: str
    restrictions: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.restrictions is None:
            self.restrictions = {}


class SchemaProcessor:
    """Handles parsing and processing of XSD and JSON Schema files."""
    
    def __init__(self):
        self.xsd_namespace = {'xs': 'http://www.w3.org/2001/XMLSchema'}
    
    def extract_fields_from_json_schema(self, filepath: str) -> List[SchemaField]:
        """Extract fields from a JSON Schema file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        fields = []
        root_props = data.get('properties', {})
        
        if len(root_props) == 1:
            root_name = list(root_props.keys())[0]
            root_obj = data['properties'][root_name]
            root_type = root_obj.get('type', 'object')
            root_desc = root_obj.get('description', '')
            root_card = '1' if root_name in data.get('required', []) else '0..1'
            
            fields.append(SchemaField(
                levels=[root_name],
                type=root_type,
                description=root_desc,
                cardinality=root_card,
                details=''
            ))
            
            self._walk_json_object(root_obj, [root_name], fields)
        else:
            self._walk_json_object(data, [], fields)
        
        return fields
    
    def _walk_json_object(self, obj: Dict, levels: List[str], fields: List[SchemaField]) -> None:
        """Recursively walk through JSON object structure."""
        if isinstance(obj, dict) and obj.get('type') == 'object' and 'properties' in obj:
            required = obj.get('required', [])
            
            for k, v in obj['properties'].items():
                next_levels = levels + [k] if k != levels[0] or levels != [levels[0]] else levels
                typ = v.get('type', '')
                desc = v.get('description', '')
                card = '1' if k in required else '0..1'
                
                if typ == 'array':
                    min_items = v.get('minItems', 0)
                    max_items = v.get('maxItems', 'unbounded' if 'maxItems' not in v else v['maxItems'])
                    card = f"{min_items}..{max_items}"
                
                details = self._extract_json_details(v)
                
                fields.append(SchemaField(
                    levels=next_levels,
                    type=typ,
                    description=desc,
                    cardinality=card,
                    details=details
                ))
                
                # Handle array items
                if typ == 'array' and 'items' in v:
                    item_levels = next_levels + ['[]']
                    if isinstance(v['items'], dict) and v['items'].get('type') == 'object' and 'properties' in v['items']:
                        for item_k, item_v in v['items']['properties'].items():
                            item_typ = item_v.get('type', '')
                            item_desc = item_v.get('description', '')
                            item_card = '0..1'
                            item_details = self._extract_json_details(item_v)
                            
                            fields.append(SchemaField(
                                levels=item_levels + [item_k],
                                type=item_typ,
                                description=item_desc,
                                cardinality=item_card,
                                details=item_details
                            ))
                    
                    self._walk_json_object(v['items'], item_levels, fields)
                elif typ == 'object' and 'properties' in v:
                    self._walk_json_object(v, next_levels, fields)
        elif isinstance(obj, dict) and obj.get('type') in ['string', 'number', 'integer', 'boolean']:
            # Handle individual properties that are not objects
            details = self._extract_json_details(obj)
            # Update the last field's details if it matches the current levels
            if fields and len(fields) > 0:
                last_field = fields[-1]
                if last_field.levels == levels:
                    last_field.details = details
    
    def _extract_json_details(self, obj: Dict) -> str:
        """Extract validation details from JSON Schema object."""
        details = []
        for key in ['enum', 'pattern', 'minLength', 'maxLength', 'minimum', 
                   'maximum', 'exclusiveMinimum', 'exclusiveMaximum', 'format', 'multipleOf']:
            if key in obj:
                details.append(f"{key}: {obj[key]}")
        # Add $comment content without the "$comment:" prefix
        if '$comment' in obj:
            details.append(obj['$comment'])
        return '; '.join(details)
    
    def extract_fields_from_xsd(self, filepath: str, keep_case: bool = False) -> List[SchemaField]:
        """Extract fields from an XSD file."""
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        complex_types = {ct.get('name'): ct for ct in root.findall('xs:complexType', self.xsd_namespace)}
        simple_types = {st.get('name'): st for st in root.findall('xs:simpleType', self.xsd_namespace)}
        
        fields = []
        root_elements = [el.get('name', '') for el in root.findall('xs:element', self.xsd_namespace)]
        
        for element in root.findall('xs:element', self.xsd_namespace):
            self._walk_xsd_element(element, [], fields, complex_types, simple_types, 
                                 root_elements, keep_case, is_root=True)
        
        return fields
    
    def _walk_xsd_element(self, element: ET.Element, levels: List[str], fields: List[SchemaField],
                         complex_types: Dict, simple_types: Dict, root_elements: List[str],
                         keep_case: bool, is_root: bool = False) -> None:
        """Recursively walk through XSD element structure."""
        name = element.get('name', '')
        if not name:
            return
        
        field_name = name if keep_case else self._to_camel_case(name)
        
        if is_root:
            lvls = [field_name]
        else:
            lvls = levels + [field_name]
        
        desc = self._extract_xsd_description(element)
        min_occurs = element.get('minOccurs', '1')
        max_occurs = element.get('maxOccurs', '1')
        
        is_array = (max_occurs == 'unbounded' or (max_occurs.isdigit() and int(max_occurs) > 1))
        if is_array:
            card = f"{min_occurs}..{max_occurs}"
        else:
            card = min_occurs if min_occurs == max_occurs else f"{min_occurs}..{max_occurs}"
        
        if card == '1..1':
            card = '1'
        elif card == '0..1':
            card = '0..1'
        elif card == '0..unbounded':
            card = '0..unbounded'
        
        typ, details, restrictions = self._get_xsd_type_and_details(element, simple_types)
        
        fields.append(SchemaField(
            levels=lvls,
            type=typ,
            description=desc or details,
            cardinality=card,
            details=details,
            restrictions=restrictions
        ))
        
        typ_ref = element.get('type', '')
        complex_type = element.find('xs:complexType', self.xsd_namespace)
        
        # Handle arrays
        if is_array:
            item_levels = lvls + ['item']
            inner_elements = element.findall('xs:element', self.xsd_namespace)
            
            if inner_elements and len(inner_elements) == 1 and inner_elements[0].get('name', '') == name:
                inner = inner_elements[0]
                inner_complex_type = inner.find('xs:complexType', self.xsd_namespace)
                if inner_complex_type is not None:
                    self._walk_complex_type(inner_complex_type, item_levels, fields, complex_types, simple_types, root_elements, keep_case)
            elif inner_elements:
                for inner in inner_elements:
                                     self._walk_xsd_element(inner, item_levels + [inner.get('name', '')], 
                                          fields, complex_types, simple_types, root_elements, 
                                          keep_case)
            else:
                if typ_ref in complex_types:
                    self._walk_complex_type(complex_types[typ_ref], item_levels, fields, complex_types, simple_types, root_elements, keep_case)
                elif complex_type is not None:
                    self._walk_complex_type(complex_type, item_levels, fields, complex_types, simple_types, root_elements, keep_case)
        else:
            if typ_ref in complex_types:
                self._walk_complex_type(complex_types[typ_ref], lvls, fields, complex_types, simple_types, root_elements, keep_case)
            if complex_type is not None:
                self._walk_complex_type(complex_type, lvls, fields, complex_types, simple_types, root_elements, keep_case)
    
    def _walk_complex_type(self, complex_type: ET.Element, levels: List[str], 
                          fields: List[SchemaField], complex_types: Dict, simple_types: Dict, 
                          root_elements: List[str], keep_case: bool = False) -> None:
        """Walk through complex type definitions."""
        sequence = complex_type.find('xs:sequence', self.xsd_namespace)
        if sequence is not None:
            for child in sequence.findall('xs:element', self.xsd_namespace):
                self._walk_xsd_element(child, levels, 
                                     fields, complex_types, simple_types, root_elements, keep_case)
    
    def _extract_xsd_description(self, element: ET.Element) -> str:
        """Extract description from XSD annotation."""
        annotation = element.find('xs:annotation/xs:documentation', self.xsd_namespace)
        if annotation is not None and annotation.text:
            return annotation.text.strip()
        return ''
    
    def _get_xsd_type_and_details(self, element: ET.Element, simple_types: Dict) -> Tuple[str, str, Dict]:
        """Get type information and details from XSD element."""
        typ = element.get('type', '')
        details = ''
        restrictions = {}
        real_type = typ
        
        simple_type = element.find('xs:simpleType', self.xsd_namespace)
        if simple_type is not None:
            restriction = simple_type.find('xs:restriction', self.xsd_namespace)
            if restriction is not None:
                real_type = restriction.get('base', typ)
                details, restrictions = self._extract_xsd_restrictions(restriction)
        elif typ in simple_types:
            restriction = simple_types[typ].find('xs:restriction', self.xsd_namespace)
            if restriction is not None:
                real_type = restriction.get('base', typ)
                details, restrictions = self._extract_xsd_restrictions(restriction)
        elif element.find('xs:complexType', self.xsd_namespace) is not None:
            real_type = 'object'
        
        # Normalize type names
        if real_type in ('xs:int', 'xs:integer', 'int', 'integer'):
            real_type = 'integer'
        elif real_type in ('xs:string', 'string'):
            real_type = 'string'
        elif real_type in ('xs:boolean', 'boolean'):
            real_type = 'boolean'
        elif real_type in ('xs:decimal', 'decimal', 'xs:float', 'float'):
            real_type = 'number'
        
        return real_type, details, restrictions
    
    def _extract_xsd_restrictions(self, restriction: ET.Element) -> Tuple[str, Dict]:
        """Extract restrictions from XSD restriction element."""
        details = []
        restrictions = {}
        
        for r in restriction:
            tag = r.tag.split('}')[-1]
            val = r.get('value')
            if val is not None:
                if tag == 'enumeration':
                    details.append(f'enum: {val}')
                    restrictions.setdefault('enum', []).append(val)
                elif tag == 'fractionDigits':
                    # For XSD files, keep fractionDigits in details
                    details.append(f'fractionDigits: {val}')
                    restrictions[tag] = val
                else:
                    details.append(f'{tag}: {val}')
                    restrictions[tag] = val
        
        return '; '.join(details), restrictions
    
    def _to_camel_case(self, s: str) -> str:
        """Convert string to camelCase."""
        if not s:
            return s
        return s[0].lower() + s[1:]
    
    def extract_paths_from_json_schema(self, filepath: str) -> List[str]:
        """Extract simple paths from JSON Schema."""
        fields = self.extract_fields_from_json_schema(filepath)
        return ['.'.join(f.levels) for f in fields]
    
    def extract_paths_from_xsd(self, filepath: str, keep_case: bool = False) -> List[str]:
        """Extract simple paths from XSD."""
        fields = self.extract_fields_from_xsd(filepath, keep_case)
        return ['.'.join(f.levels) for f in fields] 