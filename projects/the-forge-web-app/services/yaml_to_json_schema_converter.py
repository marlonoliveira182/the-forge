import yaml
import json
from typing import Dict, Any, List, Optional, Union
import re
from datetime import datetime, date, time
import uuid


class YAMLToJSONSchemaConverter:
    """
    Converts YAML content to JSON Schema format.
    Supports both YAML examples and YAML schemas.
    """
    
    def __init__(self):
        self.schema_id = 0
    
    def convert_yaml_to_json_schema(self, yaml_content: str, schema_name: str = "GeneratedSchema") -> Dict[str, Any]:
        """
        Convert YAML content to JSON Schema.
        
        Args:
            yaml_content: YAML string content
            schema_name: Name for the generated schema
            
        Returns:
            JSON Schema dictionary
        """
        try:
            # Parse YAML content
            yaml_data = yaml.safe_load(yaml_content)
            
            if yaml_data is None:
                raise ValueError("Empty or invalid YAML content")
            
            # Generate JSON Schema
            schema = self._generate_schema_from_data(yaml_data, schema_name)
            
            return schema
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML content: {str(e)}")
        except Exception as e:
            raise Exception(f"Error converting YAML to JSON Schema: {str(e)}")
    
    def _generate_schema_from_data(self, data: Any, schema_name: str) -> Dict[str, Any]:
        """
        Generate JSON Schema from YAML data.
        """
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": schema_name,
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
        
        if isinstance(data, dict):
            schema["properties"] = self._analyze_object_properties(data)
            schema["required"] = list(data.keys())
        elif isinstance(data, list):
            # If root is a list, create array schema
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": schema_name,
                "type": "array",
                "items": self._get_schema_for_value(data[0] if data else {})
            }
        else:
            # Single value
            schema = self._get_schema_for_value(data)
            schema["title"] = schema_name
        
        return schema
    
    def _analyze_object_properties(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze object properties and generate schema for each.
        """
        properties = {}
        
        for key, value in obj.items():
            properties[key] = self._get_schema_for_value(value)
        
        return properties
    
    def _get_schema_for_value(self, value: Any) -> Dict[str, Any]:
        """
        Get JSON Schema for a specific value.
        """
        if value is None:
            return {"type": "null"}
        
        elif isinstance(value, bool):
            return {"type": "boolean"}
        
        elif isinstance(value, int):
            return {"type": "integer"}
        
        elif isinstance(value, float):
            return {"type": "number"}
        
        elif isinstance(value, str):
            return self._analyze_string_schema(value)
        
        elif isinstance(value, list):
            return self._analyze_array_schema(value)
        
        elif isinstance(value, dict):
            return self._analyze_object_schema(value)
        
        elif isinstance(value, (datetime, date, time)):
            return {"type": "string", "format": "date-time"}
        
        else:
            return {"type": "string"}
    
    def _analyze_string_schema(self, value: str) -> Dict[str, Any]:
        """
        Analyze string and determine appropriate schema.
        """
        schema = {"type": "string"}
        
        # Check for common formats
        if self._is_email(value):
            schema["format"] = "email"
        elif self._is_uri(value):
            schema["format"] = "uri"
        elif self._is_date_time(value):
            schema["format"] = "date-time"
        elif self._is_date(value):
            schema["format"] = "date"
        elif self._is_time(value):
            schema["format"] = "time"
        elif self._is_uuid(value):
            schema["format"] = "uuid"
        elif self._is_ipv4(value):
            schema["format"] = "ipv4"
        elif self._is_ipv6(value):
            schema["format"] = "ipv6"
        elif self._is_hostname(value):
            schema["format"] = "hostname"
        
        # Add pattern if it looks like a specific format
        if self._looks_like_phone(value):
            schema["pattern"] = r"^[\+]?[1-9][\d]{0,15}$"
        elif self._looks_like_credit_card(value):
            schema["pattern"] = r"^[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}$"
        
        return schema
    
    def _analyze_array_schema(self, arr: List[Any]) -> Dict[str, Any]:
        """
        Analyze array and generate schema.
        """
        if not arr:
            return {"type": "array", "items": {"type": "object"}}
        
        # Check if all items are of the same type
        item_types = [type(item) for item in arr]
        if len(set(item_types)) == 1:
            # All items are the same type
            schema = {"type": "array", "items": self._get_schema_for_value(arr[0])}
        else:
            # Mixed types - use oneOf
            unique_items = list({str(item) for item in arr})
            if len(unique_items) <= 5:  # If few unique items, use enum
                schema = {
                    "type": "array",
                    "items": {"type": "string", "enum": unique_items}
                }
            else:
                # Use oneOf for mixed types
                schemas = [self._get_schema_for_value(item) for item in arr]
                schema = {
                    "type": "array",
                    "items": {"oneOf": schemas}
                }
        
        # Add min/max items if array is small
        if len(arr) <= 10:
            schema["minItems"] = len(arr)
            schema["maxItems"] = len(arr)
        
        return schema
    
    def _analyze_object_schema(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze object and generate schema.
        """
        schema = {
            "type": "object",
            "properties": self._analyze_object_properties(obj),
            "required": list(obj.keys()),
            "additionalProperties": False
        }
        
        return schema
    
    def _is_email(self, value: str) -> bool:
        """Check if string looks like an email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))
    
    def _is_uri(self, value: str) -> bool:
        """Check if string looks like a URI."""
        return value.startswith(('http://', 'https://', 'ftp://', 'file://'))
    
    def _is_date_time(self, value: str) -> bool:
        """Check if string looks like a date-time."""
        patterns = [
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?$',
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
        ]
        return any(re.match(pattern, value) for pattern in patterns)
    
    def _is_date(self, value: str) -> bool:
        """Check if string looks like a date."""
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        return bool(re.match(pattern, value))
    
    def _is_time(self, value: str) -> bool:
        """Check if string looks like a time."""
        pattern = r'^\d{2}:\d{2}:\d{2}(\.\d+)?$'
        return bool(re.match(pattern, value))
    
    def _is_uuid(self, value: str) -> bool:
        """Check if string looks like a UUID."""
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(pattern, value, re.IGNORECASE))
    
    def _is_ipv4(self, value: str) -> bool:
        """Check if string looks like an IPv4 address."""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, value):
            return False
        parts = value.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    def _is_ipv6(self, value: str) -> bool:
        """Check if string looks like an IPv6 address."""
        pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        return bool(re.match(pattern, value))
    
    def _is_hostname(self, value: str) -> bool:
        """Check if string looks like a hostname."""
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(pattern, value))
    
    def _looks_like_phone(self, value: str) -> bool:
        """Check if string looks like a phone number."""
        # Remove common separators
        clean_value = re.sub(r'[\s\-\(\)\+]', '', value)
        return len(clean_value) >= 10 and clean_value.isdigit()
    
    def _looks_like_credit_card(self, value: str) -> bool:
        """Check if string looks like a credit card number."""
        # Remove spaces and dashes
        clean_value = re.sub(r'[\s\-]', '', value)
        return len(clean_value) in [13, 15, 16, 19] and clean_value.isdigit()
    
    def validate_json_schema(self, schema: Dict[str, Any]) -> bool:
        """
        Validate that the generated schema is valid JSON Schema.
        """
        try:
            # Check required fields
            if "$schema" not in schema:
                return False
            
            if "type" not in schema:
                return False
            
            # Validate based on type
            schema_type = schema.get("type")
            if schema_type == "object":
                if "properties" not in schema:
                    return False
            elif schema_type == "array":
                if "items" not in schema:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def get_schema_statistics(self, schema: Dict[str, Any]) -> Dict[str, int]:
        """
        Get statistics about the generated schema.
        """
        stats = {
            "total_properties": 0,
            "required_properties": 0,
            "string_properties": 0,
            "number_properties": 0,
            "boolean_properties": 0,
            "array_properties": 0,
            "object_properties": 0
        }
        
        def count_properties(schema_dict: Dict[str, Any]):
            if "properties" in schema_dict:
                stats["total_properties"] += len(schema_dict["properties"])
                stats["required_properties"] += len(schema_dict.get("required", []))
                
                for prop_schema in schema_dict["properties"].values():
                    prop_type = prop_schema.get("type", "unknown")
                    if prop_type == "string":
                        stats["string_properties"] += 1
                    elif prop_type == "number" or prop_type == "integer":
                        stats["number_properties"] += 1
                    elif prop_type == "boolean":
                        stats["boolean_properties"] += 1
                    elif prop_type == "array":
                        stats["array_properties"] += 1
                    elif prop_type == "object":
                        stats["object_properties"] += 1
                    
                    # Recursively count nested objects
                    if prop_type == "object" and "properties" in prop_schema:
                        count_properties(prop_schema)
                    elif prop_type == "array" and "items" in prop_schema:
                        items_schema = prop_schema["items"]
                        if isinstance(items_schema, dict) and items_schema.get("type") == "object":
                            count_properties(items_schema)
        
        count_properties(schema)
        return stats
    
    def convert_yaml_schema_to_json_schema(self, yaml_schema_content: str, schema_name: str = "GeneratedSchema") -> Dict[str, Any]:
        """
        Convert YAML Schema (if it's already in schema format) to JSON Schema.
        This is useful when the YAML content is already structured as a schema.
        """
        try:
            # Parse YAML content
            yaml_data = yaml.safe_load(yaml_schema_content)
            
            if yaml_data is None:
                raise ValueError("Empty or invalid YAML content")
            
            # Check if it's already a schema-like structure
            if self._is_schema_like(yaml_data):
                return self._convert_schema_like_yaml_to_json_schema(yaml_data, schema_name)
            else:
                # Treat as regular YAML data
                return self.convert_yaml_to_json_schema(yaml_schema_content, schema_name)
                
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML content: {str(e)}")
        except Exception as e:
            raise Exception(f"Error converting YAML Schema to JSON Schema: {str(e)}")
    
    def _is_schema_like(self, data: Any) -> bool:
        """
        Check if YAML data looks like a schema definition.
        """
        if not isinstance(data, dict):
            return False
        
        # Check for common schema indicators
        schema_indicators = ["type", "properties", "required", "items", "enum", "format", "pattern"]
        return any(key in data for key in schema_indicators)
    
    def _convert_schema_like_yaml_to_json_schema(self, yaml_schema: Dict[str, Any], schema_name: str) -> Dict[str, Any]:
        """
        Convert YAML schema-like structure to JSON Schema.
        """
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": schema_name
        }
        
        # Copy schema properties
        for key, value in yaml_schema.items():
            if key in ["$schema", "$id", "$ref"]:
                # Skip JSON Schema specific fields that might be in YAML
                continue
            json_schema[key] = value
        
        # Ensure required fields are present
        if "type" not in json_schema:
            json_schema["type"] = "object"
        
        return json_schema 