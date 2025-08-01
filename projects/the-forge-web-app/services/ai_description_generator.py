import json
import xml.etree.ElementTree as ET
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
import time
import os

# Free AI libraries for text generation
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
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
    
    def __init__(self, enable_ai: bool = False):
        self.logger = logging.getLogger(__name__)
        self.text_generator = None
        self.tokenizer = None
        self.model = None
        self._ai_initialized = False
        self.enable_ai = enable_ai
        
        # Don't initialize AI models immediately - use lazy loading
        if enable_ai:
            self.logger.info("AIDescriptionGenerator initialized with AI enabled (models will be loaded on first use)")
        else:
            self.logger.info("AIDescriptionGenerator initialized with AI disabled (using rule-based generation only)")
    
    def _initialize_ai_models(self):
        """Initialize AI models for text generation with robust error handling and fallbacks."""
        if self._ai_initialized:
            return
            
        if not TRANSFORMERS_AVAILABLE:
            self.logger.warning("Transformers library not available, using rule-based generation only")
            self.enable_ai = False
            return
            
        try:
            start_time = time.time()
            self.logger.info("Initializing AI models with robust fallback strategy...")
            
            # Set up cache directory to avoid repeated downloads
            cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
            os.makedirs(cache_dir, exist_ok=True)
            
            # Try models in order of reliability and size
            models_to_try = [
                ("distilgpt2", "text-generation"),  # Smaller, more reliable
                ("gpt2", "text-generation"),        # Standard GPT-2
                ("microsoft/DialoGPT-small", "text-generation"),  # Alternative
                ("facebook/bart-base", "text2text-generation")    # Fallback
            ]
            
            for model_name, pipeline_type in models_to_try:
                try:
                    self.logger.info(f"Attempting to load {model_name}...")
                    
                    # Use local_files_only=False to allow download, but with better error handling
                    if pipeline_type == "text-generation":
                        self.tokenizer = AutoTokenizer.from_pretrained(
                            model_name, 
                            cache_dir=cache_dir,
                            local_files_only=False,
                            use_fast=True
                        )
                        self.model = AutoModelForCausalLM.from_pretrained(
                            model_name, 
                            cache_dir=cache_dir,
                            local_files_only=False,
                            torch_dtype=torch.float32  # Use float32 for better compatibility
                        )
                        self.text_generator = pipeline(
                            "text-generation", 
                            model=self.model, 
                            tokenizer=self.tokenizer,
                            device=-1  # Force CPU to avoid GPU issues
                        )
                    else:  # text2text-generation
                        self.tokenizer = AutoTokenizer.from_pretrained(
                            model_name, 
                            cache_dir=cache_dir,
                            local_files_only=False,
                            use_fast=True
                        )
                        self.model = AutoModelForSeq2SeqLM.from_pretrained(
                            model_name, 
                            cache_dir=cache_dir,
                            local_files_only=False,
                            torch_dtype=torch.float32
                        )
                        self.text_generator = pipeline(
                            "text2text-generation", 
                            model=self.model, 
                            tokenizer=self.tokenizer,
                            device=-1
                        )
                    
                    self.logger.info(f"Successfully loaded {model_name}")
                    break
                    
                except Exception as e:
                    self.logger.warning(f"Failed to load {model_name}: {e}")
                    # Clear any partial initialization
                    self.tokenizer = None
                    self.model = None
                    self.text_generator = None
                    continue
            
            if not self.text_generator:
                self.logger.error("All AI models failed to load, falling back to rule-based generation")
                self.enable_ai = False
                return
            
            init_time = time.time() - start_time
            self.logger.info(f"AI models initialized successfully in {init_time:.2f}s")
            self._ai_initialized = True
            
        except Exception as e:
            self.logger.error(f"Critical error during AI initialization: {e}")
            self.enable_ai = False
            self._ai_initialized = True  # Mark as initialized to prevent retries
    
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
            start_time = time.time()
            
            # Parse the schema file
            parse_start = time.time()
            schema_info = self._parse_schema_file(file_path, file_type)
            parse_time = time.time() - parse_start
            self.logger.info(f"Schema parsing completed in {parse_time:.3f}s")
            
            # Generate descriptions
            gen_start = time.time()
            short_desc = self._generate_short_description(schema_info)
            detailed_desc = self._generate_detailed_description(schema_info)
            gen_time = time.time() - gen_start
            self.logger.info(f"Description generation completed in {gen_time:.3f}s")
            
            total_time = time.time() - start_time
            self.logger.info(f"Total generation time: {total_time:.3f}s")
            
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
        # Normalize file type for case-insensitive matching
        normalized_type = file_type.lower().replace(' ', '_')
        
        if normalized_type == 'xsd':
            return self._parse_xsd_file(file_path)
        elif normalized_type == 'json':
            return self._parse_json_file(file_path)
        elif normalized_type in ['json_schema', 'jsonschema']:
            return self._parse_json_schema_file(file_path)
        elif normalized_type == 'json_example':
            return self._parse_json_example_file(file_path)
        elif normalized_type == 'wsdl':
            return self._parse_wsdl_file(file_path)
        elif normalized_type == 'xml':
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
    
    def _parse_json_example_file(self, file_path: str) -> Dict[str, Any]:
        """Parse JSON example file and extract structure information."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            structures = []
            
            # Extract structure from JSON example
            fields = self._extract_json_structure_fields(data, 'root')
            
            structure = SchemaStructure(
                name='JSON Example Structure',
                type='json_example',
                fields=fields,
                description='Structure extracted from JSON example'
            )
            structures.append(structure)
            
            return {
                'file_type': 'JSON Example',
                'structures': [self._structure_to_dict(s) for s in structures],
                'total_structures': len(structures),
                'example_info': {
                    'data_type': type(data).__name__,
                    'is_array': isinstance(data, list),
                    'is_object': isinstance(data, dict)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing JSON example file: {e}")
            raise
    
    def _extract_json_structure_fields(self, data: Any, path: str) -> List[SchemaField]:
        """Extract structure fields from JSON data, avoiding repetition of array fields."""
        fields = []
        processed_arrays = set()
        
        def extract_fields_recursive(data_part: Any, current_path: str, level: int = 0):
            if level > 10:  # Prevent infinite recursion
                return
            
            if isinstance(data_part, dict):
                for key, value in data_part.items():
                    field_path = f"{current_path}.{key}" if current_path else key
                    field_type = self._determine_field_type(value)
                    
                    field = SchemaField(
                        name=key,
                        type=field_type,
                        description=f"Field from JSON example at path: {field_path}",
                        required=True  # Assume required in examples
                    )
                    fields.append(field)
                    
                    # Recursively process nested objects
                    if isinstance(value, (dict, list)):
                        extract_fields_recursive(value, field_path, level + 1)
            
            elif isinstance(data_part, list) and data_part:
                # Check if we've already processed this array structure
                array_key = f"{current_path}:{len(data_part)}"
                if array_key not in processed_arrays:
                    processed_arrays.add(array_key)
                    
                    # Process first item as representative
                    first_item = data_part[0]
                    extract_fields_recursive(first_item, f"{current_path}[0]", level + 1)
                    
                    # Check if all items have uniform structure
                    uniform_structure = all(
                        self._compare_json_structures(first_item, item) 
                        for item in data_part[1:]
                    )
                    
                    if not uniform_structure:
                        # Process additional unique structures
                        for i, item in enumerate(data_part[1:], 1):
                            if not self._compare_json_structures(first_item, item):
                                extract_fields_recursive(item, f"{current_path}[{i}]", level + 1)
        
        extract_fields_recursive(data, path)
        return fields
    
    def _determine_field_type(self, value: Any) -> str:
        """Determine the JSON schema type from a value."""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'number'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, list):
            return 'array'
        elif isinstance(value, dict):
            return 'object'
        else:
            return 'string'
    
    def _compare_json_structures(self, obj1: Any, obj2: Any) -> bool:
        """Compare if two JSON objects have the same structure."""
        if type(obj1) != type(obj2):
            return False
        
        if isinstance(obj1, dict):
            if set(obj1.keys()) != set(obj2.keys()):
                return False
            return all(self._compare_json_structures(obj1[k], obj2[k]) for k in obj1.keys())
        
        elif isinstance(obj1, list):
            if len(obj1) != len(obj2):
                return False
            return all(self._compare_json_structures(obj1[i], obj2[i]) for i in range(len(obj1)))
        
        else:
            return True
    
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
            
        elif file_type == 'JSON Example':
            return f"This JSON example demonstrates business data structure for system integration and schema generation."
            
        elif file_type == 'XML':
            return f"This data structure contains business information for system integration and data exchange between applications."
            
        else:
            return f"This {file_type} file contains business data structures for system integration and information exchange."
    
    def _generate_detailed_description(self, schema_info: Dict[str, Any]) -> str:
        """Generate a detailed functional description (5-10 sentences) using improved rule-based approach with optional AI enhancement."""
        file_type = schema_info.get('file_type', 'Unknown')
        structures = schema_info.get('structures', [])
        
        if not structures:
            return f"This {file_type} file does not contain any defined structures or is empty."
        
        # Always start with improved rule-based generation
        base_description = self._generate_improved_rule_based_description(schema_info)
        
        # Optionally enhance with AI if enabled and working well
        if self.enable_ai:
            try:
                # Try to enhance the description with AI
                enhanced_description = self._enhance_with_ai(base_description, file_type)
                if enhanced_description and len(enhanced_description) > len(base_description):
                    return enhanced_description
            except Exception as e:
                self.logger.warning(f"AI enhancement failed: {e}, using base description")
        
        return base_description
    
    def _generate_improved_rule_based_description(self, schema_info: Dict[str, Any]) -> str:
        """Generate improved rule-based description that's more dynamic and context-aware."""
        file_type = schema_info.get('file_type', 'Unknown')
        structures = schema_info.get('structures', [])
        
        description_parts = []
        
        # Analyze the structures to determine the type of integration
        field_types = {}
        total_fields = 0
        required_fields = 0
        
        for structure in structures:
            fields = structure.get('fields', [])
            for field in fields:
                field_type = field.get('type', 'Unknown')
                if field_type not in field_types:
                    field_types[field_type] = 0
                field_types[field_type] += 1
                total_fields += 1
                if field.get('required', False):
                    required_fields += 1
        
        # Determine the primary data types and integration purpose
        primary_types = sorted(field_types.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # File type specific functional descriptions with context awareness
        if file_type == 'WSDL':
            description_parts.append("This web service definition enables business system integration by providing standardized communication protocols and data exchange mechanisms.")
            description_parts.append("It facilitates interoperability between different business applications and systems, allowing them to exchange information and execute business processes.")
            
            if total_fields > 10:
                description_parts.append("The service handles complex business operations with comprehensive data structures supporting multiple business entities and relationships.")
            else:
                description_parts.append("The service handles focused business operations with streamlined data requirements for efficient processing.")
            
            description_parts.append("This integration artifact supports both request-response patterns and asynchronous messaging for complex business workflows.")
            description_parts.append("It enables organizations to connect legacy systems, modern applications, and external business partners through standardized interfaces.")
            
        elif file_type == 'XSD':
            description_parts.append("This data schema definition ensures consistent data structure and validation across business systems and applications.")
            description_parts.append("It provides a standardized format for business information exchange, ensuring data integrity and compatibility between different platforms.")
            
            if 'string' in [t[0].lower() for t in primary_types]:
                description_parts.append("The schema primarily handles textual business data including customer information, product details, and operational records.")
            elif 'date' in [t[0].lower() for t in primary_types]:
                description_parts.append("The schema manages temporal business data including transaction dates, scheduling information, and historical records.")
            elif 'decimal' in [t[0].lower() for t in primary_types] or 'integer' in [t[0].lower() for t in primary_types]:
                description_parts.append("The schema handles numerical business data including financial transactions, quantities, and performance metrics.")
            else:
                description_parts.append("The schema supports diverse business data types for comprehensive information management.")
            
            description_parts.append("This artifact enables organizations to maintain data quality and consistency across multiple business systems and data sources.")
            description_parts.append("It facilitates data governance and compliance requirements by establishing clear data structure definitions.")
            
        elif file_type == 'JSON Schema':
            description_parts.append("This JSON schema definition provides flexible data validation and structure for modern web-based business integrations.")
            description_parts.append("It supports lightweight, efficient data exchange between web applications, mobile systems, and cloud-based services.")
            
            if total_fields > 15:
                description_parts.append("The schema accommodates complex business data models with extensive field definitions for comprehensive data management.")
            else:
                description_parts.append("The schema provides streamlined data structures optimized for fast processing and minimal overhead.")
            
            description_parts.append("This integration artifact enables real-time data synchronization and API-based business process automation.")
            description_parts.append("It supports modern integration patterns including REST APIs, microservices, and cloud-native applications.")
            
        elif file_type == 'JSON':
            description_parts.append("This JSON data structure facilitates lightweight and efficient business data exchange between modern applications and systems.")
            description_parts.append("It provides a flexible format for transmitting business information across web services, mobile applications, and cloud platforms.")
            
            if required_fields > total_fields * 0.7:
                description_parts.append("The data structure emphasizes data integrity with a high proportion of required fields for reliable business operations.")
            else:
                description_parts.append("The data structure offers flexibility with optional fields to accommodate varying business requirements and scenarios.")
            
            description_parts.append("This integration artifact supports real-time data processing and dynamic business workflow management.")
            description_parts.append("It enables seamless integration between web-based systems, mobile applications, and cloud services.")
            
        elif file_type == 'JSON Example':
            description_parts.append("This JSON example demonstrates business data structure patterns for automated schema generation and system integration.")
            description_parts.append("It provides concrete data instances that can be used to infer schema definitions and validation rules.")
            
            example_info = schema_info.get('example_info', {})
            if example_info.get('is_array'):
                description_parts.append("The example contains array data structures that enable batch processing and collection management.")
            elif example_info.get('is_object'):
                description_parts.append("The example contains object data structures that support complex business entity modeling.")
            
            description_parts.append("This integration artifact enables automated schema generation from real-world data examples.")
            description_parts.append("It facilitates rapid prototyping and schema evolution based on actual data patterns.")
            
        elif file_type == 'XML':
            description_parts.append("This XML data structure provides structured business information exchange with comprehensive metadata and validation capabilities.")
            description_parts.append("It supports complex business data hierarchies and relationships through extensible markup language features.")
            
            if total_fields > 20:
                description_parts.append("The data structure accommodates complex business scenarios with extensive field definitions and nested relationships.")
            else:
                description_parts.append("The data structure provides focused business data exchange with streamlined field definitions.")
            
            description_parts.append("This integration artifact enables robust data validation and transformation in enterprise business environments.")
            description_parts.append("It supports legacy system integration and enterprise service bus implementations for comprehensive business process management.")
            
        else:
            description_parts.append(f"This {file_type} file provides business data structure definitions for system integration and information exchange.")
            description_parts.append("It enables standardized data formats and validation rules for consistent business information processing.")
            description_parts.append("The integration artifact supports data transformation, mapping, and synchronization across multiple business systems.")
            description_parts.append("It facilitates business process automation and data governance requirements in enterprise environments.")
            description_parts.append("This artifact enables organizations to maintain data quality and consistency across diverse business applications and platforms.")
        
        return " ".join(description_parts)
    
    def _enhance_with_ai(self, base_description: str, file_type: str) -> str:
        """Attempt to enhance the base description with AI, but only if it produces good results."""
        if not self._ai_initialized:
            self._initialize_ai_models()
        
        if not self.text_generator:
            self.logger.info("No AI model available, using base description")
            return base_description
        
        try:
            # Use a very simple enhancement prompt that works well with generative models
            enhancement_prompt = f"Rewrite this business description to be more engaging and professional: {base_description}"
            
            # Check pipeline type more reliably
            pipeline_type = type(self.text_generator).__name__
            self.logger.info(f"Using pipeline type: {pipeline_type}")
            
            if "TextGenerationPipeline" in pipeline_type:
                # For text-generation models (GPT-2, DialoGPT)
                result = self.text_generator(
                    enhancement_prompt, 
                    max_length=200, 
                    min_length=100, 
                    do_sample=True, 
                    temperature=0.7, 
                    truncation=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                generated_text = result[0]['generated_text']
                # Extract only the new content after the prompt
                enhanced = generated_text[len(enhancement_prompt):].strip()
                
            elif "Text2TextGenerationPipeline" in pipeline_type:
                # For text2text-generation models (BART)
                result = self.text_generator(
                    enhancement_prompt, 
                    max_length=200, 
                    min_length=100, 
                    do_sample=True, 
                    temperature=0.7
                )
                enhanced = result[0]['generated_text']
            else:
                self.logger.warning(f"Unknown pipeline type: {pipeline_type}, using base description")
                return base_description
            
            # Validate the enhanced text
            if not enhanced or len(enhanced.strip()) < 50:
                self.logger.info("AI enhancement produced insufficient content, using base description")
                return base_description
            
            # Check if the enhancement is actually better
            if len(enhanced) > len(base_description) * 0.8 and len(enhanced) < len(base_description) * 2:
                self.logger.info("AI enhancement successful")
                return enhanced
            else:
                self.logger.info("AI enhancement not significantly better, using base description")
                return base_description
                
        except Exception as e:
            self.logger.warning(f"AI enhancement failed: {e}")
            return base_description