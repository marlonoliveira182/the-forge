"""
Schema Converter Module

Orchestrates the conversion process between different schema formats:
- XSD to JSON Schema
- JSON Schema to XSD
- Schema validation and transformation
- Conversion reporting
"""

import os
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .schema_processor import SchemaProcessor, SchemaType
from .excel_generator import ExcelGenerator
from .mapping_engine import MappingEngine


class ConversionType(Enum):
    """Supported conversion types."""
    XSD_TO_JSON = "xsd_to_json"
    JSON_TO_XSD = "json_to_xsd"
    SCHEMA_TO_EXCEL = "schema_to_excel"
    MERGE_SCHEMAS = "merge_schemas"


@dataclass
class ConversionResult:
    """Represents the result of a schema conversion."""
    success: bool
    output_path: str
    messages: List[str]
    errors: List[str]
    statistics: Dict[str, Any]


class SchemaConverter:
    """
    Orchestrates the conversion process between different schema formats.
    
    Provides methods for:
    - Converting between XSD and JSON Schema
    - Generating Excel documentation
    - Merging and mapping schemas
    - Validation and error reporting
    """
    
    def __init__(self):
        self.schema_processor = SchemaProcessor()
        self.excel_generator = ExcelGenerator()
        self.mapping_engine = MappingEngine()
    
    def convert_schema_to_excel(
        self,
        input_path: str,
        output_path: str
    ) -> ConversionResult:
        """
        Convert a schema file to Excel format.
        
        Args:
            input_path: Path to input schema file
            output_path: Path for output Excel file
            
        Returns:
            ConversionResult with success status and details
        """
        messages = []
        errors = []
        statistics = {}
        
        try:
            # Detect schema type
            schema_type = self.schema_processor.detect_schema_type(input_path)
            if not schema_type:
                errors.append(f"Unsupported file type: {input_path}")
                return ConversionResult(
                    success=False,
                    output_path="",
                    messages=messages,
                    errors=errors,
                    statistics=statistics
                )
            
            messages.append(f"Detected schema type: {schema_type.value}")
            
            # Process schema
            headers, rows = self.schema_processor.process_schema(input_path)
            messages.append(f"Processed {len(rows)} rows with {len(headers)} columns")
            
            # Validate schema
            validation_issues = self.schema_processor.validate_schema(headers, rows)
            if validation_issues:
                errors.extend(validation_issues)
                messages.append(f"Found {len(validation_issues)} validation issues")
            
            # Generate Excel
            self.excel_generator.create_schema_excel(headers, rows, output_path)
            messages.append(f"Excel file created: {output_path}")
            
            # Update statistics
            statistics = {
                'input_file': input_path,
                'schema_type': schema_type.value,
                'total_rows': len(rows),
                'total_columns': len(headers),
                'validation_issues': len(validation_issues),
                'output_file': output_path
            }
            
            return ConversionResult(
                success=True,
                output_path=output_path,
                messages=messages,
                errors=errors,
                statistics=statistics
            )
            
        except Exception as e:
            errors.append(f"Conversion failed: {str(e)}")
            return ConversionResult(
                success=False,
                output_path="",
                messages=messages,
                errors=errors,
                statistics=statistics
            )
    
    def merge_schemas(
        self,
        source_path: str,
        target_path: Optional[str],
        output_path: str
    ) -> ConversionResult:
        """
        Merge source and target schemas with mapping.
        
        Args:
            source_path: Path to source schema file
            target_path: Path to target schema file (optional)
            output_path: Path for output merged file
            
        Returns:
            ConversionResult with success status and details
        """
        messages = []
        errors = []
        statistics = {}
        
        try:
            # Process source schema
            source_headers, source_rows = self.schema_processor.process_schema(source_path)
            messages.append(f"Processed source schema: {len(source_rows)} rows")
            
            target_headers = []
            target_rows = []
            
            if target_path and os.path.exists(target_path):
                # Process target schema
                target_headers, target_rows = self.schema_processor.process_schema(target_path)
                messages.append(f"Processed target schema: {len(target_rows)} rows")
                
                # Create mapping matrix
                merged_headers, merged_rows = self.mapping_engine.create_mapping_matrix(
                    source_headers, source_rows,
                    target_headers, target_rows
                )
                
                # Generate merged Excel
                self.excel_generator.create_merged_excel(
                    source_headers, source_rows,
                    target_headers, target_rows,
                    [[''] for _ in source_rows],  # Empty mapping data for now
                    output_path
                )
                
                messages.append(f"Merged file created: {output_path}")
                
                # Update statistics
                statistics = {
                    'source_file': source_path,
                    'target_file': target_path,
                    'source_rows': len(source_rows),
                    'target_rows': len(target_rows),
                    'merged_rows': len(merged_rows),
                    'output_file': output_path
                }
            else:
                # No target file, just convert source to Excel
                self.excel_generator.create_schema_excel(source_headers, source_rows, output_path)
                messages.append(f"Source schema converted to Excel: {output_path}")
                
                statistics = {
                    'source_file': source_path,
                    'source_rows': len(source_rows),
                    'output_file': output_path
                }
            
            return ConversionResult(
                success=True,
                output_path=output_path,
                messages=messages,
                errors=errors,
                statistics=statistics
            )
            
        except Exception as e:
            errors.append(f"Merge failed: {str(e)}")
            return ConversionResult(
                success=False,
                output_path="",
                messages=messages,
                errors=errors,
                statistics=statistics
            )
    
    def convert_xsd_to_json(
        self,
        input_path: str,
        output_path: str
    ) -> ConversionResult:
        """
        Convert XSD schema to JSON Schema format.
        
        Args:
            input_path: Path to XSD file
            output_path: Path for output JSON Schema file
            
        Returns:
            ConversionResult with success status and details
        """
        messages = []
        errors = []
        statistics = {}
        
        try:
            # Process XSD
            headers, rows = self.schema_processor.process_schema(input_path)
            messages.append(f"Processed XSD: {len(rows)} elements")
            
            # Convert to JSON Schema structure
            json_schema = self._convert_rows_to_json_schema(headers, rows)
            
            # Write JSON Schema
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_schema, f, indent=2, ensure_ascii=False)
            
            messages.append(f"JSON Schema created: {output_path}")
            
            statistics = {
                'input_file': input_path,
                'total_elements': len(rows),
                'output_file': output_path
            }
            
            return ConversionResult(
                success=True,
                output_path=output_path,
                messages=messages,
                errors=errors,
                statistics=statistics
            )
            
        except Exception as e:
            errors.append(f"XSD to JSON conversion failed: {str(e)}")
            return ConversionResult(
                success=False,
                output_path="",
                messages=messages,
                errors=errors,
                statistics=statistics
            )
    
    def convert_json_to_xsd(
        self,
        input_path: str,
        output_path: str
    ) -> ConversionResult:
        """
        Convert JSON Schema to XSD format.
        
        Args:
            input_path: Path to JSON Schema file
            output_path: Path for output XSD file
            
        Returns:
            ConversionResult with success status and details
        """
        messages = []
        errors = []
        statistics = {}
        
        try:
            # Process JSON Schema
            headers, rows = self.schema_processor.process_schema(input_path)
            messages.append(f"Processed JSON Schema: {len(rows)} properties")
            
            # Convert to XSD structure
            xsd_content = self._convert_rows_to_xsd(headers, rows)
            
            # Write XSD
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xsd_content)
            
            messages.append(f"XSD created: {output_path}")
            
            statistics = {
                'input_file': input_path,
                'total_properties': len(rows),
                'output_file': output_path
            }
            
            return ConversionResult(
                success=True,
                output_path=output_path,
                messages=messages,
                errors=errors,
                statistics=statistics
            )
            
        except Exception as e:
            errors.append(f"JSON to XSD conversion failed: {str(e)}")
            return ConversionResult(
                success=False,
                output_path="",
                messages=messages,
                errors=errors,
                statistics=statistics
            )
    
    def _convert_rows_to_json_schema(
        self,
        headers: List[str],
        rows: List[List[str]]
    ) -> Dict[str, Any]:
        """
        Convert Excel rows to JSON Schema structure.
        
        Args:
            headers: Column headers
            rows: Data rows
            
        Returns:
            JSON Schema dictionary
        """
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Find column indices
        name_cols = [i for i, h in enumerate(headers) if h.startswith('Element Level')]
        type_col = headers.index('Type') if 'Type' in headers else -1
        card_col = headers.index('Cardinality') if 'Cardinality' in headers else -1
        desc_col = headers.index('Description') if 'Description' in headers else -1
        
        for row in rows:
            # Extract field name from last non-empty level column
            field_name = ""
            for i in reversed(name_cols):
                if i < len(row) and row[i]:
                    field_name = row[i]
                    break
            
            if not field_name:
                continue
            
            # Extract field information
            field_type = row[type_col] if type_col >= 0 and type_col < len(row) else "string"
            cardinality = row[card_col] if card_col >= 0 and card_col < len(row) else "1"
            description = row[desc_col] if desc_col >= 0 and desc_col < len(row) else ""
            
            # Convert to JSON Schema property
            property_schema = self._convert_field_to_json_property(field_type, cardinality, description)
            
            # Add to properties
            json_schema["properties"][field_name] = property_schema
            
            # Add to required if cardinality indicates required
            if cardinality == "1":
                json_schema["required"].append(field_name)
        
        return json_schema
    
    def _convert_field_to_json_property(
        self,
        field_type: str,
        cardinality: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Convert a field to JSON Schema property.
        
        Args:
            field_type: Field type
            cardinality: Field cardinality
            description: Field description
            
        Returns:
            JSON Schema property dictionary
        """
        property_schema = {}
        
        # Map XSD types to JSON Schema types
        type_mapping = {
            'string': 'string',
            'integer': 'integer',
            'number': 'number',
            'boolean': 'boolean',
            'object': 'object',
            'array': 'array'
        }
        
        json_type = type_mapping.get(field_type.lower(), 'string')
        property_schema['type'] = json_type
        
        # Add description if available
        if description:
            property_schema['description'] = description
        
        # Handle arrays
        if 'array' in cardinality.lower() or cardinality == '0..*':
            property_schema = {
                'type': 'array',
                'items': {'type': json_type}
            }
            if description:
                property_schema['description'] = description
        
        return property_schema
    
    def _convert_rows_to_xsd(
        self,
        headers: List[str],
        rows: List[List[str]]
    ) -> str:
        """
        Convert Excel rows to XSD structure.
        
        Args:
            headers: Column headers
            rows: Data rows
            
        Returns:
            XSD content string
        """
        xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="root">
        <xs:complexType>
            <xs:sequence>
'''
        
        # Find column indices
        name_cols = [i for i, h in enumerate(headers) if h.startswith('Element Level')]
        type_col = headers.index('Type') if 'Type' in headers else -1
        card_col = headers.index('Cardinality') if 'Cardinality' in headers else -1
        desc_col = headers.index('Description') if 'Description' in headers else -1
        
        for row in rows:
            # Extract field name from last non-empty level column
            field_name = ""
            for i in reversed(name_cols):
                if i < len(row) and row[i]:
                    field_name = row[i]
                    break
            
            if not field_name:
                continue
            
            # Extract field information
            field_type = row[type_col] if type_col >= 0 and type_col < len(row) else "string"
            cardinality = row[card_col] if card_col >= 0 and card_col < len(row) else "1"
            description = row[desc_col] if desc_col >= 0 and desc_col < len(row) else ""
            
            # Convert to XSD element
            element_xsd = self._convert_field_to_xsd_element(field_name, field_type, cardinality, description)
            xsd_content += element_xsd
        
        xsd_content += '''            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''
        
        return xsd_content
    
    def _convert_field_to_xsd_element(
        self,
        field_name: str,
        field_type: str,
        cardinality: str,
        description: str
    ) -> str:
        """
        Convert a field to XSD element.
        
        Args:
            field_name: Field name
            field_type: Field type
            cardinality: Field cardinality
            description: Field description
            
        Returns:
            XSD element string
        """
        # Map JSON types to XSD types
        type_mapping = {
            'string': 'xs:string',
            'integer': 'xs:integer',
            'number': 'xs:decimal',
            'boolean': 'xs:boolean',
            'object': 'xs:complexType',
            'array': 'xs:string'  # Default for arrays
        }
        
        xsd_type = type_mapping.get(field_type.lower(), 'xs:string')
        
        # Handle cardinality
        min_occurs = "1"
        max_occurs = "1"
        
        if cardinality == "0..1":
            min_occurs = "0"
        elif cardinality == "0..*":
            min_occurs = "0"
            max_occurs = "unbounded"
        elif cardinality == "1..*":
            max_occurs = "unbounded"
        
        # Build element
        element = f'                <xs:element name="{field_name}" type="{xsd_type}"'
        element += f' minOccurs="{min_occurs}" maxOccurs="{max_occurs}"'
        
        if description:
            element += f'>\n                    <xs:annotation>\n                        <xs:documentation>{description}</xs:documentation>\n                    </xs:annotation>\n                </xs:element>'
        else:
            element += '/>'
        
        return element + '\n'
    
    def validate_conversion(
        self,
        result: ConversionResult
    ) -> Tuple[bool, List[str]]:
        """
        Validate conversion result.
        
        Args:
            result: Conversion result to validate
            
        Returns:
            Tuple of (is_valid, validation_messages)
        """
        messages = []
        
        if not result.success:
            messages.append("Conversion failed")
            return False, messages
        
        if not os.path.exists(result.output_path):
            messages.append("Output file not created")
            return False, messages
        
        if result.errors:
            messages.append(f"Found {len(result.errors)} errors")
            return False, messages
        
        messages.append("Conversion completed successfully")
        return True, messages 