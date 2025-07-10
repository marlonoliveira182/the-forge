"""
Validation Utilities Module

Provides validation functions for:
- Schema data validation
- File format validation
- Data integrity checks
- Error reporting
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ValidationError:
    """Represents a validation error."""
    field: str
    message: str
    severity: str = "error"  # error, warning, info
    row: Optional[int] = None
    column: Optional[int] = None


class ValidationUtils:
    """
    Utility class for validation operations.
    
    Provides methods for:
    - Schema data validation
    - File format validation
    - Data integrity checks
    - Error reporting and formatting
    """
    
    def __init__(self):
        self.required_fields = ['Element', 'Type', 'Cardinality']
        self.valid_types = {
            'string', 'integer', 'number', 'boolean', 'object', 'array',
            'xs:string', 'xs:integer', 'xs:decimal', 'xs:boolean'
        }
        self.valid_cardinalities = {'0..1', '1', '0..*', '1..*', '1..1'}
    
    def validate_schema_data(
        self,
        headers: List[str],
        rows: List[List[str]]
    ) -> List[ValidationError]:
        """
        Validate schema data for completeness and correctness.
        
        Args:
            headers: Column headers
            rows: Data rows
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate headers
        header_errors = self._validate_headers(headers)
        errors.extend(header_errors)
        
        # Validate rows
        for row_idx, row in enumerate(rows, 2):  # Start from 2 (after header)
            row_errors = self._validate_row(row, headers, row_idx)
            errors.extend(row_errors)
        
        return errors
    
    def _validate_headers(self, headers: List[str]) -> List[ValidationError]:
        """Validate column headers."""
        errors = []
        
        if not headers:
            errors.append(ValidationError(
                field="headers",
                message="No headers found",
                severity="error"
            ))
            return errors
        
        # Check for required columns
        header_set = {h.lower() for h in headers}
        for required in self.required_fields:
            if required.lower() not in header_set:
                errors.append(ValidationError(
                    field="headers",
                    message=f"Missing required column: {required}",
                    severity="error"
                ))
        
        return errors
    
    def _validate_row(
        self,
        row: List[str],
        headers: List[str],
        row_idx: int
    ) -> List[ValidationError]:
        """Validate a single data row."""
        errors = []
        
        # Check for empty rows
        if not row or all(not cell for cell in row):
            errors.append(ValidationError(
                field="row",
                message="Empty row",
                severity="warning",
                row=row_idx
            ))
            return errors
        
        # Validate each cell based on column type
        for col_idx, (header, value) in enumerate(zip(headers, row)):
            if col_idx >= len(row):
                break
            
            cell_errors = self._validate_cell(value, header, row_idx, col_idx + 1)
            errors.extend(cell_errors)
        
        return errors
    
    def _validate_cell(
        self,
        value: str,
        header: str,
        row_idx: int,
        col_idx: int
    ) -> List[ValidationError]:
        """Validate a single cell value."""
        errors = []
        
        # Skip empty values for non-required fields
        if not value and not self._is_required_field(header):
            return errors
        
        # Validate based on column type
        if header.lower() == 'type':
            if value and value.lower() not in self.valid_types:
                errors.append(ValidationError(
                    field=header,
                    message=f"Invalid type: {value}",
                    severity="error",
                    row=row_idx,
                    column=col_idx
                ))
        
        elif header.lower() == 'cardinality':
            if value and value not in self.valid_cardinalities:
                errors.append(ValidationError(
                    field=header,
                    message=f"Invalid cardinality: {value}",
                    severity="error",
                    row=row_idx,
                    column=col_idx
                ))
        
        elif header.lower().startswith('element level'):
            if value and not self._is_valid_element_name(value):
                errors.append(ValidationError(
                    field=header,
                    message=f"Invalid element name: {value}",
                    severity="warning",
                    row=row_idx,
                    column=col_idx
                ))
        
        return errors
    
    def _is_required_field(self, header: str) -> bool:
        """Check if a field is required."""
        required_headers = {'element', 'type', 'cardinality'}
        return header.lower() in required_headers
    
    def _is_valid_element_name(self, name: str) -> bool:
        """Check if an element name is valid."""
        if not name:
            return True
        
        # Element names should be alphanumeric with underscores and hyphens
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_-]*$'
        return bool(re.match(pattern, name))
    
    def validate_file_format(self, file_path: str) -> List[ValidationError]:
        """
        Validate file format and structure.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of validation errors
        """
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Basic file content validation
            if not content.strip():
                errors.append(ValidationError(
                    field="file_content",
                    message="File is empty",
                    severity="error"
                ))
            
            # Check for common encoding issues
            if '\x00' in content:
                errors.append(ValidationError(
                    field="file_content",
                    message="File contains null bytes",
                    severity="error"
                ))
            
        except UnicodeDecodeError:
            errors.append(ValidationError(
                field="file_encoding",
                message="File encoding is not UTF-8",
                severity="error"
            ))
        except Exception as e:
            errors.append(ValidationError(
                field="file_access",
                message=f"Cannot read file: {str(e)}",
                severity="error"
            ))
        
        return errors
    
    def validate_json_schema(self, json_data: Dict[str, Any]) -> List[ValidationError]:
        """
        Validate JSON Schema structure.
        
        Args:
            json_data: JSON Schema data
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if not isinstance(json_data, dict):
            errors.append(ValidationError(
                field="root",
                message="Root must be an object",
                severity="error"
            ))
            return errors
        
        # Check for required JSON Schema fields
        if '$schema' not in json_data:
            errors.append(ValidationError(
                field="$schema",
                message="Missing $schema field",
                severity="warning"
            ))
        
        if 'properties' not in json_data:
            errors.append(ValidationError(
                field="properties",
                message="Missing properties field",
                severity="error"
            ))
        else:
            # Validate properties
            prop_errors = self._validate_json_properties(json_data['properties'])
            errors.extend(prop_errors)
        
        return errors
    
    def _validate_json_properties(self, properties: Dict[str, Any]) -> List[ValidationError]:
        """Validate JSON Schema properties."""
        errors = []
        
        for prop_name, prop_schema in properties.items():
            if not isinstance(prop_schema, dict):
                errors.append(ValidationError(
                    field=f"properties.{prop_name}",
                    message="Property schema must be an object",
                    severity="error"
                ))
                continue
            
            # Check for required type field
            if 'type' not in prop_schema:
                errors.append(ValidationError(
                    field=f"properties.{prop_name}.type",
                    message="Property missing type field",
                    severity="error"
                ))
            else:
                prop_type = prop_schema['type']
                if prop_type not in self.valid_types:
                    errors.append(ValidationError(
                        field=f"properties.{prop_name}.type",
                        message=f"Invalid type: {prop_type}",
                        severity="error"
                    ))
        
        return errors
    
    def validate_xsd_schema(self, xml_content: str) -> List[ValidationError]:
        """
        Validate XSD schema structure.
        
        Args:
            xml_content: XSD content as string
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Basic XML structure validation
        if not xml_content.strip():
            errors.append(ValidationError(
                field="xml_content",
                message="XSD content is empty",
                severity="error"
            ))
            return errors
        
        # Check for XML declaration
        if not xml_content.strip().startswith('<?xml'):
            errors.append(ValidationError(
                field="xml_declaration",
                message="Missing XML declaration",
                severity="warning"
            ))
        
        # Check for schema namespace
        if 'xmlns:xs="http://www.w3.org/2001/XMLSchema"' not in xml_content:
            errors.append(ValidationError(
                field="schema_namespace",
                message="Missing XSD namespace declaration",
                severity="error"
            ))
        
        # Check for schema element
        if '<xs:schema' not in xml_content:
            errors.append(ValidationError(
                field="schema_element",
                message="Missing xs:schema element",
                severity="error"
            ))
        
        return errors
    
    def format_validation_errors(self, errors: List[ValidationError]) -> str:
        """
        Format validation errors for display.
        
        Args:
            errors: List of validation errors
            
        Returns:
            Formatted error message string
        """
        if not errors:
            return "No validation errors found."
        
        lines = ["Validation Report:", "=" * 50]
        
        # Group errors by severity
        error_groups = {
            'error': [],
            'warning': [],
            'info': []
        }
        
        for error in errors:
            error_groups[error.severity].append(error)
        
        # Format each severity group
        for severity in ['error', 'warning', 'info']:
            group_errors = error_groups[severity]
            if group_errors:
                lines.append(f"\n{severity.upper()}S ({len(group_errors)}):")
                for error in group_errors:
                    location = ""
                    if error.row:
                        location += f"Row {error.row}"
                    if error.column:
                        location += f", Column {error.column}"
                    
                    if location:
                        lines.append(f"  {location}: {error.field} - {error.message}")
                    else:
                        lines.append(f"  {error.field}: {error.message}")
        
        return "\n".join(lines)
    
    def get_validation_summary(self, errors: List[ValidationError]) -> Dict[str, Any]:
        """
        Get validation summary statistics.
        
        Args:
            errors: List of validation errors
            
        Returns:
            Dictionary with validation statistics
        """
        summary = {
            'total_errors': len(errors),
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'fields_with_errors': set(),
            'rows_with_errors': set()
        }
        
        for error in errors:
            if error.severity == 'error':
                summary['error_count'] += 1
            elif error.severity == 'warning':
                summary['warning_count'] += 1
            elif error.severity == 'info':
                summary['info_count'] += 1
            
            summary['fields_with_errors'].add(error.field)
            if error.row:
                summary['rows_with_errors'].add(error.row)
        
        summary['fields_with_errors'] = list(summary['fields_with_errors'])
        summary['rows_with_errors'] = list(summary['rows_with_errors'])
        
        return summary 