#!/usr/bin/env python3
"""
Test script to verify deployment dependencies work correctly
"""

def test_imports():
    """Test all required imports"""
    try:
        print("Testing imports...")
        
        # Test FastAPI and related imports
        from fastapi import FastAPI, UploadFile, File, HTTPException, Form
        print("✓ FastAPI imports successful")
        
        from fastapi.responses import FileResponse, JSONResponse
        print("✓ FastAPI responses imports successful")
        
        from fastapi.middleware.cors import CORSMiddleware
        print("✓ CORS middleware import successful")
        
        # Test uvicorn
        import uvicorn
        print("✓ uvicorn import successful")
        
        # Test openpyxl
        import openpyxl
        print("✓ openpyxl import successful")
        
        # Test jsonschema
        import jsonschema
        print("✓ jsonschema import successful")
        
        # Test python-multipart
        import python_multipart
        print("✓ python-multipart import successful")
        
        # Test pydantic
        import pydantic
        print("✓ pydantic import successful")
        
        # Test lxml
        import lxml
        print("✓ lxml import successful")
        
        # Test xml parsing
        import xml.etree.ElementTree as ET
        print("✓ xml.etree.ElementTree import successful")
        
        # Test json
        import json
        print("✓ json import successful")
        
        # Test pathlib
        from pathlib import Path
        print("✓ pathlib import successful")
        
        # Test our services
        from services.xsd_parser import XSDParser
        print("✓ XSDParser import successful")
        
        from services.json_schema_parser import JSONSchemaParser
        print("✓ JSONSchemaParser import successful")
        
        from services.excel_generator import ExcelGenerator
        print("✓ ExcelGenerator import successful")
        
        from services.wsdl_extractor import WSDLExtractor
        print("✓ WSDLExtractor import successful")
        
        from services.mapping_service import MappingService
        print("✓ MappingService import successful")
        
        print("\n✅ All imports successful! Deployment should work correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    try:
        print("\nTesting basic functionality...")
        
        # Test XSD Parser
        parser = XSDParser()
        print("✓ XSDParser instantiation successful")
        
        # Test JSON Schema Parser
        json_parser = JSONSchemaParser()
        print("✓ JSONSchemaParser instantiation successful")
        
        # Test Excel Generator
        excel_gen = ExcelGenerator()
        print("✓ ExcelGenerator instantiation successful")
        
        # Test WSDL Extractor
        wsdl_extractor = WSDLExtractor()
        print("✓ WSDLExtractor instantiation successful")
        
        # Test Mapping Service
        mapping_service = MappingService()
        print("✓ MappingService instantiation successful")
        
        print("✅ All services instantiate correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

if __name__ == "__main__":
    print("Starting deployment test...")
    print("=" * 50)
    
    imports_ok = test_imports()
    if imports_ok:
        functionality_ok = test_basic_functionality()
        if functionality_ok:
            print("\n🎉 All tests passed! Deployment should be successful.")
        else:
            print("\n❌ Functionality tests failed.")
    else:
        print("\n❌ Import tests failed.") 