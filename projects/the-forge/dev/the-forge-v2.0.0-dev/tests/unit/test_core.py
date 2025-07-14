"""
Basic tests for The Forge v2.0.0 core functionality
"""

import pytest
from pathlib import Path
import tempfile
import json

# Import core modules
from src.core.schema_processor import SchemaProcessor, SchemaField
from src.core.mapping_engine import MappingEngine, FieldMapping
from src.core.excel_generator import ExcelGenerator
from src.core.converter import SchemaConverter

class TestSchemaProcessor:
    """Test the schema processor functionality"""
    
    def test_schema_field_creation(self):
        """Test SchemaField creation"""
        field = SchemaField(
            path="test.field",
            name="testField",
            type="string",
            description="Test field",
            cardinality="1",
            required=True,
            parent_path="",
            is_array=False,
            is_complex=False,
            constraints={},
            metadata={}
        )
        
        assert field.path == "test.field"
        assert field.name == "testField"
        assert field.type == "string"
        assert field.description == "Test field"
        assert field.cardinality == "1"
        assert field.required is True
    
    def test_schema_processor_initialization(self):
        """Test SchemaProcessor initialization"""
        processor = SchemaProcessor()
        assert processor is not None
        assert hasattr(processor, 'xsd_namespace')

class TestMappingEngine:
    """Test the mapping engine functionality"""
    
    def test_mapping_engine_initialization(self):
        """Test MappingEngine initialization"""
        engine = MappingEngine(threshold=0.7)
        assert engine.threshold == 0.7
        assert len(engine.mappings) == 0
    
    def test_field_mapping_creation(self):
        """Test FieldMapping creation"""
        source_field = SchemaField("source.path", "sourceField", "string", "desc", "1", True, "", False, False, {}, {})
        target_field = SchemaField("target.path", "targetField", "string", "User email", "1", "", True, constraints={}, metadata={})
        
        mapping = FieldMapping(
            source_field=source_field,
            target_field=target_field,
            similarity=0.8,
            confidence="auto"
        )
        
        assert mapping.source_field == source_field
        assert mapping.target_field == target_field
        assert mapping.similarity == 0.8
        assert mapping.confidence == "auto"
        assert mapping.is_good_match is True

class TestExcelGenerator:
    """Test the Excel generator functionality"""
    
    def test_excel_generator_initialization(self):
        """Test ExcelGenerator initialization"""
        generator = ExcelGenerator()
        assert generator is not None
        assert hasattr(generator, 'header_font')
        assert hasattr(generator, 'header_fill')
        assert hasattr(generator, 'border')

class TestSchemaConverter:
    """Test the schema converter functionality"""
    
    def test_schema_converter_initialization(self):
        """Test SchemaConverter initialization"""
        converter = SchemaConverter()
        assert converter is not None
        assert hasattr(converter, 'xsd_to_json_types')
        assert hasattr(converter, 'json_to_xsd_types')
    
    def test_type_mappings(self):
        """Test type mapping dictionaries"""
        converter = SchemaConverter()
        
        # Test XSD to JSON type mappings
        assert converter.xsd_to_json_types['xsd:string'] == 'string'
        assert converter.xsd_to_json_types['xsd:integer'] == 'integer'
        assert converter.xsd_to_json_types['xsd:boolean'] == 'boolean'
        
        # Test JSON to XSD type mappings
        assert converter.json_to_xsd_types['string'] == 'xs:string'
        assert converter.json_to_xsd_types['integer'] == 'xs:integer'
        assert converter.json_to_xsd_types['boolean'] == 'xs:boolean'

class TestIntegration:
    """Integration tests"""
    
    def test_basic_workflow(self):
        """Test basic workflow with sample data"""
        # Create sample fields
        source_fields = [
            SchemaField("user.name", "userName", "string", "User name", "1", True, "", False, False, {}, {}),
            SchemaField("user.email", "userEmail", "string", "User email", "1", True, "", False, False, {}, {}),
            SchemaField("user.age", "userAge", "integer", "User age", "0..1", False, "", False, False, {}, {})
        ]
        
        target_fields = [
            SchemaField("user.name", "userName", "string", "User name", "1", True, "", False, False, {}, {}),
            SchemaField("user.email", "userEmail", "string", "User email", "1", True, "", False, False, {}, {}),
            SchemaField("user.phone", "userPhone", "string", "User phone", "0..1", False, "", False, False, {}, {})
        ]
        
        # Test mapping engine
        engine = MappingEngine(threshold=0.7)
        mappings = engine.map_fields(source_fields, target_fields)
        
        assert len(mappings) == 3
        
        # Check that exact matches are found
        exact_matches = [m for m in mappings if m.is_exact_match]
        assert len(exact_matches) >= 2  # userName and userEmail should match exactly
        
        # Test Excel generator
        generator = ExcelGenerator()
        
                # Create temporary file for testing
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            success = generator.create_schema_excel(source_fields, tmp_path)
            assert success is True
        finally:
            # Clean up - use missing_ok=True to avoid permission errors
            Path(tmp_path).unlink(missing_ok=True)
    
    def test_converter_validation(self):
        """Test converter validation methods"""
        converter = SchemaConverter()
        
        # Test with invalid paths (should not crash)
        is_valid, message = converter.validate_conversion("nonexistent.xsd", "nonexistent.json", "xsd")
        assert is_valid is False
        assert "No fields found" in message or "Error" in message

if __name__ == "__main__":
    pytest.main([__file__]) 