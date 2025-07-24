import sys
from pathlib import Path
from lxml import etree

if len(sys.argv) < 3:
    print("Usage: python reorder_xsd_types.py <input.xsd> <output.xsd>")
    sys.exit(1)

input_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])

parser = etree.XMLParser(remove_blank_text=True)
tree = etree.parse(str(input_path), parser)
root = tree.getroot()

# Namespaces
nsmap = root.nsmap.copy()
xsd_ns = nsmap.get('xsd') or nsmap.get(None) or 'http://www.w3.org/2001/XMLSchema'

# Find all import/include/type/element definitions
imports_includes = []
complex_types = []
simple_types = []
elements = []
others = []

for child in list(root):
    if not (isinstance(child, etree._Element) and isinstance(child.tag, str)):
        continue
    tag = etree.QName(child).localname
    if tag in ('import', 'include'):
        imports_includes.append(child)
        root.remove(child)
    elif tag == 'complexType':
        complex_types.append(child)
        root.remove(child)
    elif tag == 'simpleType':
        simple_types.append(child)
        root.remove(child)
    elif tag == 'element':
        elements.append(child)
        root.remove(child)
    else:
        others.append(child)
        root.remove(child)

# Re-insert in order: imports/includes, types, elements, others
for child in list(root):
    if isinstance(child, etree._Element) and isinstance(child.tag, str):
        root.remove(child)
for ii in imports_includes:
    root.append(ii)
for t in complex_types:
    root.append(t)
for t in simple_types:
    root.append(t)
for e in elements:
    root.append(e)
for o in others:
    root.append(o)

# Write output
with open(output_path, 'wb') as f:
    tree.write(f, pretty_print=True, xml_declaration=True, encoding='UTF-8')

print(f"Reordered XSD written to {output_path}") 