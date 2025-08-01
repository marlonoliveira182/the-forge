import json
import tempfile
import os
from typing import Dict, List, Any, Optional

from .json_to_schema_converter import JSONToSchemaConverter
from .xml_to_xsd_converter import XMLToXSDConverter
from .xsd_to_xml_converter import XSDToXMLConverter
from .json_schema_to_json_converter import JSONSchemaToJSONConverter


class ConverterService:
    """
    Main converter service that orchestrates all conversion operations.
    """
    
    def __init__(self):
        self.json_to_schema = JSONToSchemaConverter()
        self.xml_to_xsd = XMLToXSDConverter()
        self.xsd_to_xml = XSDToXMLConverter()
        self.json_schema_to_json = JSONSchemaToJSONConverter()
    
    def convert_json_example_to_schema(self, json_data: Any, schema_name: str = "GeneratedSchema") -> Dict[str, Any]:
        """
        Convert JSON example to JSON schema.
        """
        return self.json_to_schema.convert_json_example_to_schema(json_data, schema_name)
    
    def convert_xml_example_to_xsd(self, xml_data: str, schema_name: str = "GeneratedSchema") -> str:
        """
        Convert XML example to XSD schema.
        """
        return self.xml_to_xsd.convert_xml_example_to_xsd(xml_data, schema_name)
    
    def convert_xsd_to_xml_example(self, xsd_content: str, root_element_name: Optional[str] = None) -> str:
        """
        Convert XSD schema to XML example.
        """
        return self.xsd_to_xml.convert_xsd_to_xml_example(xsd_content, root_element_name)
    
    def convert_json_schema_to_json_example(self, schema: Dict[str, Any], num_examples: int = 1) -> List[Dict[str, Any]]:
        """
        Convert JSON schema to JSON examples.
        """
        return self.json_schema_to_json.convert_json_schema_to_json_example(schema, num_examples)
    
    def validate_conversion(self, conversion_type: str, input_data: Any, output_data: Any) -> bool:
        """
        Validate a conversion result.
        """
        if conversion_type == "json_to_schema":
            return self.json_to_schema.validate_schema(output_data)
        elif conversion_type == "xml_to_xsd":
            return self.xml_to_xsd.validate_xsd(output_data)
        elif conversion_type == "xsd_to_xml":
            return self.xsd_to_xml.validate_xml(output_data)
        elif conversion_type == "json_schema_to_json":
            return self.json_schema_to_json.validate_example(output_data[0], input_data)
        else:
            return False
    
    def get_conversion_statistics(self, conversion_type: str, output_data: Any) -> Dict[str, int]:
        """
        Get statistics about a conversion result.
        """
        if conversion_type == "json_to_schema":
            return self.json_to_schema.get_schema_statistics(output_data)
        elif conversion_type == "xml_to_xsd":
            return self.xml_to_xsd.get_schema_statistics(output_data)
        elif conversion_type == "xsd_to_xml":
            return self.xsd_to_xml.get_example_statistics(output_data)
        elif conversion_type == "json_schema_to_json":
            return self.json_schema_to_json.get_example_statistics(output_data)
        else:
            return {}
    
    def get_supported_conversions(self) -> Dict[str, Dict[str, str]]:
        """
        Get list of supported conversions.
        """
        return {
            "json_to_schema": {
                "name": "JSON Example to JSON Schema",
                "description": "Convert JSON examples to JSON schemas",
                "input_type": "JSON",
                "output_type": "JSON Schema"
            },
            "xml_to_xsd": {
                "name": "XML Example to XSD",
                "description": "Convert XML examples to XSD schemas",
                "input_type": "XML",
                "output_type": "XSD"
            },
            "xsd_to_xml": {
                "name": "XSD to XML Example",
                "description": "Convert XSD schemas to XML examples",
                "input_type": "XSD",
                "output_type": "XML"
            },
            "json_schema_to_json": {
                "name": "JSON Schema to JSON Example",
                "description": "Convert JSON schemas to JSON examples",
                "input_type": "JSON Schema",
                "output_type": "JSON"
            }
        }
    
    def process_file_conversion(self, file_path: str, conversion_type: str, **kwargs) -> Any:
        """
        Process a file conversion.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if conversion_type == "json_to_schema":
                json_data = json.loads(content)
                schema_name = kwargs.get('schema_name', 'GeneratedSchema')
                return self.convert_json_example_to_schema(json_data, schema_name)
            
            elif conversion_type == "xml_to_xsd":
                schema_name = kwargs.get('schema_name', 'GeneratedSchema')
                return self.convert_xml_example_to_xsd(content, schema_name)
            
            elif conversion_type == "xsd_to_xml":
                root_element_name = kwargs.get('root_element_name')
                return self.convert_xsd_to_xml_example(content, root_element_name)
            
            elif conversion_type == "json_schema_to_json":
                schema = json.loads(content)
                num_examples = kwargs.get('num_examples', 1)
                return self.convert_json_schema_to_json_example(schema, num_examples)
            
            else:
                raise ValueError(f"Unsupported conversion type: {conversion_type}")
                
        except Exception as e:
            raise ValueError(f"Error processing file conversion: {str(e)}")
    
    def save_conversion_result(self, result: Any, conversion_type: str, output_path: str) -> str:
        """
        Save conversion result to file.
        """
        try:
            if conversion_type in ["json_to_schema", "json_schema_to_json"]:
                # JSON format
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
            
            elif conversion_type in ["xml_to_xsd", "xsd_to_xml"]:
                # XML/XSD format
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result)
            
            return output_path
            
        except Exception as e:
            raise ValueError(f"Error saving conversion result: {str(e)}")
    
    def get_conversion_help(self, conversion_type: str) -> Dict[str, str]:
        """
        Get help information for a specific conversion type.
        """
        help_info = {
            "json_to_schema": {
                "input_format": "JSON object or array",
                "output_format": "JSON Schema (Draft 07)",
                "features": "Automatic type detection, format detection, array deduplication",
                "example": '{"name": "John", "age": 30, "email": "john@example.com"}'
            },
            "xml_to_xsd": {
                "input_format": "XML document",
                "output_format": "XSD Schema",
                "features": "Element analysis, attribute detection, type inference",
                "example": '<person><name>John</name><age>30</age></person>'
            },
            "xsd_to_xml": {
                "input_format": "XSD Schema",
                "output_format": "XML Example",
                "features": "Schema parsing, element generation, sample data",
                "example": "Upload an XSD file to generate XML examples"
            },
            "json_schema_to_json": {
                "input_format": "JSON Schema",
                "output_format": "JSON Examples",
                "features": "Schema validation, random data generation, format compliance",
                "example": '{"type": "object", "properties": {"name": {"type": "string"}}}'
            }
        }
        
        return help_info.get(conversion_type, {}) 