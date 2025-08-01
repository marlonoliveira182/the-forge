#!/usr/bin/env python3
"""
JSON Example to Schema Service
Generates JSON schemas from JSON examples, extracting structure without repeating array fields.
"""

import json
import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
import logging


@dataclass
class SchemaField:
    name: str
    type: str
    description: Optional[str] = None
    required: bool = False
    min_occurrences: int = 0
    max_occurrences: int = 1
    properties: Optional[Dict] = None
    items: Optional[Dict] = None
    format: Optional[str] = None
    pattern: Optional[str] = None
    enum: Optional[List] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None


class JSONExampleToSchemaService:
    """
    Service for generating JSON schemas from JSON examples.
    Handles complex nested structures and avoids repeating array fields.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.processed_arrays = set()  # Track processed arrays to avoid repetition
        self.schema_cache = {}  # Cache for generated schemas
        self.type_patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'date': r'^\d{4}-\d{2}-\d{2}$',
            'datetime': r'^\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}',
            'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            'url': r'^https?://[^\s/$.?#].[^\s]*$',
            'ipv4': r'^(\d{1,3}\.){3}\d{1,3}$',
            'ipv6': r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        }
    
    def generate_schema_from_example(self, json_example: str, schema_name: str = "GeneratedSchema") -> Dict[str, Any]:
        """
        Generate a JSON schema from a JSON example.
        
        Args:
            json_example: JSON example as string
            schema_name: Name for the generated schema
            
        Returns:
            Generated JSON schema as dictionary
        """
        try:
            # Parse the JSON example
            data = json.loads(json_example)
            
            # Reset tracking for new generation
            self.processed_arrays.clear()
            self.schema_cache.clear()
            
            # Generate schema from the data
            schema = self._generate_schema_from_data(data, schema_name)
            
            # Add schema metadata
            schema.update({
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": schema_name,
                "description": f"Schema generated from JSON example for {schema_name}"
            })
            
            return schema
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON example: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error generating schema from example: {e}")
            raise
    
    def generate_schema_from_file(self, file_path: str, schema_name: str = None) -> Dict[str, Any]:
        """
        Generate a JSON schema from a JSON example file.
        
        Args:
            file_path: Path to the JSON example file
            schema_name: Name for the generated schema (defaults to filename)
            
        Returns:
            Generated JSON schema as dictionary
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_example = f.read()
            
            if schema_name is None:
                import os
                schema_name = os.path.splitext(os.path.basename(file_path))[0]
            
            return self.generate_schema_from_example(json_example, schema_name)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON example file not found: {file_path}")
        except Exception as e:
            self.logger.error(f"Error reading JSON example file: {e}")
            raise
    
    def _generate_schema_from_data(self, data: Any, name: str = "root", path: str = "") -> Dict[str, Any]:
        """
        Recursively generate schema from data structure.
        
        Args:
            data: The data to generate schema for
            name: Name of the current element
            path: Current path in the structure
            
        Returns:
            Generated schema dictionary
        """
        if isinstance(data, dict):
            return self._generate_object_schema(data, name, path)
        elif isinstance(data, list):
            return self._generate_array_schema(data, name, path)
        else:
            return self._generate_primitive_schema(data, name, path)
    
    def _generate_object_schema(self, obj: Dict, name: str, path: str) -> Dict[str, Any]:
        """Generate schema for object/dictionary."""
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for key, value in obj.items():
            if value is not None:  # Skip null values in example
                prop_schema = self._generate_schema_from_data(value, key, f"{path}.{key}")
                schema["properties"][key] = prop_schema
                schema["required"].append(key)
        
        # Remove required if empty
        if not schema["required"]:
            del schema["required"]
        
        return schema
    
    def _generate_array_schema(self, arr: List, name: str, path: str) -> Dict[str, Any]:
        """Generate schema for array, avoiding repetition of array fields."""
        if not arr:
            return {
                "type": "array",
                "items": {"type": "object"}
            }
        
        # Check if we've already processed this array structure
        array_key = f"{path}:{len(arr)}"
        if array_key in self.processed_arrays:
            # Return a reference to avoid repetition
            return {
                "type": "array",
                "items": {"$ref": f"#/definitions/{name}Array"}
            }
        
        # Mark this array as processed
        self.processed_arrays.add(array_key)
        
        # Generate schema for the first item (representative)
        first_item = arr[0]
        items_schema = self._generate_schema_from_data(first_item, f"{name}Item", f"{path}[0]")
        
        # Check if all items have the same structure
        uniform_structure = all(
            self._compare_structures(first_item, item) 
            for item in arr[1:]
        )
        
        if uniform_structure:
            return {
                "type": "array",
                "items": items_schema,
                "minItems": 1,
                "uniqueItems": self._has_unique_items(arr)
            }
        else:
            # Mixed array - use oneOf for different item types
            item_schemas = []
            for i, item in enumerate(arr):
                item_schema = self._generate_schema_from_data(item, f"{name}Item{i}", f"{path}[{i}]")
                if item_schema not in item_schemas:
                    item_schemas.append(item_schema)
            
            if len(item_schemas) == 1:
                return {
                    "type": "array",
                    "items": item_schemas[0]
                }
            else:
                return {
                    "type": "array",
                    "items": {
                        "oneOf": item_schemas
                    }
                }
    
    def _generate_primitive_schema(self, value: Any, name: str, path: str) -> Dict[str, Any]:
        """Generate schema for primitive values with type detection and constraints."""
        if isinstance(value, bool):
            return {"type": "boolean"}
        elif isinstance(value, int):
            schema = {"type": "integer"}
            # Add range constraints if reasonable
            if value >= 0:
                schema["minimum"] = 0
            return schema
        elif isinstance(value, float):
            schema = {"type": "number"}
            # Add range constraints if reasonable
            if value >= 0:
                schema["minimum"] = 0
            return schema
        elif isinstance(value, str):
            return self._generate_string_schema(value, name, path)
        else:
            return {"type": "string"}
    
    def _generate_string_schema(self, value: str, name: str, path: str) -> Dict[str, Any]:
        """Generate schema for string values with format detection."""
        schema = {"type": "string"}
        
        # Detect format patterns
        detected_format = self._detect_string_format(value)
        if detected_format:
            schema["format"] = detected_format
        
        # Add length constraints
        length = len(value)
        if length > 0:
            schema["minLength"] = 1
            schema["maxLength"] = length * 2  # Allow some flexibility
        
        # Add pattern if it's a specific format
        if detected_format == "email":
            schema["pattern"] = self.type_patterns["email"]
        elif detected_format == "date":
            schema["pattern"] = self.type_patterns["date"]
        elif detected_format == "datetime":
            schema["pattern"] = self.type_patterns["datetime"]
        elif detected_format == "uuid":
            schema["pattern"] = self.type_patterns["uuid"]
        elif detected_format == "url":
            schema["pattern"] = self.type_patterns["url"]
        
        return schema
    
    def _detect_string_format(self, value: str) -> Optional[str]:
        """Detect the format of a string value."""
        import re
        
        # Check for email
        if re.match(self.type_patterns["email"], value):
            return "email"
        
        # Check for date
        if re.match(self.type_patterns["date"], value):
            return "date"
        
        # Check for datetime
        if re.match(self.type_patterns["datetime"], value):
            return "date-time"
        
        # Check for UUID
        if re.match(self.type_patterns["uuid"], value):
            return "uuid"
        
        # Check for URL
        if re.match(self.type_patterns["url"], value):
            return "uri"
        
        # Check for IPv4
        if re.match(self.type_patterns["ipv4"], value):
            return "ipv4"
        
        # Check for IPv6
        if re.match(self.type_patterns["ipv6"], value):
            return "ipv6"
        
        return None
    
    def _compare_structures(self, obj1: Any, obj2: Any) -> bool:
        """Compare if two objects have the same structure."""
        if type(obj1) != type(obj2):
            return False
        
        if isinstance(obj1, dict):
            if set(obj1.keys()) != set(obj2.keys()):
                return False
            return all(self._compare_structures(obj1[k], obj2[k]) for k in obj1.keys())
        
        elif isinstance(obj1, list):
            if len(obj1) != len(obj2):
                return False
            return all(self._compare_structures(obj1[i], obj2[i]) for i in range(len(obj1)))
        
        else:
            return True
    
    def _has_unique_items(self, arr: List) -> bool:
        """Check if array has unique items."""
        try:
            # Convert to JSON strings for comparison
            items_str = [json.dumps(item, sort_keys=True) for item in arr]
            return len(items_str) == len(set(items_str))
        except:
            return False
    
    def validate_schema(self, schema: Dict[str, Any]) -> bool:
        """
        Validate the generated schema using jsonschema library.
        
        Args:
            schema: The schema to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            import jsonschema
            jsonschema.Draft7Validator.check_schema(schema)
            return True
        except Exception as e:
            self.logger.error(f"Schema validation failed: {e}")
            return False
    
    def save_schema_to_file(self, schema: Dict[str, Any], output_path: str) -> None:
        """
        Save the generated schema to a file.
        
        Args:
            schema: The schema to save
            output_path: Path where to save the schema
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Schema saved to: {output_path}")
        except Exception as e:
            self.logger.error(f"Error saving schema to file: {e}")
            raise
    
    def get_schema_statistics(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics about the generated schema.
        
        Args:
            schema: The schema to analyze
            
        Returns:
            Dictionary with schema statistics
        """
        stats = {
            "total_properties": 0,
            "required_properties": 0,
            "array_properties": 0,
            "object_properties": 0,
            "primitive_properties": 0,
            "max_depth": 0
        }
        
        def analyze_schema(schema_part: Any, depth: int = 0):
            stats["max_depth"] = max(stats["max_depth"], depth)
            
            if isinstance(schema_part, dict):
                if schema_part.get("type") == "object":
                    stats["object_properties"] += 1
                    properties = schema_part.get("properties", {})
                    stats["total_properties"] += len(properties)
                    
                    for prop_schema in properties.values():
                        analyze_schema(prop_schema, depth + 1)
                
                elif schema_part.get("type") == "array":
                    stats["array_properties"] += 1
                    items = schema_part.get("items", {})
                    analyze_schema(items, depth + 1)
                
                else:
                    stats["primitive_properties"] += 1
                
                required = schema_part.get("required", [])
                stats["required_properties"] += len(required)
        
        analyze_schema(schema)
        return stats 