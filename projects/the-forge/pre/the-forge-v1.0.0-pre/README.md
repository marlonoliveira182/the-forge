# The Forge v1.0.0

A comprehensive schema conversion and mapping tool for XSD and JSON Schema formats, designed with scalability, decoupling, and best practices in mind.

> **Versioning:** This project follows [Semantic Versioning (SemVer)](https://semver.org/): MAJOR.MINOR.PATCH (e.g., 1.0.0, 1.1.0, 2.0.0).

> **Environment Structure:** This is the **Production (PRD)** version. Development versions are in `/dev/` and pre-production versions are in `/pre/`.

## Features

- **Schema Conversion**: Convert between XSD and JSON Schema formats
- **Excel Generation**: Generate detailed Excel documentation from schemas
- **Schema Mapping**: Create mappings between different schema formats
- **Validation**: Comprehensive validation of schemas and outputs
- **CLI Interface**: Command-line interface for automation
- **GUI Interface**: User-friendly graphical interface
- **Comprehensive Testing**: Full test suite with automated validation

## Architecture

The project follows a modular, decoupled architecture:

```
src/
├── core/           # Core business logic
│   ├── schema_processor.py    # Schema parsing and processing
│   ├── mapping_engine.py      # Field mapping and similarity
│   ├── excel_generator.py     # Excel file generation
│   └── converter.py           # Schema format conversion
├── utils/          # Utility modules
│   ├── path_utils.py         # Path handling utilities
│   ├── validation.py         # Validation utilities
│   ├── normalization.py      # Field normalization
│   └── excel_utils.py        # Excel-specific utilities
├── cli/            # Command-line interface
└── gui/            # Graphical user interface
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Installation Options

1. **Install from source:**
```bash
git clone <repository-url>
cd the-forge-v1.0.0
pip install -e .
```

2. **Install with development dependencies:**
```bash
pip install -e .[dev]
```

3. **Install with GUI support:**
```bash
pip install -e .[gui]
```

## Usage

### Command Line Interface

The Forge provides a comprehensive CLI for all operations:

#### Convert XSD to JSON Schema
```bash
python -m src.cli.main xsd-to-json input.xsd output.json
```

#### Convert JSON Schema to XSD
```bash
python -m src.cli.main json-to-xsd input.json output.xsd
```

#### Generate Excel from Schema
```bash
python -m src.cli.main schema-to-excel input.xsd output.xlsx
```

#### Create Schema Mapping
```bash
python -m src.cli.main mapping source.xsd target.json output.xlsx --threshold 0.7
```

#### Validate Schema
```bash
python -m src.cli.main validate input.xsd
```

### Programmatic Usage

```python
from src.core.schema_processor import SchemaProcessor
from src.core.mapping_engine import MappingEngine
from src.core.excel_generator import ExcelGenerator
from src.core.converter import SchemaConverter

# Process schemas
processor = SchemaProcessor()
fields = processor.extract_fields_from_xsd("input.xsd")

# Create mappings
engine = MappingEngine(threshold=0.7)
mapping = engine.map_fields(source_fields, target_fields)

# Generate Excel
generator = ExcelGenerator()
generator.create_schema_excel(fields, "output.xlsx")

# Convert schemas
converter = SchemaConverter()
converter.xsd_to_json_schema("input.xsd", "output.json")
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with verbose output
pytest -v
```

### Test Structure

```
tests/
├── conftest.py           # Pytest configuration and fixtures
├── unit/                 # Unit tests
│   ├── test_schema_processor.py
│   ├── test_mapping_engine.py
│   ├── test_excel_generator.py
│   └── test_converter.py
├── integration/          # Integration tests
│   ├── test_end_to_end.py
│   └── test_cli.py
└── fixtures/            # Test data and fixtures
    ├── sample_schemas/
    └── expected_outputs/
```

## Development

### Code Quality

The project uses several tools to maintain code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing

### Development Setup

```bash
# Install development dependencies
pip install -e .[dev]

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Run tests
pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Configuration

### Environment Variables

- `THE_FORGE_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `THE_FORGE_OUTPUT_DIR`: Default output directory
- `THE_FORGE_TEMP_DIR`: Temporary directory for processing

### Configuration File

Create a `config.json` file in the project root:

```json
{
  "default_threshold": 0.7,
  "max_levels": 10,
  "output_format": "xlsx",
  "logging": {
    "level": "INFO",
    "file": "the-forge.log"
  }
}
```

## API Reference

### Core Modules

#### SchemaProcessor

Main class for processing schemas:

```python
processor = SchemaProcessor()

# Extract fields from XSD
fields = processor.extract_fields_from_xsd("input.xsd")

# Extract fields from JSON Schema
fields = processor.extract_fields_from_json_schema("input.json")

# Extract simple paths
paths = processor.extract_paths_from_xsd("input.xsd")
```

#### MappingEngine

Handles field mapping and similarity calculations:

```python
engine = MappingEngine(threshold=0.7)

# Map fields between schemas
mapping = engine.map_fields(source_fields, target_fields)

# Validate mapping results
validation = engine.validate_mapping(mapping)

# Get unmapped fields
unmapped = engine.get_unmapped_fields(mapping, source_fields, target_fields)
```

#### ExcelGenerator

Generates formatted Excel files:

```python
generator = ExcelGenerator()

# Create schema Excel
generator.create_schema_excel(fields, "output.xlsx")

# Create mapping Excel
generator.create_mapping_excel(source_fields, target_fields, mapping, "output.xlsx")

# Create simple mapping Excel
generator.create_simple_mapping_excel(mapping, "output.xlsx")
```

#### SchemaConverter

Converts between schema formats:

```python
converter = SchemaConverter()

# XSD to JSON Schema
converter.xsd_to_json_schema("input.xsd", "output.json")

# JSON Schema to XSD
converter.json_schema_to_xsd("input.json", "output.xsd")
```

### Utility Modules

#### PathUtils

Path handling utilities:

```python
# Validate file paths
is_valid, error = PathUtils.validate_file_path("input.xsd", [".xsd"])

# Validate directories
is_valid, error = PathUtils.validate_directory_path("output/")

# Generate output filenames
filename = PathUtils.generate_output_filename("input.xsd", "schema-to-excel")
```

#### ValidationUtils

Validation utilities:

```python
# Validate JSON Schema
is_valid, error = ValidationUtils.validate_json_schema("input.json")

# Validate XSD
is_valid, error = ValidationUtils.validate_xsd_schema("input.xsd")

# Validate Excel file
is_valid, error = ValidationUtils.validate_excel_file("output.xlsx")

# Compare schema structures
comparison = ValidationUtils.compare_schema_structures(fields1, fields2)
```

## Performance

### Optimization Features

- **Lazy Loading**: Schemas are processed on-demand
- **Caching**: Repeated operations are cached
- **Memory Management**: Large files are processed in chunks
- **Parallel Processing**: Multiple operations can run concurrently

### Benchmarks

Typical performance metrics:

- **XSD Processing**: ~1000 fields/second
- **JSON Schema Processing**: ~1500 fields/second
- **Mapping Generation**: ~500 mappings/second
- **Excel Generation**: ~2000 rows/second

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **File Permission Errors**: Check file and directory permissions
3. **Memory Issues**: Use smaller files or increase system memory
4. **Excel Generation Errors**: Ensure output directory is writable

### Debug Mode

Enable debug logging:

```bash
export THE_FORGE_LOG_LEVEL=DEBUG
python -m src.cli.main validate input.xsd
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue on GitHub
- Check the documentation
- Review the test examples

## Changelog

### v7.0.0

- Complete refactoring with modular architecture
- Comprehensive test suite
- CLI interface
- Enhanced validation
- Performance optimizations
- Better error handling
- Documentation improvements 