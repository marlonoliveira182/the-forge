#!/usr/bin/env python3
"""
Test script for the AI Description Generator functionality.
"""

import sys
import os
import tempfile
import json

# Add the current directory to the path so we can import the service
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_description_generator import AIDescriptionGenerator

def test_ai_description_generator():
    """Test the AI Description Generator with a sample JSON Schema."""
    print("🔨 The Forge - AI Description Generator Test")
    print("=" * 50)
    print("🤖 Testing AI Description Generator...")
    print("📝 Generating descriptions...")
    
    # Create a temporary JSON Schema file
    json_schema_content = '''
    {
        "title": "Customer Order",
        "type": "object",
        "properties": {
            "customerId": {
                "type": "string",
                "description": "Customer identifier"
            },
            "orderId": {
                "type": "string",
                "description": "Order identifier"
            },
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "productId": {"type": "string"},
                        "quantity": {"type": "integer"}
                    }
                }
            },
            "totalAmount": {
                "type": "number",
                "description": "Total order amount"
            },
            "status": {
                "type": "string",
                "enum": ["pending", "confirmed", "shipped"]
            }
        },
        "required": ["customerId", "orderId", "items"]
    }
    '''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(json_schema_content)
        temp_file = f.name
    
    try:
        # Initialize the generator
        generator = AIDescriptionGenerator()
        
        # Generate descriptions
        result = generator.generate_descriptions(temp_file, 'json_schema')
        
        print("\n" + "=" * 50)
        print("📋 GENERATED DESCRIPTIONS")
        print("=" * 50)
        print()
        
        print("🔹 Short Description:")
        print(result['short_description'])
        print()
        
        print("📋 Detailed Description:")
        print(result['detailed_description'])
        print()
        
        # Display schema information
        schema_info = result.get('schema_info', {})
        print("🔍 Schema Information:")
        print(f"File Type: {schema_info.get('file_type', 'Unknown')}")
        print(f"Total Structures: {schema_info.get('total_structures', 0)}")
        
        structures = schema_info.get('structures', [])
        if structures:
            main_structure = structures[0]
            print(f"Main Structure: {main_structure.get('name', 'Unknown')}")
            print(f"Field Count: {len(main_structure.get('fields', []))}")
        
        print()
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def test_xml_schema():
    """Test XML Schema parsing."""
    print("\n🔧 Testing XML Schema parsing...")
    print("📝 Generating XSD descriptions...")
    
    # Create a temporary XSD file
    xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <xsd:element name="Order">
        <xsd:complexType>
            <xsd:sequence>
                <xsd:element name="CustomerID" type="xsd:string"/>
                <xsd:element name="OrderID" type="xsd:string"/>
                <xsd:element name="OrderDate" type="xsd:date"/>
                <xsd:element name="Items" type="xsd:string" maxOccurs="unbounded"/>
                <xsd:element name="TotalAmount" type="xsd:decimal"/>
            </xsd:sequence>
        </xsd:complexType>
    </xsd:element>
</xsd:schema>'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as f:
        f.write(xsd_content)
        temp_file = f.name
    
    try:
        generator = AIDescriptionGenerator()
        result = generator.generate_descriptions(temp_file, 'xsd')
        
        print("\n🔹 Short Description:")
        print(result['short_description'])
        print()
        
        print("📋 Detailed Description:")
        print(result['detailed_description'])
        print()
        
        print("✅ XSD test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error processing xsd file: {e}")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def test_wsdl():
    """Test WSDL parsing."""
    print("\n🌐 Testing WSDL parsing...")
    print("📝 Generating WSDL descriptions...")
    
    # Use the test WSDL file
    wsdl_file = "test_wsdl.xml"
    
    try:
        generator = AIDescriptionGenerator()
        result = generator.generate_descriptions(wsdl_file, 'wsdl')
        
        print("\n🔹 Short Description:")
        print(result['short_description'])
        print()
        
        print("📋 Detailed Description:")
        print(result['detailed_description'])
        print()
        
        # Display schema information
        schema_info = result.get('schema_info', {})
        print("🔍 Schema Information:")
        print(f"File Type: {schema_info.get('file_type', 'Unknown')}")
        print(f"Total Structures: {schema_info.get('total_structures', 0)}")
        
        structures = schema_info.get('structures', [])
        if structures:
            for i, structure in enumerate(structures):
                print(f"Structure {i+1}: {structure.get('name', 'Unknown')} ({structure.get('type', 'Unknown')})")
        
        print()
        print("✅ WSDL test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error processing wsdl file: {e}")

if __name__ == "__main__":
    test_ai_description_generator()
    test_xml_schema()
    test_wsdl()
    print("\n🎉 All tests completed!") 