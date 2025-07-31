import xml.etree.ElementTree as ET
import os
from collections import defaultdict
import io

def merge_xsd_from_wsdl(wsdl_content: str) -> str:
    """
    Extracts and merges all XSD schemas from a WSDL string into a single XSD string.
    Uses built-in xml.etree.ElementTree instead of lxml to avoid compilation issues.
    """
    try:
        # Parse WSDL content
        root = ET.fromstring(wsdl_content)
        
        # Define namespaces
        namespaces = {
            'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
            'xsd': 'http://www.w3.org/2001/XMLSchema',
            'soap': 'http://schemas.xmlsoap.org/wsdl/soap/'
        }
        
        # Find all XSD schema elements
        xsd_elements = root.findall('.//xsd:schema', namespaces)
        if not xsd_elements:
            return ''
        
        # Use the first schema's attributes for the merged schema
        first_schema = xsd_elements[0]
        schema_attrs = dict(first_schema.attrib)
        
        # Create merged schema
        merged_schema = ET.Element('{http://www.w3.org/2001/XMLSchema}schema')
        for k, v in schema_attrs.items():
            if not k.startswith('xmlns'):
                merged_schema.set(k, v)
        
        # Collect target/imported namespaces for comments
        target_ns = first_schema.get('targetNamespace', '')
        imported_ns = set()
        
        for xsd in xsd_elements:
            for child in xsd:
                if child.tag.endswith('import'):
                    ns = child.get('namespace')
                    if ns:
                        imported_ns.add(ns)
        
        # Helper to remove prefixes from type/element references
        def strip_prefix(val):
            if val and ':' in val:
                return val.split(':', 1)[1]
            return val
        
        # Collect all unique (tag, name) definitions
        seen_types = set()
        for xsd in xsd_elements:
            for child in xsd:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                name = child.get('name')
                key = (tag, name)
                if name and key in seen_types:
                    continue
                if name:
                    seen_types.add(key)
                
                # Remove prefixes from type/element references in this definition
                for attr in child.attrib:
                    if attr in ('type', 'base', 'ref', 'itemType'):
                        child.set(attr, strip_prefix(child.get(attr)))
                
                # Recursively fix children (for complexType, etc.)
                for elem in child.iter():
                    for attr in elem.attrib:
                        if attr in ('type', 'base', 'ref', 'itemType'):
                            elem.set(attr, strip_prefix(elem.get(attr)))
                
                # Add to merged schema
                merged_schema.append(child)
        
        # Remove all import elements from merged schema
        for imp in merged_schema.findall('.//{http://www.w3.org/2001/XMLSchema}import'):
            merged_schema.remove(imp)
        
        # Convert to string
        ET.indent(merged_schema, space="  ")
        return ET.tostring(merged_schema, encoding='unicode')
        
    except Exception as e:
        return f"Error processing WSDL: {str(e)}" 