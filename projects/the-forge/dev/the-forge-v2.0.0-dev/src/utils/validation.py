"""
Validation utilities for The Forge v2.0.0
"""

import json
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

class ValidationUtils:
    """Utility class for validation operations"""
    
    @staticmethod
    def validate_json_schema(file_path: str) -> Tuple[bool, str]:
        """Validate JSON Schema file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            # Basic JSON Schema validation
            if not isinstance(schema, dict):
                return False, "Schema is not a valid JSON object"
            
            # Check for required JSON Schema fields
            if '$schema' not in schema:
                return False, "Missing $schema field"
            
            if 'type' not in schema and 'properties' not in schema:
                return False, "Missing type or properties field"
            
            return True, "JSON Schema is valid"
            
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON format: {str(e)}"
        except Exception as e:
            return False, f"Error validating JSON Schema: {str(e)}"
    
    @staticmethod
    def validate_xsd_schema(file_path: str) -> Tuple[bool, str]:
        """Validate XSD schema file"""
        try:
            # Basic XSD validation - check if it's well-formed XML
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Check for schema element
            if root.tag.endswith('schema'):
                return True, "XSD schema is valid"
            else:
                return False, "Root element is not a schema"
                
        except ET.ParseError as e:
            return False, f"Invalid XML format: {str(e)}"
        except Exception as e:
            return False, f"Error validating XSD schema: {str(e)}"
    
    @staticmethod
    def validate_excel_file(file_path: str) -> Tuple[bool, str]:
        """Validate Excel file"""
        try:
            from openpyxl import load_workbook
            
            # Try to load the workbook
            wb = load_workbook(file_path, read_only=True)
            wb.close()
            
            return True, "Excel file is valid"
            
        except Exception as e:
            return False, f"Error validating Excel file: {str(e)}"
    
    @staticmethod
    def compare_schema_structures(fields1: List[Dict], fields2: List[Dict]) -> Dict[str, Any]:
        """Compare two schema structures and return differences"""
        comparison = {
            "total_fields_1": len(fields1),
            "total_fields_2": len(fields2),
            "common_fields": [],
            "unique_to_1": [],
            "unique_to_2": [],
            "type_mismatches": [],
            "similarity_score": 0.0
        }
        
        # Extract field names
        names1 = {field.get('path', '') for field in fields1}
        names2 = {field.get('path', '') for field in fields2}
        
        # Find common and unique fields
        comparison["common_fields"] = list(names1 & names2)
        comparison["unique_to_1"] = list(names1 - names2)
        comparison["unique_to_2"] = list(names2 - names1)
        
        # Calculate similarity score
        total_fields = len(names1 | names2)
        if total_fields > 0:
            comparison["similarity_score"] = len(comparison["common_fields"]) / total_fields
        
        # Find type mismatches for common fields
        fields1_dict = {field.get('path', ''): field for field in fields1}
        fields2_dict = {field.get('path', ''): field for field in fields2}
        
        for field_name in comparison["common_fields"]:
            field1 = fields1_dict.get(field_name, {})
            field2 = fields2_dict.get(field_name, {})
            
            type1 = field1.get('type', '')
            type2 = field2.get('type', '')
            
            if type1 != type2:
                comparison["type_mismatches"].append({
                    "field": field_name,
                    "type1": type1,
                    "type2": type2
                })
        
        return comparison
    
    @staticmethod
    def validate_mapping_completeness(mappings: List[Dict], source_fields: List[Dict], 
                                    target_fields: List[Dict]) -> Dict[str, Any]:
        """Validate the completeness of field mappings"""
        validation = {
            "total_mappings": len(mappings),
            "mapped_source_fields": 0,
            "mapped_target_fields": 0,
            "unmapped_source_fields": [],
            "unmapped_target_fields": [],
            "duplicate_mappings": [],
            "coverage_percentage": 0.0
        }
        
        # Get mapped fields
        mapped_source = {mapping.get('source_path', '') for mapping in mappings if mapping.get('target_path')}
        mapped_target = {mapping.get('target_path', '') for mapping in mappings if mapping.get('target_path')}
        
        # Get all field names
        source_names = {field.get('path', '') for field in source_fields}
        target_names = {field.get('path', '') for field in target_fields}
        
        validation["mapped_source_fields"] = len(mapped_source)
        validation["mapped_target_fields"] = len(mapped_target)
        validation["unmapped_source_fields"] = list(source_names - mapped_source)
        validation["unmapped_target_fields"] = list(target_names - mapped_target)
        
        # Calculate coverage
        total_source = len(source_names)
        if total_source > 0:
            validation["coverage_percentage"] = (len(mapped_source) / total_source) * 100
        
        # Check for duplicate mappings
        source_paths = [mapping.get('source_path', '') for mapping in mappings]
        duplicates = [path for path in set(source_paths) if source_paths.count(path) > 1]
        validation["duplicate_mappings"] = duplicates
        
        return validation
    
    @staticmethod
    def validate_constraint_preservation(source_constraints: Dict, target_constraints: Dict) -> Dict[str, Any]:
        """Validate if constraints are properly preserved during conversion"""
        validation = {
            "preserved_constraints": [],
            "lost_constraints": [],
            "added_constraints": [],
            "modified_constraints": [],
            "preservation_score": 0.0
        }
        
        # Compare constraints
        for key, value in source_constraints.items():
            if key in target_constraints:
                if target_constraints[key] == value:
                    validation["preserved_constraints"].append(key)
                else:
                    validation["modified_constraints"].append({
                        "constraint": key,
                        "source_value": value,
                        "target_value": target_constraints[key]
                    })
            else:
                validation["lost_constraints"].append(key)
        
        for key in target_constraints:
            if key not in source_constraints:
                validation["added_constraints"].append(key)
        
        # Calculate preservation score
        total_source = len(source_constraints)
        if total_source > 0:
            validation["preservation_score"] = len(validation["preserved_constraints"]) / total_source
        
        return validation 