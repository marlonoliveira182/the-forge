import json
import openpyxl
import os
from .excel_mapping_service import ExcelMappingService

class JSONToExcelService:
    def __init__(self, max_level=8):
        self.max_level = max_level

    def load_json_schema(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        return schema

    def flatten_json_schema(self, schema):
        # Use the flatten_schema from ExcelMappingService
        return ExcelMappingService.flatten_schema(schema)

    def generate_mapping_rows(self, json_path):
        schema = self.load_json_schema(json_path)
        paths = self.flatten_json_schema(schema)
        # For mapping: just fill Source Path, leave Target Path blank
        return [{'Source Path': p, 'Target Path': ''} for p in paths]

    def export_to_excel(self, mapping_rows, output_file, headers=None):
        wb = openpyxl.Workbook()
        ws = wb.active
        # Use two header rows as in the template
        if headers is None:
            headers = ['Source Path', 'Target Path']
        ws.append(headers)
        ws.append(['', ''])  # Second header row blank for now
        for row in mapping_rows:
            ws.append([row.get('Source Path', ''), row.get('Target Path', '')])
        wb.save(output_file)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Convert JSON Schema to Excel mapping file.')
    parser.add_argument('json_schema', help='Input JSON Schema file')
    parser.add_argument('output', help='Output Excel file')
    args = parser.parse_args()

    service = JSONToExcelService()
    mapping_rows = service.generate_mapping_rows(args.json_schema)
    service.export_to_excel(mapping_rows, args.output)
    print(f'Excel mapping file exported to {args.output}') 