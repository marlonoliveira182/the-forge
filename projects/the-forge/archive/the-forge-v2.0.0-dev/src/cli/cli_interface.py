"""
CLI Interface Module

Provides command-line interface for the-forge-v2 operations:
- Schema conversion
- Excel generation
- Schema merging
- Validation and reporting
"""

import argparse
import sys
import os
from typing import Optional, List, Dict, Any
from pathlib import Path

from ..core.converter import SchemaConverter
from ..core.schema_processor import SchemaProcessor
from ..core.excel_generator import ExcelGenerator
from ..core.mapping_engine import MappingEngine
from ..utils.path_utils import PathUtils
from ..utils.validation import ValidationUtils


class CLIInterface:
    """
    Command-line interface for the-forge-v2 operations.
    
    Provides methods for:
    - Argument parsing and validation
    - Command execution
    - Error handling and reporting
    """
    
    def __init__(self):
        self.converter = SchemaConverter()
        self.path_utils = PathUtils()
        self.validation_utils = ValidationUtils()
        self.parser = self._create_argument_parser()
    
    def _create_argument_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all available commands."""
        parser = argparse.ArgumentParser(
            description="The Forge v2 - Schema Conversion and Mapping Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Convert schema to Excel
  python -m src.cli.cli_interface convert-to-excel input.xsd output.xlsx
  
  # Merge schemas
  python -m src.cli.cli_interface merge source.xlsx target.xlsx output.xlsx
  
  # Convert XSD to JSON Schema
  python -m src.cli.cli_interface xsd-to-json input.xsd output.json
  
  # Validate schema
  python -m src.cli.cli_interface validate input.xsd
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Convert to Excel command
        convert_parser = subparsers.add_parser(
            'convert-to-excel',
            help='Convert schema file to Excel format'
        )
        convert_parser.add_argument('input', help='Input schema file (XSD, JSON, XML)')
        convert_parser.add_argument('output', help='Output Excel file')
        convert_parser.add_argument('--validate', action='store_true', help='Validate output')
        
        # Merge schemas command
        merge_parser = subparsers.add_parser(
            'merge',
            help='Merge source and target schemas'
        )
        merge_parser.add_argument('source', help='Source schema file')
        merge_parser.add_argument('target', help='Target schema file (optional)', nargs='?')
        merge_parser.add_argument('output', help='Output merged file')
        
        # XSD to JSON Schema command
        xsd_to_json_parser = subparsers.add_parser(
            'xsd-to-json',
            help='Convert XSD to JSON Schema'
        )
        xsd_to_json_parser.add_argument('input', help='Input XSD file')
        xsd_to_json_parser.add_argument('output', help='Output JSON Schema file')
        
        # JSON Schema to XSD command
        json_to_xsd_parser = subparsers.add_parser(
            'json-to-xsd',
            help='Convert JSON Schema to XSD'
        )
        json_to_xsd_parser.add_argument('input', help='Input JSON Schema file')
        json_to_xsd_parser.add_argument('output', help='Output XSD file')
        
        # Validate command
        validate_parser = subparsers.add_parser(
            'validate',
            help='Validate schema file'
        )
        validate_parser.add_argument('input', help='Input schema file')
        validate_parser.add_argument('--detailed', action='store_true', help='Show detailed validation')
        
        # Info command
        info_parser = subparsers.add_parser(
            'info',
            help='Get information about schema file'
        )
        info_parser.add_argument('input', help='Input schema file')
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI interface.
        
        Args:
            args: Command line arguments (defaults to sys.argv[1:])
            
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            parsed_args = self.parser.parse_args(args)
            
            if not parsed_args.command:
                self.parser.print_help()
                return 1
            
            # Execute the appropriate command
            if parsed_args.command == 'convert-to-excel':
                return self._handle_convert_to_excel(parsed_args)
            elif parsed_args.command == 'merge':
                return self._handle_merge(parsed_args)
            elif parsed_args.command == 'xsd-to-json':
                return self._handle_xsd_to_json(parsed_args)
            elif parsed_args.command == 'json-to-xsd':
                return self._handle_json_to_xsd(parsed_args)
            elif parsed_args.command == 'validate':
                return self._handle_validate(parsed_args)
            elif parsed_args.command == 'info':
                return self._handle_info(parsed_args)
            else:
                print(f"Unknown command: {parsed_args.command}")
                return 1
                
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return 1
        except Exception as e:
            print(f"Error: {str(e)}")
            return 1
    
    def _handle_convert_to_excel(self, args) -> int:
        """Handle convert-to-excel command."""
        # Validate input file
        is_valid, errors = self.path_utils.validate_file_path(args.input)
        if not is_valid:
            print("Input file validation failed:")
            for error in errors:
                print(f"  - {error}")
            return 1
        
        # Validate output directory
        output_dir = os.path.dirname(args.output)
        if output_dir:
            is_valid, errors = self.path_utils.validate_directory_path(output_dir)
            if not is_valid:
                print("Output directory validation failed:")
                for error in errors:
                    print(f"  - {error}")
                return 1
        
        print(f"Converting {args.input} to Excel format...")
        
        # Perform conversion
        result = self.converter.convert_schema_to_excel(args.input, args.output)
        
        if result.success:
            print(f"✓ Successfully converted to: {result.output_path}")
            print(f"  - Processed {result.statistics.get('total_rows', 0)} rows")
            print(f"  - Schema type: {result.statistics.get('schema_type', 'unknown')}")
            
            if result.errors and args.validate:
                print("\nValidation issues found:")
                for error in result.errors:
                    print(f"  - {error}")
            
            return 0
        else:
            print("✗ Conversion failed:")
            for error in result.errors:
                print(f"  - {error}")
            return 1
    
    def _handle_merge(self, args) -> int:
        """Handle merge command."""
        # Validate source file
        is_valid, errors = self.path_utils.validate_file_path(args.source)
        if not is_valid:
            print("Source file validation failed:")
            for error in errors:
                print(f"  - {error}")
            return 1
        
        # Validate target file if provided
        if args.target:
            is_valid, errors = self.path_utils.validate_file_path(args.target)
            if not is_valid:
                print("Target file validation failed:")
                for error in errors:
                    print(f"  - {error}")
                return 1
        
        # Validate output directory
        output_dir = os.path.dirname(args.output)
        if output_dir:
            is_valid, errors = self.path_utils.validate_directory_path(output_dir)
            if not is_valid:
                print("Output directory validation failed:")
                for error in errors:
                    print(f"  - {error}")
                return 1
        
        print(f"Merging schemas...")
        if args.target:
            print(f"  Source: {args.source}")
            print(f"  Target: {args.target}")
        else:
            print(f"  Source: {args.source}")
        
        # Perform merge
        result = self.converter.merge_schemas(args.source, args.target, args.output)
        
        if result.success:
            print(f"✓ Successfully merged to: {result.output_path}")
            print(f"  - Source rows: {result.statistics.get('source_rows', 0)}")
            if args.target:
                print(f"  - Target rows: {result.statistics.get('target_rows', 0)}")
                print(f"  - Merged rows: {result.statistics.get('merged_rows', 0)}")
            return 0
        else:
            print("✗ Merge failed:")
            for error in result.errors:
                print(f"  - {error}")
            return 1
    
    def _handle_xsd_to_json(self, args) -> int:
        """Handle xsd-to-json command."""
        # Validate input file
        is_valid, errors = self.path_utils.validate_file_path(args.input)
        if not is_valid:
            print("Input file validation failed:")
            for error in errors:
                print(f"  - {error}")
            return 1
        
        # Validate output directory
        output_dir = os.path.dirname(args.output)
        if output_dir:
            is_valid, errors = self.path_utils.validate_directory_path(output_dir)
            if not is_valid:
                print("Output directory validation failed:")
                for error in errors:
                    print(f"  - {error}")
                return 1
        
        print(f"Converting XSD to JSON Schema...")
        print(f"  Input: {args.input}")
        print(f"  Output: {args.output}")
        
        # Perform conversion
        result = self.converter.convert_xsd_to_json(args.input, args.output)
        
        if result.success:
            print(f"✓ Successfully converted to: {result.output_path}")
            print(f"  - Total elements: {result.statistics.get('total_elements', 0)}")
            return 0
        else:
            print("✗ Conversion failed:")
            for error in result.errors:
                print(f"  - {error}")
            return 1
    
    def _handle_json_to_xsd(self, args) -> int:
        """Handle json-to-xsd command."""
        # Validate input file
        is_valid, errors = self.path_utils.validate_file_path(args.input)
        if not is_valid:
            print("Input file validation failed:")
            for error in errors:
                print(f"  - {error}")
            return 1
        
        # Validate output directory
        output_dir = os.path.dirname(args.output)
        if output_dir:
            is_valid, errors = self.path_utils.validate_directory_path(output_dir)
            if not is_valid:
                print("Output directory validation failed:")
                for error in errors:
                    print(f"  - {error}")
                return 1
        
        print(f"Converting JSON Schema to XSD...")
        print(f"  Input: {args.input}")
        print(f"  Output: {args.output}")
        
        # Perform conversion
        result = self.converter.convert_json_to_xsd(args.input, args.output)
        
        if result.success:
            print(f"✓ Successfully converted to: {result.output_path}")
            print(f"  - Total properties: {result.statistics.get('total_properties', 0)}")
            return 0
        else:
            print("✗ Conversion failed:")
            for error in result.errors:
                print(f"  - {error}")
            return 1
    
    def _handle_validate(self, args) -> int:
        """Handle validate command."""
        # Validate input file
        is_valid, errors = self.path_utils.validate_file_path(args.input)
        if not is_valid:
            print("Input file validation failed:")
            for error in errors:
                print(f"  - {error}")
            return 1
        
        print(f"Validating schema file: {args.input}")
        
        # Get file info
        file_info = self.path_utils.get_file_info(args.input)
        
        # Validate file format
        format_errors = self.validation_utils.validate_file_format(args.input)
        
        # Process schema for validation
        try:
            schema_processor = SchemaProcessor()
            headers, rows = schema_processor.process_schema(args.input)
            
            # Validate schema data
            data_errors = self.validation_utils.validate_schema_data(headers, rows)
            
            all_errors = format_errors + data_errors
            
            if not all_errors:
                print("✓ Schema is valid")
                print(f"  - File size: {file_info.get('size', 0)} bytes")
                print(f"  - Total rows: {len(rows)}")
                print(f"  - Total columns: {len(headers)}")
                return 0
            else:
                print("✗ Schema validation failed:")
                if args.detailed:
                    error_report = self.validation_utils.format_validation_errors(all_errors)
                    print(error_report)
                else:
                    summary = self.validation_utils.get_validation_summary(all_errors)
                    print(f"  - Total issues: {summary['total_errors']}")
                    print(f"  - Errors: {summary['error_count']}")
                    print(f"  - Warnings: {summary['warning_count']}")
                return 1
                
        except Exception as e:
            print(f"✗ Validation failed: {str(e)}")
            return 1
    
    def _handle_info(self, args) -> int:
        """Handle info command."""
        # Validate input file
        is_valid, errors = self.path_utils.validate_file_path(args.input)
        if not is_valid:
            print("Input file validation failed:")
            for error in errors:
                print(f"  - {error}")
            return 1
        
        print(f"File information: {args.input}")
        
        # Get file info
        file_info = self.path_utils.get_file_info(args.input)
        
        print(f"  - Exists: {file_info['exists']}")
        print(f"  - File size: {file_info['size']} bytes")
        print(f"  - Extension: {file_info['extension']}")
        print(f"  - Base name: {file_info['base_name']}")
        print(f"  - Directory: {file_info['directory']}")
        print(f"  - Supported: {file_info['is_supported']}")
        
        # Get schema type
        schema_processor = SchemaProcessor()
        schema_type = schema_processor.detect_schema_type(args.input)
        
        if schema_type:
            print(f"  - Schema type: {schema_type.value}")
            
            # Process schema for additional info
            try:
                headers, rows = schema_processor.process_schema(args.input)
                print(f"  - Total rows: {len(rows)}")
                print(f"  - Total columns: {len(headers)}")
                
                # Show column headers
                print(f"  - Columns: {', '.join(headers[:5])}{'...' if len(headers) > 5 else ''}")
                
            except Exception as e:
                print(f"  - Processing error: {str(e)}")
        else:
            print(f"  - Schema type: Unknown")
        
        return 0


def main():
    """Main entry point for CLI."""
    cli = CLIInterface()
    exit_code = cli.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 