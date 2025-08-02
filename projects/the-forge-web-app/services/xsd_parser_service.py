import xml.etree.ElementTree as ET
import os

XSD_NS = '{http://www.w3.org/2001/XMLSchema}'

class XSDParser:
    def __init__(self, max_level=8):
        self.max_level = max_level

    def get_attr(self, el, attr, default=None):
        return el.get(attr) if el.get(attr) is not None else default

    def get_cardinality(self, element):
        # For attributes, use 'use' property
        if element.tag == XSD_NS+'attribute':
            use = self.get_attr(element, 'use', 'optional')
            if use == 'required':
                return '1..1'
            else:
                return '0..1'
        min_occurs = self.get_attr(element, 'minOccurs', '1')
        max_occurs = self.get_attr(element, 'maxOccurs', '1')
        if max_occurs == 'unbounded':
            card = f"{min_occurs}..n"
        elif min_occurs == max_occurs:
            card = f"{min_occurs}..{max_occurs}"
        else:
            card = f"{min_occurs}..{max_occurs}"
        return card

    def get_type(self, element, simple_types=None):
        t = self.get_attr(element, 'type')
        if t:
            return t
        for child in element:
            if child.tag == XSD_NS+'simpleType':
                return 'simpleType'
            if child.tag == XSD_NS+'complexType':
                return 'complexType'
        return ''

    def get_base_type(self, element, simple_types=None, complex_types=None):
        t = self.get_attr(element, 'type')
        # If it's a custom simpleType, resolve its base type
        if t and simple_types and t in simple_types:
            base = simple_types[t].get('base')
            return base if base else t
        # If it's a complexType with simpleContent, resolve its base type
        if t and complex_types and t in complex_types:
            ct = complex_types[t]
            sc = ct.find(XSD_NS+'simpleContent')
            if sc is not None:
                ext = sc.find(XSD_NS+'extension')
                if ext is not None:
                    base = ext.get('base')
                    if base:
                        return base
        # Inline simpleType
        for child in element:
            if child.tag == XSD_NS+'simpleType':
                restriction = child.find(XSD_NS+'restriction')
                if restriction is not None:
                    base = restriction.get('base')
                    if base:
                        return base
        return t or ''

    def get_details(self, element, simple_types=None, complex_types=None):
        details = []
        t = self.get_attr(element, 'type')
        # Add restrictions from referenced simpleType
        if t and simple_types and t in simple_types:
            for cons_name, val in simple_types[t]['restrictions'].items():
                details.append(f"{cons_name}={val}")
        # Add restrictions from referenced complexType with simpleContent
        if t and complex_types and t in complex_types:
            ct = complex_types[t]
            sc = ct.find(XSD_NS+'simpleContent')
            if sc is not None:
                ext = sc.find(XSD_NS+'extension')
                if ext is not None:
                    base = ext.get('base')
                    restriction = None
                    # Try to find the base in simple_types
                    if simple_types and base in simple_types:
                        restriction = simple_types[base]['restrictions']
                    if restriction:
                        for cons_name, val in restriction.items():
                            details.append(f"{cons_name}={val}")
        # Inline simpleType
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

    def parse_complex_type_children(self, complex_type, complex_types, simple_types, level, parent_path, req_param, category='element'):
        """Parse all children of a complexType, including inherited ones"""
        rows = []
        
        # First, check if this complexType extends another one
        for child in complex_type:
            if child.tag == XSD_NS+'complexContent':
                ext = child.find(XSD_NS+'extension')
                if ext is not None:
                    base_type_name = ext.get('base')
                    if base_type_name and base_type_name in complex_types:
                        # Recursively parse the base type first
                        base_rows = self.parse_complex_type_children(
                            complex_types[base_type_name], 
                            complex_types, 
                            simple_types, 
                            level, 
                            parent_path, 
                            req_param, 
                            category
                        )
                        rows.extend(base_rows)
                    
                    # Then parse the extension elements
                    for ext_child in ext:
                        if ext_child.tag == XSD_NS+'sequence':
                            for seq_child in ext_child:
                                if seq_child.tag == XSD_NS+'element':
                                    rows.extend(self.parse_element(seq_child, complex_types, simple_types, level+1, parent_path, req_param, 'element'))
                                elif seq_child.tag == XSD_NS+'attribute':
                                    rows.extend(self.parse_attribute(seq_child, parent_path, req_param, complex_types, simple_types))
                        elif ext_child.tag == XSD_NS+'attribute':
                            rows.extend(self.parse_attribute(ext_child, parent_path, req_param, complex_types, simple_types))
                return rows
        
        # If no complexContent, parse direct children
        for child in complex_type:
            if child.tag == XSD_NS+'sequence':
                for seq_child in child:
                    if seq_child.tag == XSD_NS+'element':
                        rows.extend(self.parse_element(seq_child, complex_types, simple_types, level+1, parent_path, req_param, 'element'))
                    elif seq_child.tag == XSD_NS+'attribute':
                        rows.extend(self.parse_attribute(seq_child, parent_path, req_param, complex_types, simple_types))
            elif child.tag == XSD_NS+'attribute':
                rows.extend(self.parse_attribute(child, parent_path, req_param, complex_types, simple_types))
            elif child.tag in [XSD_NS+'simpleContent', XSD_NS+'complexContent']:
                ext = child.find(XSD_NS+'extension')
                if ext is not None:
                    for ext_child in ext:
                        if ext_child.tag == XSD_NS+'attribute':
                            rows.extend(self.parse_attribute(ext_child, parent_path, req_param, complex_types, simple_types))
        
        return rows

    def parse_element(self, element, complex_types, simple_types, level=1, parent_path=None, req_param='Body', category='element'):
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
            'Type': self.get_type(element, simple_types),
            'Base Type': self.get_base_type(element, simple_types, complex_types),
            'Details': self.get_details(element, simple_types, complex_types),
            'Description': self.get_documentation(element),
            'Category': category,
            'Example': ''
        }
        rows.append(row)
        type_name = self.get_type(element, simple_types)
        if type_name and type_name in complex_types:
            ct = complex_types[type_name]
            # Use the new method to parse complex type children (including inheritance)
            rows.extend(self.parse_complex_type_children(ct, complex_types, simple_types, level, path, req_param, category))
        else:
            for ct in element.findall(XSD_NS+'complexType'):
                rows.extend(self.parse_complex_type_children(ct, complex_types, simple_types, level, path, req_param, category))
        # Direct attributes on the element itself (not in complexType)
        for child in element:
            if child.tag == XSD_NS+'attribute':
                rows.extend(self.parse_attribute(child, path, req_param, complex_types, simple_types))
        return rows

    def parse_attribute(self, attr, parent_path, req_param, complex_types, simple_types):
        name = self.get_attr(attr, 'name')
        if not name:
            return []
        path = parent_path + [f'@{name}']
        row = {
            'levels': path[:self.max_level] + [''] * (self.max_level - len(path)),
            'Request Parameter': req_param,
            'GDPR': '',
            'Cardinality': self.get_cardinality(attr),
            'Type': self.get_type(attr, simple_types),
            'Base Type': self.get_base_type(attr, simple_types, complex_types),
            'Details': self.get_details(attr, simple_types, complex_types),
            'Description': self.get_documentation(attr),
            'Category': 'attribute',
            'Example': ''
        }
        return [row]

    def parse_xsd_file(self, xsd_path):
        tree = ET.parse(xsd_path)
        root = tree.getroot()
        # Collect all simpleTypes and their restrictions
        simple_types = {}
        for st in root.findall(f'.//{XSD_NS}simpleType'):
            name = st.get('name')
            if not name:
                continue
            restriction = st.find(XSD_NS+'restriction')
            base = restriction.get('base') if restriction is not None else None
            restrictions = {}
            if restriction is not None:
                for cons in restriction:
                    cons_name = cons.tag.replace(XSD_NS, '')
                    val = cons.get('value')
                    if val:
                        restrictions[cons_name] = val
            simple_types[name] = {'base': base, 'restrictions': restrictions}
        complex_types = {ct.get('name'): ct for ct in root.findall(f'.//{XSD_NS}complexType') if ct.get('name')}
        rows = []
        for elem in root.findall(f'{XSD_NS}element'):
            rows.extend(self.parse_element(elem, complex_types, simple_types, 1, category='message'))
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

    def parse_xsd_string(self, xsd_string):
        root = ET.fromstring(xsd_string)
        # Collect all simpleTypes and their restrictions
        simple_types = {}
        for st in root.findall(f'.//{XSD_NS}simpleType'):
            name = st.get('name')
            if not name:
                continue
            restriction = st.find(XSD_NS+'restriction')
            base = restriction.get('base') if restriction is not None else None
            restrictions = {}
            if restriction is not None:
                for cons in restriction:
                    cons_name = cons.tag.replace(XSD_NS, '')
                    val = cons.get('value')
                    if val:
                        restrictions[cons_name] = val
            simple_types[name] = {'base': base, 'restrictions': restrictions}
        complex_types = {ct.get('name'): ct for ct in root.findall(f'.//{XSD_NS}complexType') if ct.get('name')}
        rows = []
        for elem in root.findall(f'{XSD_NS}element'):
            rows.extend(self.parse_element(elem, complex_types, simple_types, 1, category='message'))
        return rows 

    def parse_xsd_file_by_messages(self, xsd_path):
        """
        Parse XSD file and group results by message/element name.
        Returns a dictionary where keys are message names and values are lists of rows.
        """
        tree = ET.parse(xsd_path)
        root = tree.getroot()
        # Collect all simpleTypes and their restrictions
        simple_types = {}
        for st in root.findall(f'.//{XSD_NS}simpleType'):
            name = st.get('name')
            if not name:
                continue
            restriction = st.find(XSD_NS+'restriction')
            base = restriction.get('base') if restriction is not None else None
            restrictions = {}
            if restriction is not None:
                for cons in restriction:
                    cons_name = cons.tag.replace(XSD_NS, '')
                    val = cons.get('value')
                    if val:
                        restrictions[cons_name] = val
            simple_types[name] = {'base': base, 'restrictions': restrictions}
        complex_types = {ct.get('name'): ct for ct in root.findall(f'.//{XSD_NS}complexType') if ct.get('name')}
        
        # Group rows by element name
        messages = {}
        for elem in root.findall(f'{XSD_NS}element'):
            element_name = self.get_attr(elem, 'name')
            if not element_name:
                continue
            
            # Parse this element's rows
            rows = self.parse_element(elem, complex_types, simple_types, 1, category='message')
            
            # Use element name as sheet name (sanitized for Excel)
            sheet_name = self._sanitize_sheet_name(element_name)
            messages[sheet_name] = rows
        
        return messages
    
    def _sanitize_sheet_name(self, name):
        """
        Sanitize a name to be used as an Excel sheet name.
        Excel sheet names have restrictions: max 31 chars, no special chars.
        """
        # Remove or replace invalid characters
        invalid_chars = ['\\', '/', '*', '?', ':', '[', ']']
        sanitized = name
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Limit length to 31 characters
        if len(sanitized) > 31:
            sanitized = sanitized[:31]
        
        # Ensure it's not empty
        if not sanitized:
            sanitized = "Sheet"
        
        return sanitized 