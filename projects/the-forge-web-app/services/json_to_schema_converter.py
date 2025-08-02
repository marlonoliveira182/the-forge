import json
import re
from typing import Any, Dict, List, Set, Optional
from jsonschema import validate, ValidationError


class JSONToSchemaConverter:
    """
    Service for converting JSON examples to JSON schemas.
    """
    
    def __init__(self):
        self.processed_arrays: Set[str] = set()
    
    def convert_json_example_to_schema(self, json_data: Any, schema_name: str = "GeneratedSchema") -> Dict[str, Any]:
        """
        Convert a JSON example to a JSON schema.
        
        Args:
            json_data: The JSON data (dict, list, or primitive)
            schema_name: Name for the generated schema
            
        Returns:
            Dict containing the generated JSON schema
        """
        self.processed_arrays.clear()
        
        if isinstance(json_data, dict):
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "title": schema_name,
                "properties": {},
                "required": []
            }
            
            for key, value in json_data.items():
                schema["properties"][key] = self._generate_schema_from_data(value, key)
                if value is not None:  # Only add to required if not null
                    schema["required"].append(key)
            
            return schema
        elif isinstance(json_data, list):
            if len(json_data) == 0:
                return {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "array",
                    "items": {},
                    "title": schema_name
                }
            
            # Use the first item as template
            item_schema = self._generate_schema_from_data(json_data[0], "item")
            return {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "array",
                "items": item_schema,
                "title": schema_name,
                "minItems": 1,
                "uniqueItems": True
            }
        else:
            # Primitive value
            schema = self._generate_schema_from_data(json_data, "root")
            schema["$schema"] = "http://json-schema.org/draft-07/schema#"
            schema["title"] = schema_name
            return schema
    
    def _generate_schema_from_data(self, data: Any, name: str = "root", path: str = "") -> Dict[str, Any]:
        """
        Recursively generate schema from data structure.
        """
        if data is None:
            return {"type": "null"}
        
        if isinstance(data, bool):
            return {"type": "boolean"}
        
        if isinstance(data, int):
            return {
                "type": "integer",
                "minimum": 0 if data >= 0 else None
            }
        
        if isinstance(data, float):
            return {
                "type": "number",
                "minimum": 0 if data >= 0 else None
            }
        
        if isinstance(data, str):
            schema = {"type": "string"}
            
            # Add format detection
            format_type = self._detect_string_format(data)
            if format_type:
                schema["format"] = format_type
            
            # Add length constraints
            if len(data) > 0:
                schema["minLength"] = 1
                schema["maxLength"] = len(data)
                
                # Add pattern for email
                if format_type == "email":
                    schema["pattern"] = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            
            return schema
        
        if isinstance(data, list):
            array_key = f"{path}.{name}" if path else name
            
            # Check if we've already processed this array structure
            if array_key in self.processed_arrays:
                return {"type": "array", "items": {}}  # Avoid repetition
            
            self.processed_arrays.add(array_key)
            
            if len(data) == 0:
                return {"type": "array", "items": {}}
            
            # Use the first item as template, but check for consistency
            first_item_schema = self._generate_schema_from_data(data[0], "item", array_key)
            
            # Check if all items have the same structure
            consistent = True
            for item in data[1:]:
                if not self._compare_structures(first_item_schema, self._generate_schema_from_data(item, "item", array_key)):
                    consistent = False
                    break
            
            schema = {
                "type": "array",
                "items": first_item_schema,
                "minItems": 1,
                "uniqueItems": True
            }
            
            return schema
        
        if isinstance(data, dict):
            properties = {}
            required = []
            
            for key, value in data.items():
                properties[key] = self._generate_schema_from_data(value, key, f"{path}.{name}" if path else name)
                if value is not None:  # Only add to required if not null
                    required.append(key)
            
            schema = {"type": "object", "properties": properties}
            if required:
                schema["required"] = required
            
            return schema
        
        # Fallback for unknown types
        return {"type": "string"}
    
    def _detect_string_format(self, value: str) -> Optional[str]:
        """
        Detect the format of a string value.
        """
        if not value:
            return None
        
        # Email
        if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
            return "email"
        
        # Date (ISO format)
        if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            return "date"
        
        # DateTime (ISO format)
        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", value):
            return "date-time"
        
        # UUID
        if re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", value, re.IGNORECASE):
            return "uuid"
        
        # URL
        if re.match(r"^https?://", value):
            return "uri"
        
        # IPv4
        if re.match(r"^(\d{1,3}\.){3}\d{1,3}$", value):
            return "ipv4"
        
        # IPv6
        if ":" in value and re.match(r"^[0-9a-fA-F:]+$", value):
            return "ipv6"
        
        return None
    
    def _compare_structures(self, schema1: Dict[str, Any], schema2: Dict[str, Any]) -> bool:
        """
        Compare two schema structures for consistency.
        """
        if schema1.get("type") != schema2.get("type"):
            return False
        
        if schema1.get("type") == "object":
            props1 = set(schema1.get("properties", {}).keys())
            props2 = set(schema2.get("properties", {}).keys())
            return props1 == props2
        
        return True
    
    def validate_schema(self, schema: Dict[str, Any]) -> bool:
        """
        Validate a generated schema using jsonschema.
        """
        try:
            # Create a minimal test instance based on the schema
            test_instance = self._create_test_instance(schema)
            validate(instance=test_instance, schema=schema)
            return True
        except ValidationError:
            return False
    
    def _create_test_instance(self, schema: Dict[str, Any]) -> Any:
        """
        Create a minimal test instance from a schema that satisfies all constraints.
        """
        schema_type = schema.get("type")
        
        if schema_type == "object":
            instance = {}
            for prop_name, prop_schema in schema.get("properties", {}).items():
                instance[prop_name] = self._create_test_instance(prop_schema)
            return instance
        
        elif schema_type == "array":
            items_schema = schema.get("items", {})
            min_items = schema.get("minItems", 1)
            # Create at least min_items instances
            return [self._create_test_instance(items_schema) for _ in range(min_items)]
        
        elif schema_type == "string":
            # Handle format-specific constraints
            format_type = schema.get("format")
            min_length = schema.get("minLength", 1)
            max_length = schema.get("maxLength", 100)
            
            if format_type == "email":
                return "test@example.com"
            elif format_type == "date":
                return "2023-01-01"
            elif format_type == "date-time":
                return "2023-01-01T00:00:00"
            elif format_type == "uuid":
                return "123e4567-e89b-12d3-a456-426614174000"
            elif format_type == "uri":
                return "https://example.com"
            elif format_type == "ipv4":
                return "192.168.1.1"
            elif format_type == "ipv6":
                return "2001:db8::1"
            else:
                # Create a string that satisfies length constraints
                test_str = "test"
                if min_length > len(test_str):
                    test_str = "a" * min_length
                elif max_length < len(test_str):
                    test_str = test_str[:max_length]
                return test_str
        
        elif schema_type == "integer":
            minimum = schema.get("minimum")
            if minimum is not None:
                return max(0, minimum)
            return 0
        
        elif schema_type == "number":
            minimum = schema.get("minimum")
            if minimum is not None:
                return max(0.0, minimum)
            return 0.0
        
        elif schema_type == "boolean":
            return True
        
        elif schema_type == "null":
            return None
        
        return None
    
    def get_schema_statistics(self, schema: Dict[str, Any]) -> Dict[str, int]:
        """
        Get statistics about a generated schema.
        """
        stats = {
            'total_properties': 0,
            'required_properties': 0,
            'object_properties': 0,
            'array_properties': 0,
            'primitive_properties': 0,
            'max_depth': 0
        }
        
        self._analyze_schema(schema, stats, 0)
        return stats
    
    def _analyze_schema(self, schema: Dict[str, Any], stats: Dict[str, int], depth: int):
        """
        Recursively analyze schema for statistics.
        """
        stats['max_depth'] = max(stats['max_depth'], depth)
        
        if schema.get("type") == "object":
            properties = schema.get("properties", {})
            stats['total_properties'] += len(properties)
            stats['object_properties'] += 1
            
            required = schema.get("required", [])
            stats['required_properties'] += len(required)
            
            for prop_schema in properties.values():
                self._analyze_schema(prop_schema, stats, depth + 1)
        
        elif schema.get("type") == "array":
            stats['array_properties'] += 1
            items_schema = schema.get("items", {})
            self._analyze_schema(items_schema, stats, depth + 1)
        
        else:
            stats['primitive_properties'] += 1 