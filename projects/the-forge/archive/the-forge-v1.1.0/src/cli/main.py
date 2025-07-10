"""
Main CLI module for The Forge.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.schema_processor import SchemaProcessor
from src.core.mapping_engine import MappingEngine
from src.core.excel_generator import ExcelGenerator
from src.core.converter import SchemaConverter
from src.utils.path_utils import PathUtils
from src.utils.validation import ValidationUtils


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="The Forge - Schema Conversion and Mapping Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert XSD to JSON Schema
  python -m src.cli.main xsd-to-json input.xsd output.json

  # Convert JSON Schema to XSD
  python -m src.cli.main json-to-xsd input.json output.xsd

  # Generate Excel from schema
  python -m src.cli.main schema-to-excel input.xsd output.xlsx

  # Create mapping between schemas
  python -m src.cli.main mapping source.xsd target.json output.xlsx

  # Validate schema file
  python -m src.cli.main validate input.xsd
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # XSD to JSON Schema
    xsd_to_json_parser = subparsers.add_parser('xsd-to-json', help='Convert XSD to JSON Schema')
    xsd_to_json_parser.add_argument('input', help='Input XSD file')
    xsd_to_json_parser.add_argument('output', help='Output JSON Schema file')
    
    # JSON Schema to XSD
    json_to_xsd_parser = subparsers.add_parser('json-to-xsd', help='Convert JSON Schema to XSD')
    json_to_xsd_parser.add_argument('input', help='Input JSON Schema file')
    json_to_xsd_parser.add_argument('output', help='Output XSD file')
    
    # Schema to Excel
    schema_to_excel_parser = subparsers.add_parser('schema-to-excel', help='Generate Excel from schema')
    schema_to_excel_parser.add_argument('input', help='Input schema file (XSD or JSON)')
    schema_to_excel_parser.add_argument('output', help='Output Excel file')
    
    # Mapping
    mapping_parser = subparsers.add_parser('mapping', help='Create mapping between schemas')
    mapping_parser.add_argument('source', help='Source schema file')
    mapping_parser.add_argument('target', help='Target schema file')
    mapping_parser.add_argument('output', help='Output Excel file')
    mapping_parser.add_argument('--threshold', type=float, default=0.7, 
                              help='Similarity threshold (default: 0.7)')
    
    # Validate
    validate_parser = subparsers.add_parser('validate', help='Validate schema file')
    validate_parser.add_argument('input', help='Input schema file')
    
    return parser


def validate_input_file(filepath: str, expected_extensions: Optional[list] = None) -> None:
    """Validate input file."""
    is_valid, error_msg = PathUtils.validate_file_path(filepath, expected_extensions)
    if not is_valid:
        print(f"Error: {error_msg}")
        sys.exit(1)


def validate_output_directory(filepath: str) -> None:
    """Validate output directory."""
    output_dir = PathUtils.get_directory(filepath)
    if output_dir:
        is_valid, error_msg = PathUtils.validate_directory_path(output_dir)
        if not is_valid:
            print(f"Error: {error_msg}")
            sys.exit(1)


def handle_xsd_to_json(args) -> None:
    """Handle XSD to JSON Schema conversion."""
    print(f"Converting XSD to JSON Schema: {args.input} -> {args.output}")
    
    validate_input_file(args.input, ['.xsd'])
    validate_output_directory(args.output)
    
    try:
        converter = SchemaConverter()
        converter.xsd_to_json_schema(args.input, args.output)
        print(f"✓ Successfully converted to: {args.output}")
        
        # Validate the output
        is_valid, error_msg = ValidationUtils.validate_json_schema(args.output)
        if is_valid:
            print("✓ Output JSON Schema is valid")
        else:
            print(f"⚠ Warning: {error_msg}")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)


def handle_json_to_xsd(args) -> None:
    """Handle JSON Schema to XSD conversion."""
    print(f"Converting JSON Schema to XSD: {args.input} -> {args.output}")
    
    validate_input_file(args.input, ['.json'])
    validate_output_directory(args.output)
    
    try:
        converter = SchemaConverter()
        converter.json_schema_to_xsd(args.input, args.output)
        print(f"✓ Successfully converted to: {args.output}")
        
        # Validate the output
        is_valid, error_msg = ValidationUtils.validate_xsd_schema(args.output)
        if is_valid:
            print("✓ Output XSD is valid")
        else:
            print(f"⚠ Warning: {error_msg}")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)


def handle_schema_to_excel(args) -> None:
    """Handle schema to Excel conversion."""
    print(f"Generating Excel from schema: {args.input} -> {args.output}")
    
    validate_input_file(args.input, ['.xsd', '.json'])
    validate_output_directory(args.output)
    
    try:
        processor = SchemaProcessor()
        generator = ExcelGenerator()
        
        # Determine file type and extract fields
        if PathUtils.is_xsd_file(args.input):
            fields = processor.extract_fields_from_xsd(args.input)
            schema_type = "XSD"
        else:
            fields = processor.extract_fields_from_json_schema(args.input)
            schema_type = "JSON Schema"
        
        # Generate Excel
        generator.create_schema_excel(fields, args.output, schema_type)
        print(f"✓ Successfully generated Excel: {args.output}")
        
        # Validate the output
        is_valid, error_msg = ValidationUtils.validate_excel_file(args.output)
        if is_valid:
            print("✓ Output Excel file is valid")
        else:
            print(f"⚠ Warning: {error_msg}")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)


def handle_mapping(args) -> None:
    """Handle schema mapping."""
    print(f"Creating mapping: {args.source} -> {args.target} -> {args.output}")
    
    validate_input_file(args.source, ['.xsd', '.json'])
    validate_input_file(args.target, ['.xsd', '.json'])
    validate_output_directory(args.output)
    
    try:
        processor = SchemaProcessor()
        engine = MappingEngine(threshold=args.threshold)
        generator = ExcelGenerator()
        
        # Extract fields from both schemas
        if PathUtils.is_xsd_file(args.source):
            source_fields = processor.extract_fields_from_xsd(args.source)
        else:
            source_fields = processor.extract_fields_from_json_schema(args.source)
        
        if PathUtils.is_xsd_file(args.target):
            target_fields = processor.extract_fields_from_xsd(args.target)
        else:
            target_fields = processor.extract_fields_from_json_schema(args.target)
        
        # Create mapping
        mapping = engine.map_fields(source_fields, target_fields)
        
        # Generate Excel
        source_name = PathUtils.get_filename_without_extension(args.source)
        target_name = PathUtils.get_filename_without_extension(args.target)
        generator.create_mapping_excel(source_fields, target_fields, mapping, 
                                    args.output, source_name, target_name)
        
        print(f"✓ Successfully created mapping: {args.output}")
        
        # Validate and show statistics
        validation = engine.validate_mapping(mapping)
        print(f"  - Total mappings: {validation['total_mappings']}")
        print(f"  - Exact matches: {validation['exact_matches']}")
        print(f"  - Threshold matches: {validation['threshold_matches']}")
        print(f"  - No matches: {validation['no_matches']}")
        print(f"  - Average similarity: {validation['average_similarity']}")
        print(f"  - Coverage: {validation['coverage_percentage']}%")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)


def handle_validate(args) -> None:
    """Handle schema validation."""
    print(f"Validating schema: {args.input}")
    
    validate_input_file(args.input, ['.xsd', '.json'])
    
    try:
        if PathUtils.is_xsd_file(args.input):
            is_valid, error_msg = ValidationUtils.validate_xsd_schema(args.input)
            schema_type = "XSD"
        else:
            is_valid, error_msg = ValidationUtils.validate_json_schema(args.input)
            schema_type = "JSON Schema"
        
        if is_valid:
            print(f"✓ {schema_type} schema is valid")
            
            # Additional analysis
            processor = SchemaProcessor()
            if PathUtils.is_xsd_file(args.input):
                fields = processor.extract_fields_from_xsd(args.input)
            else:
                fields = processor.extract_fields_from_json_schema(args.input)
            
            print(f"  - Total fields: {len(fields)}")
            print(f"  - Max depth: {max((len(f.levels) for f in fields), default=0)}")
            
        else:
            print(f"✗ {schema_type} schema is invalid: {error_msg}")
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to appropriate handler
    handlers = {
        'xsd-to-json': handle_xsd_to_json,
        'json-to-xsd': handle_json_to_xsd,
        'schema-to-excel': handle_schema_to_excel,
        'mapping': handle_mapping,
        'validate': handle_validate
    }
    
    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main() 