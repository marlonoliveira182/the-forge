import xml.etree.ElementTree as ET
import os
from collections import defaultdict
import io
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to get the frontend handler from the main app
try:
    import sys
    if 'app' in sys.modules:
        from app import frontend_handler
        logger.addHandler(frontend_handler)
except ImportError:
    # If app module is not available, just use console logging
    pass

def merge_xsd_from_wsdl(wsdl_content: str) -> str:
    """
    Extracts and merges all XSD schemas from a WSDL string into a single XSD string.
    Uses built-in xml.etree.ElementTree instead of lxml to avoid compilation issues.
    """
    logger.debug("Starting merge_xsd_from_wsdl")
    try:
        # Parse WSDL content
        logger.debug("Parsing WSDL content...")
        root = ET.fromstring(wsdl_content)
        logger.debug(f"WSDL root tag: {root.tag}")
        
        # Define namespaces
        namespaces = {
            'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
            'xsd': 'http://www.w3.org/2001/XMLSchema',
            'soap': 'http://schemas.xmlsoap.org/wsdl/soap/'
        }
        logger.debug(f"Using namespaces: {namespaces}")
        
        # Find all XSD schema elements
        logger.debug("Finding XSD schema elements...")
        xsd_elements = root.findall('.//xsd:schema', namespaces)
        logger.debug(f"Found {len(xsd_elements)} XSD schema elements")
        
        if not xsd_elements:
            logger.warning("No XSD schema elements found in WSDL")
            return ''
        
        # Use the first schema's attributes for the merged schema
        first_schema = xsd_elements[0]
        schema_attrs = dict(first_schema.attrib)
        logger.debug(f"First schema attributes: {schema_attrs}")
        
        # Create merged schema
        logger.debug("Creating merged schema...")
        merged_schema = ET.Element('{http://www.w3.org/2001/XMLSchema}schema')
        for k, v in schema_attrs.items():
            if not k.startswith('xmlns'):
                merged_schema.set(k, v)
                logger.debug(f"Set attribute {k}={v}")
        
        # Collect target/imported namespaces for comments
        target_ns = first_schema.get('targetNamespace', '')
        imported_ns = set()
        logger.debug(f"Target namespace: {target_ns}")
        
        for xsd in xsd_elements:
            for child in xsd:
                if child.tag.endswith('import'):
                    ns = child.get('namespace')
                    if ns:
                        imported_ns.add(ns)
                        logger.debug(f"Found imported namespace: {ns}")
        
        # Helper to remove prefixes from type/element references
        def strip_prefix(val):
            if val and ':' in val:
                return val.split(':', 1)[1]
            return val
        
        # Collect all unique (tag, name) definitions
        logger.debug("Processing schema elements...")
        seen_types = set()
        for i, xsd in enumerate(xsd_elements):
            logger.debug(f"Processing schema element {i+1}/{len(xsd_elements)}")
            for child in xsd:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                name = child.get('name')
                key = (tag, name)
                logger.debug(f"Processing child: tag={tag}, name={name}, key={key}")
                
                if name and key in seen_types:
                    logger.debug(f"Skipping duplicate key: {key}")
                    continue
                if name:
                    seen_types.add(key)
                
                # Remove prefixes from type/element references in this definition
                for attr in child.attrib:
                    if attr in ('type', 'base', 'ref', 'itemType'):
                        old_val = child.get(attr)
                        new_val = strip_prefix(old_val)
                        if old_val != new_val:
                            child.set(attr, new_val)
                            logger.debug(f"Stripped prefix from {attr}: {old_val} -> {new_val}")
                
                # Recursively fix children (for complexType, etc.)
                for elem in child.iter():
                    for attr in elem.attrib:
                        if attr in ('type', 'base', 'ref', 'itemType'):
                            old_val = elem.get(attr)
                            new_val = strip_prefix(old_val)
                            if old_val != new_val:
                                elem.set(attr, new_val)
                                logger.debug(f"Stripped prefix from child {attr}: {old_val} -> {new_val}")
                
                # Add to merged schema
                merged_schema.append(child)
                logger.debug(f"Added child to merged schema: {tag}")
        
        # Remove all import elements from merged schema
        logger.debug("Removing import elements...")
        for imp in merged_schema.findall('.//{http://www.w3.org/2001/XMLSchema}import'):
            merged_schema.remove(imp)
            logger.debug("Removed import element")
        
        # Convert to string
        logger.debug("Converting merged schema to string...")
        # ET.indent() is only available in Python 3.9+
        try:
            logger.debug("Attempting to indent merged schema...")
            ET.indent(merged_schema, space="  ")
            logger.debug("Successfully indented merged schema")
        except AttributeError as e:
            logger.debug(f"ET.indent() not available (Python < 3.9): {e}")
            # Fallback for older Python versions
            pass
        
        result = ET.tostring(merged_schema, encoding='unicode')
        logger.debug(f"Generated XSD string with {len(result)} characters")
        return result
        
    except Exception as e:
        logger.error(f"Exception in merge_xsd_from_wsdl: {e}", exc_info=True)
        return f"Error processing WSDL: {str(e)}" 