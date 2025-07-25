import xml.etree.ElementTree as ET
import os
from collections import defaultdict

def extract_xsds_from_wsdl(wsdl_path, output_dir=None):
    """
    Extracts all <xsd:schema> elements from a WSDL file.
    If output_dir is provided, writes each schema to a separate .xsd file.
    Returns a list of (namespace, xsd_string) tuples.
    """
    ns = {
        'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
        'xsd': 'http://www.w3.org/2001/XMLSchema'
    }
    tree = ET.parse(wsdl_path)
    root = tree.getroot()
    schemas = []
    for types in root.findall('wsdl:types', ns):
        for schema in types.findall('xsd:schema', ns):
            tns = schema.get('targetNamespace', '')
            xsd_str = ET.tostring(schema, encoding='unicode')
            schemas.append((tns, xsd_str))
            if output_dir:
                fname = f"schema_{len(schemas)}.xsd"
                out_path = os.path.join(output_dir, fname)
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(xsd_str)
    return schemas

def extract_wsdl_operations(wsdl_path):
    """
    Returns a list of operations with their input/output messages and referenced elements.
    [{
        'name': operation_name,
        'input_message': message_name,
        'output_message': message_name,
        'input_element': (namespace, element_name),
        'output_element': (namespace, element_name)
    }, ...]
    """
    ns = {
        'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
        'xsd': 'http://www.w3.org/2001/XMLSchema'
    }
    tree = ET.parse(wsdl_path)
    root = tree.getroot()
    # Map message name to (namespace, element/type)
    messages = {}
    for msg in root.findall('wsdl:message', ns):
        msg_name = msg.get('name')
        for part in msg.findall('wsdl:part', ns):
            elem = part.get('element') or part.get('type')
            if elem:
                if ':' in elem:
                    prefix, local = elem.split(':', 1)
                    uri = msg.nsmap[prefix] if hasattr(msg, 'nsmap') and prefix in msg.nsmap else ''
                else:
                    local = elem
                    uri = ''
                messages[msg_name] = (uri, local)
    # List operations
    operations = []
    for portType in root.findall('wsdl:portType', ns):
        for op in portType.findall('wsdl:operation', ns):
            op_name = op.get('name')
            input_msg = None
            output_msg = None
            input_elem = None
            output_elem = None
            input_tag = op.find('wsdl:input', ns)
            if input_tag is not None:
                input_msg = input_tag.get('message')
                if input_msg and ':' in input_msg:
                    input_msg = input_msg.split(':', 1)[1]
                input_elem = messages.get(input_msg)
            output_tag = op.find('wsdl:output', ns)
            if output_tag is not None:
                output_msg = output_tag.get('message')
                if output_msg and ':' in output_msg:
                    output_msg = output_msg.split(':', 1)[1]
                output_elem = messages.get(output_msg)
            operations.append({
                'name': op_name,
                'input_message': input_msg,
                'output_message': output_msg,
                'input_element': input_elem,
                'output_element': output_elem
            })
    return operations

def merge_xsd_schemas(xsd_strings):
    """
    Merges multiple XSD <schema> strings into a single <schema> string (naive, for mapping root extraction).
    """
    # Parse all schemas and collect children
    schemas = [ET.fromstring(xsd) for xsd in xsd_strings]
    if not schemas:
        return ''
    # Use the first schema as the base
    base = schemas[0]
    for s in schemas[1:]:
        for child in s:
            base.append(child)
    return ET.tostring(base, encoding='unicode')

def extract_merged_xsd_with_zeep(wsdl_path, output_path=None):
    try:
        from zeep import Client
        from lxml import etree
    except ImportError:
        raise ImportError('zeep and lxml are required for this operation. Please install with: pip install zeep lxml')
    client = Client(wsdl=wsdl_path)
    # Always include the main schema root
    schema_roots = [client.wsdl.types.root]
    # Add all imported schemas (if any)
    if hasattr(client.wsdl.types, 'imports'):
        for imported_schema in client.wsdl.types.imports.values():
            # imported_schema is a dict of {namespace: Schema}
            for schema in imported_schema.values():
                if hasattr(schema, 'root'):
                    schema_roots.append(schema.root)
    if not schema_roots:
        raise ValueError('No schemas found in WSDL via Zeep.')
    # Use the first schema as the base, append all children from others
    base = etree.Element(schema_roots[0].tag, nsmap=schema_roots[0].nsmap)
    for k, v in schema_roots[0].attrib.items():
        base.set(k, v)
    for schema in schema_roots:
        for child in schema:
            base.append(child)
    xsd_string = etree.tostring(base, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf-8')
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xsd_string)
    return xsd_string

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python wsdl_to_xsd_extractor.py <wsdl_path> [output_dir]")
        sys.exit(1)
    wsdl_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    schemas = extract_xsds_from_wsdl(wsdl_path, output_dir)
    print(f"Extracted {len(schemas)} XSD schemas from {wsdl_path}")
    operations = extract_wsdl_operations(wsdl_path)
    print(f"Found {len(operations)} operations:")
    for op in operations:
        print(op) 