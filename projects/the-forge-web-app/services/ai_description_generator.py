import json
import xml.etree.ElementTree as ET
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

# Free AI libraries for text generation
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

@dataclass
class SchemaField:
    name: str
    type: str
    description: Optional[str] = None
    required: bool = False
    min_occurrences: int = 0
    max_occurrences: int = 1

@dataclass
class SchemaStructure:
    name: str
    type: str
    fields: List[SchemaField]
    description: Optional[str] = None
    namespace: Optional[str] = None

class AIDescriptionGenerator:
    """
    AI-powered service for generating functional descriptions of integration artifacts
    from WSDL, XSD, JSON, XML, or JSON schema files.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_generator = None
        self.tokenizer = None
        self.model = None
        
        # Initialize AI models if available
        self._initialize_ai_models()
    
    def _initialize_ai_models(self):
        """Initialize AI models for text generation."""
        if TRANSFORMERS_AVAILABLE:
            try:
                # Use a smaller model for faster processing
                model_name = "facebook/bart-large-cnn"  # Good for summarization
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                self.text_generator = pipeline("summarization", model=self.model, tokenizer=self.tokenizer)
                self.logger.info("AI models initialized successfully")
            except Exception as e:
                self.logger.warning(f"Could not initialize AI models: {e}")
                self.text_generator = None
    
    def generate_descriptions(self, file_path: str, file_type: str) -> Dict[str, str]:
        """
        Generate short description and detailed description for an integration artifact.
        
        Args:
            file_path: Path to the schema file
            file_type: Type of file (wsdl, xsd, json, xml, json_schema)
            
        Returns:
            Dictionary with 'short_description' and 'detailed_description'
        """
        try:
            # Parse the schema file
            schema_info = self._parse_schema_file(file_path, file_type)
            
            # Generate descriptions
            short_desc = self._generate_short_description(schema_info)
            detailed_desc = self._generate_detailed_description(schema_info)
            
            return {
                'short_description': short_desc,
                'detailed_description': detailed_desc,
                'schema_info': schema_info
            }
            
        except Exception as e:
            self.logger.error(f"Error generating descriptions: {e}")
            return {
                'short_description': f"Error processing {file_type} file: {str(e)}",
                'detailed_description': f"Unable to generate description due to error: {str(e)}",
                'schema_info': {}
            }
    
    def _parse_schema_file(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Parse different types of schema files and extract relevant information."""
        if file_type.lower() == 'xsd':
            return self._parse_xsd_file(file_path)
        elif file_type.lower() == 'json':
            return self._parse_json_file(file_path)
        elif file_type.lower() == 'json_schema':
            return self._parse_json_schema_file(file_path)
        elif file_type.lower() == 'wsdl':
            return self._parse_wsdl_file(file_path)
        elif file_type.lower() == 'xml':
            return self._parse_xml_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _parse_xsd_file(self, file_path: str) -> Dict[str, Any]:
        """Parse XSD file and extract schema information."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract namespace information
            namespaces = {
                'xs': 'http://www.w3.org/2001/XMLSchema',
                'xsd': 'http://www.w3.org/2001/XMLSchema'
            }
            
            # Find all complex types and elements
            complex_types = root.findall('.//xs:complexType', namespaces)
            elements = root.findall('.//xs:element', namespaces)
            simple_types = root.findall('.//xs:simpleType', namespaces)
            
            structures = []
            
            # Process complex types
            for ct in complex_types:
                name = ct.get('name', 'Unknown')
                fields = []
                
                # Extract sequence elements
                sequence = ct.find('.//xs:sequence', namespaces)
                if sequence is not None:
                    for elem in sequence.findall('.//xs:element', namespaces):
                        # Handle unbounded maxOccurs
                        max_occurs = elem.get('maxOccurs', '1')
                        max_occurrences = 999 if max_occurs == 'unbounded' else int(max_occurs)
                        
                        field = SchemaField(
                            name=elem.get('name', 'Unknown'),
                            type=elem.get('type', 'string'),
                            required=elem.get('minOccurs', '1') == '1',
                            min_occurrences=int(elem.get('minOccurs', '1')),
                            max_occurrences=max_occurrences
                        )
                        fields.append(field)
                
                # Extract attributes
                for attr in ct.findall('.//xs:attribute', namespaces):
                    field = SchemaField(
                        name=attr.get('name', 'Unknown'),
                        type=attr.get('type', 'string'),
                        required=attr.get('use', 'optional') == 'required'
                    )
                    fields.append(field)
                
                structure = SchemaStructure(
                    name=name,
                    type='complexType',
                    fields=fields
                )
                structures.append(structure)
            
            # Process top-level elements
            for elem in elements:
                name = elem.get('name', 'Unknown')
                elem_type = elem.get('type', 'string')
                
                structure = SchemaStructure(
                    name=name,
                    type='element',
                    fields=[SchemaField(name=name, type=elem_type)]
                )
                structures.append(structure)
            
            return {
                'file_type': 'XSD',
                'structures': [self._structure_to_dict(s) for s in structures],
                'total_structures': len(structures),
                'namespaces': dict(root.nsmap) if hasattr(root, 'nsmap') else {}
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing XSD file: {e}")
            raise
    
    def _parse_json_file(self, file_path: str) -> Dict[str, Any]:
        """Parse JSON file and extract structure information."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            structures = []
            fields = self._extract_json_fields(data, 'root')
            
            structure = SchemaStructure(
                name='JSON Document',
                type='json',
                fields=fields
            )
            structures.append(structure)
            
            return {
                'file_type': 'JSON',
                'structures': [self._structure_to_dict(s) for s in structures],
                'total_structures': len(structures)
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing JSON file: {e}")
            raise
    
    def _parse_json_schema_file(self, file_path: str) -> Dict[str, Any]:
        """Parse JSON Schema file and extract schema information."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            structures = []
            
            # Extract main schema info
            title = schema.get('title', 'JSON Schema')
            description = schema.get('description', '')
            
            # Extract properties
            properties = schema.get('properties', {})
            fields = []
            
            for prop_name, prop_def in properties.items():
                field = SchemaField(
                    name=prop_name,
                    type=prop_def.get('type', 'string'),
                    description=prop_def.get('description', ''),
                    required=prop_name in schema.get('required', [])
                )
                fields.append(field)
            
            structure = SchemaStructure(
                name=title,
                type='json_schema',
                fields=fields,
                description=description
            )
            structures.append(structure)
            
            return {
                'file_type': 'JSON Schema',
                'structures': [self._structure_to_dict(s) for s in structures],
                'total_structures': len(structures),
                'schema_info': {
                    'title': title,
                    'description': description,
                    'version': schema.get('$schema', '')
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing JSON Schema file: {e}")
            raise
    
    def _parse_wsdl_file(self, file_path: str) -> Dict[str, Any]:
        """Parse WSDL file and extract service information."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract namespace information
            namespaces = {
                'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
                'soap': 'http://schemas.xmlsoap.org/wsdl/soap/',
                'xsd': 'http://www.w3.org/2001/XMLSchema'
            }
            
            # Extract service information
            services = root.findall('.//wsdl:service', namespaces)
            ports = root.findall('.//wsdl:port', namespaces)
            operations = root.findall('.//wsdl:operation', namespaces)
            
            structures = []
            
            # Process services
            for service in services:
                service_name = service.get('name', 'Unknown Service')
                fields = []
                
                # Extract port information
                for port in service.findall('.//wsdl:port', namespaces):
                    field = SchemaField(
                        name=port.get('name', 'Unknown Port'),
                        type='port',
                        description=f"Port binding: {port.get('binding', 'Unknown')}"
                    )
                    fields.append(field)
                
                structure = SchemaStructure(
                    name=service_name,
                    type='service',
                    fields=fields
                )
                structures.append(structure)
            
            # Process operations
            for operation in operations:
                op_name = operation.get('name', 'Unknown Operation')
                fields = []
                
                # Extract input/output
                for io in operation.findall('.//wsdl:input', namespaces) + operation.findall('.//wsdl:output', namespaces):
                    field = SchemaField(
                        name=io.get('name', 'Unknown'),
                        type=io.tag.split('}')[-1],  # Extract local name
                        description=f"Message: {io.get('message', 'Unknown')}"
                    )
                    fields.append(field)
                
                structure = SchemaStructure(
                    name=op_name,
                    type='operation',
                    fields=fields
                )
                structures.append(structure)
            
            return {
                'file_type': 'WSDL',
                'structures': [self._structure_to_dict(s) for s in structures],
                'total_structures': len(structures),
                'namespaces': dict(root.nsmap) if hasattr(root, 'nsmap') else {}
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing WSDL file: {e}")
            raise
    
    def _parse_xml_file(self, file_path: str) -> Dict[str, Any]:
        """Parse XML file and extract structure information."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            structures = []
            fields = self._extract_xml_fields(root)
            
            structure = SchemaStructure(
                name=root.tag.split('}')[-1] if '}' in root.tag else root.tag,
                type='xml',
                fields=fields
            )
            structures.append(structure)
            
            return {
                'file_type': 'XML',
                'structures': [self._structure_to_dict(s) for s in structures],
                'total_structures': len(structures)
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing XML file: {e}")
            raise
    
    def _extract_json_fields(self, data: Any, path: str) -> List[SchemaField]:
        """Recursively extract fields from JSON data."""
        fields = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                field_type = type(value).__name__
                field = SchemaField(
                    name=key,
                    type=field_type,
                    description=f"Path: {path}.{key}"
                )
                fields.append(field)
                
                # Recursively process nested objects
                if isinstance(value, (dict, list)):
                    nested_fields = self._extract_json_fields(value, f"{path}.{key}")
                    fields.extend(nested_fields)
        
        elif isinstance(data, list) and data:
            # Process first item as representative
            nested_fields = self._extract_json_fields(data[0], f"{path}[0]")
            fields.extend(nested_fields)
        
        return fields
    
    def _extract_xml_fields(self, element: ET.Element) -> List[SchemaField]:
        """Recursively extract fields from XML element."""
        fields = []
        
        # Process attributes
        for attr_name, attr_value in element.attrib.items():
            field = SchemaField(
                name=attr_name,
                type='attribute',
                description=f"Attribute: {attr_value}"
            )
            fields.append(field)
        
        # Process child elements
        for child in element:
            child_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            field = SchemaField(
                name=child_name,
                type='element',
                description=f"Child element: {child.text[:50] if child.text else 'No content'}"
            )
            fields.append(field)
            
            # Recursively process nested elements
            nested_fields = self._extract_xml_fields(child)
            fields.extend(nested_fields)
        
        return fields
    
    def _structure_to_dict(self, structure: SchemaStructure) -> Dict[str, Any]:
        """Convert SchemaStructure to dictionary."""
        return {
            'name': structure.name,
            'type': structure.type,
            'description': structure.description,
            'namespace': structure.namespace,
            'fields': [
                {
                    'name': field.name,
                    'type': field.type,
                    'description': field.description,
                    'required': field.required,
                    'min_occurrences': field.min_occurrences,
                    'max_occurrences': field.max_occurrences
                }
                for field in structure.fields
            ]
        }
    
    def _generate_short_description(self, schema_info: Dict[str, Any]) -> str:
        """Generate a short functional description (1-2 sentences)."""
        file_type = schema_info.get('file_type', 'Unknown')
        structures = schema_info.get('structures', [])
        
        if not structures:
            return f"This {file_type} file does not contain any defined structures or is empty."
        
        # Extract key information for functional context
        main_structure = structures[0]
        structure_type = main_structure.get('type', 'Unknown')
        field_count = len(main_structure.get('fields', []))
        
        # Generate functional descriptions based on file type and structure
        if file_type == 'WSDL':
            if structure_type == 'service':
                return f"This web service provides business operations for system integration and data exchange between applications."
            elif structure_type == 'operation':
                return f"This web service operation enables data processing and communication between different business systems."
            else:
                return f"This web service definition enables system integration and data exchange between business applications."
                
        elif file_type == 'XSD':
            if field_count > 10:
                return f"This data schema defines comprehensive business information structures for system integration and data validation."
            else:
                return f"This data schema defines business information structures for data exchange and validation between systems."
                
        elif file_type == 'JSON Schema':
            return f"This data contract defines business information structure and validation rules for data exchange between applications."
            
        elif file_type == 'JSON':
            return f"This data structure contains business information for system integration and data processing workflows."
            
        elif file_type == 'XML':
            return f"This data structure contains business information for system integration and data exchange between applications."
            
        else:
            return f"This {file_type} file contains business data structures for system integration and information exchange."
    
    def _generate_detailed_description(self, schema_info: Dict[str, Any]) -> str:
        """Generate a detailed functional description (5-10 sentences) using AI if available."""
        file_type = schema_info.get('file_type', 'Unknown')
        structures = schema_info.get('structures', [])
        
        if not structures:
            return f"This {file_type} file does not contain any defined structures or is empty."
        
        # Build context for AI generation
        context = self._build_ai_context(schema_info)
        
        # Try AI generation if available
        if self.text_generator and len(context) < 1000:  # Model input limit
            try:
                ai_description = self._generate_ai_description(context, file_type)
                if ai_description:
                    return ai_description
            except Exception as e:
                self.logger.warning(f"AI generation failed: {e}")
        
        # Fallback to rule-based generation
        return self._generate_rule_based_description(schema_info)
    
    def _build_ai_context(self, schema_info: Dict[str, Any]) -> str:
        """Build context string for AI generation focusing on functional aspects."""
        file_type = schema_info.get('file_type', 'Unknown')
        structures = schema_info.get('structures', [])
        
        context_parts = [f"Integration artifact type: {file_type}"]
        
        for i, structure in enumerate(structures[:3]):  # Limit to first 3 structures
            context_parts.append(f"\nBusiness component {i+1}: {structure.get('name', 'Unknown')}")
            context_parts.append(f"Component type: {structure.get('type', 'Unknown')}")
            
            if structure.get('description'):
                context_parts.append(f"Purpose: {structure.get('description')}")
            
            fields = structure.get('fields', [])
            if fields:
                # Categorize fields by type for functional context
                field_types = {}
                for field in fields:
                    field_type = field.get('type', 'Unknown')
                    if field_type not in field_types:
                        field_types[field_type] = 0
                    field_types[field_type] += 1
                
                context_parts.append(f"Data categories: {', '.join([f'{count} {type_name}' for type_name, count in field_types.items()])}")
                
                # Identify if this is request/response/flow
                required_fields = [f for f in fields if f.get('required', False)]
                if required_fields:
                    context_parts.append(f"Required data elements: {len(required_fields)}")
                
                if len(fields) > 10:
                    context_parts.append(f"Total data elements: {len(fields)}")
        
        return "\n".join(context_parts)
    
    def _generate_ai_description(self, context: str, file_type: str) -> str:
        """Generate description using AI model with strict business focus."""
        try:
            prompt = f"""
            You are an expert AI assistant specialized in system integration documentation. 
            Analyze this {file_type} integration artifact and generate a detailed functional description.
            
            Context:
            {context}
            
            Generate a complete, detailed, and professional description (5-10 sentences) that:
            1. Describes the functional purpose of the integration
            2. Identifies which systems or domains are typically involved
            3. Describes the type of information exchanged (e.g., customer data, billing records, inventory updates)
            4. Highlights whether the operation is related to querying, creating, updating, or deleting data
            5. Mentions whether the artifact represents a request, a response, or a complete message flow
            6. Is generic enough to apply to various platforms (ETL, API Gateway, ESB)
            7. Uses business-friendly language, avoiding technical jargon
            8. Does not reference specific field names or technical identifiers
            9. Does not hallucinate information not clearly present in the input
            
            Focus strictly on functional understanding and business context.
            """
            
            # Use the text generator to create a summary
            result = self.text_generator(prompt, max_length=200, min_length=100, do_sample=False)
            return result[0]['summary_text']
            
        except Exception as e:
            self.logger.error(f"AI generation error: {e}")
            return ""
    
    def _generate_rule_based_description(self, schema_info: Dict[str, Any]) -> str:
        """Generate description using rule-based approach with strict business focus."""
        file_type = schema_info.get('file_type', 'Unknown')
        structures = schema_info.get('structures', [])
        
        description_parts = []
        
        # File type specific functional descriptions
        if file_type == 'WSDL':
            description_parts.append("This web service definition enables business system integration by providing standardized communication protocols and data exchange mechanisms.")
            description_parts.append("It facilitates interoperability between different business applications and systems, allowing them to exchange information and execute business processes.")
            description_parts.append("The service typically handles business operations such as data retrieval, processing, and synchronization across multiple enterprise systems.")
            description_parts.append("This integration artifact supports both request-response patterns and asynchronous messaging for complex business workflows.")
            description_parts.append("It enables organizations to connect legacy systems, modern applications, and external business partners through standardized interfaces.")
            
        elif file_type == 'XSD':
            description_parts.append("This data schema definition ensures consistent data structure and validation across business systems and applications.")
            description_parts.append("It provides a standardized format for business information exchange, ensuring data integrity and compatibility between different platforms.")
            description_parts.append("The schema supports business data validation, transformation, and mapping processes in enterprise integration scenarios.")
            description_parts.append("This artifact enables organizations to maintain data quality and consistency across multiple business systems and data sources.")
            description_parts.append("It facilitates data governance and compliance requirements by establishing clear data structure definitions.")
            
        elif file_type == 'JSON Schema':
            description_parts.append("This data contract defines business information structure and validation rules for modern application integration.")
            description_parts.append("It provides a standardized format for business data exchange, ensuring compatibility and data quality across different systems.")
            description_parts.append("The schema supports business process automation and data synchronization between web applications and services.")
            description_parts.append("This artifact enables organizations to establish clear data requirements and validation rules for business information exchange.")
            description_parts.append("It facilitates integration with modern web-based business applications and cloud services.")
            
        elif file_type == 'JSON':
            description_parts.append("This data structure contains business information formatted for efficient system integration and data exchange.")
            description_parts.append("It provides a lightweight format for transmitting business data between different applications and services.")
            description_parts.append("The structure supports real-time data exchange and processing in business integration scenarios.")
            description_parts.append("This artifact enables organizations to exchange business information quickly and efficiently across multiple systems.")
            description_parts.append("It facilitates integration with modern web applications and mobile business solutions.")
            
        elif file_type == 'XML':
            description_parts.append("This data structure contains business information in a standardized format for system integration and data exchange.")
            description_parts.append("It provides a structured format for transmitting business data between different applications and enterprise systems.")
            description_parts.append("The structure supports complex business data relationships and hierarchical information organization.")
            description_parts.append("This artifact enables organizations to exchange structured business information across multiple platforms and systems.")
            description_parts.append("It facilitates integration with enterprise systems and supports business process automation workflows.")
        
        # Add structure information without technical details
        if structures:
            main_structure = structures[0]
            field_count = len(main_structure.get('fields', []))
            
            if field_count > 0:
                description_parts.append(f"The integration artifact contains comprehensive business data elements to support various business operations and information exchange requirements.")
                
                # Determine operation type based on structure analysis
                required_fields = [f for f in main_structure.get('fields', []) if f.get('required', False)]
                if required_fields:
                    description_parts.append("The artifact includes essential business data elements that are required for successful integration and data processing.")
                
                if field_count > 20:
                    description_parts.append("This comprehensive data structure supports complex business scenarios with extensive information requirements.")
                elif field_count > 10:
                    description_parts.append("The data structure accommodates moderate complexity business operations with multiple data requirements.")
                else:
                    description_parts.append("The data structure supports focused business operations with streamlined information requirements.")
        
        # Add integration context
        description_parts.append("This integration artifact facilitates seamless data exchange and system interoperability in enterprise business environments.")
        description_parts.append("It supports business process automation, data synchronization, and information sharing across multiple business systems and platforms.")
        
        return " ".join(description_parts) 