"""
Schema converter for converting between XSD and JSON Schema formats.
"""

import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from pathlib import Path


class SchemaConverter:
    """Handles conversion between XSD and JSON Schema formats."""
    
    def __init__(self):
        self.xsd_namespace = {'xs': 'http://www.w3.org/2001/XMLSchema'}
    
    def xsd_to_json_schema(self, xsd_path: str, output_path: str) -> None:
        """Convert XSD to JSON Schema."""
        tree = ET.parse(xsd_path)
        root = tree.getroot()
        
        simple_types = {st.get('name'): st for st in root.findall('xs:simpleType', self.xsd_namespace)}
        complex_types = {ct.get('name'): ct for ct in root.findall('xs:complexType', self.xsd_namespace)}
        
        # Find root element
        root_element = None
        for el in root.findall('xs:element', self.xsd_namespace):
            root_element = el
            break
        
        if root_element is None:
            raise ValueError("No root element found in XSD")
        
        root_name = self._to_camel_case(root_element.get('name', 'Root'))
        root_schema = self._parse_element(root_element, complex_types, simple_types)[1]
        
        # Wrap the root element as a property
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": root_name,
            "type": "object",
            "properties": {
                root_name: root_schema
            },
            "required": [root_name]
        }
        
        # Recursively camelCase all property names
        json_schema = self._camelize_json_schema(json_schema)
        
        # Validate conversion
        self._validate_conversion(root_element, json_schema)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_schema, f, indent=2)
    
    def json_schema_to_xsd(self, json_schema_path: str, output_path: str) -> None:
        """Convert JSON Schema to XSD."""
        with open(json_schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        title = schema.get('title', 'Root')
        root_props = schema.get('properties', {})
        
        # Handle single root property case
        if len(root_props) == 1 and list(root_props.keys())[0].lower() == title.lower():
            root_obj = root_props[list(root_props.keys())[0]]
            xsd_content = self._generate_flat_root_element(title, root_obj)
        else:
            xsd_content = self._generate_xsd_element(title, schema, is_root=True)
        
        xsd = f'<?xml version="1.0" encoding="UTF-8"?>\n<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"><xs:element name="{self._to_pascal_case(title)}">{xsd_content}</xs:element></xs:schema>'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xsd)
    
    def _parse_element(self, element: ET.Element, complex_types: Dict, 
                      simple_types: Dict) -> tuple[str, Dict]:
        """Parse XSD element and return (name, schema)."""
        name = self._to_camel_case(element.get('name', ''))
        typ = element.get('type', '')
        min_occurs = element.get('minOccurs', '1')
        max_occurs = element.get('maxOccurs', '1')
        
        # Extract description
        desc = self._extract_xsd_description(element)
        
        # Handle different element types
        if typ in complex_types:
            schema = self._parse_complex_type(complex_types[typ])
            if desc:
                schema['description'] = desc
        elif element.find('xs:complexType', self.xsd_namespace) is not None:
            schema = self._parse_complex_type(element.find('xs:complexType', self.xsd_namespace))
            if desc:
                schema['description'] = desc
        elif element.find('xs:simpleType', self.xsd_namespace) is not None:
            schema = self._parse_simple_type(element.find('xs:simpleType', self.xsd_namespace))
            if desc:
                schema['description'] = desc
        elif typ in simple_types:
            schema = self._parse_simple_type(simple_types[typ])
            if desc:
                schema['description'] = desc
        else:
            schema = {'type': self._xsd_type_to_json_type(typ)} if typ else {'type': 'string'}
            if desc:
                schema['description'] = desc
        
        # Handle cardinality (arrays)
        is_array = (max_occurs == 'unbounded' or (max_occurs.isdigit() and int(max_occurs) > 1))
        if is_array:
            arr_schema = {'type': 'array', 'items': schema}
            if min_occurs.isdigit() and int(min_occurs) > 0:
                arr_schema['minItems'] = int(min_occurs)
            if max_occurs.isdigit():
                arr_schema['maxItems'] = int(max_occurs)
            if desc and 'description' not in arr_schema['items']:
                arr_schema['description'] = desc
            return name, arr_schema
        else:
            return name, schema
    
    def _parse_complex_type(self, complex_type: ET.Element) -> Dict:
        """Parse XSD complex type."""
        props = {}
        required = []
        sequence = complex_type.find('xs:sequence', self.xsd_namespace)
        
        if sequence is not None:
            for child in sequence.findall('xs:element', self.xsd_namespace):
                child_name, child_schema = self._parse_element(child, {}, {})
                child_name = self._to_camel_case(child_name)
                
                if child_schema.get('type') == 'object' and 'properties' in child_schema:
                    child_schema['properties'] = {self._to_camel_case(k): v for k, v in child_schema['properties'].items()}
                
                props[child_name] = child_schema
                min_occurs = child.get('minOccurs', '1')
                if min_occurs == '1':
                    required.append(child_name)
        
        return_schema = {'type': 'object', 'properties': props}
        if required:
            return_schema['required'] = required
        
        return return_schema
    
    def _parse_simple_type(self, simple_type: ET.Element) -> Dict:
        """Parse XSD simple type."""
        restriction = simple_type.find('xs:restriction', self.xsd_namespace)
        if restriction is None:
            return {'type': 'string'}
        
        base_type = restriction.get('base', 'string')
        prop = {'type': self._xsd_type_to_json_type(base_type)}
        
        # Extract restrictions
        details = self._extract_restrictions(restriction)
        
        if 'enum' in details:
            prop['enum'] = details['enum']
        if 'pattern' in details:
            prop['pattern'] = details['pattern']
        if 'minLength' in details:
            prop['minLength'] = int(details['minLength'])
        if 'maxLength' in details:
            prop['maxLength'] = int(details['maxLength'])
        if 'minInclusive' in details:
            prop['minimum'] = float(details['minInclusive'])
        if 'maxInclusive' in details:
            prop['maximum'] = float(details['maxInclusive'])
        if 'minExclusive' in details:
            prop['exclusiveMinimum'] = float(details['minExclusive'])
        if 'maxExclusive' in details:
            prop['exclusiveMaximum'] = float(details['maxExclusive'])
        if 'fractionDigits' in details:
            try:
                digits = int(details['fractionDigits'])
                prop['multipleOf'] = float(f'1e-{digits}')
            except Exception:
                pass
        
        # Add unsupported restrictions to $comment
        unsupported = []
        for key in ['totalDigits']:  # Remove fractionDigits since it's converted to multipleOf
            if key in details:
                unsupported.append(f"{key}: {details[key]}")
        if unsupported:
            prop['$comment'] = '; '.join(unsupported)
        
        return prop
    
    def _extract_restrictions(self, restriction: ET.Element) -> Dict:
        """Extract restrictions from XSD restriction element."""
        details = {}
        for r in restriction:
            tag = r.tag.split('}')[-1]
            val = r.get('value')
            if val is not None:
                if tag == 'enumeration':
                    details.setdefault('enum', []).append(val)
                else:
                    details[tag] = val
        return details
    
    def _extract_xsd_description(self, element: ET.Element) -> str:
        """Extract description from XSD annotation."""
        annotation = element.find('xs:annotation/xs:documentation', self.xsd_namespace)
        if annotation is not None and annotation.text:
            return annotation.text.strip()
        return ''
    
    def _xsd_type_to_json_type(self, xsd_type: str) -> str:
        """Convert XSD type to JSON Schema type."""
        if xsd_type.endswith(':string') or xsd_type == 'string':
            return 'string'
        elif xsd_type.endswith(':int') or xsd_type == 'int' or xsd_type.endswith(':integer') or xsd_type == 'integer':
            return 'integer'
        elif xsd_type.endswith(':boolean') or xsd_type == 'boolean':
            return 'boolean'
        elif xsd_type.endswith(':decimal') or xsd_type == 'decimal' or xsd_type.endswith(':float') or xsd_type == 'float':
            return 'number'
        else:
            return 'string'
    
    def _to_camel_case(self, s: str) -> str:
        """Convert string to camelCase."""
        if not s:
            return s
        return s[0].lower() + s[1:]
    
    def _to_pascal_case(self, s: str) -> str:
        """Convert string to PascalCase."""
        return s[0].upper() + s[1:] if s else s
    
    def _camelize_json_schema(self, obj: Any) -> Any:
        """Recursively camelCase JSON Schema property names."""
        if isinstance(obj, dict):
            new_obj = {}
            for k, v in obj.items():
                # Keep JSON Schema meta keys as-is
                if k in ('$schema', 'title', 'type', 'required', 'enum', 'pattern', 
                         'minLength', 'maxLength', 'minimum', 'maximum', 'format', 
                         'description', 'allOf', 'anyOf', 'oneOf', 'not', 'default', 
                         'examples', 'items', 'properties'):
                    new_obj[k] = self._camelize_json_schema(v)
                elif k == 'properties' and isinstance(v, dict):
                    new_obj[k] = {self._to_camel_case(pk): self._camelize_json_schema(pv) for pk, pv in v.items()}
                else:
                    new_obj[self._to_camel_case(k)] = self._camelize_json_schema(v)
            return new_obj
        elif isinstance(obj, list):
            return [self._camelize_json_schema(i) for i in obj]
        else:
            return obj
    
    def _validate_conversion(self, root_element: ET.Element, json_schema: Dict) -> None:
        """Validate that all XSD elements are present in JSON Schema."""
        xsd_names = self._collect_xsd_element_names(root_element)
        root_camel = self._to_camel_case(root_element.get('name', ''))
        if root_camel in xsd_names:
            xsd_names.remove(root_camel)
        
        json_names = self._collect_json_schema_property_names(json_schema)
        missing = sorted(xsd_names - json_names)
        
        if missing:
            raise ValueError(f"Missing fields in JSON Schema conversion: {missing}")
    
    def _collect_xsd_element_names(self, element: ET.Element, names: Optional[set] = None) -> set:
        """Collect all XSD element names."""
        if names is None:
            names = set()
        
        name = element.get('name')
        if name:
            names.add(self._to_camel_case(name))
        
        # Check children
        ns_seq = element.find('xs:complexType/xs:sequence', self.xsd_namespace)
        if ns_seq is not None:
            for child in ns_seq.findall('xs:element', self.xsd_namespace):
                self._collect_xsd_element_names(child, names)
        
        seq = element.find('xs:sequence', self.xsd_namespace)
        if seq is not None:
            for child in seq.findall('xs:element', self.xsd_namespace):
                self._collect_xsd_element_names(child, names)
        
        return names
    
    def _collect_json_schema_property_names(self, schema: Any, names: Optional[set] = None) -> set:
        """Collect all property names from JSON Schema."""
        if names is None:
            names = set()
        
        if isinstance(schema, dict):
            for k, v in schema.items():
                if k == 'properties' and isinstance(v, dict):
                    for pk, pv in v.items():
                        names.add(pk)
                        self._collect_json_schema_property_names(pv, names)
                else:
                    self._collect_json_schema_property_names(v, names)
        elif isinstance(schema, list):
            for item in schema:
                self._collect_json_schema_property_names(item, names)
        
        return names
    
    def _generate_flat_root_element(self, title: str, obj: Dict) -> str:
        """Generate flat root element for XSD."""
        annotation = ''
        if 'description' in obj:
            annotation = f'<xs:annotation><xs:documentation>{obj["description"]}</xs:documentation></xs:annotation>'
        
        props = obj.get('properties', {})
        required = obj.get('required', [])
        children = []
        
        for k, v in props.items():
            child = self._generate_xsd_element(k, v, required)
            if child:
                children.append(child)
        
        return f'{annotation}<xs:complexType><xs:sequence>' + ''.join(children) + '</xs:sequence></xs:complexType>'
    
    def _generate_xsd_element(self, name: str, obj: Dict, required_fields: Optional[List] = None, 
                             is_root: bool = False) -> str:
        """Generate XSD element from JSON Schema object."""
        if required_fields is None:
            required_fields = []
        
        t = obj.get('type', 'string')
        restrictions = []
        annotation = ''
        
        if 'description' in obj:
            annotation = f'<xs:annotation><xs:documentation>{obj["description"]}</xs:documentation></xs:annotation>'
        
        if t == 'object':
            props = obj.get('properties', {})
            required = obj.get('required', [])
            children = []
            
            for k, v in props.items():
                child = self._generate_xsd_element(k, v, required)
                if child:
                    children.append(child)
            
            min_occurs = '1' if name in (required_fields or []) else '0'
            
            if is_root:
                return f'{annotation}<xs:complexType><xs:sequence>' + ''.join(children) + '</xs:sequence></xs:complexType>'
            else:
                return f'<xs:element name="{self._to_pascal_case(name)}" minOccurs="{min_occurs}" maxOccurs="1">{annotation}<xs:complexType><xs:sequence>' + ''.join(children) + '</xs:sequence></xs:complexType></xs:element>'
        
        elif t == 'array':
            items = obj.get('items', {})
            min_occurs = '1' if name in (required_fields or []) else '0'
            max_occurs = str(obj.get('maxItems')) if 'maxItems' in obj else 'unbounded'
            inner = self._generate_xsd_element(name, items)
            if not inner:
                return ''
            return f'<xs:element name="{self._to_pascal_case(name)}" minOccurs="{min_occurs}" maxOccurs="{max_occurs}">{annotation}' + inner + '</xs:element>'
        
        elif t == 'string':
            if 'maxLength' in obj:
                restrictions.append(f'<xs:maxLength value="{obj["maxLength"]}"/>')
            if 'minLength' in obj:
                restrictions.append(f'<xs:minLength value="{obj["minLength"]}"/>')
            if 'pattern' in obj:
                restrictions.append(f'<xs:pattern value="{obj["pattern"]}"/>')
            if 'enum' in obj:
                for v in obj['enum']:
                    restrictions.append(f'<xs:enumeration value="{v}"/>')
            restrictions += self._parse_comment_restrictions(obj.get('$comment', ''))
        
        elif t in ('integer', 'number'):
            if 'minimum' in obj:
                restrictions.append(f'<xs:minInclusive value="{obj["minimum"]}"/>')
            if 'maximum' in obj:
                restrictions.append(f'<xs:maxInclusive value="{obj["maximum"]}"/>')
            if 'exclusiveMinimum' in obj:
                restrictions.append(f'<xs:minExclusive value="{obj["exclusiveMinimum"]}"/>')
            if 'exclusiveMaximum' in obj:
                restrictions.append(f'<xs:maxExclusive value="{obj["exclusiveMaximum"]}"/>')
            if 'multipleOf' in obj:
                import decimal
                try:
                    dec = decimal.Decimal(str(obj['multipleOf']))
                    if dec < 1:
                        digits = abs(dec.as_tuple().exponent)
                        restrictions.append(f'<xs:fractionDigits value="{digits}"/>')
                except Exception:
                    pass
            restrictions += self._parse_comment_restrictions(obj.get('$comment', ''))
            if 'enum' in obj:
                for v in obj['enum']:
                    restrictions.append(f'<xs:enumeration value="{v}"/>')
        
        if restrictions:
            base_type = 'xs:string' if t == 'string' else ('xs:int' if t == 'integer' else 'xs:decimal')
            restr = ''.join(restrictions)
            min_occurs = '1' if name in (required_fields or []) else '0'
            return f'<xs:element name="{self._to_pascal_case(name)}" minOccurs="{min_occurs}" maxOccurs="1">{annotation}<xs:simpleType><xs:restriction base="{base_type}">{restr}</xs:restriction></xs:simpleType></xs:element>'
        else:
            min_occurs = '1' if name in (required_fields or []) else '0'
            xsd_type = 'xs:string' if t == 'string' else ('xs:int' if t == 'integer' else ('xs:decimal' if t == 'number' else 'xs:string'))
            return f'<xs:element name="{self._to_pascal_case(name)}" type="{xsd_type}" minOccurs="{min_occurs}" maxOccurs="1">{annotation}</xs:element>'
    
    def _parse_comment_restrictions(self, comment: str) -> List[str]:
        """Parse restrictions from $comment field."""
        import re
        restrictions = []
        if comment:
            m = re.search(r'totalDigits\s*[:=]\s*(\d+)', comment)
            if m:
                restrictions.append(f'<xs:totalDigits value="{m.group(1)}"/>')
            m2 = re.search(r'fractionDigits\s*[:=]\s*(\d+)', comment)
            if m2:
                restrictions.append(f'<xs:fractionDigits value="{m2.group(1)}"/>')
        return restrictions 