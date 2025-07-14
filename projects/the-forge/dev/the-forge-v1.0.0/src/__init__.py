"""
The Forge - Schema Conversion and Mapping Tool

A comprehensive tool for converting between XSD and JSON Schema formats,
generating Excel documentation, and creating schema mappings.
"""

__version__ = "7.0.0"
__author__ = "EDP Team"
__description__ = "Schema conversion and mapping tool for XSD and JSON Schema"

from .core.schema_processor import SchemaProcessor
from .core.mapping_engine import MappingEngine
from .core.excel_generator import ExcelGenerator
from .core.converter import SchemaConverter
from .utils.path_utils import PathUtils
from .utils.validation import ValidationUtils

__all__ = [
    'SchemaProcessor',
    'MappingEngine', 
    'ExcelGenerator',
    'SchemaConverter',
    'PathUtils',
    'ValidationUtils'
] 