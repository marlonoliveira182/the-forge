"""
Enhanced Mapping Engine for The Forge v2.0.0
Maps fields between schemas with exact name preservation
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher

from .schema_field import SchemaField

class FieldMapping:
    def __init__(self, source_field: SchemaField, target_field: SchemaField, similarity: float, confidence: str = "auto"):
        self.source_field = source_field
        self.target_field = target_field
        self.similarity = similarity
        self.confidence = confidence

class MappingEngine:
    def map_fields(self, source_fields: List[SchemaField], target_fields: List[SchemaField]) -> List[FieldMapping]:
        mappings = []
        for src in source_fields:
            # Find best match by name similarity
            best_match = None
            best_score = 0.0
            for tgt in target_fields:
                score = difflib.SequenceMatcher(None, src.name.lower(), tgt.name.lower()).ratio()
                if score > best_score:
                    best_score = score
                    best_match = tgt
            if best_match and best_score > 0.5:  # Threshold for auto-mapping
                mappings.append(FieldMapping(src, best_match, best_score, confidence="auto"))
        return mappings 