"""
Unit tests for schema processor module.
"""

import pytest
import tempfile
import os
from src.core.schema_processor import SchemaProcessor, SchemaField


class TestSchemaProcessor:
    """Test cases for SchemaProcessor class."""
    
    def test_extract_fields_from_xsd_simple(self, sample_xsd_file):
        """Test extracting fields from simple XSD."""
        processor = SchemaProcessor()
        fields = processor.extract_fields_from_xsd(sample_xsd_file)
        
        assert len(fields) > 0
        assert all(isinstance(field, SchemaField) for field in fields)
        
        # Check for expected fields (note: XSD element names are converted to camelCase)
        field_paths = ['.'.join(field.levels) for field in fields]
        assert 'person' in field_paths
        assert 'person.name' in field_paths
        assert 'person.age' in field_paths
        assert 'person.email' in field_paths
    
    def test_extract_fields_from_xsd_complex(self, complex_xsd_file):
        """Test extracting fields from complex XSD."""
        processor = SchemaProcessor()
        fields = processor.extract_fields_from_xsd(complex_xsd_file)
        
        assert len(fields) > 0
        
        # Check for expected fields (note: XSD element names are converted to camelCase)
        field_paths = ['.'.join(field.levels) for field in fields]
        assert 'order' in field_paths
        assert 'order.orderId' in field_paths
        assert 'order.customer' in field_paths
        assert 'order.items' in field_paths
        assert 'order.items.item.productId' in field_paths
    
    def test_extract_fields_from_json_schema_simple(self, sample_json_schema_file):
        """Test extracting fields from simple JSON Schema."""
        processor = SchemaProcessor()
        fields = processor.extract_fields_from_json_schema(sample_json_schema_file)
        
        assert len(fields) > 0
        assert all(isinstance(field, SchemaField) for field in fields)
        
        # Check for expected fields
        field_paths = ['.'.join(field.levels) for field in fields]
        assert 'person' in field_paths
        assert 'person.name' in field_paths
        assert 'person.age' in field_paths
        assert 'person.email' in field_paths
    
    def test_extract_fields_from_json_schema_complex(self, complex_json_schema_file):
        """Test extracting fields from complex JSON Schema."""
        processor = SchemaProcessor()
        fields = processor.extract_fields_from_json_schema(complex_json_schema_file)
        
        assert len(fields) > 0
        
        # Check for expected fields
        field_paths = ['.'.join(field.levels) for field in fields]
        assert 'order' in field_paths
        assert 'order.orderId' in field_paths
        assert 'order.customer' in field_paths
        assert 'order.items' in field_paths
        assert 'order.items.[].productId' in field_paths
    
    def test_extract_paths_from_xsd(self, sample_xsd_file):
        """Test extracting paths from XSD."""
        processor = SchemaProcessor()
        paths = processor.extract_paths_from_xsd(sample_xsd_file)
        
        assert len(paths) > 0
        assert all(isinstance(path, str) for path in paths)
        assert 'person.name' in paths
        assert 'person.age' in paths
    
    def test_extract_paths_from_json_schema(self, sample_json_schema_file):
        """Test extracting paths from JSON Schema."""
        processor = SchemaProcessor()
        paths = processor.extract_paths_from_json_schema(sample_json_schema_file)
        
        assert len(paths) > 0
        assert all(isinstance(path, str) for path in paths)
        assert 'person.name' in paths
        assert 'person.age' in paths
    
    def test_schema_field_creation(self):
        """Test SchemaField creation."""
        field = SchemaField(
            levels=['person', 'name'],
            type='string',
            description='Person name',
            cardinality='1',
            details='',
            restrictions={'maxLength': 100}
        )
        
        assert field.levels == ['person', 'name']
        assert field.type == 'string'
        assert field.description == 'Person name'
        assert field.cardinality == '1'
        assert field.details == ''
        assert field.restrictions == {'maxLength': 100}
    
    def test_schema_field_default_restrictions(self):
        """Test SchemaField with default restrictions."""
        field = SchemaField(
            levels=['person', 'name'],
            type='string',
            description='Person name',
            cardinality='1',
            details=''
        )
        
        assert field.restrictions == {}
    
    def test_invalid_xsd_file(self, temp_dir):
        """Test handling of invalid XSD file."""
        processor = SchemaProcessor()
        
        # Create invalid XSD
        invalid_xsd = os.path.join(temp_dir, "invalid.xsd")
        with open(invalid_xsd, 'w') as f:
            f.write("invalid xml content")
        
        with pytest.raises(Exception):
            processor.extract_fields_from_xsd(invalid_xsd)
    
    def test_invalid_json_schema_file(self, temp_dir):
        """Test handling of invalid JSON Schema file."""
        processor = SchemaProcessor()
        
        # Create invalid JSON
        invalid_json = os.path.join(temp_dir, "invalid.json")
        with open(invalid_json, 'w') as f:
            f.write("invalid json content")
        
        with pytest.raises(Exception):
            processor.extract_fields_from_json_schema(invalid_json)
    
    def test_empty_xsd_file(self, temp_dir):
        """Test handling of empty XSD file."""
        processor = SchemaProcessor()
        
        # Create empty XSD
        empty_xsd = os.path.join(temp_dir, "empty.xsd")
        with open(empty_xsd, 'w') as f:
            f.write("")
        
        with pytest.raises(Exception):
            processor.extract_fields_from_xsd(empty_xsd)
    
    def test_xsd_with_annotations(self, temp_dir):
        """Test XSD with annotations."""
        xsd_with_annotations = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="Person">
        <xs:annotation>
            <xs:documentation>Person information</xs:documentation>
        </xs:annotation>
        <xs:complexType>
            <xs:sequence>
                <xs:element name="Name" type="xs:string">
                    <xs:annotation>
                        <xs:documentation>Full name of the person</xs:documentation>
                    </xs:annotation>
                </xs:element>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''
        
        file_path = os.path.join(temp_dir, "annotated.xsd")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xsd_with_annotations)
        
        processor = SchemaProcessor()
        fields = processor.extract_fields_from_xsd(file_path)
        
        assert len(fields) > 0
        # Check that descriptions are extracted (note: 'Name' becomes 'name')
        name_field = next(f for f in fields if 'name' in f.levels)
        assert 'Full name of the person' in name_field.description
    
    def test_xsd_with_restrictions(self, temp_dir):
        """Test XSD with restrictions."""
        xsd_with_restrictions = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="Person">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="Age">
                    <xs:simpleType>
                        <xs:restriction base="xs:int">
                            <xs:minInclusive value="0"/>
                            <xs:maxInclusive value="150"/>
                        </xs:restriction>
                    </xs:simpleType>
                </xs:element>
                <xs:element name="Email">
                    <xs:simpleType>
                        <xs:restriction base="xs:string">
                            <xs:pattern value="[^@]+@[^@]+\\.[^@]+"/>
                            <xs:maxLength value="255"/>
                        </xs:restriction>
                    </xs:simpleType>
                </xs:element>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''
        
        file_path = os.path.join(temp_dir, "restricted.xsd")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xsd_with_restrictions)
        
        processor = SchemaProcessor()
        fields = processor.extract_fields_from_xsd(file_path)
        
        assert len(fields) > 0
        
        # Check that restrictions are extracted (note: 'Age' becomes 'age', 'Email' becomes 'email')
        age_field = next(f for f in fields if 'age' in f.levels)
        assert 'minInclusive: 0' in age_field.details
        assert 'maxInclusive: 150' in age_field.details
        
        email_field = next(f for f in fields if 'email' in f.levels)
        assert 'pattern: [^@]+@[^@]+\\.[^@]+' in email_field.details
        assert 'maxLength: 255' in email_field.details 