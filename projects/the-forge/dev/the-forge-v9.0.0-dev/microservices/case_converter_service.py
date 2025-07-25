import re

def pascal_to_camel(s):
    if not s:
        return s
    return s[0].lower() + s[1:] if s[0].isupper() else s

def camel_to_pascal(s):
    if not s:
        return s
    return s[0].upper() + s[1:] if s[0].islower() else s

def convert_dict_keys(d, converter):
    if isinstance(d, dict):
        return {converter(k): convert_dict_keys(v, converter) for k, v in d.items()}
    elif isinstance(d, list):
        return [convert_dict_keys(i, converter) for i in d]
    else:
        return d 