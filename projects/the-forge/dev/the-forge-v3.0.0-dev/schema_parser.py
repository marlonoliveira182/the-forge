from typing import List
import os

def flatten_xsd_schema(xsd_path: str) -> List[List[str]]:
    import xmlschema
    schema = xmlschema.XMLSchema(xsd_path, validation='skip')
    paths = []
    def walk(element, path):
        if len(path) > 6:
            return
        children = list(element.iterchildren())
        if not children:
            # Try to get type, but handle unresolved types gracefully
            try:
                type_name = element.type.name if element.type is not None else None
            except Exception as ex:
                # Unresolved type, use the type string from the element
                type_name = getattr(element, 'type', None)
                if hasattr(type_name, 'name'):
                    type_name = type_name.name
                if not type_name and hasattr(element, 'type_name'):
                    type_name = str(element.type_name)
                if not type_name:
                    type_name = 'unresolved'
            # Add the path, including the type as the last level if not None
            full_path = path + [element.name] if element.name else path
            if type_name and type_name != full_path[-1]:
                full_path.append(str(type_name))
            paths.append(full_path)
        else:
            for child in children:
                walk(child, path + [element.name] if element.name else path)
    for e in schema.elements.values():
        try:
            walk(e, [])
        except Exception as ex:
            # Add a placeholder for unresolved root elements
            name = getattr(e, 'name', 'unresolved')
            type_name = getattr(e, 'type_name', 'unresolved')
            paths.append([name, str(type_name)] + [None]*4)
    # Clean up: remove empty levels, pad to 6
    result = []
    for p in paths:
        p = [x for x in p if x]
        result.append(p[:6] + [None]*(6-len(p)))
    return result

def flatten_json_schema(json_path: str) -> List[List[str]]:
    import json
    with open(json_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    paths = []
    def walk(obj, path):
        if len(path) > 6:
            return
        if isinstance(obj, dict):
            if 'properties' in obj:
                for k, v in obj['properties'].items():
                    walk(v, path + [k])
            else:
                paths.append(path)
        else:
            paths.append(path)
    walk(schema, [])
    result = []
    for p in paths:
        result.append(p[:6] + [None]*(6-len(p)))
    return result 