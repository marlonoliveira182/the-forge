import os
import xml.etree.ElementTree as ET

# Directory to scan (change as needed or use sys.argv)
DIRECTORY = input('Enter the directory with WSDL/XSDs: ').strip()

# Map namespace to file name for all XSDs in the directory
def build_ns_to_file_map(directory):
    ns_to_file = {}
    for fname in os.listdir(directory):
        if fname.lower().endswith('.xsd'):
            path = os.path.join(directory, fname)
            try:
                tree = ET.parse(path)
                root = tree.getroot()
                tns = root.attrib.get('targetNamespace')
                if tns:
                    ns_to_file[tns] = fname
            except Exception as e:
                print(f'Failed to parse {fname}: {e}')
    return ns_to_file

def patch_file(path, ns_to_file):
    changed = False
    tree = ET.parse(path)
    root = tree.getroot()
    for schema_elem in root.findall('.//{http://www.w3.org/2001/XMLSchema}schema'):
        for imp in schema_elem.findall('{http://www.w3.org/2001/XMLSchema}import'):
            ns = imp.attrib.get('namespace')
            if ns and 'schemaLocation' not in imp.attrib:
                fname = ns_to_file.get(ns)
                if fname:
                    imp.set('schemaLocation', fname)
                    print(f'Patched import in {os.path.basename(path)}: namespace={ns} -> {fname}')
                    changed = True
        for inc in schema_elem.findall('{http://www.w3.org/2001/XMLSchema}include'):
            if 'schemaLocation' not in inc.attrib:
                # Try to match by file name (not always possible)
                # For now, skip includes without schemaLocation
                continue
    if changed:
        tree.write(path, encoding='utf-8', xml_declaration=True)

if __name__ == '__main__':
    ns_to_file = build_ns_to_file_map(DIRECTORY)
    for fname in os.listdir(DIRECTORY):
        if fname.lower().endswith(('.wsdl', '.xsd')):
            path = os.path.join(DIRECTORY, fname)
            patch_file(path, ns_to_file)
    print('Done.') 