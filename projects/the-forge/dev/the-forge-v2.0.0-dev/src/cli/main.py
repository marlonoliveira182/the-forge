#!/usr/bin/env python3
"""
Command Line Interface for The Forge v2.0.0
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from core.schema_processor import SchemaProcessor
from core.mapping_engine import MappingEngine
from core.excel_generator import ExcelGenerator
from core.converter import SchemaConverter

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="The Forge v2.0.0 - Schema Conversion and Mapping Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert XSD to JSON Schema
  the-forge-cli convert --input schema.xsd --output schema.json --type xsd-to-json
  
  # Convert JSON Schema to XSD
  the-forge-cli convert --input schema.json --output schema.xsd --type json-to-xsd
  
  # Generate Excel documentation
  the-forge-cli document --input schema.xsd --output documentation.xlsx
  
  # Create field mapping
  the-forge-cli map --source source.xsd --target target.json --output mapping.xlsx
  
  # Validate schema
  the-forge-cli validate --input schema.xsd
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert between schema formats')
    convert_parser.add_argument('--input', '-i', required=True, help='Input schema file')
    convert_parser.add_argument('--output', '-o', required=True, help='Output schema file')
    convert_parser.add_argument('--type', '-t', required=True, 
                              choices=['xsd-to-json', 'json-to-xsd'],
                              help='Conversion type')
    
    # Document command
    doc_parser = subparsers.add_parser('document', help='Generate Excel documentation')
    doc_parser.add_argument('--input', '-i', required=True, help='Input schema file')
    doc_parser.add_argument('--output', '-o', required=True, help='Output Excel file')
    
    # Map command
    map_parser = subparsers.add_parser('map', help='Create field mapping between schemas')
    map_parser.add_argument('--source', '-s', required=True, help='Source schema file')
    map_parser.add_argument('--target', '-t', required=True, help='Target schema file')
    map_parser.add_argument('--output', '-o', required=True, help='Output Excel file')
    map_parser.add_argument('--threshold', type=float, default=0.7, 
                          help='Similarity threshold (0.0-1.0)')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate schema file')
    validate_parser.add_argument('--input', '-i', required=True, help='Schema file to validate')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'convert':
            return handle_convert(args)
        elif args.command == 'document':
            return handle_document(args)
        elif args.command == 'map':
            return handle_map(args)
        elif args.command == 'validate':
            return handle_validate(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        return 1

def handle_convert(args) -> int:
    """Handle schema conversion"""
    converter = SchemaConverter()
    
    print(f"Converting {args.input} to {args.output}...")
    
    if args.type == 'xsd-to-json':
        success = converter.xsd_to_json_schema(args.input, args.output)
    else:  # json-to-xsd
        success = converter.json_schema_to_xsd(args.input, args.output)
    
    if success:
        print("✅ Conversion completed successfully")
        
        # Validate conversion
        source_type = 'xsd' if args.type == 'xsd-to-json' else 'json'
        is_valid, message = converter.validate_conversion(args.input, args.output, source_type)
        
        if is_valid:
            print(f"✅ Validation passed: {message}")
        else:
            print(f"⚠️  Validation warning: {message}")
        
        return 0
    else:
        print("❌ Conversion failed")
        return 1

def handle_document(args) -> int:
    """Handle documentation generation"""
    processor = SchemaProcessor()
    generator = ExcelGenerator()
    
    print(f"Generating documentation for {args.input}...")
    
    # Determine schema type and load fields
    input_path = Path(args.input)
    if input_path.suffix.lower() == '.xsd':
        fields = processor.extract_fields_from_xsd(args.input)
    elif input_path.suffix.lower() == '.json':
        fields = processor.extract_fields_from_json_schema(args.input)
    else:
        print(f"❌ Unsupported file type: {input_path.suffix}")
        return 1
    
    # Generate Excel documentation
    success = generator.create_schema_excel(fields, args.output)
    
    if success:
        print(f"✅ Documentation generated: {args.output}")
        print(f"📊 Processed {len(fields)} fields")
        return 0
    else:
        print("❌ Documentation generation failed")
        return 1

def handle_map(args) -> int:
    """Handle schema mapping"""
    processor = SchemaProcessor()
    engine = MappingEngine(threshold=args.threshold)
    generator = ExcelGenerator()
    
    print(f"Creating mapping between {args.source} and {args.target}...")
    
    # Load schemas
    source_ext = Path(args.source).suffix.lower()
    target_ext = Path(args.target).suffix.lower()
    
    if source_ext == '.xsd':
        source_fields = processor.extract_fields_from_xsd(args.source)
    elif source_ext == '.json':
        source_fields = processor.extract_fields_from_json_schema(args.source)
    else:
        print(f"❌ Unsupported source file type: {source_ext}")
        return 1
    
    if target_ext == '.xsd':
        target_fields = processor.extract_fields_from_xsd(args.target)
    elif target_ext == '.json':
        target_fields = processor.extract_fields_from_json_schema(args.target)
    else:
        print(f"❌ Unsupported target file type: {target_ext}")
        return 1
    
    # Create mappings
    mappings = engine.map_fields(source_fields, target_fields)
    
    # Generate Excel mapping
    success = generator.create_mapping_excel(source_fields, target_fields, mappings, args.output)
    
    if success:
        print(f"✅ Mapping created: {args.output}")
        print(f"📊 {len(mappings)} mappings found")
        
        # Show mapping statistics
        validation = engine.validate_mapping()
        print(f"📈 Exact matches: {validation['exact_matches']}")
        print(f"📈 Good matches: {validation['good_matches']}")
        print(f"📈 Weak matches: {validation['weak_matches']}")
        print(f"📈 Unmapped: {validation['unmapped']}")
        print(f"📈 Average similarity: {validation['average_similarity']:.3f}")
        
        return 0
    else:
        print("❌ Mapping creation failed")
        return 1

def handle_validate(args) -> int:
    """Handle schema validation"""
    processor = SchemaProcessor()
    
    print(f"Validating {args.input}...")
    
    input_path = Path(args.input)
    if input_path.suffix.lower() == '.xsd':
        is_valid, message = processor.validate_xsd_schema(args.input)
    elif input_path.suffix.lower() == '.json':
        is_valid, message = processor.validate_json_schema(args.input)
    else:
        print(f"❌ Unsupported file type: {input_path.suffix}")
        return 1
    
    if is_valid:
        print(f"✅ {message}")
        return 0
    else:
        print(f"❌ {message}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 