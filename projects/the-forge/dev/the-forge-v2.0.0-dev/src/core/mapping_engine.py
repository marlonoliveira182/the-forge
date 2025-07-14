"""
Enhanced Mapping Engine for The Forge v2.0.0
Maps fields between schemas with exact name preservation
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher

from .schema_processor import SchemaField

@dataclass
class FieldMapping:
    """Represents a mapping between source and target fields"""
    source_field: SchemaField
    target_field: SchemaField
    similarity: float
    confidence: str  # 'exact', 'good', 'weak', 'manual'
    mapping_notes: str = ""
    
    @property
    def is_exact_match(self) -> bool:
        """Check if this is an exact match"""
        return self.similarity >= 0.95 and self.confidence in ['exact', 'manual']
    
    @property
    def is_good_match(self) -> bool:
        """Check if this is a good match"""
        return 0.7 <= self.similarity < 0.95 and self.confidence in ['good', 'manual']
    
    @property
    def is_weak_match(self) -> bool:
        """Check if this is a weak match"""
        return 0.3 <= self.similarity < 0.7 and self.confidence in ['weak', 'manual']
    
    @property
    def is_unmapped(self) -> bool:
        """Check if this field is unmapped"""
        return self.similarity < 0.3 or self.confidence == 'unmapped'

class MappingEngine:
    """Enhanced mapping engine that preserves exact field names"""
    
    def __init__(self):
        self.mappings: List[FieldMapping] = []
        self.similarity_threshold = 0.3
        self.exact_match_threshold = 0.95
        self.good_match_threshold = 0.7
    
    def map_fields(self, source_fields: List[SchemaField], target_fields: List[SchemaField]) -> List[FieldMapping]:
        """Map fields between source and target schemas with exact name preservation"""
        self.mappings = []

        # Only consider leaf fields (not complex containers) for mapping
        filtered_source_fields = [f for f in source_fields if not f.is_complex]
        filtered_target_fields = [f for f in target_fields if not f.is_complex]

        # Create mappings for all source fields
        for source_field in filtered_source_fields:
            best_mapping = self._find_best_match(source_field, filtered_target_fields)
            if best_mapping:
                self.mappings.append(best_mapping)
            else:
                # Create unmapped entry
                unmapped_mapping = FieldMapping(
                    source_field=source_field,
                    target_field=SchemaField(
                        path="",
                        name="",
                        type="",
                        description="",
                        cardinality="",
                        required=False,
                        parent_path="",
                        is_array=False,
                        is_complex=False,
                        constraints={},
                        metadata={}
                    ),
                    similarity=0.0,
                    confidence="unmapped",
                    mapping_notes="No matching field found"
                )
                self.mappings.append(unmapped_mapping)

        return self.mappings
    
    def _find_best_match(self, source_field: SchemaField, target_fields: List[SchemaField]) -> Optional[FieldMapping]:
        """Find the best matching target field for a source field"""
        best_match = None
        best_similarity = 0.0
        
        for target_field in target_fields:
            similarity = self._calculate_field_similarity(source_field, target_field)
            
            if similarity > best_similarity and similarity >= self.similarity_threshold:
                best_similarity = similarity
                best_match = target_field
        
        if best_match:
            confidence = self._determine_confidence(best_similarity)
            notes = self._generate_mapping_notes(source_field, best_match, best_similarity)
            
            return FieldMapping(
                source_field=source_field,
                target_field=best_match,
                similarity=best_similarity,
                confidence=confidence,
                mapping_notes=notes
            )
        
        return None
    
    def _calculate_field_similarity(self, source_field: SchemaField, target_field: SchemaField) -> float:
        """Calculate similarity between two fields with exact name preservation"""
        # Exact name match (case-insensitive)
        if source_field.name.strip().lower() == target_field.name.strip().lower():
            print(f"[DEBUG] Similarity: Exact name match: {source_field.name} == {target_field.name} -> 1.0")
            return 1.0
        # Compute similarities
        name_similarity = SequenceMatcher(None, source_field.name.lower(), target_field.name.lower()).ratio()
        path_similarity = SequenceMatcher(None, source_field.path.lower(), target_field.path.lower()).ratio()
        type_compatibility = 1.0 if source_field.type.lower() == target_field.type.lower() else 0.0
        # If type is not compatible and name similarity is low, force very low similarity
        if type_compatibility == 0.0 and name_similarity < 0.85:
            total_similarity = 0.2 * name_similarity
            print(f"[DEBUG] Similarity: Forced very low for unrelated fields: name_sim={name_similarity:.3f} type_sim={type_compatibility:.1f} -> total={total_similarity:.3f}")
            return total_similarity
        # Weighted sum (lower name weight, higher type penalty)
        weights = {'name': 0.4, 'type': 0.4, 'path': 0.2}
        total_similarity = (
            name_similarity * weights['name'] +
            type_compatibility * weights['type'] +
            path_similarity * weights['path']
        )
        print(f"[DEBUG] Similarity: src={source_field.name} tgt={target_field.name} | name_sim={name_similarity:.3f} type_sim={type_compatibility:.1f} path_sim={path_similarity:.3f} -> total={total_similarity:.3f}")
        return max(0.0, min(1.0, total_similarity))
    
    def _calculate_type_compatibility(self, source_type: str, target_type: str) -> float:
        """Calculate type compatibility between source and target types"""
        # Normalize types
        source_norm = self._normalize_type(source_type)
        target_norm = self._normalize_type(target_type)
        
        # Exact type match
        if source_norm == target_norm:
            return 1.0
        
        # Compatible types
        compatible_groups = [
            ['string', 'text', 'char'],
            ['integer', 'int', 'number'],
            ['decimal', 'float', 'double'],
            ['boolean', 'bool'],
            ['date', 'datetime', 'timestamp'],
            ['array', 'list'],
            ['object', 'complex', 'struct']
        ]
        
        for group in compatible_groups:
            if source_norm in group and target_norm in group:
                return 0.8
        
        # Partial compatibility
        if source_norm in target_norm or target_norm in source_norm:
            return 0.6
        
        return 0.0
    
    def _normalize_type(self, type_str: str) -> str:
        """Normalize type string for comparison"""
        if not type_str:
            return 'string'
        
        # Remove namespace prefixes
        if ':' in type_str:
            type_str = type_str.split(':')[-1]
        
        # Normalize common types
        type_mapping = {
            'xs:string': 'string',
            'xs:integer': 'integer',
            'xs:decimal': 'decimal',
            'xs:boolean': 'boolean',
            'xs:date': 'date',
            'xs:dateTime': 'datetime',
            'xs:array': 'array',
            'xs:object': 'object'
        }
        
        return type_mapping.get(type_str.lower(), type_str.lower())
    
    def _determine_confidence(self, similarity: float) -> str:
        """Determine confidence level based on similarity score"""
        if similarity >= self.exact_match_threshold:
            return 'exact'
        elif similarity >= self.good_match_threshold:
            return 'good'
        elif similarity >= self.similarity_threshold:
            return 'weak'
        else:
            return 'unmapped'
    
    def _generate_mapping_notes(self, source_field: SchemaField, target_field: SchemaField, similarity: float) -> str:
        """Generate mapping notes explaining the match"""
        notes = []
        
        # Name match quality
        if source_field.name.lower() == target_field.name.lower():
            notes.append("Exact name match")
        elif similarity >= 0.8:
            notes.append("High similarity match")
        elif similarity >= 0.6:
            notes.append("Good similarity match")
        else:
            notes.append("Weak similarity match")
        
        # Type compatibility
        if source_field.type == target_field.type:
            notes.append("Exact type match")
        elif self._calculate_type_compatibility(source_field.type, target_field.type) >= 0.8:
            notes.append("Compatible types")
        else:
            notes.append("Type mismatch")
        
        # Cardinality comparison
        if source_field.cardinality == target_field.cardinality:
            notes.append("Same cardinality")
        else:
            notes.append(f"Cardinality: {source_field.cardinality} -> {target_field.cardinality}")
        
        # Required field comparison
        if source_field.required == target_field.required:
            notes.append("Same required status")
        else:
            notes.append(f"Required: {source_field.required} -> {target_field.required}")
        
        return "; ".join(notes)
    
    def validate_mapping(self) -> Dict[str, Any]:
        """Validate the current mapping and return statistics"""
        if not self.mappings:
            return {
                'total_mappings': 0,
                'exact_matches': 0,
                'good_matches': 0,
                'weak_matches': 0,
                'unmapped': 0,
                'completeness': {'source_coverage': 0.0, 'target_coverage': 0.0},
                'average_similarity': 0.0,
                'issues': [],
                'warnings': []
            }
        
        # Count different types of matches
        exact_matches = len([m for m in self.mappings if m.is_exact_match])
        good_matches = len([m for m in self.mappings if m.is_good_match])
        weak_matches = len([m for m in self.mappings if m.is_weak_match])
        unmapped = len([m for m in self.mappings if m.is_unmapped])
        
        # Calculate average similarity
        mapped_similarities = [m.similarity for m in self.mappings if not m.is_unmapped]
        average_similarity = sum(mapped_similarities) / len(mapped_similarities) if mapped_similarities else 0.0
        
        # Calculate coverage
        total_source_fields = len(self.mappings)
        mapped_source_fields = total_source_fields - unmapped
        source_coverage = mapped_source_fields / total_source_fields if total_source_fields > 0 else 0.0
        
        # Count unique target fields used
        used_target_fields = set()
        for mapping in self.mappings:
            if not mapping.is_unmapped and mapping.target_field.path:
                used_target_fields.add(mapping.target_field.path)
        
        # This would need target field count from the original schema
        target_coverage = 0.0  # Would need total target fields to calculate
        
        # Identify issues and warnings
        issues = []
        warnings = []
        
        for mapping in self.mappings:
            if mapping.is_unmapped:
                issues.append({
                    'type': 'unmapped_field',
                    'message': f"Source field '{mapping.source_field.name}' has no mapping"
                })
            
            if mapping.similarity < 0.5 and not mapping.is_unmapped:
                warnings.append({
                    'type': 'low_similarity',
                    'message': f"Low similarity mapping: {mapping.source_field.name} -> {mapping.target_field.name} ({mapping.similarity:.3f})"
                })
            
            if mapping.source_field.type != mapping.target_field.type and not mapping.is_unmapped:
                warnings.append({
                    'type': 'type_mismatch',
                    'message': f"Type mismatch: {mapping.source_field.name} ({mapping.source_field.type}) -> {mapping.target_field.name} ({mapping.target_field.type})"
                })
        
        return {
            'total_mappings': len(self.mappings),
            'exact_matches': exact_matches,
            'good_matches': good_matches,
            'weak_matches': weak_matches,
            'unmapped': unmapped,
            'completeness': {
                'source_coverage': source_coverage,
                'target_coverage': target_coverage
            },
            'average_similarity': average_similarity,
            'issues': issues,
            'warnings': warnings
        }
    
    def get_mapping_summary(self) -> Dict[str, Any]:
        """Get a summary of the current mappings"""
        if not self.mappings:
            return {'message': 'No mappings available'}
        
        validation = self.validate_mapping()
        
        return {
            'total_mappings': validation['total_mappings'],
            'mapping_quality': {
                'exact_matches': validation['exact_matches'],
                'good_matches': validation['good_matches'],
                'weak_matches': validation['weak_matches'],
                'unmapped': validation['unmapped']
            },
            'coverage': validation['completeness'],
            'average_similarity': validation['average_similarity'],
            'issues_count': len(validation['issues']),
            'warnings_count': len(validation['warnings'])
        } 