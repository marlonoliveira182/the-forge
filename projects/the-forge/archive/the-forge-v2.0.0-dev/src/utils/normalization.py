"""
Normalization Utilities Module

Handles data normalization and field name standardization:
- Field name normalization
- Path normalization
- Data type standardization
- Case conversion
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class CaseStyle(Enum):
    """Supported case styles for field names."""
    CAMEL_CASE = "camelCase"
    PASCAL_CASE = "PascalCase"
    SNAKE_CASE = "snake_case"
    KEBAB_CASE = "kebab-case"
    UPPER_CASE = "UPPER_CASE"
    LOWER_CASE = "lower_case"


class NormalizationUtils:
    """
    Utility class for data normalization and field name standardization.
    
    Provides methods for:
    - Field name normalization
    - Path normalization
    - Data type standardization
    - Case conversion
    """
    
    def __init__(self):
        # Common field name mappings
        self.field_mappings = {
            'element': 'field',
            'property': 'field',
            'attribute': 'field',
            'node': 'field',
            'item': 'element'
        }
        
        # Type mappings for standardization
        self.type_mappings = {
            'xs:string': 'string',
            'xs:integer': 'integer',
            'xs:decimal': 'number',
            'xs:boolean': 'boolean',
            'xs:date': 'date',
            'xs:datetime': 'datetime',
            'xs:time': 'time',
            'text': 'string',
            'int': 'integer',
            'float': 'number',
            'double': 'number',
            'bool': 'boolean',
            'date': 'date',
            'datetime': 'datetime',
            'timestamp': 'datetime'
        }
    
    def normalize_field_name(self, field_name: str, target_case: CaseStyle = CaseStyle.CAMEL_CASE) -> str:
        """
        Normalize a field name to the target case style.
        
        Args:
            field_name: Original field name
            target_case: Target case style
            
        Returns:
            Normalized field name
        """
        if not field_name:
            return ""
        
        # Clean the field name
        cleaned = self._clean_field_name(field_name)
        
        # Convert to target case
        if target_case == CaseStyle.CAMEL_CASE:
            return self._to_camel_case(cleaned)
        elif target_case == CaseStyle.PASCAL_CASE:
            return self._to_pascal_case(cleaned)
        elif target_case == CaseStyle.SNAKE_CASE:
            return self._to_snake_case(cleaned)
        elif target_case == CaseStyle.KEBAB_CASE:
            return self._to_kebab_case(cleaned)
        elif target_case == CaseStyle.UPPER_CASE:
            return cleaned.upper()
        elif target_case == CaseStyle.LOWER_CASE:
            return cleaned.lower()
        else:
            return cleaned
    
    def _clean_field_name(self, field_name: str) -> str:
        """Clean a field name by removing special characters and normalizing."""
        # Remove special characters except alphanumeric and spaces
        cleaned = re.sub(r'[^a-zA-Z0-9\s_-]', '', field_name)
        
        # Replace multiple spaces with single space
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove leading/trailing spaces
        cleaned = cleaned.strip()
        
        # Apply field mappings
        for old, new in self.field_mappings.items():
            if cleaned.lower() == old.lower():
                cleaned = new
                break
        
        return cleaned
    
    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase."""
        if not text:
            return ""
        
        # Split by common delimiters
        words = re.split(r'[\s_-]+', text)
        
        if not words:
            return ""
        
        # First word in lowercase, rest capitalized
        result = words[0].lower()
        for word in words[1:]:
            if word:
                result += word.capitalize()
        
        return result
    
    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        if not text:
            return ""
        
        # Split by common delimiters
        words = re.split(r'[\s_-]+', text)
        
        if not words:
            return ""
        
        # All words capitalized
        result = ""
        for word in words:
            if word:
                result += word.capitalize()
        
        return result
    
    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case."""
        if not text:
            return ""
        
        # Insert underscores before capitals and convert to lowercase
        result = re.sub(r'([A-Z])', r'_\1', text)
        result = result.lower()
        
        # Clean up multiple underscores
        result = re.sub(r'_+', '_', result)
        
        # Remove leading/trailing underscores
        result = result.strip('_')
        
        return result
    
    def _to_kebab_case(self, text: str) -> str:
        """Convert text to kebab-case."""
        if not text:
            return ""
        
        # Convert to snake_case first, then replace underscores with hyphens
        snake_case = self._to_snake_case(text)
        return snake_case.replace('_', '-')
    
    def normalize_path(self, path: str, separator: str = '.') -> str:
        """
        Normalize a path string.
        
        Args:
            path: Path string to normalize
            separator: Path separator character
            
        Returns:
            Normalized path string
        """
        if not path:
            return ""
        
        # Split path into components
        components = path.split(separator)
        
        # Clean each component
        cleaned_components = []
        for component in components:
            cleaned = self._clean_field_name(component)
            if cleaned:
                cleaned_components.append(cleaned)
        
        # Join components back together
        return separator.join(cleaned_components)
    
    def normalize_data_type(self, data_type: str) -> str:
        """
        Normalize a data type to standard format.
        
        Args:
            data_type: Original data type
            
        Returns:
            Normalized data type
        """
        if not data_type:
            return "string"
        
        # Convert to lowercase for comparison
        type_lower = data_type.lower().strip()
        
        # Check type mappings
        for old_type, new_type in self.type_mappings.items():
            if type_lower == old_type.lower():
                return new_type
        
        # If no mapping found, return original (cleaned)
        return type_lower
    
    def normalize_cardinality(self, cardinality: str) -> str:
        """
        Normalize cardinality expression.
        
        Args:
            cardinality: Original cardinality string
            
        Returns:
            Normalized cardinality string
        """
        if not cardinality:
            return "1"
        
        # Convert to lowercase and clean
        cleaned = cardinality.lower().strip()
        
        # Common cardinality mappings
        cardinality_mappings = {
            'optional': '0..1',
            'required': '1',
            'multiple': '0..*',
            'one_or_more': '1..*',
            'zero_or_one': '0..1',
            'one': '1',
            'many': '0..*',
            'at_least_one': '1..*'
        }
        
        # Check mappings
        for old, new in cardinality_mappings.items():
            if cleaned == old:
                return new
        
        # If it's already in standard format, return as is
        if re.match(r'^\d+\.\.\*?$|^\d+$', cleaned):
            return cleaned
        
        return "1"  # Default to required
    
    def normalize_description(self, description: str) -> str:
        """
        Normalize a description field.
        
        Args:
            description: Original description
            
        Returns:
            Normalized description
        """
        if not description:
            return ""
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', description.strip())
        
        # Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        return cleaned
    
    def normalize_field_list(self, fields: List[str], target_case: CaseStyle = CaseStyle.CAMEL_CASE) -> List[str]:
        """
        Normalize a list of field names.
        
        Args:
            fields: List of field names
            target_case: Target case style
            
        Returns:
            List of normalized field names
        """
        return [self.normalize_field_name(field, target_case) for field in fields if field]
    
    def normalize_schema_data(
        self,
        headers: List[str],
        rows: List[List[str]],
        target_case: CaseStyle = CaseStyle.CAMEL_CASE
    ) -> Tuple[List[str], List[List[str]]]:
        """
        Normalize schema data including headers and field names.
        
        Args:
            headers: Column headers
            rows: Data rows
            target_case: Target case style for field names
            
        Returns:
            Tuple of (normalized_headers, normalized_rows)
        """
        # Normalize headers
        normalized_headers = []
        for header in headers:
            if header.startswith('Element Level'):
                # Keep level headers as is
                normalized_headers.append(header)
            else:
                # Normalize other headers
                normalized_headers.append(self.normalize_field_name(header, target_case))
        
        # Normalize rows
        normalized_rows = []
        for row in rows:
            normalized_row = []
            for i, cell in enumerate(row):
                if i < len(headers):
                    header = headers[i]
                    if header.startswith('Element Level'):
                        # Normalize element names
                        normalized_row.append(self.normalize_field_name(cell, target_case))
                    elif header.lower() == 'type':
                        # Normalize data types
                        normalized_row.append(self.normalize_data_type(cell))
                    elif header.lower() == 'cardinality':
                        # Normalize cardinality
                        normalized_row.append(self.normalize_cardinality(cell))
                    elif header.lower() == 'description':
                        # Normalize descriptions
                        normalized_row.append(self.normalize_description(cell))
                    else:
                        # Keep other fields as is
                        normalized_row.append(cell)
                else:
                    normalized_row.append(cell)
            normalized_rows.append(normalized_row)
        
        return normalized_headers, normalized_rows
    
    def create_field_mapping(
        self,
        source_fields: List[str],
        target_fields: List[str]
    ) -> Dict[str, str]:
        """
        Create a mapping between source and target fields based on similarity.
        
        Args:
            source_fields: List of source field names
            target_fields: List of target field names
            
        Returns:
            Dictionary mapping source fields to target fields
        """
        mapping = {}
        
        for source_field in source_fields:
            best_match = None
            best_similarity = 0.0
            
            for target_field in target_fields:
                similarity = self._calculate_field_similarity(source_field, target_field)
                if similarity > best_similarity and similarity > 0.7:  # Threshold
                    best_similarity = similarity
                    best_match = target_field
            
            if best_match:
                mapping[source_field] = best_match
        
        return mapping
    
    def _calculate_field_similarity(self, field1: str, field2: str) -> float:
        """
        Calculate similarity between two field names.
        
        Args:
            field1: First field name
            field2: Second field name
            
        Returns:
            Similarity score between 0 and 1
        """
        if not field1 or not field2:
            return 0.0
        
        # Normalize both fields to same case for comparison
        norm1 = self.normalize_field_name(field1, CaseStyle.LOWER_CASE)
        norm2 = self.normalize_field_name(field2, CaseStyle.LOWER_CASE)
        
        # Exact match
        if norm1 == norm2:
            return 1.0
        
        # Calculate similarity using simple string matching
        # This is a simplified version - could be enhanced with more sophisticated algorithms
        shorter = norm1 if len(norm1) < len(norm2) else norm2
        longer = norm2 if len(norm1) < len(norm2) else norm1
        
        if len(shorter) == 0:
            return 0.0
        
        # Count common characters
        common_chars = sum(1 for c in shorter if c in longer)
        return common_chars / len(longer)
    
    def standardize_field_names(
        self,
        field_names: List[str],
        convention: str = "camelCase"
    ) -> List[str]:
        """
        Standardize field names according to a naming convention.
        
        Args:
            field_names: List of field names
            convention: Naming convention to apply
            
        Returns:
            List of standardized field names
        """
        case_style = CaseStyle.CAMEL_CASE  # Default
        
        if convention.lower() == "pascalcase":
            case_style = CaseStyle.PASCAL_CASE
        elif convention.lower() == "snake_case":
            case_style = CaseStyle.SNAKE_CASE
        elif convention.lower() == "kebab-case":
            case_style = CaseStyle.KEBAB_CASE
        elif convention.lower() == "uppercase":
            case_style = CaseStyle.UPPER_CASE
        elif convention.lower() == "lowercase":
            case_style = CaseStyle.LOWER_CASE
        
        return self.normalize_field_list(field_names, case_style) 