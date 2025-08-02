import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.json_to_schema_converter import JSONToSchemaConverter

def test_json_schema_validation():
    """Test JSON schema validation to identify the issue."""
    
    # Sample JSON example that might cause validation issues
    json_example = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "active": True,
        "tags": ["developer", "python"],
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": "12345"
        },
        "scores": [85, 92, 78]
    }
    
    converter = JSONToSchemaConverter()
    
    # Generate schema
    schema = converter.convert_json_example_to_schema(json_example, "TestSchema")
    
    print("Generated Schema:")
    print(json.dumps(schema, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Test validation
    is_valid = converter.validate_schema(schema)
    print(f"Schema validation result: {is_valid}")
    
    # Let's also test the test instance creation
    test_instance = converter._create_test_instance(schema)
    print(f"\nTest instance created: {json.dumps(test_instance, indent=2)}")
    
    # Try to validate the test instance manually
    try:
        from jsonschema import validate, ValidationError
        validate(instance=test_instance, schema=schema)
        print("✅ Manual validation of test instance succeeded")
    except ValidationError as e:
        print(f"❌ Manual validation of test instance failed: {e}")
        print(f"Validation error path: {e.path}")
        print(f"Validation error message: {e.message}")
    
    # Let's also try with the original JSON example
    try:
        validate(instance=json_example, schema=schema)
        print("✅ Original JSON example validates against generated schema")
    except ValidationError as e:
        print(f"❌ Original JSON example fails validation: {e}")
        print(f"Validation error path: {e.path}")
        print(f"Validation error message: {e.message}")

if __name__ == "__main__":
    test_json_schema_validation() 