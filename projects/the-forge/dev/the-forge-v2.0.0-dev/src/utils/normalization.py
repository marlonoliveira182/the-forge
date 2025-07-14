"""
Normalization utilities for The Forge v2.0.0
"""

import re
from typing import List, Dict, Any

class NormalizationUtils:
    """Utility class for field name normalization and case conversion"""
    
    @staticmethod
    def to_camel_case(text: str) -> str:
        """Convert text to camelCase"""
        if not text:
            return text
        
        # Remove special characters and split by common separators
        words = re.split(r'[_\s\-\.]+', text)
        
        if not words:
            return text
        
        # First word is lowercase, rest are capitalized
        result = words[0].lower()
        for word in words[1:]:
            if word:
                result += word.capitalize()
        
        return result
    
    @staticmethod
    def to_pascal_case(text: str) -> str:
        """Convert text to PascalCase"""
        if not text:
            return text
        
        # Remove special characters and split by common separators
        words = re.split(r'[_\s\-\.]+', text)
        
        if not words:
            return text
        
        # All words are capitalized
        result = ""
        for word in words:
            if word:
                result += word.capitalize()
        
        return result
    
    @staticmethod
    def to_snake_case(text: str) -> str:
        """Convert text to snake_case"""
        if not text:
            return text
        
        # Insert underscore before capital letters and convert to lowercase
        text = re.sub(r'([A-Z])', r'_\1', text)
        text = text.lower()
        
        # Remove leading/trailing underscores and multiple underscores
        text = re.sub(r'^_+|_+$', '', text)
        text = re.sub(r'_+', '_', text)
        
        return text
    
    @staticmethod
    def to_kebab_case(text: str) -> str:
        """Convert text to kebab-case"""
        if not text:
            return text
        
        # Convert to snake case first, then replace underscores with hyphens
        snake_case = NormalizationUtils.to_snake_case(text)
        return snake_case.replace('_', '-')
    
    @staticmethod
    def normalize_field_name(name: str, target_case: str = "camel") -> str:
        """Normalize field name to target case convention"""
        if not name:
            return name
        
        if target_case == "camel":
            return NormalizationUtils.to_camel_case(name)
        elif target_case == "pascal":
            return NormalizationUtils.to_pascal_case(name)
        elif target_case == "snake":
            return NormalizationUtils.to_snake_case(name)
        elif target_case == "kebab":
            return NormalizationUtils.to_kebab_case(name)
        else:
            return name
    
    @staticmethod
    def normalize_path(path: str, target_case: str = "camel") -> str:
        """Normalize a field path to target case convention"""
        if not path:
            return path
        
        # Split path by dots and normalize each part
        parts = path.split('.')
        normalized_parts = [NormalizationUtils.normalize_field_name(part, target_case) for part in parts]
        
        return '.'.join(normalized_parts)
    
    @staticmethod
    def extract_field_name_from_path(path: str) -> str:
        """Extract the field name from a path"""
        if not path:
            return path
        
        # Get the last part of the path
        parts = path.split('.')
        return parts[-1] if parts else path
    
    @staticmethod
    def get_parent_path(path: str) -> str:
        """Get the parent path"""
        if not path:
            return path
        
        parts = path.split('.')
        if len(parts) <= 1:
            return ""
        
        return '.'.join(parts[:-1])
    
    @staticmethod
    def normalize_constraints(constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize constraint values"""
        normalized = {}
        
        for key, value in constraints.items():
            # Normalize constraint key names
            normalized_key = NormalizationUtils.to_snake_case(key)
            
            # Handle specific constraint types
            if key in ['maxLength', 'minLength']:
                normalized[normalized_key] = int(value) if value is not None else None
            elif key in ['maximum', 'minimum', 'multipleOf']:
                normalized[normalized_key] = float(value) if value is not None else None
            elif key in ['pattern']:
                normalized[normalized_key] = str(value) if value is not None else None
            elif key in ['enum']:
                if isinstance(value, list):
                    normalized[normalized_key] = [str(item) for item in value]
                else:
                    normalized[normalized_key] = [str(value)]
            else:
                normalized[normalized_key] = value
        
        return normalized
    
    @staticmethod
    def compare_field_names(name1: str, name2: str, case_sensitive: bool = False) -> bool:
        """Compare two field names"""
        if not case_sensitive:
            name1 = name1.lower()
            name2 = name2.lower()
        
        return name1 == name2
    
    @staticmethod
    def get_field_similarity(name1: str, name2: str) -> float:
        """Calculate similarity between two field names"""
        if not name1 or not name2:
            return 0.0
        
        # Normalize names for comparison
        norm1 = NormalizationUtils.to_camel_case(name1.lower())
        norm2 = NormalizationUtils.to_camel_case(name2.lower())
        
        if norm1 == norm2:
            return 1.0
        
        # Calculate simple similarity based on common characters
        common_chars = 0
        total_chars = max(len(norm1), len(norm2))
        
        for char in norm1:
            if char in norm2:
                common_chars += 1
        
        return common_chars / total_chars if total_chars > 0 else 0.0
    
    @staticmethod
    def suggest_field_name(base_name: str, existing_names: List[str], target_case: str = "camel") -> str:
        """Suggest a field name that doesn't conflict with existing names"""
        if not base_name:
            return base_name
        
        normalized_base = NormalizationUtils.normalize_field_name(base_name, target_case)
        
        if normalized_base not in existing_names:
            return normalized_base
        
        # Try adding numbers until we find a unique name
        counter = 1
        while True:
            suggested_name = f"{normalized_base}{counter}"
            if suggested_name not in existing_names:
                return suggested_name
            counter += 1 