import xml.etree.ElementTree as ET
import os
import json
import sys

XSD_NS = '{http://www.w3.org/2001/XMLSchema}'

class XSDParser:
    def __init__(self, max_level=8):
        self.max_level = max_level

    def get_attr(self, el, attr, default=None):
        return el.get(attr) if el.get(attr) is not None else default

    def get_cardinality(self, element):
        min_occurs = self.get_attr(element, 'minOccurs', '1')
        max_occurs = self.get_attr(element, 'maxOccurs', '1')
        if max_occurs == 'unbounded':
            card = f"{min_occurs}..n"
        elif min_occurs == max_occurs:
            card = f"{min_occurs}..{max_occurs}"
        else:
            card = f"{min_occurs}..{max_occurs}"
        return card

    def get_type(self, element):
        t = self.get_attr(element, 'type')
        if t:
            return t
        for child in element:
            if child.tag in (XSD_NS+'simpleType', XSD_NS+'complexType'):
                return child.tag.replace(XSD_NS, 'xsd:')
        return ''

    def get_details(self, element):
        details = []
        for child in element:
            if child.tag == XSD_NS+'simpleType':
                for restriction in child.findall(XSD_NS+'restriction'):
                    for cons in restriction:
                        cons_name = cons.tag.replace(XSD_NS, '')
                        val = cons.get('value')
                        if val:
                            details.append(f"{cons_name}={val}")
        return ', '.join(details)

    def get_documentation(self, element):
        for ann in element.findall(XSD_NS+'annotation'):
            for doc in ann.findall(XSD_NS+'documentation'):
                return doc.text or ''
        return ''

    def parse_element(self, element, complex_types, level=1, parent_path=None, req_param='Body'):
        if parent_path is None:
            parent_path = []
        rows = []
        name = self.get_attr(element, 'name')
        if not name:
            return rows
        path = parent_path + [name]
        row = {
            'levels': path[:self.max_level] + [''] * (self.max_level - len(path)),
            'Request Parameter': req_param,
            'GDPR': '',
            'Cardinality': self.get_cardinality(element),
            'Type': self.get_type(element),
            'Details': self.get_details(element),
            'Description': self.get_documentation(element)
        }
        rows.append(row)
        type_name = self.get_attr(element, 'type')
        if type_name and type_name in complex_types:
            ct = complex_types[type_name]
            seq = ct.find(XSD_NS+'sequence')
            if seq is not None:
                for child in seq.findall(XSD_NS+'element'):
                    rows.extend(self.parse_element(child, complex_types, level+1, path, req_param))
        else:
            for ct in element.findall(XSD_NS+'complexType'):
                seq = ct.find(XSD_NS+'sequence')
                if seq is not None:
                    for child in seq.findall(XSD_NS+'element'):
                        rows.extend(self.parse_element(child, complex_types, level+1, path, req_param))
        return rows

    def parse_xsd_file(self, xsd_path):
        tree = ET.parse(xsd_path)
        root = tree.getroot()
        complex_types = {ct.get('name'): ct for ct in root.findall(f'.//{XSD_NS}complexType') if ct.get('name')}
        rows = []
        for elem in root.findall(f'{XSD_NS}element'):
            rows.extend(self.parse_element(elem, complex_types, 1))
        return rows

    def parse_xsd_directory(self, dir_path):
        result = {}
        for fname in os.listdir(dir_path):
            if fname.lower().endswith('.xsd'):
                xsd_path = os.path.join(dir_path, fname)
                rows = self.parse_xsd_file(xsd_path)
                sheet_name = os.path.splitext(fname)[0]
                result[sheet_name] = rows
        return result

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Parse XSD file(s) and output as JSON.')
    parser.add_argument('input', help='XSD file or directory')
    parser.add_argument('--output', help='Output JSON file (default: stdout)')
    args = parser.parse_args()

    xsd_parser = XSDParser()
    if os.path.isdir(args.input):
        data = xsd_parser.parse_xsd_directory(args.input)
    else:
        data = {os.path.splitext(os.path.basename(args.input))[0]: xsd_parser.parse_xsd_file(args.input)}
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2)) 