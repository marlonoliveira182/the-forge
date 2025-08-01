#!/usr/bin/env python3
"""
Test script for the converter services.
"""

import json
import tempfile
import os
from services.converter_service import ConverterService

def test_json_to_schema_converter():
    """Test JSON example to schema conversion."""
    print("🧪 Testing JSON Example to Schema Converter")
    print("=" * 50)
    
    # Test JSON example
    test_json = {
        "orderId": "ORD-2024-001",
        "customer": {
            "id": "CUST-12345",
            "name": "John Doe",
            "email": "john.doe@example.com"
        },
        "items": [
            {
                "productId": "PROD-001",
                "name": "Laptop Computer",
                "quantity": 2,
                "unitPrice": 1299.99
            }
        ]
    }
    
    converter = ConverterService()
    
    try:
        # Convert JSON example to schema
        schema = converter.convert_json_example_to_schema(test_json, "OrderSchema")
        
        print("✅ JSON to Schema conversion successful!")
        print(f"📊 Schema statistics: {converter.get_conversion_statistics('json_to_schema', schema)}")
        
        # Validate the schema
        is_valid = converter.validate_conversion('json_to_schema', None, schema)
        print(f"✅ Schema validation: {'PASSED' if is_valid else 'FAILED'}")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON to Schema conversion failed: {str(e)}")
        return False

def test_xml_to_xsd_converter():
    """Test XML example to XSD conversion."""
    print("\n🧪 Testing XML Example to XSD Converter")
    print("=" * 50)
    
    # Test XML example
    test_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<order>
    <orderId>ORD-2024-001</orderId>
    <customer>
        <id>CUST-12345</id>
        <name>John Doe</name>
        <email>john.doe@example.com</email>
    </customer>
    <items>
        <item>
            <productId>PROD-001</productId>
            <name>Laptop Computer</name>
            <quantity>2</quantity>
            <unitPrice>1299.99</unitPrice>
        </item>
    </items>
</order>'''
    
    converter = ConverterService()
    
    try:
        # Convert XML example to XSD
        xsd = converter.convert_xml_example_to_xsd(test_xml, "OrderSchema")
        
        print("✅ XML to XSD conversion successful!")
        print(f"📊 XSD statistics: {converter.get_conversion_statistics('xml_to_xsd', xsd)}")
        
        # Validate the XSD
        is_valid = converter.validate_conversion('xml_to_xsd', None, xsd)
        print(f"✅ XSD validation: {'PASSED' if is_valid else 'FAILED'}")
        
        return True
        
    except Exception as e:
        print(f"❌ XML to XSD conversion failed: {str(e)}")
        return False

def test_xsd_to_xml_converter():
    """Test XSD to XML example conversion."""
    print("\n🧪 Testing XSD to XML Example Converter")
    print("=" * 50)
    
    # Test XSD schema
    test_xsd = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="order" type="orderType"/>
    <xs:complexType name="orderType">
        <xs:sequence>
            <xs:element name="orderId" type="xs:string"/>
            <xs:element name="customer" type="customerType"/>
            <xs:element name="items" type="itemsType"/>
        </xs:sequence>
    </xs:complexType>
    <xs:complexType name="customerType">
        <xs:sequence>
            <xs:element name="id" type="xs:string"/>
            <xs:element name="name" type="xs:string"/>
            <xs:element name="email" type="xs:string"/>
        </xs:sequence>
    </xs:complexType>
    <xs:complexType name="itemsType">
        <xs:sequence>
            <xs:element name="item" type="itemType" maxOccurs="unbounded"/>
        </xs:sequence>
    </xs:complexType>
    <xs:complexType name="itemType">
        <xs:sequence>
            <xs:element name="productId" type="xs:string"/>
            <xs:element name="name" type="xs:string"/>
            <xs:element name="quantity" type="xs:integer"/>
            <xs:element name="unitPrice" type="xs:decimal"/>
        </xs:sequence>
    </xs:complexType>
</xs:schema>'''
    
    converter = ConverterService()
    
    try:
        # Convert XSD to XML example
        xml_example = converter.convert_xsd_to_xml_example(test_xsd, "order")
        
        print("✅ XSD to XML conversion successful!")
        print(f"📊 XML statistics: {converter.get_conversion_statistics('xsd_to_xml', xml_example)}")
        
        # Validate the XML
        is_valid = converter.validate_conversion('xsd_to_xml', None, xml_example)
        print(f"✅ XML validation: {'PASSED' if is_valid else 'FAILED'}")
        
        return True
        
    except Exception as e:
        print(f"❌ XSD to XML conversion failed: {str(e)}")
        return False

def test_json_schema_to_json_converter():
    """Test JSON schema to JSON example conversion."""
    print("\n🧪 Testing JSON Schema to JSON Example Converter")
    print("=" * 50)
    
    # Test JSON schema
    test_schema = {
        "type": "object",
        "properties": {
            "orderId": {"type": "string"},
            "customer": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"}
                },
                "required": ["id", "name", "email"]
            },
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "productId": {"type": "string"},
                        "name": {"type": "string"},
                        "quantity": {"type": "integer"},
                        "unitPrice": {"type": "number"}
                    },
                    "required": ["productId", "name", "quantity", "unitPrice"]
                }
            }
        },
        "required": ["orderId", "customer", "items"]
    }
    
    converter = ConverterService()
    
    try:
        # Convert JSON schema to JSON examples
        examples = converter.convert_json_schema_to_json_example(test_schema, 2)
        
        print("✅ JSON Schema to JSON conversion successful!")
        print(f"📊 Examples statistics: {converter.get_conversion_statistics('json_schema_to_json', examples)}")
        
        # Validate the examples
        is_valid = converter.validate_conversion('json_schema_to_json', test_schema, examples)
        print(f"✅ Examples validation: {'PASSED' if is_valid else 'FAILED'}")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON Schema to JSON conversion failed: {str(e)}")
        return False

def main():
    """Run all converter tests."""
    print("🔨 Testing The Forge Converter Services")
    print("=" * 60)
    
    tests = [
        test_json_to_schema_converter,
        test_xml_to_xsd_converter,
        test_xsd_to_xml_converter,
        test_json_schema_to_json_converter
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All converter tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    main() 