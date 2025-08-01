#!/usr/bin/env python3
"""
Minimal test to isolate the import issue.
"""

print("Starting minimal import test...")

try:
    import streamlit as st
    print("✅ streamlit imported")
except Exception as e:
    print(f"❌ streamlit failed: {e}")
    exit(1)

try:
    from services.converter_service import ConverterService
    print("✅ ConverterService imported")
except Exception as e:
    print(f"❌ ConverterService failed: {e}")
    exit(1)

try:
    from services.xsd_parser_service import XSDParser
    print("✅ XSDParser imported")
except Exception as e:
    print(f"❌ XSDParser failed: {e}")
    exit(1)

try:
    from services.json_schema_parser_service import JSONSchemaParser
    print("✅ JSONSchemaParser imported")
except Exception as e:
    print(f"❌ JSONSchemaParser failed: {e}")
    exit(1)

try:
    from services.excel_export_service import ExcelExporter
    print("✅ ExcelExporter imported")
except Exception as e:
    print(f"❌ ExcelExporter failed: {e}")
    exit(1)

print("✅ All imports successful!") 