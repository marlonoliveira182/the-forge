import xml.etree.ElementTree as ET
import os
from collections import defaultdict
import io
from lxml import etree

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