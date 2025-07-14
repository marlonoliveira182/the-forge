"""
Normalization utilities for standardizing field names and paths.
"""

import re
from typing import List, Dict, Any


class NormalizationUtils:
    """Utility class for normalization operations."""
    
    @staticmethod
    def to_camel_case(s: str) -> str:
        """Convert string to camelCase."""
        if not s:
            return s
        return s[0].lower() + s[1:]
    
    @staticmethod
    def to_pascal_case(s: str) -> str:
        """Convert string to PascalCase."""
        return s[0].upper() + s[1:] if s else s
    
    @staticmethod
    def to_snake_case(s: str) -> str:
        """Convert string to snake_case."""
        if not s:
            return s
        # Insert underscore before capital letters
        s = re.sub(r'([A-Z])', r'_\1', s)
        # Convert to lowercase and remove leading underscore
        return s.lower().lstrip('_')
    
    @staticmethod
    def normalize_field_name(name: str, target_case: str = 'camel') -> str:
        """Normalize field name to target case."""
        if not name:
            return name
        
        if target_case == 'camel':
            return NormalizationUtils.to_camel_case(name)
        elif target_case == 'pascal':
            return NormalizationUtils.to_pascal_case(name)
        elif target_case == 'snake':
            return NormalizationUtils.to_snake_case(name)
        else:
            return name
    
    @staticmethod
    def normalize_levels(levels: List[str]) -> List[str]:
        """Normalize field levels for comparison."""
        return [
            'arrayitem' if (isinstance(l, str) and l.lower() in ('item', '[]')) 
            else (l.lower() if isinstance(l, str) else l)
            for l in levels
        ]
    
    @staticmethod
    def normalized_path_from_levels(levels: List[str]) -> str:
        """Create normalized path from field levels."""
        return '.'.join([
            'arrayitem' if (isinstance(l, str) and l.lower() in ('item', '[]')) 
            else (l.lower() if isinstance(l, str) else l)
            for l in levels
        ])
    
    @staticmethod
    def normalize_schema_field(field: Dict[str, Any], target_case: str = 'camel') -> Dict[str, Any]:
        """Normalize a schema field's levels to target case."""
        normalized_field = field.copy()
        
        if 'levels' in normalized_field:
            normalized_field['levels'] = [
                NormalizationUtils.normalize_field_name(level, target_case)
                for level in normalized_field['levels']
            ]
        
        return normalized_field
    
    @staticmethod
    def normalize_schema_fields(fields: List[Dict[str, Any]], 
                              target_case: str = 'camel') -> List[Dict[str, Any]]:
        """Normalize all schema fields to target case."""
        return [NormalizationUtils.normalize_schema_field(field, target_case) for field in fields]
    
    @staticmethod
    def standardize_array_indicators(levels: List[str]) -> List[str]:
        """Standardize array indicators in field levels."""
        return [
            '[]' if (isinstance(l, str) and l.lower() in ('item', 'arrayitem')) 
            else l
            for l in levels
        ]
    
    @staticmethod
    def remove_duplicate_levels(levels: List[str]) -> List[str]:
        """Remove duplicate consecutive levels."""
        if len(levels) <= 1:
            return levels
        
        result = [levels[0]]
        for level in levels[1:]:
            if level != result[-1]:
                result.append(level)
        
        return result
    
    @staticmethod
    def clean_field_name(name: str) -> str:
        """Clean field name by removing special characters and normalizing."""
        if not name:
            return name
        
        # Remove special characters except alphanumeric and underscore
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '', name)
        
        # Ensure it starts with a letter or underscore
        if cleaned and not cleaned[0].isalpha() and cleaned[0] != '_':
            cleaned = 'field_' + cleaned
        
        return cleaned or 'unnamed_field'
    
    @staticmethod
    def normalize_json_schema_properties(schema: Dict[str, Any], 
                                       target_case: str = 'camel') -> Dict[str, Any]:
        """Normalize JSON Schema property names to target case."""
        if not isinstance(schema, dict):
            return schema
        
        normalized = {}
        for key, value in schema.items():
            # Keep JSON Schema meta keys as-is
            if key in ('$schema', 'title', 'type', 'required', 'enum', 'pattern', 
                      'minLength', 'maxLength', 'minimum', 'maximum', 'format', 
                      'description', 'allOf', 'anyOf', 'oneOf', 'not', 'default', 
                      'examples', 'items', 'properties'):
                normalized[key] = NormalizationUtils.normalize_json_schema_properties(value, target_case)
            elif key == 'properties' and isinstance(value, dict):
                # Recursively normalize property names
                normalized[key] = {
                    NormalizationUtils.normalize_field_name(pk, target_case): 
                    NormalizationUtils.normalize_json_schema_properties(pv, target_case)
                    for pk, pv in value.items()
                }
            else:
                normalized[NormalizationUtils.normalize_field_name(key, target_case)] = \
                    NormalizationUtils.normalize_json_schema_properties(value, target_case)
        
        return normalized
    
    @staticmethod
    def normalize_xsd_element_names(schema: str, target_case: str = 'pascal') -> str:
        """Normalize XSD element names to target case."""
        # This is a simplified version - in practice, you'd want to use an XML parser
        # For now, we'll use regex to find and replace element names
        
        def replace_element_name(match):
            name = match.group(1)
            normalized_name = NormalizationUtils.normalize_field_name(name, target_case)
            return f'name="{normalized_name}"'
        
        # Replace element names in name attributes
        schema = re.sub(r'name="([^"]+)"', replace_element_name, schema)
        
        return schema
    
    @staticmethod
    def create_field_mapping(source_fields: List[Dict[str, Any]], 
                           target_fields: List[Dict[str, Any]]) -> Dict[str, str]:
        """Create a mapping between source and target fields based on normalized paths."""
        source_paths = {NormalizationUtils.normalized_path_from_levels(f['levels']): f 
                       for f in source_fields}
        target_paths = {NormalizationUtils.normalized_path_from_levels(f['levels']): f 
                       for f in target_fields}
        
        mapping = {}
        for source_path, source_field in source_paths.items():
            if source_path in target_paths:
                mapping[source_path] = source_path  # Exact match
            else:
                # Find best match
                best_match = None
                best_similarity = 0
                
                for target_path in target_paths:
                    similarity = NormalizationUtils.calculate_similarity(source_path, target_path)
                    if similarity > best_similarity and similarity > 0.5:
                        best_similarity = similarity
                        best_match = target_path
                
                if best_match:
                    mapping[source_path] = best_match
        
        return mapping
    
    @staticmethod
    def calculate_similarity(str1: str, str2: str) -> float:
        """Calculate similarity between two strings."""
        if not str1 or not str2:
            return 0.0
        
        # Simple similarity based on common prefix
        min_len = min(len(str1), len(str2))
        common = 0
        for i in range(min_len):
            if str1[i] == str2[i]:
                common += 1
            else:
                break
        
        return common / max(len(str1), len(str2))
    
    @staticmethod
    def validate_normalization(fields: List[Dict[str, Any]], 
                             target_case: str = 'camel') -> Dict[str, Any]:
        """Validate normalization results."""
        issues = []
        normalized_count = 0
        
        for i, field in enumerate(fields):
            if 'levels' in field:
                original_levels = field['levels']
                normalized_levels = [
                    NormalizationUtils.normalize_field_name(level, target_case)
                    for level in original_levels
                ]
                
                if original_levels != normalized_levels:
                    normalized_count += 1
                    
                    # Check for potential issues
                    for j, (orig, norm) in enumerate(zip(original_levels, normalized_levels)):
                        if orig != norm:
                            issues.append({
                                'field_index': i,
                                'level_index': j,
                                'original': orig,
                                'normalized': norm,
                                'issue_type': 'case_conversion'
                            })
        
        return {
            'total_fields': len(fields),
            'normalized_fields': normalized_count,
            'issues': issues,
            'has_issues': len(issues) > 0
        } 