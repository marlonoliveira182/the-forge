#!/usr/bin/env python3
"""
Test script for the enhanced converter functionality.
"""

import json
import tempfile
import os
from services.converter_service import ConverterService

def test_enhanced_converter():
    """Test the enhanced converter service."""
    print("🔧 Testing Enhanced Converter Service...")
    
    # Initialize converter service
    converter = ConverterService()
    
    # Test source types
    print("\n📋 Testing source types:")
    source_types = converter.get_source_types()
    print(f"Available source types: {source_types}")
    
    # Test target types for each source
    print("\n🎯 Testing target types for each source:")
    for source_type in source_types:
        target_types = converter.get_target_types_for_source(source_type)
        print(f"  {source_type} → {target_types}")
    
    # Test conversion keys
    print("\n🔑 Testing conversion keys:")
    test_conversions = [
        ("json example", "json schema"),
        ("xml example", "xsd"),
        ("xsd", "xml example"),
        ("json schema", "json example"),
        ("json example", "excel"),
        ("json schema", "excel"),
        ("xsd", "excel"),
        ("xml example", "excel"),
        ("xsd", "json schema"),
        ("json schema", "xsd"),
        ("xml example", "json schema"),
        ("json example", "xml"),
        ("json schema", "xml")
    ]
    
    for source, target in test_conversions:
        conversion_key = converter.get_conversion_key(source, target)
        print(f"  {source} → {target}: {conversion_key}")
    
    # Test supported conversions
    print("\n📊 Testing supported conversions:")
    supported = converter.get_supported_conversions()
    for key, info in supported.items():
        print(f"  {key}: {info['name']}")
    
    print("\n✅ Enhanced converter tests completed!")

def test_json_conversion():
    """Test JSON example to schema conversion."""
    print("\n🔄 Testing JSON example to schema conversion...")
    
    converter = ConverterService()
    
    # Test JSON data
    test_json = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": "12345"
        },
        "hobbies": ["reading", "swimming"],
        "active": True
    }
    
    try:
        schema = converter.convert_json_example_to_schema(test_json, "TestSchema")
        print("✅ JSON to schema conversion successful!")
        print(f"Schema properties: {len(schema.get('properties', {}))}")
        
        # Test validation
        is_valid = converter.validate_conversion("json_to_schema", None, schema)
        print(f"Schema validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        # Test statistics
        stats = converter.get_conversion_statistics("json_to_schema", schema)
        print(f"Statistics: {stats}")
        
    except Exception as e:
        print(f"❌ JSON conversion failed: {e}")

def test_xml_conversion():
    """Test XML example to XSD conversion."""
    print("\n🔄 Testing XML example to XSD conversion...")
    
    converter = ConverterService()
    
    # Test XML data
    test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<person>
    <name>John Doe</name>
    <age>30</age>
    <email>john@example.com</email>
    <address>
        <street>123 Main St</street>
        <city>Anytown</city>
        <zip>12345</zip>
    </address>
    <hobbies>
        <hobby>reading</hobby>
        <hobby>swimming</hobby>
    </hobbies>
    <active>true</active>
</person>"""
    
    try:
        xsd = converter.convert_xml_example_to_xsd(test_xml, "TestSchema")
        print("✅ XML to XSD conversion successful!")
        print(f"XSD length: {len(xsd)} characters")
        
        # Test validation
        is_valid = converter.validate_conversion("xml_to_xsd", None, xsd)
        print(f"XSD validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        # Test statistics
        stats = converter.get_conversion_statistics("xml_to_xsd", xsd)
        print(f"Statistics: {stats}")
        
    except Exception as e:
        print(f"❌ XML conversion failed: {e}")

def test_xsd_conversion():
    """Test XSD to XML example conversion."""
    print("\n🔄 Testing XSD to XML example conversion...")
    
    converter = ConverterService()
    
    # Test XSD data
    test_xsd = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="person">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="name" type="xs:string"/>
                <xs:element name="age" type="xs:integer"/>
                <xs:element name="email" type="xs:string"/>
                <xs:element name="address">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="street" type="xs:string"/>
                            <xs:element name="city" type="xs:string"/>
                            <xs:element name="zip" type="xs:string"/>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>
                <xs:element name="hobbies">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="hobby" type="xs:string" maxOccurs="unbounded"/>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>
                <xs:element name="active" type="xs:boolean"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>"""
    
    try:
        xml = converter.convert_xsd_to_xml_example(test_xsd)
        print("✅ XSD to XML conversion successful!")
        print(f"XML length: {len(xml)} characters")
        
        # Test validation
        is_valid = converter.validate_conversion("xsd_to_xml", None, xml)
        print(f"XML validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        # Test statistics
        stats = converter.get_conversion_statistics("xsd_to_xml", xml)
        print(f"Statistics: {stats}")
        
    except Exception as e:
        print(f"❌ XSD conversion failed: {e}")

def test_json_schema_conversion():
    """Test JSON schema to JSON example conversion."""
    print("\n🔄 Testing JSON schema to JSON example conversion...")
    
    converter = ConverterService()
    
    # Test JSON schema
    test_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0},
            "email": {"type": "string", "format": "email"},
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "zip": {"type": "string"}
                },
                "required": ["street", "city"]
            },
            "hobbies": {
                "type": "array",
                "items": {"type": "string"}
            },
            "active": {"type": "boolean"}
        },
        "required": ["name", "age"]
    }
    
    try:
        examples = converter.convert_json_schema_to_json_example(test_schema, 2)
        print("✅ JSON schema to JSON example conversion successful!")
        print(f"Generated {len(examples)} examples")
        
        # Test validation
        is_valid = converter.validate_conversion("json_schema_to_json", test_schema, examples)
        print(f"Examples validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        # Test statistics
        stats = converter.get_conversion_statistics("json_schema_to_json", examples)
        print(f"Statistics: {stats}")
        
    except Exception as e:
        print(f"❌ JSON schema conversion failed: {e}")

def main():
    """Run all tests."""
    print("🚀 Starting Enhanced Converter Tests...")
    
    test_enhanced_converter()
    test_json_conversion()
    test_xml_conversion()
    test_xsd_conversion()
    test_json_schema_conversion()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main() 