#!/usr/bin/env python3
"""
Simple test to verify the app and AI description generator are working.
"""

import sys
import os
import tempfile

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_imports():
    """Test that all app imports work correctly."""
    print("🔧 Testing App Imports...")
    
    try:
        # Test importing the main app
        import app
        print("✅ App imports successfully")
        
        # Test importing services
        from services.ai_description_generator import AIDescriptionGenerator
        from services.xsd_parser_service import XSDParser
        from services.json_schema_parser_service import JSONSchemaParser
        from services.excel_export_service import ExcelExporter
        from services.excel_mapping_service import ExcelMappingService
        from services.json_to_excel_service import JSONToExcelService
        
        print("✅ All services import successfully")
        
        # Test creating AI description generator
        ai_generator = AIDescriptionGenerator(enable_ai=True)
        print("✅ AI Description Generator created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_description_generator():
    """Test the AI description generator with a simple file."""
    print("\n🤖 Testing AI Description Generator...")
    
    # Create a simple test file
    test_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="TestOrder">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="orderId" type="xs:string"/>
                <xs:element name="amount" type="xs:decimal"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as f:
        f.write(test_content)
        temp_file_path = f.name
    
    try:
        from services.ai_description_generator import AIDescriptionGenerator
        
        # Create generator
        ai_generator = AIDescriptionGenerator(enable_ai=True)
        
        # Generate descriptions
        descriptions = ai_generator.generate_descriptions(temp_file_path, 'XSD')
        
        print("✅ Descriptions generated successfully")
        print(f"Short description: {descriptions.get('short_description', 'N/A')}")
        print(f"Detailed description length: {len(descriptions.get('detailed_description', ''))} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Description Generator error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        try:
            os.unlink(temp_file_path)
        except:
            pass

def main():
    """Run all tests."""
    print("🧪 Testing The Forge Web App")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_app_imports()
    
    # Test AI description generator
    ai_ok = test_ai_description_generator()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"AI Description Generator: {'✅ PASS' if ai_ok else '❌ FAIL'}")
    
    if imports_ok and ai_ok:
        print("\n🎉 All tests passed! The app is working correctly.")
        print("You can now run: streamlit run app.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 