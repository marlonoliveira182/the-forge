"""
Pytest configuration and fixtures for The Forge tests.
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Dict, Any


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def sample_xsd_file(temp_dir):
    """Create a sample XSD file for testing."""
    xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="Person">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="Name" type="xs:string" minOccurs="1" maxOccurs="1"/>
                <xs:element name="Age" type="xs:int" minOccurs="1" maxOccurs="1"/>
                <xs:element name="Email" type="xs:string" minOccurs="0" maxOccurs="1"/>
                <xs:element name="Addresses" minOccurs="0" maxOccurs="unbounded">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="Street" type="xs:string"/>
                            <xs:element name="City" type="xs:string"/>
                            <xs:element name="Country" type="xs:string"/>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''
    
    file_path = os.path.join(temp_dir, "sample.xsd")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(xsd_content)
    
    return file_path


@pytest.fixture
def sample_json_schema_file(temp_dir):
    """Create a sample JSON Schema file for testing."""
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Person",
        "type": "object",
        "properties": {
            "person": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "email": {"type": "string"},
                    "addresses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "street": {"type": "string"},
                                "city": {"type": "string"},
                                "country": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["name", "age"]
            }
        },
        "required": ["person"]
    }
    
    import json
    file_path = os.path.join(temp_dir, "sample.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(json_schema, f, indent=2)
    
    return file_path


@pytest.fixture
def complex_xsd_file(temp_dir):
    """Create a complex XSD file for testing."""
    xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="Order">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="OrderId" type="xs:string"/>
                <xs:element name="Customer" type="xs:string"/>
                <xs:element name="Items" minOccurs="1" maxOccurs="unbounded">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="ProductId" type="xs:string"/>
                            <xs:element name="Quantity" type="xs:int"/>
                            <xs:element name="Price" type="xs:decimal"/>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>
                <xs:element name="Total" type="xs:decimal"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''
    
    file_path = os.path.join(temp_dir, "complex.xsd")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(xsd_content)
    
    return file_path


@pytest.fixture
def complex_json_schema_file(temp_dir):
    """Create a complex JSON Schema file for testing."""
    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Order",
        "type": "object",
        "properties": {
            "order": {
                "type": "object",
                "properties": {
                    "orderId": {"type": "string"},
                    "customer": {"type": "string"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "productId": {"type": "string"},
                                "quantity": {"type": "integer"},
                                "price": {"type": "number"}
                            },
                            "required": ["productId", "quantity", "price"]
                        }
                    },
                    "total": {"type": "number"}
                },
                "required": ["orderId", "customer", "items", "total"]
            }
        },
        "required": ["order"]
    }
    
    import json
    file_path = os.path.join(temp_dir, "complex.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(json_schema, f, indent=2)
    
    return file_path


@pytest.fixture
def sample_fields():
    """Sample schema fields for testing."""
    return [
        {
            'levels': ['person'],
            'type': 'object',
            'description': 'Person object',
            'cardinality': '1',
            'details': ''
        },
        {
            'levels': ['person', 'name'],
            'type': 'string',
            'description': 'Person name',
            'cardinality': '1',
            'details': ''
        },
        {
            'levels': ['person', 'age'],
            'type': 'integer',
            'description': 'Person age',
            'cardinality': '1',
            'details': ''
        },
        {
            'levels': ['person', 'addresses', '[]'],
            'type': 'array',
            'description': 'Addresses array',
            'cardinality': '0..unbounded',
            'details': ''
        },
        {
            'levels': ['person', 'addresses', '[]', 'street'],
            'type': 'string',
            'description': 'Street address',
            'cardinality': '0..1',
            'details': ''
        }
    ]


@pytest.fixture
def sample_mapping():
    """Sample mapping results for testing."""
    return [
        {
            'source': 'person.name',
            'target': 'person.name',
            'similarity': 1.0
        },
        {
            'source': 'person.age',
            'target': 'person.age',
            'similarity': 1.0
        },
        {
            'source': 'person.email',
            'target': 'person.email',
            'similarity': 1.0
        },
        {
            'source': 'person.addresses',
            'target': 'person.addresses',
            'similarity': 1.0
        },
        {
            'source': 'person.addresses.[].street',
            'target': 'person.addresses.[].street',
            'similarity': 1.0
        }
    ]


@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        'threshold': 0.7,
        'max_levels': 5,
        'output_format': 'xlsx'
    } 