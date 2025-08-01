#!/usr/bin/env python3
"""
Test script for JSON Schema mapping functionality.
Tests the new single-sheet approach for JSON Schema to JSON Schema mapping.
"""

import json
import tempfile
import os
import sys

# Add the current directory to Python path
sys.path.append('.')

from services.json_schema_parser_service import JSONSchemaParser
from services.excel_mapping_service import ExcelMappingService

def create_test_json_schemas():
    """Create test JSON schemas for mapping."""
    
    # Source JSON Schema
    source_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["id", "name"],
        "properties": {
            "id": {
                "type": "integer",
                "description": "Unique identifier"
            },
            "name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 100,
                "description": "User name"
            },
            "email": {
                "type": "string",
                "format": "email",
                "description": "Email address"
            },
            "age": {
                "type": "integer",
                "minimum": 0,
                "maximum": 150,
                "description": "Age in years"
            },
            "addresses": {
                "type": "array",
                "minItems": 0,
                "maxItems": 5,
                "items": {
                    "type": "object",
                    "required": ["street", "city"],
                    "properties": {
                        "street": {
                            "type": "string",
                            "description": "Street address"
                        },
                        "city": {
                            "type": "string",
                            "description": "City name"
                        },
                        "zipCode": {
                            "type": "string",
                            "pattern": "^[0-9]{5}(-[0-9]{4})?$",
                            "description": "ZIP code"
                        }
                    }
                }
            },
            "preferences": {
                "type": "object",
                "properties": {
                    "theme": {
                        "type": "string",
                        "enum": ["light", "dark", "auto"],
                        "default": "auto"
                    },
                    "notifications": {
                        "type": "boolean",
                        "default": True
                    }
                }
            }
        }
    }
    
    # Target JSON Schema (similar but with some differences)
    target_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["user_id", "full_name"],
        "properties": {
            "user_id": {
                "type": "integer",
                "description": "User identifier"
            },
            "full_name": {
                "type": "string",
                "minLength": 2,
                "maxLength": 200,
                "description": "Full user name"
            },
            "email_address": {
                "type": "string",
                "format": "email",
                "description": "User email"
            },
            "user_age": {
                "type": "integer",
                "minimum": 1,
                "maximum": 120,
                "description": "User age"
            },
            "contact_addresses": {
                "type": "array",
                "minItems": 1,
                "maxItems": 10,
                "items": {
                    "type": "object",
                    "required": ["address_line", "city_name"],
                    "properties": {
                        "address_line": {
                            "type": "string",
                            "description": "Address line"
                        },
                        "city_name": {
                            "type": "string",
                            "description": "City name"
                        },
                        "postal_code": {
                            "type": "string",
                            "pattern": "^[0-9]{5}(-[0-9]{4})?$",
                            "description": "Postal code"
                        }
                    }
                }
            },
            "user_settings": {
                "type": "object",
                "properties": {
                    "display_theme": {
                        "type": "string",
                        "enum": ["light", "dark", "system"],
                        "default": "system"
                    },
                    "enable_notifications": {
                        "type": "boolean",
                        "default": True
                    }
                }
            }
        }
    }
    
    return source_schema, target_schema

def test_json_schema_parsing():
    """Test JSON Schema parsing functionality."""
    print("Testing JSON Schema parsing...")
    
    source_schema, target_schema = create_test_json_schemas()
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as source_file:
        json.dump(source_schema, source_file, indent=2)
        source_path = source_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as target_file:
        json.dump(target_schema, target_file, indent=2)
        target_path = target_file.name
    
    try:
        # Test JSON Schema parser
        parser = JSONSchemaParser()
        
        # Parse source schema
        source_rows = parser.parse_json_schema_file(source_path)
        print(f"Source schema parsed: {len(source_rows)} rows")
        
        # Parse target schema
        target_rows = parser.parse_json_schema_file(target_path)
        print(f"Target schema parsed: {len(target_rows)} rows")
        
        # Print some sample rows
        print("\nSource schema sample rows:")
        for i, row in enumerate(source_rows[:3]):
            print(f"  {i+1}. {row['levels']} -> {row['Type']} ({row['Cardinality']})")
        
        print("\nTarget schema sample rows:")
        for i, row in enumerate(target_rows[:3]):
            print(f"  {i+1}. {row['levels']} -> {row['Type']} ({row['Cardinality']})")
        
        # Test mapping service
        mapping_service = ExcelMappingService()
        mapping_rows = mapping_service.generate_mapping_from_schemas(source_schema, target_schema)
        
        print(f"\nGenerated mapping: {len(mapping_rows)} rows")
        
        # Print some sample mappings
        print("\nSample mappings:")
        for i, mapping in enumerate(mapping_rows[:5]):
            print(f"  {i+1}. {mapping['Source Path']} -> {mapping['Target Path']}")
        
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        return False
    
    finally:
        # Clean up temporary files
        os.unlink(source_path)
        os.unlink(target_path)

def test_json_schema_mapping_logic():
    """Test the JSON Schema mapping logic specifically."""
    print("\nTesting JSON Schema mapping logic...")
    
    source_schema, target_schema = create_test_json_schemas()
    
    # Test the new cardinality determination
    parser = JSONSchemaParser()
    
    # Test array cardinality
    array_prop = {
        "type": "array",
        "minItems": 1,
        "maxItems": 5
    }
    cardinality = parser._determine_cardinality(array_prop)
    print(f"Array cardinality: {cardinality}")
    
    # Test required field cardinality
    required_prop = {"type": "string"}
    cardinality = parser._determine_cardinality(required_prop, True)
    print(f"Required field cardinality: {cardinality}")
    
    # Test optional field cardinality
    optional_prop = {"type": "string"}
    cardinality = parser._determine_cardinality(optional_prop, False)
    print(f"Optional field cardinality: {cardinality}")
    
    # Test details extraction
    detailed_prop = {
        "type": "string",
        "minLength": 1,
        "maxLength": 100,
        "pattern": "^[a-zA-Z]+$",
        "format": "email"
    }
    details = parser._extract_details(detailed_prop)
    print(f"Property details: {details}")

if __name__ == "__main__":
    print("=== JSON Schema Mapping Test ===")
    
    # Test JSON Schema parsing
    if test_json_schema_parsing():
        print("✅ JSON Schema parsing test passed")
    else:
        print("❌ JSON Schema parsing test failed")
    
    # Test mapping logic
    test_json_schema_mapping_logic()
    
    print("\n=== Test completed ===") 