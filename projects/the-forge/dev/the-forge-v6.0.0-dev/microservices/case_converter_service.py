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

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Convert between PascalCase and camelCase.')
    parser.add_argument('string', nargs='?', help='String to convert')
    parser.add_argument('--to', choices=['camel', 'pascal'], required=True, help='Convert to camel or pascal case')
    args = parser.parse_args()

    if args.string:
        if args.to == 'camel':
            print(pascal_to_camel(args.string))
        else:
            print(camel_to_pascal(args.string))
    else:
        # Read lines from stdin
        import sys
        for line in sys.stdin:
            line = line.strip()
            if args.to == 'camel':
                print(pascal_to_camel(line))
            else:
                print(camel_to_pascal(line)) 