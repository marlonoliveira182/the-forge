#!/usr/bin/env python3
"""
Test script for The Forge API
Creates sample schema files and tests the API endpoints
"""

import json
import tempfile
import requests
from pathlib import Path

# Sample JSON Schema
SAMPLE_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "user": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "User ID"},
                "name": {"type": "string", "description": "User name"},
                "email": {"type": "string", "description": "User email"},
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                        "zip": {"type": "string"}
                    },
                    "required": ["street", "city"]
                }
            },
            "required": ["id", "name", "email"]
        },
        "orders": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "orderId": {"type": "string"},
                    "amount": {"type": "number"},
                    "items": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        }
    },
    "required": ["user"]
}

# Sample XSD Schema
SAMPLE_XSD_SCHEMA = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="customer">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="customerId" type="xs:integer"/>
                <xs:element name="customerName" type="xs:string"/>
                <xs:element name="customerEmail" type="xs:string"/>
                <xs:element name="address" nillable="true">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="street" type="xs:string"/>
                            <xs:element name="city" type="xs:string"/>
                            <xs:element name="zipCode" type="xs:string"/>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>
                <xs:element name="orders" nillable="true">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="order" maxOccurs="unbounded">
                                <xs:complexType>
                                    <xs:sequence>
                                        <xs:element name="orderId" type="xs:string"/>
                                        <xs:element name="orderAmount" type="xs:decimal"/>
                                        <xs:element name="orderItems" nillable="true">
                                            <xs:complexType>
                                                <xs:sequence>
                                                    <xs:element name="item" type="xs:string" maxOccurs="unbounded"/>
                                                </xs:sequence>
                                            </xs:complexType>
                                        </xs:element>
                                    </xs:sequence>
                                </xs:complexType>
                            </xs:element>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''

def create_sample_files():
    """Create sample schema files for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(SAMPLE_JSON_SCHEMA, f, indent=2)
        json_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xsd', delete=False) as f:
        f.write(SAMPLE_XSD_SCHEMA)
        xsd_file = f.name
    
    return json_file, xsd_file

def test_health_check(base_url):
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✓ Health check passed")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Health check error: {e}")

def test_schema_to_excel(base_url, json_file):
    """Test schema to Excel conversion"""
    print("\nTesting schema to Excel conversion...")
    try:
        with open(json_file, 'rb') as f:
            files = {'schema_file': f}
            response = requests.post(f"{base_url}/api/schema-to-excel", files=files)
        
        if response.status_code == 200:
            print("✓ Schema to Excel conversion passed")
            # Save the result
            with open('test_schema.xlsx', 'wb') as f:
                f.write(response.content)
            print("  Saved as: test_schema.xlsx")
        else:
            print(f"✗ Schema to Excel conversion failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Schema to Excel conversion error: {e}")

def test_xsd_to_jsonschema(base_url, xsd_file):
    """Test XSD to JSON Schema conversion"""
    print("\nTesting XSD to JSON Schema conversion...")
    try:
        with open(xsd_file, 'rb') as f:
            files = {'xsd_file': f}
            response = requests.post(f"{base_url}/api/xsd-to-jsonschema", files=files)
        
        if response.status_code == 200:
            print("✓ XSD to JSON Schema conversion passed")
            # Save the result
            with open('test_converted.json', 'wb') as f:
                f.write(response.content)
            print("  Saved as: test_converted.json")
        else:
            print(f"✗ XSD to JSON Schema conversion failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ XSD to JSON Schema conversion error: {e}")

def test_mapping(base_url, json_file, xsd_file):
    """Test schema mapping"""
    print("\nTesting schema mapping...")
    try:
        with open(json_file, 'rb') as f1, open(xsd_file, 'rb') as f2:
            files = {
                'source_file': f1,
                'target_file': f2
            }
            data = {
                'threshold': '0.7',
                'keep_case': 'false'
            }
            response = requests.post(f"{base_url}/api/mapping", files=files, data=data)
        
        if response.status_code == 200:
            print("✓ Schema mapping passed")
            # Save the result
            with open('test_mapping.xlsx', 'wb') as f:
                f.write(response.content)
            print("  Saved as: test_mapping.xlsx")
        else:
            print(f"✗ Schema mapping failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Schema mapping error: {e}")

def main():
    """Run all tests"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python test_api.py <base_url>")
        print("Example: python test_api.py http://localhost:8000")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print(f"Testing The Forge API at: {base_url}")
    print("=" * 50)
    
    # Create sample files
    json_file, xsd_file = create_sample_files()
    
    try:
        # Run tests
        test_health_check(base_url)
        test_schema_to_excel(base_url, json_file)
        test_xsd_to_jsonschema(base_url, xsd_file)
        test_mapping(base_url, json_file, xsd_file)
        
        print("\n" + "=" * 50)
        print("Test completed!")
        print("Generated files:")
        print("- test_schema.xlsx")
        print("- test_converted.json")
        print("- test_mapping.xlsx")
        
    finally:
        # Cleanup
        Path(json_file).unlink(missing_ok=True)
        Path(xsd_file).unlink(missing_ok=True)

if __name__ == "__main__":
    main() 