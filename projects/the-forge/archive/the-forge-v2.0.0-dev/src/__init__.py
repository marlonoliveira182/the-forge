"""
The Forge v2 - Schema Conversion and Mapping Tool

A modular, object-oriented tool for converting between XSD and JSON Schema formats,
with Excel documentation generation and schema mapping capabilities.

This package provides:
- Schema processing and conversion
- Excel generation with formatting
- Path-based mapping between schemas
- GUI and CLI interfaces
- Comprehensive validation and error handling
"""

__version__ = "2.0.0"
__author__ = "The Forge Team"
__description__ = "Schema conversion and mapping tool with Excel documentation"

from .core.schema_processor import SchemaProcessor
from .core.excel_generator import ExcelGenerator
from .core.mapping_engine import MappingEngine
from .core.converter import SchemaConverter

__all__ = [
    'SchemaProcessor',
    'ExcelGenerator', 
    'MappingEngine',
    'SchemaConverter'
] 