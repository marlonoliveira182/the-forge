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
    Can handle multiple operations in a single YAML file (e.g., OpenAPI/Swagger).
    """
    
    def __init__(self):
        self.schema_id = 0
    
    def convert_yaml_to_json_schema(self, yaml_content: str, schema_name: str = "GeneratedSchema") -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Convert YAML content to JSON Schema.
        
        Args:
            yaml_content: YAML string content
            schema_name: Name for the generated schema
            
        Returns:
            JSON Schema dictionary or list of schemas if multiple operations detected
        """
        try:
            # Parse YAML content
            yaml_data = yaml.safe_load(yaml_content)
            
            if yaml_data is None:
                raise ValueError("Empty or invalid YAML content")
            
            # Check if it's a multi-operation YAML (like OpenAPI/Swagger)
            if self._is_multi_operation_yaml(yaml_data):
                return self._convert_multi_operation_yaml_to_schemas(yaml_data, schema_name)
            else:
                # Generate single JSON Schema
                schema = self._generate_schema_from_data(yaml_data, schema_name)
                return schema
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML content: {str(e)}")
        except Exception as e:
            raise Exception(f"Error converting YAML to JSON Schema: {str(e)}")
    
    def _is_multi_operation_yaml(self, yaml_data: Any) -> bool:
        """
        Check if YAML contains multiple operations (like OpenAPI/Swagger).
        """
        if not isinstance(yaml_data, dict):
            return False
        
        # Check for OpenAPI/Swagger indicators
        openapi_indicators = ["openapi", "swagger", "info", "paths", "components"]
        if any(key in yaml_data for key in openapi_indicators):
            return True
        
        # Check for other multi-operation patterns
        if "paths" in yaml_data and isinstance(yaml_data["paths"], dict):
            return True
        
        if "components" in yaml_data and isinstance(yaml_data["components"], dict):
            return True
        
        return False
    
    def _convert_multi_operation_yaml_to_schemas(self, yaml_data: Dict[str, Any], base_schema_name: str) -> List[Dict[str, Any]]:
        """
        Convert multi-operation YAML (like OpenAPI/Swagger) to multiple JSON Schemas.
        """
        schemas = []
        
        # Handle OpenAPI/Swagger format
        if "paths" in yaml_data:
            schemas.extend(self._extract_path_schemas(yaml_data, base_schema_name))
        
        # Handle components/schemas
        if "components" in yaml_data and "schemas" in yaml_data["components"]:
            schemas.extend(self._extract_component_schemas(yaml_data["components"]["schemas"], base_schema_name))
        
        # Handle definitions (older Swagger format)
        if "definitions" in yaml_data:
            schemas.extend(self._extract_definition_schemas(yaml_data["definitions"], base_schema_name))
        
        # Only return schemas if we found actual data structures
        # Don't fall back to generating schema from entire YAML (which includes metadata)
        return schemas
    
    def _extract_path_schemas(self, yaml_data: Dict[str, Any], base_schema_name: str) -> List[Dict[str, Any]]:
        """
        Extract schemas from OpenAPI/Swagger paths.
        """
        schemas = []
        paths = yaml_data.get("paths", {})
        
        for path, path_data in paths.items():
            if not isinstance(path_data, dict):
                continue
            
            for method, operation_data in path_data.items():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    # Generate schema for request body
                    if "requestBody" in operation_data:
                        request_schema = self._extract_request_schema(operation_data["requestBody"], 
                                                                   f"{base_schema_name}_{path.replace('/', '_')}_{method.upper()}_Request")
                        if request_schema:
                            schemas.append(request_schema)
                    
                    # Generate schema for response
                    if "responses" in operation_data:
                        response_schemas = self._extract_response_schemas(operation_data["responses"], 
                                                                       f"{base_schema_name}_{path.replace('/', '_')}_{method.upper()}_Response")
                        schemas.extend(response_schemas)
        
        return schemas
    
    def _extract_request_schema(self, request_body: Dict[str, Any], schema_name: str) -> Optional[Dict[str, Any]]:
        """
        Extract schema from request body.
        """
        if "content" in request_body:
            for content_type, content_data in request_body["content"].items():
                if "schema" in content_data:
                    schema_data = content_data["schema"]
                    return self._convert_schema_like_yaml_to_json_schema(schema_data, schema_name)
        
        return None
    
    def _extract_response_schemas(self, responses: Dict[str, Any], base_schema_name: str) -> List[Dict[str, Any]]:
        """
        Extract schemas from responses.
        """
        schemas = []
        
        for status_code, response_data in responses.items():
            if "content" in response_data:
                for content_type, content_data in response_data["content"].items():
                    if "schema" in content_data:
                        schema_data = content_data["schema"]
                        schema_name = f"{base_schema_name}_{status_code}"
                        schema = self._convert_schema_like_yaml_to_json_schema(schema_data, schema_name)
                        if schema:
                            schemas.append(schema)
        
        return schemas
    
    def _extract_component_schemas(self, components: Dict[str, Any], base_schema_name: str) -> List[Dict[str, Any]]:
        """
        Extract schemas from OpenAPI components.
        Only process actual schema definitions, not metadata structures.
        """
        schemas = []
        
        for component_name, component_data in components.items():
            # Skip metadata structures that are not actual schemas
            if component_name in ["info", "openapi", "swagger", "servers", "security", "tags", "externalDocs"]:
                continue
            
            # Only process if it looks like a schema
            if self._is_schema_like(component_data):
                schema_name = f"{base_schema_name}_{component_name}"
                schema = self._convert_schema_like_yaml_to_json_schema(component_data, schema_name)
                if schema:
                    schemas.append(schema)
        
        return schemas
    
    def _extract_definition_schemas(self, definitions: Dict[str, Any], base_schema_name: str) -> List[Dict[str, Any]]:
        """
        Extract schemas from Swagger definitions.
        Only process actual schema definitions, not metadata structures.
        """
        schemas = []
        
        for definition_name, definition_data in definitions.items():
            # Skip metadata structures that are not actual schemas
            if definition_name in ["info", "swagger", "host", "basePath", "schemes", "consumes", "produces", "securityDefinitions"]:
                continue
            
            # Only process if it looks like a schema
            if self._is_schema_like(definition_data):
                schema_name = f"{base_schema_name}_{definition_name}"
                schema = self._convert_schema_like_yaml_to_json_schema(definition_data, schema_name)
                if schema:
                    schemas.append(schema)
        
        return schemas
    
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
        has_schema_indicators = any(key in data for key in schema_indicators)
        
        # Also check for OpenAPI/Swagger schema indicators
        openapi_indicators = ["schema", "allOf", "anyOf", "oneOf", "not", "additionalProperties"]
        has_openapi_indicators = any(key in data for key in openapi_indicators)
        
        # Exclude metadata structures that might have some schema-like properties
        metadata_indicators = ["info", "openapi", "swagger", "host", "basePath", "schemes", "consumes", "produces", "securityDefinitions", "servers", "security", "tags", "externalDocs"]
        is_metadata = any(key in data for key in metadata_indicators)
        
        return (has_schema_indicators or has_openapi_indicators) and not is_metadata
    
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