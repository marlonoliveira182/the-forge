"""
Mapping Engine Module

Handles path-based mapping between schemas with:
- Path normalization and matching
- Similarity heuristics
- Field mapping algorithms
- Mapping validation
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from difflib import SequenceMatcher
from dataclasses import dataclass


@dataclass
class MappingResult:
    """Represents a mapping between source and target fields."""
    source_path: str
    target_path: str
    confidence: float
    mapping_type: str
    notes: str = ""


class MappingEngine:
    """
    Handles path-based mapping between schemas with similarity heuristics.
    
    Provides methods for:
    - Path normalization and matching
    - Similarity-based field mapping
    - Mapping validation and quality assessment
    """
    
    def __init__(self):
        self.similarity_threshold = 0.7
        self.exact_match_weight = 1.0
        self.similarity_weight = 0.8
        self.path_weight = 0.6
        self.name_weight = 0.4
    
    def normalize_path(self, path: str) -> str:
        """
        Normalize a path for comparison.
        
        Args:
            path: The path to normalize
            
        Returns:
            Normalized path string
        """
        if not path:
            return ""
        
        # Convert to lowercase and trim
        normalized = path.lower().strip()
        
        # Remove empty parts and collapse multiple dots
        parts = [p.strip() for p in normalized.split('.') if p.strip()]
        
        return '.'.join(parts)
    
    def build_path_from_levels(
        self,
        row: List[str],
        level_indices: List[int],
        all_rows: Optional[List[List[str]]] = None,
        row_idx: Optional[int] = None
    ) -> str:
        """
        Build a path from level columns, filling empty values from above.
        
        Args:
            row: Data row
            level_indices: Indices of level columns
            all_rows: All data rows for lookup
            row_idx: Current row index
            
        Returns:
            Built path string
        """
        path_parts = []
        
        for idx in level_indices:
            val = row[idx] if idx < len(row) else None
            
            # If value is empty and we have all_rows, look up
            if (val is None or str(val).strip() == '') and all_rows is not None and row_idx is not None:
                # Search upward for non-empty value
                for up_idx in range(row_idx - 1, -1, -1):
                    if up_idx < len(all_rows) and idx < len(all_rows[up_idx]):
                        up_val = all_rows[up_idx][idx]
                        if up_val is not None and str(up_val).strip() != '':
                            val = up_val
                            break
            
            if val is not None and str(val).strip() != '':
                path_parts.append(str(val).strip())
        
        return '.'.join(path_parts)
    
    def get_level_indices(self, headers: List[str]) -> List[int]:
        """
        Get indices of level columns from headers.
        
        Args:
            headers: List of header strings
            
        Returns:
            List of level column indices
        """
        return [i for i, h in enumerate(headers) if h.strip().startswith('Element Level')]
    
    def extract_paths_from_excel(
        self,
        headers: List[str],
        rows: List[List[str]]
    ) -> Dict[str, str]:
        """
        Extract paths from Excel data.
        
        Args:
            headers: Column headers
            rows: Data rows
            
        Returns:
            Dictionary mapping normalized paths to original paths
        """
        level_indices = self.get_level_indices(headers)
        path_map = {}
        
        for idx, row in enumerate(rows):
            path = self.build_path_from_levels(row, level_indices, rows, idx)
            if path:
                norm_path = self.normalize_path(path)
                path_map[norm_path] = path
        
        return path_map
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0 and 1
        """
        if not str1 or not str2:
            return 0.0
        
        # Use SequenceMatcher for similarity
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def calculate_path_similarity(self, path1: str, path2: str) -> float:
        """
        Calculate similarity between two paths.
        
        Args:
            path1: First path
            path2: Second path
            
        Returns:
            Path similarity score
        """
        if not path1 or not path2:
            return 0.0
        
        # Split paths into parts
        parts1 = path1.lower().split('.')
        parts2 = path2.lower().split('.')
        
        # Calculate similarity for each part
        similarities = []
        max_len = max(len(parts1), len(parts2))
        
        for i in range(max_len):
            part1 = parts1[i] if i < len(parts1) else ""
            part2 = parts2[i] if i < len(parts2) else ""
            
            if part1 and part2:
                similarity = self.calculate_similarity(part1, part2)
                similarities.append(similarity)
            elif part1 == part2:  # Both empty
                similarities.append(1.0)
            else:
                similarities.append(0.0)
        
        # Return average similarity
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def find_best_matches(
        self,
        source_paths: Dict[str, str],
        target_paths: Dict[str, str],
        max_matches: int = 3
    ) -> List[MappingResult]:
        """
        Find best matches between source and target paths.
        
        Args:
            source_paths: Dictionary of source paths
            target_paths: Dictionary of target paths
            max_matches: Maximum number of matches to return per source
            
        Returns:
            List of mapping results
        """
        mappings = []
        
        for norm_src_path, src_path in source_paths.items():
            matches = []
            
            for norm_tgt_path, tgt_path in target_paths.items():
                # Calculate different similarity metrics
                exact_match = norm_src_path == norm_tgt_path
                path_similarity = self.calculate_path_similarity(norm_src_path, norm_tgt_path)
                name_similarity = self.calculate_similarity(
                    norm_src_path.split('.')[-1] if '.' in norm_src_path else norm_src_path,
                    norm_tgt_path.split('.')[-1] if '.' in norm_tgt_path else norm_tgt_path
                )
                
                # Calculate weighted confidence
                if exact_match:
                    confidence = self.exact_match_weight
                    mapping_type = "exact"
                else:
                    confidence = (
                        path_similarity * self.path_weight +
                        name_similarity * self.name_weight
                    )
                    mapping_type = "similar" if confidence >= self.similarity_threshold else "low_confidence"
                
                if confidence > 0:
                    matches.append(MappingResult(
                        source_path=src_path,
                        target_path=tgt_path,
                        confidence=confidence,
                        mapping_type=mapping_type,
                        notes=f"Path similarity: {path_similarity:.2f}, Name similarity: {name_similarity:.2f}"
                    ))
            
            # Sort by confidence and take top matches
            matches.sort(key=lambda x: x.confidence, reverse=True)
            mappings.extend(matches[:max_matches])
        
        return mappings
    
    def create_mapping_matrix(
        self,
        source_headers: List[str],
        source_rows: List[List[str]],
        target_headers: List[str],
        target_rows: List[List[str]]
    ) -> Tuple[List[str], List[List[str]]]:
        """
        Create a mapping matrix between source and target schemas.
        
        Args:
            source_headers: Source schema headers
            source_rows: Source schema data
            target_headers: Target schema headers
            target_rows: Target schema data
            
        Returns:
            Tuple of (headers, rows) for the mapping matrix
        """
        # Extract paths from both schemas
        source_paths = self.extract_paths_from_excel(source_headers, source_rows)
        target_paths = self.extract_paths_from_excel(target_headers, target_rows)
        
        # Find mappings
        mappings = self.find_best_matches(source_paths, target_paths)
        
        # Create mapping matrix
        headers = source_headers + ['Destination Field (Target Path)'] + target_headers
        rows = []
        
        # Create a mapping lookup
        mapping_lookup = {}
        for mapping in mappings:
            mapping_lookup[mapping.source_path] = mapping.target_path
        
        # Build rows
        for source_row in source_rows:
            source_path = self.build_path_from_levels(
                source_row,
                self.get_level_indices(source_headers),
                source_rows,
                source_rows.index(source_row)
            )
            
            # Find corresponding target row
            target_row = [''] * len(target_headers)
            if source_path in mapping_lookup:
                target_path = mapping_lookup[source_path]
                # Find target row with matching path
                for tgt_row in target_rows:
                    tgt_path = self.build_path_from_levels(
                        tgt_row,
                        self.get_level_indices(target_headers),
                        target_rows,
                        target_rows.index(tgt_row)
                    )
                    if tgt_path == target_path:
                        target_row = tgt_row
                        break
            
            # Create merged row
            destination_field = mapping_lookup.get(source_path, '')
            merged_row = source_row + [destination_field] + target_row
            rows.append(merged_row)
        
        return headers, rows
    
    def validate_mappings(
        self,
        mappings: List[MappingResult]
    ) -> Tuple[List[str], Dict[str, Any]]:
        """
        Validate mapping results and return issues and statistics.
        
        Args:
            mappings: List of mapping results
            
        Returns:
            Tuple of (issues, statistics)
        """
        issues = []
        stats = {
            'total_mappings': len(mappings),
            'exact_matches': 0,
            'similar_matches': 0,
            'low_confidence': 0,
            'average_confidence': 0.0,
            'unmapped_sources': 0
        }
        
        if not mappings:
            issues.append("No mappings found")
            return issues, stats
        
        total_confidence = 0.0
        
        for mapping in mappings:
            total_confidence += mapping.confidence
            
            if mapping.mapping_type == "exact":
                stats['exact_matches'] += 1
            elif mapping.mapping_type == "similar":
                stats['similar_matches'] += 1
            else:
                stats['low_confidence'] += 1
            
            if mapping.confidence < self.similarity_threshold:
                issues.append(
                    f"Low confidence mapping: {mapping.source_path} -> {mapping.target_path} "
                    f"(confidence: {mapping.confidence:.2f})"
                )
        
        stats['average_confidence'] = total_confidence / len(mappings)
        
        return issues, stats
    
    def suggest_mappings(
        self,
        source_paths: List[str],
        target_paths: List[str]
    ) -> List[MappingResult]:
        """
        Suggest potential mappings based on similarity.
        
        Args:
            source_paths: List of source paths
            target_paths: List of target paths
            
        Returns:
            List of suggested mappings
        """
        suggestions = []
        
        for src_path in source_paths:
            best_match = None
            best_confidence = 0.0
            
            for tgt_path in target_paths:
                confidence = self.calculate_path_similarity(src_path, tgt_path)
                
                if confidence > best_confidence and confidence >= self.similarity_threshold:
                    best_confidence = confidence
                    best_match = tgt_path
            
            if best_match:
                suggestions.append(MappingResult(
                    source_path=src_path,
                    target_path=best_match,
                    confidence=best_confidence,
                    mapping_type="suggested",
                    notes=f"Suggested based on path similarity"
                ))
        
        return suggestions
    
    def export_mapping_report(
        self,
        mappings: List[MappingResult],
        output_path: str
    ) -> None:
        """
        Export mapping results to a report file.
        
        Args:
            mappings: List of mapping results
            output_path: Output file path
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("Mapping Report\n")
            f.write("=" * 50 + "\n\n")
            
            for i, mapping in enumerate(mappings, 1):
                f.write(f"Mapping {i}:\n")
                f.write(f"  Source: {mapping.source_path}\n")
                f.write(f"  Target: {mapping.target_path}\n")
                f.write(f"  Confidence: {mapping.confidence:.2f}\n")
                f.write(f"  Type: {mapping.mapping_type}\n")
                f.write(f"  Notes: {mapping.notes}\n")
                f.write("-" * 30 + "\n") 