import xml.etree.ElementTree as ET
import json
import os

XSD_NS = '{http://www.w3.org/2001/XMLSchema}'

class XSDJSONConverterService:
    def xsd_to_json_schema(self, xsd_path):
        tree = ET.parse(xsd_path)
        root = tree.getroot()
        def parse_element(element):
            name = element.get('name')
            type_ = element.get('type')
            schema = {}
            if type_:
                schema['type'] = type_.replace('xsd:', '')
            for child in element:
                if child.tag == XSD_NS+'annotation':
                    for doc in child.findall(XSD_NS+'documentation'):
                        schema['description'] = doc.text
                elif child.tag == XSD_NS+'complexType':
                    schema['type'] = 'object'
                    properties = {}
                    seq = child.find(XSD_NS+'sequence')
                    if seq is not None:
                        for sub in seq.findall(XSD_NS+'element'):
                            sub_name = sub.get('name')
                            properties[sub_name] = parse_element(sub)
                    schema['properties'] = properties
            return schema
        json_schema = {'type': 'object', 'properties': {}}
        for elem in root.findall(f'{XSD_NS}element'):
            name = elem.get('name')
            if name:
                json_schema['properties'][name] = parse_element(elem)
        return json_schema

    def json_schema_to_xsd(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        def build_element(name, definition):
            elem = ET.Element(XSD_NS+'element', name=name)
            t = definition.get('type')
            if t and t != 'object':
                elem.set('type', 'xsd:' + t)
            if 'description' in definition:
                ann = ET.SubElement(elem, XSD_NS+'annotation')
                doc = ET.SubElement(ann, XSD_NS+'documentation')
                doc.text = definition['description']
            if t == 'object' or 'properties' in definition:
                ct = ET.SubElement(elem, XSD_NS+'complexType')
                seq = ET.SubElement(ct, XSD_NS+'sequence')
                for sub_name, sub_def in definition.get('properties', {}).items():
                    seq.append(build_element(sub_name, sub_def))
            return elem
        schema_elem = ET.Element(XSD_NS+'schema', attrib={'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema'})
        for name, definition in schema.get('properties', {}).items():
            schema_elem.append(build_element(name, definition))
        return ET.tostring(schema_elem, encoding='unicode')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Convert XSD <-> JSON Schema.')
    parser.add_argument('--xsd-to-json', help='Input XSD file to convert to JSON Schema')
    parser.add_argument('--json-to-xsd', help='Input JSON Schema file to convert to XSD')
    parser.add_argument('--output', help='Output file')
    args = parser.parse_args()

    service = XSDJSONConverterService()
    if args.xsd_to_json:
        jschema = service.xsd_to_json_schema(args.xsd_to_json)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(jschema, f, ensure_ascii=False, indent=2)
        else:
            print(json.dumps(jschema, ensure_ascii=False, indent=2))
    elif args.json_to_xsd:
        xsd_str = service.json_schema_to_xsd(args.json_to_xsd)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(xsd_str)
        else:
            print(xsd_str) 