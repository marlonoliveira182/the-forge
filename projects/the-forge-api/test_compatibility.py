#!/usr/bin/env python3
"""
Test script to verify FastAPI and Pydantic compatibility
"""

import sys
import importlib

def test_imports():
    """Test that all required modules can be imported successfully"""
    print("Testing imports...")
    
    try:
        import fastapi
        print(f"✓ FastAPI imported successfully (version: {fastapi.__version__})")
    except Exception as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        import pydantic
        print(f"✓ Pydantic imported successfully (version: {pydantic.__version__})")
    except Exception as e:
        print(f"✗ Pydantic import failed: {e}")
        return False
    
    try:
        import uvicorn
        print(f"✓ Uvicorn imported successfully (version: {uvicorn.__version__})")
    except Exception as e:
        print(f"✗ Uvicorn import failed: {e}")
        return False
    
    try:
        import openpyxl
        print(f"✓ OpenPyXL imported successfully (version: {openpyxl.__version__})")
    except Exception as e:
        print(f"✗ OpenPyXL import failed: {e}")
        return False
    
    try:
        import jsonschema
        print(f"✓ JSONSchema imported successfully (version: {jsonschema.__version__})")
    except Exception as e:
        print(f"✗ JSONSchema import failed: {e}")
        return False
    
    return True

def test_fastapi_app():
    """Test that a basic FastAPI app can be created"""
    print("\nTesting FastAPI app creation...")
    
    try:
        from fastapi import FastAPI
        app = FastAPI(title="Test API")
        print("✓ FastAPI app created successfully")
        return True
    except Exception as e:
        print(f"✗ FastAPI app creation failed: {e}")
        return False

def test_pydantic_models():
    """Test that Pydantic models work correctly"""
    print("\nTesting Pydantic models...")
    
    try:
        from pydantic import BaseModel
        from typing import Optional
        
        class TestModel(BaseModel):
            name: str
            age: Optional[int] = None
        
        # Test model creation
        model = TestModel(name="test")
        print("✓ Pydantic model created successfully")
        
        # Test model validation
        data = {"name": "test", "age": 25}
        model = TestModel(**data)
        print("✓ Pydantic model validation works")
        
        return True
    except Exception as e:
        print(f"✗ Pydantic model test failed: {e}")
        return False

def main():
    print("Testing The Forge API compatibility...")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        sys.exit(1)
    
    # Test FastAPI
    if not test_fastapi_app():
        print("\n❌ FastAPI tests failed")
        sys.exit(1)
    
    # Test Pydantic
    if not test_pydantic_models():
        print("\n❌ Pydantic tests failed")
        sys.exit(1)
    
    print("\n✅ All compatibility tests passed!")
    print("The updated dependencies should work correctly with Python 3.11+")

if __name__ == "__main__":
    main() 