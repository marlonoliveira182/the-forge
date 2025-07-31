# Test script for The Forge Web App
import os
import sys

def test_imports():
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
    
    try:
        import openpyxl
        print("✅ openpyxl imported successfully")
    except ImportError as e:
        print(f"❌ openpyxl import failed: {e}")
    
    try:
        import jsonschema
        print("✅ jsonschema imported successfully")
    except ImportError as e:
        print(f"❌ jsonschema import failed: {e}")

def test_services():
    try:
        from services.xsd_parser_service import XSDParser
        print("✅ XSDParser imported successfully")
    except ImportError as e:
        print(f"❌ XSDParser import failed: {e}")
    
    try:
        from services.excel_export_service import ExcelExporter
        print("✅ ExcelExporter imported successfully")
    except ImportError as e:
        print(f"❌ ExcelExporter import failed: {e}")

if __name__ == "__main__":
    print("Testing The Forge Web App...")
    test_imports()
    test_services()
    print("Test completed.") 