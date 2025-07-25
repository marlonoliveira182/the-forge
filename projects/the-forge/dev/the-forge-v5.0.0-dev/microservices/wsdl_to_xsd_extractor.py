import xml.etree.ElementTree as ET
import os
from collections import defaultdict
import io
from lxml import etree

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

def merge_xsd_from_wsdl(wsdl_content: str) -> str:
    """
    Extracts and merges all XSD schemas from a WSDL string into a single XSD string.
    Produces output matching UtilityArena's style:
      - Uses the first schema's targetNamespace and attributes
      - Removes all namespace prefixes from type/element references and definitions
      - Adds comments for target/imported namespaces at the top
      - Ensures all type/element references are unprefixed
      - Copies all relevant type/element definitions into a single schema
    """
    parser = etree.XMLParser(remove_blank_text=True)
    wsdl_tree = etree.parse(io.BytesIO(wsdl_content.encode('utf-8')), parser)
    namespaces = wsdl_tree.getroot().nsmap
    namespaces = {k or 'wsdl': v for k, v in namespaces.items()}
    xsd_elements = wsdl_tree.xpath('//xsd:schema', namespaces={**namespaces, 'xsd': 'http://www.w3.org/2001/XMLSchema'})
    if not xsd_elements:
        return ''

    # Use the first schema's attributes for the merged schema
    first_schema = xsd_elements[0]
    schema_attrs = dict(first_schema.attrib)
    # Remove xmlns:* attributes (handled by nsmap)
    schema_attrs = {k: v for k, v in schema_attrs.items() if not k.startswith('xmlns')}
    merged_schema = etree.Element('{http://www.w3.org/2001/XMLSchema}schema', nsmap={'xsd': 'http://www.w3.org/2001/XMLSchema'})
    for k, v in schema_attrs.items():
        merged_schema.set(k, v)

    # Collect target/imported namespaces for comments
    target_ns = first_schema.get('targetNamespace', '')
    imported_ns = set()
    for xsd in xsd_elements:
        for child in xsd:
            if etree.QName(child).localname == 'import':
                ns = child.get('namespace')
                if ns:
                    imported_ns.add(ns)

    # Add UtilityArena-style comments at the top
    comments = []
    if target_ns:
        comments.append(f'##SCHEMA_TARGET_NAMESPACE##:{target_ns}')
    if imported_ns:
        comments.append(f'##SCHEMA_IMPORTED_NAMESPACE##:' + '#'.join(imported_ns))
    for c in comments:
        merged_schema.addprevious(etree.Comment(c))

    # Helper to remove prefixes from type/element references
    def strip_prefix(val):
        if val and ':' in val:
            return val.split(':', 1)[1]
        return val

    # Collect all unique (tag, name) definitions
    seen_types = set()
    for xsd in xsd_elements:
        for child in xsd:
            tag = etree.QName(child).localname
            name = child.get('name')
            key = (tag, name)
            if name and key in seen_types:
                continue
            if name:
                seen_types.add(key)
            # Remove prefixes from type/element references in this definition
            for attr in child.attrib:
                if attr in ('type', 'base', 'ref', 'itemType'):  # common XSD ref attrs
                    child.set(attr, strip_prefix(child.get(attr)))
            # Recursively fix children (for complexType, etc.)
            for elem in child.iter():
                for attr in elem.attrib:
                    if attr in ('type', 'base', 'ref', 'itemType'):
                        elem.set(attr, strip_prefix(elem.get(attr)))
            # Remove prefixes from tag itself if present (shouldn't be, but for safety)
            merged_schema.append(child)

    # Remove all <xsd:import> from merged schema
    for imp in merged_schema.xpath('.//xsd:import', namespaces={'xsd': 'http://www.w3.org/2001/XMLSchema'}):
        parent = imp.getparent()
        if parent is not None:
            parent.remove(imp)

    # Add UtilityArena generator comment at the very top
    # doc_comment = etree.Comment(' Created with WSDL to XSD Generator (https://www.UtilityArena.com) ')
    # merged_schema.addprevious(doc_comment)

    return etree.tostring(merged_schema.getroottree(), pretty_print=True, encoding='unicode')

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

# For CLI or microservice use
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python wsdl_to_xsd_extractor.py <wsdl_file>")
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        wsdl_content = f.read()
    merged_xsd = merge_xsd_from_wsdl(wsdl_content)
    print(merged_xsd) 