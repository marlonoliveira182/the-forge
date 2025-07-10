"""
Mapping engine for creating correspondences between schema fields.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .schema_processor import SchemaField


@dataclass
class MappingResult:
    """Represents a mapping between source and target fields."""
    source: str
    target: str
    similarity: float
    source_field: Optional[SchemaField] = None
    target_field: Optional[SchemaField] = None


class MappingEngine:
    """Handles mapping between schema fields using similarity algorithms."""
    
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self._setup_similarity_function()
    
    def _setup_similarity_function(self):
        """Setup the similarity function with fallback."""
        try:
            from Levenshtein import ratio as levenshtein_ratio
            self._similarity_func = levenshtein_ratio
        except ImportError:
            self._similarity_func = self._fallback_similarity
    
    def _fallback_similarity(self, a: str, b: str) -> float:
        """Fallback similarity function using common prefix ratio."""
        min_len = min(len(a), len(b))
        common = 0
        for i in range(min_len):
            if a[i] == b[i]:
                common += 1
            else:
                break
        return common / max(len(a), len(b)) if max(len(a), len(b)) > 0 else 0
    
    def normalize_levels(self, levels: List[str]) -> List[str]:
        """Normalize field levels for comparison."""
        return [
            'arrayitem' if (isinstance(l, str) and l.lower() in ('item', '[]')) 
            else (l.lower() if isinstance(l, str) else l)
            for l in levels
        ]
    
    def normalized_path_from_levels(self, levels: List[str]) -> str:
        """Create normalized path from field levels."""
        return '.'.join([
            'arrayitem' if (isinstance(l, str) and l.lower() in ('item', '[]')) 
            else (l.lower() if isinstance(l, str) else l)
            for l in levels
        ])
    
    def map_fields(self, source_fields: List[SchemaField], 
                   target_fields: List[SchemaField]) -> List[MappingResult]:
        """Map source fields to target fields based on similarity."""
        # Build normalized path lists
        source_paths = [self.normalized_path_from_levels(f.levels) for f in source_fields]
        target_paths = [self.normalized_path_from_levels(f.levels) for f in target_fields]
        
        # Create field maps for lookup
        source_field_map = {self.normalized_path_from_levels(f.levels): f for f in source_fields}
        target_field_map = {self.normalized_path_from_levels(f.levels): f for f in target_fields}
        
        mapping = []
        
        for s_path, s_field in zip(source_paths, source_fields):
            # Try exact match first
            exact_match = None
            for t_path in target_paths:
                if s_path == t_path:
                    exact_match = t_path
                    break
            
            if exact_match:
                mapping.append(MappingResult(
                    source=s_path,
                    target=exact_match,
                    similarity=1.0,
                    source_field=s_field,
                    target_field=target_field_map[exact_match]
                ))
            else:
                # Find best similarity match
                best_match = ('', 0.0)
                for t_path in target_paths:
                    sim = self._similarity_func(s_path, t_path)
                    if sim > best_match[1]:
                        best_match = (t_path, sim)
                
                if best_match[1] >= self.threshold:
                    mapping.append(MappingResult(
                        source=s_path,
                        target=best_match[0],
                        similarity=round(best_match[1], 3),
                        source_field=s_field,
                        target_field=target_field_map.get(best_match[0])
                    ))
                else:
                    mapping.append(MappingResult(
                        source=s_path,
                        target='',
                        similarity=0.0,
                        source_field=s_field,
                        target_field=None
                    ))
        
        return mapping
    
    def validate_mapping(self, mapping: List[MappingResult]) -> Dict[str, Any]:
        """Validate mapping results and provide statistics."""
        total_mappings = len(mapping)
        exact_matches = sum(1 for m in mapping if m.similarity == 1.0)
        threshold_matches = sum(1 for m in mapping if m.similarity >= self.threshold and m.similarity < 1.0)
        no_matches = sum(1 for m in mapping if m.similarity < self.threshold)
        
        avg_similarity = sum(m.similarity for m in mapping) / total_mappings if total_mappings > 0 else 0
        
        return {
            'total_mappings': total_mappings,
            'exact_matches': exact_matches,
            'threshold_matches': threshold_matches,
            'no_matches': no_matches,
            'average_similarity': round(avg_similarity, 3),
            'coverage_percentage': round((exact_matches + threshold_matches) / total_mappings * 100, 1) if total_mappings > 0 else 0
        }
    
    def get_unmapped_fields(self, mapping: List[MappingResult], 
                           source_fields: List[SchemaField], 
                           target_fields: List[SchemaField]) -> Dict[str, List[str]]:
        """Get lists of unmapped fields from both source and target."""
        mapped_source_paths = {m.source for m in mapping if m.similarity >= self.threshold}
        mapped_target_paths = {m.target for m in mapping if m.similarity >= self.threshold}
        
        all_source_paths = {self.normalized_path_from_levels(f.levels) for f in source_fields}
        all_target_paths = {self.normalized_path_from_levels(f.levels) for f in target_fields}
        
        unmapped_source = list(all_source_paths - mapped_source_paths)
        unmapped_target = list(all_target_paths - mapped_target_paths)
        
        return {
            'unmapped_source': unmapped_source,
            'unmapped_target': unmapped_target
        }
    
    def suggest_mappings(self, unmapped_source: List[str], 
                        unmapped_target: List[str]) -> List[MappingResult]:
        """Suggest additional mappings for unmapped fields."""
        suggestions = []
        
        for s_path in unmapped_source:
            best_match = ('', 0.0)
            for t_path in unmapped_target:
                sim = self._similarity_func(s_path, t_path)
                if sim > best_match[1]:
                    best_match = (t_path, sim)
            
            if best_match[1] > 0.3:  # Lower threshold for suggestions
                suggestions.append(MappingResult(
                    source=s_path,
                    target=best_match[0],
                    similarity=round(best_match[1], 3)
                ))
        
        return suggestions 