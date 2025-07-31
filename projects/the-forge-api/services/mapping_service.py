from typing import List, Dict, Any
import re

class MappingService:
    def __init__(self):
        pass
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using various metrics"""
        if not str1 or not str2:
            return 0.0
        
        # Normalize strings
        s1 = str1.lower().strip()
        s2 = str2.lower().strip()
        
        # Exact match
        if s1 == s2:
            return 1.0
        
        # Check for common prefixes
        min_len = min(len(s1), len(s2))
        common_prefix = 0
        for i in range(min_len):
            if s1[i] == s2[i]:
                common_prefix += 1
            else:
                break
        
        # Check for common suffixes
        common_suffix = 0
        for i in range(1, min_len + 1):
            if s1[-i] == s2[-i]:
                common_suffix += 1
            else:
                break
        
        # Calculate similarity based on common parts
        total_common = common_prefix + common_suffix
        max_len = max(len(s1), len(s2))
        
        if max_len == 0:
            return 0.0
        
        # Weight the similarity (prefix is more important than suffix)
        similarity = (common_prefix * 0.7 + common_suffix * 0.3) / max_len
        
        # Add bonus for length similarity
        length_diff = abs(len(s1) - len(s2))
        length_penalty = length_diff / max_len * 0.2
        
        return max(0.0, similarity - length_penalty)
    
    def normalize_field_name(self, field_name: str) -> str:
        """Normalize field name for better matching"""
        if not field_name:
            return ""
        
        # Remove common prefixes/suffixes
        normalized = field_name.lower()
        normalized = re.sub(r'^(the|a|an)_', '', normalized)
        normalized = re.sub(r'_(the|a|an)$', '', normalized)
        
        # Replace common separators
        normalized = re.sub(r'[_\-\s]+', '_', normalized)
        
        # Remove common suffixes
        normalized = re.sub(r'_(id|name|type|value|data|info|details)$', '', normalized)
        
        return normalized
    
    def create_field_mapping(self, source_fields: List[Dict[str, Any]], 
                           target_fields: List[Dict[str, Any]], 
                           threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Create mapping between source and target fields"""
        mapping = []
        
        # Extract field names and paths
        source_paths = [field.get('path', '') for field in source_fields]
        target_paths = [field.get('path', '') for field in target_fields]
        
        # Create mapping for each source field
        for i, source_field in enumerate(source_fields):
            source_path = source_paths[i]
            source_name = source_field.get('name', '')
            source_type = source_field.get('type', '')
            
            # Find best match in target fields
            best_match = None
            best_similarity = 0.0
            
            for j, target_field in enumerate(target_fields):
                target_path = target_paths[j]
                target_name = target_field.get('name', '')
                target_type = target_field.get('type', '')
                
                # Calculate similarity for different aspects
                name_similarity = self.calculate_similarity(source_name, target_name)
                path_similarity = self.calculate_similarity(source_path, target_path)
                type_similarity = self.calculate_similarity(source_type, target_type)
                
                # Weighted similarity score
                overall_similarity = (name_similarity * 0.5 + path_similarity * 0.3 + type_similarity * 0.2)
                
                if overall_similarity > best_similarity and overall_similarity >= threshold:
                    best_similarity = overall_similarity
                    best_match = {
                        'target_field': target_name,
                        'target_path': target_path,
                        'target_type': target_type,
                        'similarity': overall_similarity
                    }
            
            # Create mapping entry
            mapping_entry = {
                'source': source_name,
                'source_path': source_path,
                'source_type': source_type,
                'target': best_match['target_field'] if best_match else '',
                'target_path': best_match['target_path'] if best_match else '',
                'target_type': best_match['target_type'] if best_match else '',
                'similarity': best_match['similarity'] if best_match else 0.0,
                'notes': self._generate_mapping_notes(source_field, best_match) if best_match else 'No match found'
            }
            
            mapping.append(mapping_entry)
        
        return mapping
    
    def _generate_mapping_notes(self, source_field: Dict[str, Any], target_match: Dict[str, Any]) -> str:
        """Generate notes about the mapping"""
        notes = []
        
        similarity = target_match.get('similarity', 0.0)
        if similarity >= 0.9:
            notes.append("Excellent match")
        elif similarity >= 0.7:
            notes.append("Good match")
        elif similarity >= 0.5:
            notes.append("Partial match")
        else:
            notes.append("Weak match")
        
        # Add type compatibility note
        source_type = source_field.get('type', '')
        target_type = target_match.get('target_type', '')
        
        if source_type == target_type:
            notes.append("Type compatible")
        elif self._are_types_compatible(source_type, target_type):
            notes.append("Type convertible")
        else:
            notes.append("Type mismatch")
        
        return "; ".join(notes)
    
    def _are_types_compatible(self, type1: str, type2: str) -> bool:
        """Check if two types are compatible for conversion"""
        if not type1 or not type2:
            return False
        
        # Define type compatibility groups
        string_types = {'string', 'text', 'char', 'varchar'}
        number_types = {'integer', 'int', 'number', 'float', 'double', 'decimal'}
        boolean_types = {'boolean', 'bool'}
        date_types = {'date', 'datetime', 'timestamp'}
        
        type1_lower = type1.lower()
        type2_lower = type2.lower()
        
        # Check if both types are in the same group
        if type1_lower in string_types and type2_lower in string_types:
            return True
        if type1_lower in number_types and type2_lower in number_types:
            return True
        if type1_lower in boolean_types and type2_lower in boolean_types:
            return True
        if type1_lower in date_types and type2_lower in date_types:
            return True
        
        return False 