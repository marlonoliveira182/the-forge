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
    """Test the AI Description Generator with sample data."""
    
    print("🤖 Testing AI Description Generator...")
    
    # Initialize the generator
    generator = AIDescriptionGenerator()
    
    # Test with a sample JSON Schema
    sample_json_schema = {
        "title": "Customer Order",
        "description": "Schema for customer order data",
        "type": "object",
        "properties": {
            "orderId": {
                "type": "string",
                "description": "Unique order identifier"
            },
            "customerId": {
                "type": "string",
                "description": "Customer identifier"
            },
            "orderDate": {
                "type": "string",
                "format": "date-time",
                "description": "Order creation date"
            },
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "productId": {"type": "string"},
                        "quantity": {"type": "integer"},
                        "price": {"type": "number"}
                    }
                }
            },
            "totalAmount": {
                "type": "number",
                "description": "Total order amount"
            }
        },
        "required": ["orderId", "customerId", "orderDate", "items", "totalAmount"]
    }
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        json.dump(sample_json_schema, temp_file)
        temp_file_path = temp_file.name
    
    try:
        # Generate descriptions
        print("📝 Generating descriptions...")
        result = generator.generate_descriptions(temp_file_path, 'json_schema')
        
        # Display results
        print("\n" + "="*50)
        print("📋 GENERATED DESCRIPTIONS")
        print("="*50)
        
        print("\n🔹 Short Description:")
        print(result['short_description'])
        
        print("\n📋 Detailed Description:")
        print(result['detailed_description'])
        
        print("\n🔍 Schema Information:")
        schema_info = result.get('schema_info', {})
        print(f"File Type: {schema_info.get('file_type', 'Unknown')}")
        print(f"Total Structures: {schema_info.get('total_structures', 0)}")
        
        if schema_info.get('structures'):
            main_structure = schema_info['structures'][0]
            print(f"Main Structure: {main_structure.get('name', 'Unknown')}")
            print(f"Field Count: {len(main_structure.get('fields', []))}")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_xml_schema():
    """Test with a sample XML Schema."""
    
    print("\n🔧 Testing XML Schema parsing...")
    
    generator = AIDescriptionGenerator()
    
    # Sample XSD content
    sample_xsd = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="order">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="orderId" type="xs:string"/>
                <xs:element name="customerId" type="xs:string"/>
                <xs:element name="orderDate" type="xs:dateTime"/>
                <xs:element name="items" type="itemList"/>
                <xs:element name="totalAmount" type="xs:decimal"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
    
    <xs:complexType name="itemList">
        <xs:sequence>
            <xs:element name="item" type="orderItem" maxOccurs="unbounded"/>
        </xs:sequence>
    </xs:complexType>
    
    <xs:complexType name="orderItem">
        <xs:sequence>
            <xs:element name="productId" type="xs:string"/>
            <xs:element name="quantity" type="xs:integer"/>
            <xs:element name="price" type="xs:decimal"/>
        </xs:sequence>
    </xs:complexType>
</xs:schema>'''
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as temp_file:
        temp_file.write(sample_xsd)
        temp_file_path = temp_file.name
    
    try:
        # Generate descriptions
        print("📝 Generating XSD descriptions...")
        result = generator.generate_descriptions(temp_file_path, 'xsd')
        
        print("\n🔹 Short Description:")
        print(result['short_description'])
        
        print("\n📋 Detailed Description:")
        print(result['detailed_description'])
        
        print("\n✅ XSD test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during XSD test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    print("🔨 The Forge - AI Description Generator Test")
    print("="*50)
    
    # Test JSON Schema
    test_ai_description_generator()
    
    # Test XML Schema
    test_xml_schema()
    
    print("\n🎉 All tests completed!") 