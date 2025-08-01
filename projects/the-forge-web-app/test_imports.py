#!/usr/bin/env python3
"""
Test script to check if all imports work correctly.
"""

def test_imports():
    """Test all the imports used in app.py"""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✅ streamlit imported")
    except Exception as e:
        print(f"❌ streamlit import failed: {e}")
    
    try:
        from services.xsd_parser_service import XSDParser
        print("✅ XSDParser imported")
    except Exception as e:
        print(f"❌ XSDParser import failed: {e}")
    
    try:
        from services.json_schema_parser_service import JSONSchemaParser
        print("✅ JSONSchemaParser imported")
    except Exception as e:
        print(f"❌ JSONSchemaParser import failed: {e}")
    
    try:
        from services.excel_export_service import ExcelExporter
        print("✅ ExcelExporter imported")
    except Exception as e:
        print(f"❌ ExcelExporter import failed: {e}")
    
    try:
        from services.wsdl_to_xsd_extractor import merge_xsd_from_wsdl
        print("✅ merge_xsd_from_wsdl imported")
    except Exception as e:
        print(f"❌ merge_xsd_from_wsdl import failed: {e}")
    
    try:
        from services.excel_mapping_service import ExcelMappingService
        print("✅ ExcelMappingService imported")
    except Exception as e:
        print(f"❌ ExcelMappingService import failed: {e}")
    
    try:
        from services.json_to_excel_service import JSONToExcelService
        print("✅ JSONToExcelService imported")
    except Exception as e:
        print(f"❌ JSONToExcelService import failed: {e}")
    
    try:
        from services.case_converter_service import pascal_to_camel, camel_to_pascal
        print("✅ case_converter_service imported")
    except Exception as e:
        print(f"❌ case_converter_service import failed: {e}")
    
    try:
        from services.converter_service import ConverterService
        print("✅ ConverterService imported")
    except Exception as e:
        print(f"❌ ConverterService import failed: {e}")
    
    try:
        from homepage import show_home_page
        print("✅ homepage imported")
    except Exception as e:
        print(f"❌ homepage import failed: {e}")
    
    print("\nImport test completed!")

if __name__ == "__main__":
    test_imports() 