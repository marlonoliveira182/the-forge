import json
import tempfile
import os
from typing import Dict, List, Any, Optional

from .json_to_schema_converter import JSONToSchemaConverter
from .xml_to_xsd_converter import XMLToXSDConverter
from .xsd_to_xml_converter import XSDToXMLConverter
from .json_schema_to_json_converter import JSONSchemaToJSONConverter
from .xsd_to_json_schema_converter import XSDToJSONSchemaConverter
from .json_schema_to_xsd_converter import JSONSchemaToXSDConverter
from .xml_to_json_schema_converter import XMLToJSONSchemaConverter
from .json_to_xml_converter import JSONToXMLConverter


class ConverterService:
    """
    Main converter service that orchestrates all conversion operations.
    """
    
    def __init__(self):
        self.json_to_schema = JSONToSchemaConverter()
        self.xml_to_xsd = XMLToXSDConverter()
        self.xsd_to_xml = XSDToXMLConverter()
        self.json_schema_to_json = JSONSchemaToJSONConverter()
        self.xsd_to_json_schema = XSDToJSONSchemaConverter()
        self.json_schema_to_xsd = JSONSchemaToXSDConverter()
        self.xml_to_json_schema = XMLToJSONSchemaConverter()
        self.json_to_xml = JSONToXMLConverter()
    
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
    
    def convert_xsd_to_json_schema(self, xsd_content: str, schema_name: str = "GeneratedSchema") -> Dict[str, Any]:
        """
        Convert XSD schema to JSON Schema.
        """
        return self.xsd_to_json_schema.convert_xsd_to_json_schema(xsd_content, schema_name)
    
    def convert_json_schema_to_xsd(self, schema: Dict[str, Any], schema_name: str = "GeneratedSchema") -> str:
        """
        Convert JSON Schema to XSD schema.
        """
        return self.json_schema_to_xsd.convert_json_schema_to_xsd(schema, schema_name)
    
    def convert_xml_to_json_schema(self, xml_content: str, schema_name: str = "GeneratedSchema") -> Dict[str, Any]:
        """
        Convert XML example to JSON Schema.
        """
        return self.xml_to_json_schema.convert_xml_to_json_schema(xml_content, schema_name)
    
    def convert_json_to_xml(self, json_data: Any, root_name: str = "root") -> str:
        """
        Convert JSON example to XML.
        """
        return self.json_to_xml.convert_json_to_xml(json_data, root_name)
    
    def convert_json_schema_to_xml(self, schema: Dict[str, Any], root_name: str = "root") -> str:
        """
        Convert JSON Schema to XML example.
        """
        return self.json_to_xml.convert_json_schema_to_xml(schema, root_name)
    
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
        elif conversion_type == "xsd_to_json_schema":
            return self.xsd_to_json_schema.validate_json_schema(output_data)
        elif conversion_type == "json_schema_to_xsd":
            return self.json_schema_to_xsd.validate_xsd(output_data)
        elif conversion_type == "xml_to_json_schema":
            return self.xml_to_json_schema.validate_json_schema(output_data)
        elif conversion_type in ["json_to_xml", "json_schema_to_xml"]:
            return self.json_to_xml.validate_xml(output_data)
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
        elif conversion_type == "xsd_to_json_schema":
            return self.xsd_to_json_schema.get_schema_statistics(output_data)
        elif conversion_type == "json_schema_to_xsd":
            return self.json_schema_to_xsd.get_schema_statistics(output_data)
        elif conversion_type == "xml_to_json_schema":
            return self.xml_to_json_schema.get_schema_statistics(output_data)
        elif conversion_type in ["json_to_xml", "json_schema_to_xml"]:
            return self.json_to_xml.get_xml_statistics(output_data)
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
            },
            "xsd_to_json_schema": {
                "name": "XSD to JSON Schema",
                "description": "Convert XSD schemas to JSON Schema",
                "input_type": "XSD",
                "output_type": "JSON Schema"
            },
            "json_schema_to_xsd": {
                "name": "JSON Schema to XSD",
                "description": "Convert JSON Schema to XSD schemas",
                "input_type": "JSON Schema",
                "output_type": "XSD"
            },
            "xml_to_json_schema": {
                "name": "XML Example to JSON Schema",
                "description": "Convert XML examples to JSON Schema",
                "input_type": "XML",
                "output_type": "JSON Schema"
            },
            "json_to_xml": {
                "name": "JSON Example to XML",
                "description": "Convert JSON examples to XML",
                "input_type": "JSON",
                "output_type": "XML"
            },
            "json_schema_to_xml": {
                "name": "JSON Schema to XML Example",
                "description": "Convert JSON Schema to XML examples",
                "input_type": "JSON Schema",
                "output_type": "XML"
            },
            "json_to_excel": {
                "name": "JSON Example to Excel",
                "description": "Convert JSON examples to Excel format",
                "input_type": "JSON",
                "output_type": "Excel"
            },
            "json_schema_to_excel": {
                "name": "JSON Schema to Excel",
                "description": "Convert JSON Schema to Excel format",
                "input_type": "JSON Schema",
                "output_type": "Excel"
            },
            "xsd_to_excel": {
                "name": "XSD to Excel",
                "description": "Convert XSD schemas to Excel format",
                "input_type": "XSD",
                "output_type": "Excel"
            },
            "xml_to_excel": {
                "name": "XML Example to Excel",
                "description": "Convert XML examples to Excel format",
                "input_type": "XML",
                "output_type": "Excel"
            }
        }
    
    def get_source_types(self) -> List[str]:
        """
        Get list of available source types.
        """
        return ["json example", "json schema", "xsd", "xml example", "excel"]
    
    def get_target_types_for_source(self, source_type: str) -> List[str]:
        """
        Get available target types for a given source type.
        """
        conversion_map = {
            "json example": ["json schema", "excel", "xml"],
            "json schema": ["json example", "excel", "xsd", "xml"],
            "xsd": ["xml example", "excel", "json schema"],
            "xml example": ["xsd", "excel", "json schema"],
            "excel": ["json schema", "xsd", "xml example"]
        }
        return conversion_map.get(source_type, [])
    
    def get_conversion_key(self, source_type: str, target_type: str) -> str:
        """
        Get the conversion key for a source-target combination.
        """
        conversion_keys = {
            ("json example", "json schema"): "json_to_schema",
            ("xml example", "xsd"): "xml_to_xsd",
            ("xsd", "xml example"): "xsd_to_xml",
            ("json schema", "json example"): "json_schema_to_json",
            ("json example", "excel"): "json_to_excel",
            ("json schema", "excel"): "json_schema_to_excel",
            ("xsd", "excel"): "xsd_to_excel",
            ("xml example", "excel"): "xml_to_excel",
            ("xsd", "json schema"): "xsd_to_json_schema",
            ("json schema", "xsd"): "json_schema_to_xsd",
            ("xml example", "json schema"): "xml_to_json_schema",
            ("json example", "xml"): "json_to_xml",
            ("json schema", "xml"): "json_schema_to_xml"
        }
        return conversion_keys.get((source_type, target_type), "")
    
    def process_file_conversion(self, file_path: str, conversion_type: str, **kwargs) -> Any:
        """
        Process a file conversion based on the conversion type.
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
            
            elif conversion_type == "xsd_to_json_schema":
                schema_name = kwargs.get('schema_name', 'GeneratedSchema')
                return self.convert_xsd_to_json_schema(content, schema_name)
            
            elif conversion_type == "json_schema_to_xsd":
                schema = json.loads(content)
                schema_name = kwargs.get('schema_name', 'GeneratedSchema')
                return self.convert_json_schema_to_xsd(schema, schema_name)
            
            elif conversion_type == "xml_to_json_schema":
                schema_name = kwargs.get('schema_name', 'GeneratedSchema')
                return self.convert_xml_to_json_schema(content, schema_name)
            
            elif conversion_type == "json_to_xml":
                json_data = json.loads(content)
                root_name = kwargs.get('root_name', 'root')
                return self.convert_json_to_xml(json_data, root_name)
            
            elif conversion_type == "json_schema_to_xml":
                schema = json.loads(content)
                root_name = kwargs.get('root_name', 'root')
                return self.convert_json_schema_to_xml(schema, root_name)
            
            elif conversion_type in ["json_to_excel", "json_schema_to_excel", "xsd_to_excel", "xml_to_excel"]:
                # These will be handled by the ExcelExporter service
                return self._convert_to_excel(file_path, conversion_type)
            
            else:
                raise ValueError(f"Unsupported conversion type: {conversion_type}")
                
        except Exception as e:
            raise Exception(f"Error processing conversion {conversion_type}: {str(e)}")
    
    def _convert_to_excel(self, file_path: str, conversion_type: str) -> bytes:
        """
        Convert various formats to Excel using the ExcelExporter service.
        This method will be called from the main app with the ExcelExporter service.
        """
        # This is a placeholder - the actual conversion will be handled in the app
        # by calling the appropriate ExcelExporter methods
        raise NotImplementedError(f"Excel conversion for {conversion_type} will be handled by ExcelExporter service")
    
    def save_conversion_result(self, result: Any, conversion_type: str, output_path: str) -> str:
        """
        Save conversion result to a file.
        """
        try:
            if conversion_type in ["json_to_schema", "json_schema_to_json", "xsd_to_json_schema", "xml_to_json_schema"]:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result)
            return output_path
        except Exception as e:
            raise Exception(f"Error saving conversion result: {str(e)}")
    
    def get_conversion_help(self, conversion_type: str) -> Dict[str, str]:
        """
        Get help information for a conversion type.
        """
        help_info = {
            "json_to_schema": {
                "input_format": "JSON object or array",
                "output_format": "JSON Schema (draft-07)",
                "features": "Type inference, format detection, array deduplication",
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
                "features": "Sample data generation, namespace handling",
                "example": '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">...</xs:schema>'
            },
            "json_schema_to_json": {
                "input_format": "JSON Schema",
                "output_format": "JSON Example",
                "features": "Random data generation, format compliance",
                "example": '{"type": "object", "properties": {"name": {"type": "string"}}}'
            },
            "xsd_to_json_schema": {
                "input_format": "XSD Schema",
                "output_format": "JSON Schema (draft-07)",
                "features": "Type mapping, constraint conversion",
                "example": '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">...</xs:schema>'
            },
            "json_schema_to_xsd": {
                "input_format": "JSON Schema",
                "output_format": "XSD Schema",
                "features": "Type mapping, constraint conversion",
                "example": '{"type": "object", "properties": {"name": {"type": "string"}}}'
            },
            "xml_to_json_schema": {
                "input_format": "XML document",
                "output_format": "JSON Schema (draft-07)",
                "features": "Structure analysis, type inference",
                "example": '<person><name>John</name><age>30</age></person>'
            },
            "json_to_xml": {
                "input_format": "JSON object or array",
                "output_format": "XML document",
                "features": "Element creation, attribute support",
                "example": '{"name": "John", "age": 30}'
            },
            "json_schema_to_xml": {
                "input_format": "JSON Schema",
                "output_format": "XML Example",
                "features": "Sample data generation, structure preservation",
                "example": '{"type": "object", "properties": {"name": {"type": "string"}}}'
            },
            "json_to_excel": {
                "input_format": "JSON object or array",
                "output_format": "Excel file (.xlsx)",
                "features": "Structure analysis, hierarchical mapping",
                "example": '{"name": "John", "age": 30}'
            },
            "json_schema_to_excel": {
                "input_format": "JSON Schema",
                "output_format": "Excel file (.xlsx)",
                "features": "Schema analysis, property mapping",
                "example": '{"type": "object", "properties": {...}}'
            },
            "xsd_to_excel": {
                "input_format": "XSD Schema",
                "output_format": "Excel file (.xlsx)",
                "features": "Element analysis, type mapping",
                "example": '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">...</xs:schema>'
            },
            "xml_to_excel": {
                "input_format": "XML document",
                "output_format": "Excel file (.xlsx)",
                "features": "Structure analysis, element mapping",
                "example": '<person><name>John</name><age>30</age></person>'
            }
        }
        return help_info.get(conversion_type, {
            "input_format": "N/A",
            "output_format": "N/A",
            "features": "N/A",
            "example": "N/A"
        }) 