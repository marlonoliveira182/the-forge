import os
from pathlib import Path
import sys
src_path = str(Path(__file__).resolve().parents[3] / 'src')
print(f"[DEBUG] Adding src path to sys.path: {src_path}")
sys.path.insert(0, src_path)
from core.schema_processor import SchemaProcessor
from core.excel_generator import ExcelGenerator
from core.mapping_engine import MappingEngine

# Paths
BASE_DIR = Path(__file__).parent
SRC_XSD = BASE_DIR / "source.xsd"
TGT_JSON = BASE_DIR / "target.json"
OUTPUT_XLSX = BASE_DIR / "exported_mapping.xlsx"

def main():
    # 1. Extract fields
    processor = SchemaProcessor()
    source_fields = processor.extract_fields_from_xsd(str(SRC_XSD))
    target_fields = processor.extract_fields_from_json_schema(str(TGT_JSON))

    # 2. Use the real mapping engine for similarity-based mappings
    engine = MappingEngine()
    mappings = engine.map_fields(source_fields, target_fields)

    # 3. Export to Excel
    excel_gen = ExcelGenerator()
    success = excel_gen.create_field_level_mapping_excel(mappings, str(OUTPUT_XLSX))
    if success:
        print(f"Excel export successful: {OUTPUT_XLSX}")
    else:
        print(f"Excel export failed.")

if __name__ == "__main__":
    main() 