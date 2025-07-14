"""
Schema Converter - Converts between XSD and JSON Schema formats
"""

import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from .schema_processor import SchemaField
from collections import OrderedDict

class SchemaConverter:
    """Converts between XSD and JSON Schema formats"""
    
    def __init__(self):
        self.xsd_namespace = {'xs': 'http://www.w3.org/2001/XMLSchema'}
        
        # Type mapping from XSD to JSON Schema
        self.xsd_to_json_types = {
            'xsd:string': 'string',
            'xsd:integer': 'integer',
            'xsd:int': 'integer',
            'xsd:long': 'integer',
            'xsd:short': 'integer',
            'xsd:decimal': 'number',
            'xsd:float': 'number',
            'xsd:double': 'number',
            'xsd:boolean': 'boolean',
            'xsd:date': 'string',
            'xsd:dateTime': 'string',
            'xsd:time': 'string',
            'xsd:base64Binary': 'string',
            'xsd:hexBinary': 'string',
            'xsd:anyURI': 'string',
            'xsd:QName': 'string',
            'xsd:NOTATION': 'string'
        }
        
        # Type mapping from JSON Schema to XSD
        self.json_to_xsd_types = {
            'string': 'xs:string',
            'integer': 'xs:integer',
            'number': 'xs:decimal',
            'boolean': 'xs:boolean',
            'array': 'xs:sequence',
            'object': 'xs:complexType'
        }
    
    def xsd_to_json_schema(self, xsd_path: str, output_path: str) -> bool:
        """Convert XSD to JSON Schema (Draft-07+)"""
        try:
            tree = ET.parse(xsd_path)
            root = tree.getroot()

            # Build a lookup for named complex types
            complex_types = {}
            for ct in root.findall('xs:complexType', self.xsd_namespace):
                name = ct.get('name')
                if name:
                    complex_types[name] = ct

            # Build a lookup for named simple types
            simple_types = {}
            for st in root.findall('xs:simpleType', self.xsd_namespace):
                name = st.get('name')
                if name:
                    simple_types[name] = st

            def to_camel_case(s: str) -> str:
                if not s:
                    return s
                return s[0].lower() + s[1:]

            def convert_xsd_type_to_json(xsd_type: str) -> str:
                if not xsd_type:
                    return 'string'
                if ':' in xsd_type:
                    xsd_type = xsd_type.split(':')[-1]
                return self.xsd_to_json_types.get(f'xsd:{xsd_type}', 'string')

            def extract_constraints(element) -> dict:
                constraints = {}
                
                # Check for direct restrictions
                restriction = element.find('xs:restriction', self.xsd_namespace)
                if restriction is not None:
                    for child in restriction:
                        tag = child.tag.split('}')[-1]
                        value = child.get('value', '')
                        if tag == 'maxLength':
                            constraints['maxLength'] = int(value)
                        elif tag == 'minLength':
                            constraints['minLength'] = int(value)
                        elif tag == 'pattern':
                            constraints['pattern'] = value
                        elif tag == 'enumeration':
                            if 'enum' not in constraints:
                                constraints['enum'] = []
                            constraints['enum'].append(value)
                        elif tag == 'fractionDigits':
                            fraction = int(value)
                            constraints['multipleOf'] = 1.0 / (10 ** fraction)
                        elif tag == 'totalDigits':
                            constraints['maxLength'] = int(value)
                        elif tag == 'minInclusive':
                            constraints['minimum'] = float(value)
                        elif tag == 'maxInclusive':
                            constraints['maximum'] = float(value)
                        elif tag == 'minExclusive':
                            constraints['exclusiveMinimum'] = float(value)
                        elif tag == 'maxExclusive':
                            constraints['exclusiveMaximum'] = float(value)
                
                # Check for simpleType with restrictions
                simple_type = element.find('xs:simpleType', self.xsd_namespace)
                if simple_type is not None:
                    restriction = simple_type.find('xs:restriction', self.xsd_namespace)
                    if restriction is not None:
                        for child in restriction:
                            tag = child.tag.split('}')[-1]
                            value = child.get('value', '')
                            if tag == 'maxLength':
                                constraints['maxLength'] = int(value)
                            elif tag == 'minLength':
                                constraints['minLength'] = int(value)
                            elif tag == 'pattern':
                                constraints['pattern'] = value
                            elif tag == 'enumeration':
                                if 'enum' not in constraints:
                                    constraints['enum'] = []
                                constraints['enum'].append(value)
                            elif tag == 'fractionDigits':
                                fraction = int(value)
                                constraints['multipleOf'] = 1.0 / (10 ** fraction)
                            elif tag == 'totalDigits':
                                constraints['maxLength'] = int(value)
                            elif tag == 'minInclusive':
                                constraints['minimum'] = float(value)
                            elif tag == 'maxInclusive':
                                constraints['maximum'] = float(value)
                            elif tag == 'minExclusive':
                                constraints['exclusiveMinimum'] = float(value)
                            elif tag == 'maxExclusive':
                                constraints['exclusiveMaximum'] = float(value)
                
                return constraints

            def process_element(element, parent_props: OrderedDict, parent_required: list):
                name = element.get('name', '')
                if not name:
                    return
                field_name = to_camel_case(name)
                element_type = element.get('type', '')
                min_occurs = int(element.get('minOccurs', '1'))
                max_occurs = element.get('maxOccurs', '1')

                # If type is a named complexType, resolve and process it
                if element_type and element_type in complex_types:
                    prop_def = process_complex_type(complex_types[element_type])
                else:
                    complex_type = element.find('xs:complexType', self.xsd_namespace)
                    if complex_type is not None:
                        prop_def = process_complex_type(complex_type)
                    else:
                        json_type = convert_xsd_type_to_json(element_type)
                        prop_def = OrderedDict()
                        prop_def["type"] = json_type
                        constraints = extract_constraints(element)
                        prop_def.update(constraints)

                # Handle arrays
                if max_occurs == 'unbounded' or (isinstance(max_occurs, str) and max_occurs.isdigit() and int(max_occurs) > 1):
                    arr_def = OrderedDict()
                    arr_def["type"] = "array"
                    arr_def["items"] = prop_def
                    if min_occurs > 0:
                        arr_def["minItems"] = min_occurs
                    if max_occurs != 'unbounded' and max_occurs.isdigit():
                        arr_def["maxItems"] = int(max_occurs)
                    prop_def = arr_def

                # Add description from annotation
                annotation = element.find('xs:annotation', self.xsd_namespace)
                if annotation is not None:
                    documentation = annotation.find('xs:documentation', self.xsd_namespace)
                    if documentation is not None and documentation.text:
                        prop_def["description"] = documentation.text.strip()

                parent_props[field_name] = prop_def
                if min_occurs > 0:
                    parent_required.append(field_name)

            def process_complex_type(complex_type) -> OrderedDict:
                sequence = complex_type.find('xs:sequence', self.xsd_namespace)
                if sequence is not None:
                    nested_props = OrderedDict()
                    nested_required = []
                    for child in sequence.findall('xs:element', self.xsd_namespace):
                        process_element(child, nested_props, nested_required)
                    result = OrderedDict()
                    result["type"] = "object"
                    result["properties"] = nested_props
                    if nested_required:
                        result["required"] = nested_required
                    return result
                return OrderedDict([("type", "object"), ("properties", OrderedDict())])

            # Find the root element(s)
            root_elements = root.findall('xs:element', self.xsd_namespace)
            json_schema = OrderedDict()
            json_schema["$schema"] = "http://json-schema.org/draft-07/schema#"
            json_schema["type"] = "object"
            json_schema["properties"] = OrderedDict()
            json_schema["required"] = []
            
            for element in root_elements:
                process_element(element, json_schema["properties"], json_schema["required"])

            with open(output_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(json_schema, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error converting XSD to JSON Schema: {e}")
            return False
    
    def json_schema_to_xsd(self, json_path: str, output_path: str) -> bool:
        """Convert JSON Schema to XSD"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_schema = json.load(f)
            
            def to_pascal_case(s: str) -> str:
                """Convert to PascalCase"""
                if not s:
                    return s
                return s[0].upper() + s[1:]
            
            def convert_json_type_to_xsd(json_type: str) -> str:
                """Convert JSON Schema type to XSD type"""
                return self.json_to_xsd_types.get(json_type, 'xs:string')
            
            def convert_constraints_to_xsd(constraints: dict) -> list:
                """Convert JSON Schema constraints to XSD restrictions"""
                restrictions = []
                
                for key, value in constraints.items():
                    if key == 'maxLength':
                        restrictions.append(f'<xs:maxLength value="{value}"/>')
                    elif key == 'minLength':
                        restrictions.append(f'<xs:minLength value="{value}"/>')
                    elif key == 'pattern':
                        restrictions.append(f'<xs:pattern value="{value}"/>')
                    elif key == 'enum':
                        for enum_value in value:
                            restrictions.append(f'<xs:enumeration value="{enum_value}"/>')
                    elif key == 'multipleOf':
                        # Convert multipleOf to fractionDigits
                        fraction = 0
                        temp_value = value
                        while temp_value < 1:
                            temp_value *= 10
                            fraction += 1
                        restrictions.append(f'<xs:fractionDigits value="{fraction}"/>')
                    elif key == 'minimum':
                        restrictions.append(f'<xs:minInclusive value="{value}"/>')
                    elif key == 'maximum':
                        restrictions.append(f'<xs:maxInclusive value="{value}"/>')
                    elif key == 'exclusiveMinimum':
                        restrictions.append(f'<xs:minExclusive value="{value}"/>')
                    elif key == 'exclusiveMaximum':
                        restrictions.append(f'<xs:maxExclusive value="{value}"/>')
                    elif key == 'format':
                        # Handle format constraints (date, date-time, etc.)
                        if value in ['date', 'date-time', 'time']:
                            restrictions.append(f'<xs:pattern value="[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}"/>')
                
                return restrictions
            
            def process_json_property(name: str, prop_def: dict, required_fields: list, indent: int = 0) -> str:
                """Process JSON Schema property and return XSD element"""
                field_name = to_pascal_case(name)
                prop_type = prop_def.get('type', 'string')
                
                # Convert type
                xsd_type = convert_json_type_to_xsd(prop_type)
                
                # Handle arrays
                if prop_type == 'array':
                    items = prop_def.get('items', {})
                    item_type = items.get('type', 'string')
                    
                    if item_type == 'object':
                        # Array of objects - create complex type
                        element = f'<xs:element name="{field_name}">\n'
                        element += ' ' * (indent + 4) + '<xs:complexType>\n'
                        element += ' ' * (indent + 8) + '<xs:sequence>\n'
                        
                        # Process array item properties
                        item_props = items.get('properties', {})
                        item_required = items.get('required', [])
                        
                        for item_prop_name, item_prop_def in item_props.items():
                            element += ' ' * (indent + 12) + process_json_property(item_prop_name, item_prop_def, item_required, indent + 12) + '\n'
                        
                        element += ' ' * (indent + 8) + '</xs:sequence>\n'
                        element += ' ' * (indent + 4) + '</xs:complexType>\n'
                        element += ' ' * indent + '</xs:element>'
                        return element
                    else:
                        # Array of simple types
                        xsd_item_type = convert_json_type_to_xsd(item_type)
                        element = f'<xs:element name="{field_name}" type="{xsd_item_type}"'
                        
                        # Add cardinality
                        min_items = prop_def.get('minItems', 0)
                        max_items = prop_def.get('maxItems', 'unbounded')
                        if min_items > 0:
                            element += f' minOccurs="{min_items}"'
                        if max_items != 'unbounded':
                            element += f' maxOccurs="{max_items}"'
                        else:
                            element += ' maxOccurs="unbounded"'
                        
                        element += '/>'
                        return element
                
                # Handle objects
                elif prop_type == 'object':
                    nested_props = prop_def.get('properties', {})
                    nested_required = prop_def.get('required', [])
                    
                    if nested_props:
                        # Create complex type
                        element = f'<xs:element name="{field_name}">\n'
                        element += ' ' * (indent + 4) + '<xs:complexType>\n'
                        element += ' ' * (indent + 8) + '<xs:sequence>\n'
                        
                        for nested_name, nested_prop in nested_props.items():
                            element += ' ' * (indent + 12) + process_json_property(nested_name, nested_prop, nested_required, indent + 12) + '\n'
                        
                        element += ' ' * (indent + 8) + '</xs:sequence>\n'
                        element += ' ' * (indent + 4) + '</xs:complexType>\n'
                        element += ' ' * indent + '</xs:element>'
                        return element
                    else:
                        # Simple object
                        element = f'<xs:element name="{field_name}" type="xs:string"/>'
                        return element
                
                else:
                    # Simple type
                    element = f'<xs:element name="{field_name}" type="{xsd_type}"'
                    
                    # Add cardinality based on required
                    is_required = name in required_fields
                    if not is_required:
                        element += ' minOccurs="0"'
                    
                    # Add constraints
                    constraints = convert_constraints_to_xsd(prop_def)
                    if constraints:
                        element += '>\n'
                        element += ' ' * (indent + 4) + '<xs:simpleType>\n'
                        element += ' ' * (indent + 8) + '<xs:restriction base="xs:string">\n'
                        for constraint in constraints:
                            element += ' ' * (indent + 12) + constraint + '\n'
                        element += ' ' * (indent + 8) + '</xs:restriction>\n'
                        element += ' ' * (indent + 4) + '</xs:simpleType>\n'
                        element += ' ' * indent + '</xs:element>'
                    else:
                        element += '/>'
                    
                    return element
            
            def process_nested_structure(properties: dict, required_fields: list, indent: int = 0) -> str:
                """Process nested structure and return XSD content"""
                content = ''
                for prop_name, prop_def in properties.items():
                    content += ' ' * indent + process_json_property(prop_name, prop_def, required_fields, indent) + '\n'
                return content
            
            # Generate XSD content
            xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="ControllingOrderChangeRequest">
        <xs:complexType>
            <xs:sequence>
'''
            
            # Process properties - handle nested structures
            properties = json_schema.get('properties', {})
            required_fields = json_schema.get('required', [])
            
            # If the root has a single property that is an object, process its nested properties
            if len(properties) == 1:
                root_prop_name = list(properties.keys())[0]
                root_prop_def = properties[root_prop_name]
                if root_prop_def.get('type') == 'object':
                    # Process the nested properties
                    nested_props = root_prop_def.get('properties', {})
                    nested_required = root_prop_def.get('required', [])
                    
                    xsd_content += process_nested_structure(nested_props, nested_required, 16)
                else:
                    # Process the single root property
                    xsd_content += '                ' + process_json_property(root_prop_name, root_prop_def, required_fields, 16) + '\n'
            else:
                # Process multiple root properties
                for prop_name, prop_def in properties.items():
                    xsd_content += '                ' + process_json_property(prop_name, prop_def, required_fields, 16) + '\n'
            
            xsd_content += '''            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''
            
            # Write XSD to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xsd_content)
            
            return True
            
        except Exception as e:
            print(f"Error converting JSON Schema to XSD: {e}")
            return False
    
    def validate_conversion(self, source_path: str, target_path: str, source_type: str) -> Tuple[bool, str]:
        """Validate the conversion result"""
        try:
            if source_type == 'xsd':
                # Validate XSD to JSON Schema conversion
                from .schema_processor import SchemaProcessor
                processor = SchemaProcessor()
                
                # Extract fields from both
                source_fields = processor.extract_fields_from_xsd(source_path)
                target_fields = processor.extract_fields_from_json_schema(target_path)
                
                # Basic validation
                if len(source_fields) == 0:
                    return False, "No fields found in source XSD"
                
                if len(target_fields) == 0:
                    return False, "No fields found in target JSON Schema"
                
                # Check if field count is reasonable (allowing for some differences due to conversion)
                field_ratio = len(target_fields) / len(source_fields)
                if field_ratio < 0.5 or field_ratio > 2.0:
                    return False, f"Field count mismatch: {len(source_fields)} -> {len(target_fields)}"
                
                return True, f"Conversion validated: {len(source_fields)} -> {len(target_fields)} fields"
                
            elif source_type == 'json':
                # Validate JSON Schema to XSD conversion
                from .schema_processor import SchemaProcessor
                processor = SchemaProcessor()
                
                # Extract fields from both
                source_fields = processor.extract_fields_from_json_schema(source_path)
                target_fields = processor.extract_fields_from_xsd(target_path)
                
                # Basic validation
                if len(source_fields) == 0:
                    return False, "No fields found in source JSON Schema"
                
                if len(target_fields) == 0:
                    return False, "No fields found in target XSD"
                
                # Check if field count is reasonable
                field_ratio = len(target_fields) / len(source_fields)
                if field_ratio < 0.5 or field_ratio > 2.0:
                    return False, f"Field count mismatch: {len(source_fields)} -> {len(target_fields)} fields"
                
                return True, f"Conversion validated: {len(source_fields)} -> {len(target_fields)} fields"
            
            else:
                return False, f"Unknown source type: {source_type}"
                
        except Exception as e:
            return False, f"Validation error: {str(e)}" 