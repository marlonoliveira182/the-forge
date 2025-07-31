#!/usr/bin/env python3
"""
Test script for The Forge API
Tests all endpoints with sample files
"""

import requests
import json
import os
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_schema_to_excel():
    """Test schema to Excel conversion"""
    print("Testing schema to Excel conversion...")
    
    # Create a simple XSD test file
    test_xsd = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="Person">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="Name" type="xs:string"/>
                <xs:element name="Age" type="xs:integer"/>
                <xs:element name="Email" type="xs:string"/>
            </xs:sequence>
            <xs:attribute name="id" type="xs:string"/>
        </xs:complexType>
    </xs:element>
</xs:schema>'''
    
    # Save test file
    test_file = "test_schema.xsd"
    with open(test_file, "w") as f:
        f.write(test_xsd)
    
    # Test the endpoint
    with open(test_file, "rb") as f:
        files = {"schema_file": ("test_schema.xsd", f, "application/xml")}
        data = {"keep_case": False}
        response = requests.post(f"{BASE_URL}/api/schema-to-excel", files=files, data=data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        # Save the response
        with open("test_output.xlsx", "wb") as f:
            f.write(response.content)
        print("Excel file saved as test_output.xlsx")
    else:
        print(f"Error: {response.text}")
    
    # Clean up
    os.remove(test_file)
    print()

def test_wsdl_to_xsd():
    """Test WSDL to XSD extraction"""
    print("Testing WSDL to XSD extraction...")
    
    # Create a simple WSDL test file
    test_wsdl = '''<?xml version="1.0" encoding="UTF-8"?>
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
                  xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
                  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                  targetNamespace="http://example.com/">
    <wsdl:types>
        <xsd:schema targetNamespace="http://example.com/">
            <xsd:element name="GetPersonRequest">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="id" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="GetPersonResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="name" type="xsd:string"/>
                        <xsd:element name="age" type="xsd:integer"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
    </wsdl:types>
    <wsdl:message name="GetPersonRequest">
        <wsdl:part name="parameters" element="GetPersonRequest"/>
    </wsdl:message>
    <wsdl:message name="GetPersonResponse">
        <wsdl:part name="parameters" element="GetPersonResponse"/>
    </wsdl:message>
    <wsdl:portType name="PersonService">
        <wsdl:operation name="GetPerson">
            <wsdl:input message="GetPersonRequest"/>
            <wsdl:output message="GetPersonResponse"/>
        </wsdl:operation>
    </wsdl:portType>
    <wsdl:binding name="PersonServiceBinding" type="PersonService">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <wsdl:operation name="GetPerson">
            <soap:operation soapAction=""/>
            <wsdl:input><soap:body use="literal"/></wsdl:input>
            <wsdl:output><soap:body use="literal"/></wsdl:output>
        </wsdl:operation>
    </wsdl:binding>
    <wsdl:service name="PersonService">
        <wsdl:port name="PersonServicePort" binding="PersonServiceBinding">
            <soap:address location="http://example.com/PersonService"/>
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>'''
    
    # Save test file
    test_file = "test_service.wsdl"
    with open(test_file, "w") as f:
        f.write(test_wsdl)
    
    # Test the endpoint
    with open(test_file, "rb") as f:
        files = {"wsdl_file": ("test_service.wsdl", f, "application/xml")}
        response = requests.post(f"{BASE_URL}/api/wsdl-to-xsd", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        # Save the response
        with open("test_wsdl_output.xsd", "wb") as f:
            f.write(response.content)
        print("XSD file saved as test_wsdl_output.xsd")
    else:
        print(f"Error: {response.text}")
    
    # Clean up
    os.remove(test_file)
    print()

def test_mapping():
    """Test field mapping between schemas"""
    print("Testing field mapping...")
    
    # Create source JSON schema
    source_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string"}
        }
    }
    
    # Create target JSON schema
    target_schema = {
        "type": "object",
        "properties": {
            "fullName": {"type": "string"},
            "userAge": {"type": "integer"},
            "contactEmail": {"type": "string"}
        }
    }
    
    # Save test files
    with open("source_schema.json", "w") as f:
        json.dump(source_schema, f)
    
    with open("target_schema.json", "w") as f:
        json.dump(target_schema, f)
    
    # Test the endpoint
    with open("source_schema.json", "rb") as source_file, open("target_schema.json", "rb") as target_file:
        files = {
            "source_file": ("source_schema.json", source_file, "application/json"),
            "target_file": ("target_schema.json", target_file, "application/json")
        }
        data = {"threshold": 0.7, "keep_case": False}
        response = requests.post(f"{BASE_URL}/api/mapping", files=files, data=data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        # Save the response
        with open("test_mapping_output.xlsx", "wb") as f:
            f.write(response.content)
        print("Mapping file saved as test_mapping_output.xlsx")
    else:
        print(f"Error: {response.text}")
    
    # Clean up
    os.remove("source_schema.json")
    os.remove("target_schema.json")
    print()

def test_xsd_to_jsonschema():
    """Test XSD to JSON Schema conversion"""
    print("Testing XSD to JSON Schema conversion...")
    
    # Create a simple XSD test file
    test_xsd = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="Person">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="Name" type="xs:string"/>
                <xs:element name="Age" type="xs:integer"/>
                <xs:element name="Email" type="xs:string"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''
    
    # Save test file
    test_file = "test_xsd_to_json.xsd"
    with open(test_file, "w") as f:
        f.write(test_xsd)
    
    # Test the endpoint
    with open(test_file, "rb") as f:
        files = {"xsd_file": ("test_xsd_to_json.xsd", f, "application/xml")}
        data = {"keep_case": False}
        response = requests.post(f"{BASE_URL}/api/xsd-to-jsonschema", files=files, data=data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        # Save the response
        with open("test_xsd_to_json_output.json", "wb") as f:
            f.write(response.content)
        print("JSON Schema file saved as test_xsd_to_json_output.json")
    else:
        print(f"Error: {response.text}")
    
    # Clean up
    os.remove(test_file)
    print()

def main():
    """Run all tests"""
    print("Starting The Forge API tests...")
    print("=" * 50)
    
    try:
        test_health_check()
        test_schema_to_excel()
        test_wsdl_to_xsd()
        test_mapping()
        test_xsd_to_jsonschema()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main() 