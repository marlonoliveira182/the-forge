import json
import random
import string
from typing import Any, Dict, List, Optional


class JSONSchemaToJSONConverter:
    """
    Service for converting JSON schemas to JSON examples.
    """
    
    def __init__(self):
        self.generated_examples = []
    
    def convert_json_schema_to_json_example(self, schema: Dict[str, Any], num_examples: int = 1) -> List[Dict[str, Any]]:
        """
        Convert a JSON schema to JSON examples.
        
        Args:
            schema: The JSON schema as dictionary
            num_examples: Number of examples to generate
            
        Returns:
            List of generated JSON examples
        """
        self.generated_examples = []
        
        for i in range(num_examples):
            example = self._generate_example_from_schema(schema)
            self.generated_examples.append(example)
        
        return self.generated_examples
    
    def _generate_example_from_schema(self, schema: Dict[str, Any]) -> Any:
        """
        Generate an example from a JSON schema.
        """
        schema_type = schema.get("type")
        
        if schema_type == "object":
            return self._generate_object_example(schema)
        elif schema_type == "array":
            return self._generate_array_example(schema)
        elif schema_type == "string":
            return self._generate_string_example(schema)
        elif schema_type == "integer":
            return self._generate_integer_example(schema)
        elif schema_type == "number":
            return self._generate_number_example(schema)
        elif schema_type == "boolean":
            return self._generate_boolean_example(schema)
        elif schema_type == "null":
            return None
        else:
            # Handle oneOf, anyOf, allOf
            if "oneOf" in schema:
                return self._generate_example_from_schema(random.choice(schema["oneOf"]))
            elif "anyOf" in schema:
                return self._generate_example_from_schema(random.choice(schema["anyOf"]))
            elif "allOf" in schema:
                # Merge all schemas and generate
                merged_schema = self._merge_all_of_schemas(schema["allOf"])
                return self._generate_example_from_schema(merged_schema)
            else:
                # Default to string
                return self._generate_string_example({"type": "string"})
    
    def _generate_object_example(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an object example from schema.
        """
        example = {}
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        # Generate required properties
        for prop_name in required:
            if prop_name in properties:
                example[prop_name] = self._generate_example_from_schema(properties[prop_name])
        
        # Generate optional properties (with some probability)
        for prop_name, prop_schema in properties.items():
            if prop_name not in required and random.random() < 0.7:  # 70% chance
                example[prop_name] = self._generate_example_from_schema(prop_schema)
        
        return example
    
    def _generate_array_example(self, schema: Dict[str, Any]) -> List[Any]:
        """
        Generate an array example from schema.
        """
        items_schema = schema.get("items", {})
        min_items = schema.get("minItems", 1)
        max_items = schema.get("maxItems", 3)
        
        # Determine number of items
        if min_items == max_items:
            num_items = min_items
        else:
            num_items = random.randint(min_items, max_items)
        
        # Generate items
        items = []
        for i in range(num_items):
            item_example = self._generate_example_from_schema(items_schema)
            items.append(item_example)
        
        return items
    
    def _generate_string_example(self, schema: Dict[str, Any]) -> str:
        """
        Generate a string example from schema.
        """
        # Check for enum
        if "enum" in schema:
            return random.choice(schema["enum"])
        
        # Check for format
        format_type = schema.get("format")
        if format_type:
            return self._generate_formatted_string(format_type)
        
        # Check for pattern
        pattern = schema.get("pattern")
        if pattern:
            return self._generate_pattern_string(pattern)
        
        # Check for min/max length
        min_length = schema.get("minLength", 1)
        max_length = schema.get("maxLength", 20)
        
        # Generate random string
        length = random.randint(min_length, max_length)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def _generate_integer_example(self, schema: Dict[str, Any]) -> int:
        """
        Generate an integer example from schema.
        """
        # Check for enum
        if "enum" in schema:
            return random.choice(schema["enum"])
        
        # Get min/max values
        minimum = schema.get("minimum", 0)
        maximum = schema.get("maximum", 1000)
        
        # Handle exclusive min/max
        if schema.get("exclusiveMinimum", False):
            minimum += 1
        if schema.get("exclusiveMaximum", False):
            maximum -= 1
        
        return random.randint(minimum, maximum)
    
    def _generate_number_example(self, schema: Dict[str, Any]) -> float:
        """
        Generate a number example from schema.
        """
        # Check for enum
        if "enum" in schema:
            return random.choice(schema["enum"])
        
        # Get min/max values
        minimum = schema.get("minimum", 0.0)
        maximum = schema.get("maximum", 1000.0)
        
        # Handle exclusive min/max
        if schema.get("exclusiveMinimum", False):
            minimum += 0.1
        if schema.get("exclusiveMaximum", False):
            maximum -= 0.1
        
        return round(random.uniform(minimum, maximum), 2)
    
    def _generate_boolean_example(self, schema: Dict[str, Any]) -> bool:
        """
        Generate a boolean example from schema.
        """
        return random.choice([True, False])
    
    def _generate_formatted_string(self, format_type: str) -> str:
        """
        Generate a formatted string based on format type.
        """
        if format_type == "email":
            domains = ["example.com", "test.org", "demo.net"]
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            domain = random.choice(domains)
            return f"{username}@{domain}"
        
        elif format_type == "date":
            year = random.randint(2020, 2024)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            return f"{year:04d}-{month:02d}-{day:02d}"
        
        elif format_type == "date-time":
            year = random.randint(2020, 2024)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}"
        
        elif format_type == "time":
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            return f"{hour:02d}:{minute:02d}:{second:02d}"
        
        elif format_type == "uri":
            protocols = ["https", "http"]
            domains = ["example.com", "test.org", "demo.net"]
            paths = ["/api", "/data", "/resource", "/item"]
            
            protocol = random.choice(protocols)
            domain = random.choice(domains)
            path = random.choice(paths)
            return f"{protocol}://{domain}{path}"
        
        elif format_type == "uuid":
            return f"{random.randint(0, 0xffffffff):08x}-{random.randint(0, 0xffff):04x}-{random.randint(0, 0xffff):04x}-{random.randint(0, 0xffff):04x}-{random.randint(0, 0xffffffffffff):012x}"
        
        elif format_type == "ipv4":
            return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
        
        elif format_type == "ipv6":
            segments = [f"{random.randint(0, 0xffff):04x}" for _ in range(8)]
            return ":".join(segments)
        
        else:
            # Default string
            return ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    def _generate_pattern_string(self, pattern: str) -> str:
        """
        Generate a string that matches a regex pattern.
        This is a simplified implementation.
        """
        # For now, return a simple string that might match common patterns
        if "email" in pattern.lower():
            return self._generate_formatted_string("email")
        elif "url" in pattern.lower():
            return self._generate_formatted_string("uri")
        else:
            return ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    def _merge_all_of_schemas(self, schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple schemas in allOf.
        """
        merged = {}
        
        for schema in schemas:
            # Merge properties
            if "properties" in schema:
                if "properties" not in merged:
                    merged["properties"] = {}
                merged["properties"].update(schema["properties"])
            
            # Merge required
            if "required" in schema:
                if "required" not in merged:
                    merged["required"] = []
                merged["required"].extend(schema["required"])
            
            # Merge other fields
            for key, value in schema.items():
                if key not in ["properties", "required"]:
                    merged[key] = value
        
        return merged
    
    def validate_example(self, example: Any, schema: Dict[str, Any]) -> bool:
        """
        Validate a generated example against the schema.
        """
        try:
            from jsonschema import validate
            validate(instance=example, schema=schema)
            return True
        except Exception:
            return False
    
    def get_example_statistics(self, examples: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get statistics about generated examples.
        """
        if not examples:
            return {
                'total_examples': 0,
                'avg_object_properties': 0,
                'avg_array_length': 0,
                'max_depth': 0
            }
        
        total_properties = 0
        total_array_lengths = 0
        max_depth = 0
        
        for example in examples:
            stats = self._analyze_example(example, 0)
            total_properties += stats['properties']
            total_array_lengths += stats['array_lengths']
            max_depth = max(max_depth, stats['max_depth'])
        
        return {
            'total_examples': len(examples),
            'avg_object_properties': total_properties // len(examples) if examples else 0,
            'avg_array_length': total_array_lengths // len(examples) if examples else 0,
            'max_depth': max_depth
        }
    
    def _analyze_example(self, example: Any, depth: int) -> Dict[str, int]:
        """
        Recursively analyze an example for statistics.
        """
        stats = {
            'properties': 0,
            'array_lengths': 0,
            'max_depth': depth
        }
        
        if isinstance(example, dict):
            stats['properties'] = len(example)
            for value in example.values():
                child_stats = self._analyze_example(value, depth + 1)
                stats['max_depth'] = max(stats['max_depth'], child_stats['max_depth'])
                stats['array_lengths'] += child_stats['array_lengths']
        
        elif isinstance(example, list):
            stats['array_lengths'] = len(example)
            for item in example:
                child_stats = self._analyze_example(item, depth + 1)
                stats['max_depth'] = max(stats['max_depth'], child_stats['max_depth'])
                stats['array_lengths'] += child_stats['array_lengths']
        
        return stats 