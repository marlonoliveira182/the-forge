# The Forge API

A FastAPI-based REST API for schema transformation and mapping operations, adapted from The Forge v8 desktop application.

## Features

- **XSD Schema Parsing**: Parse XML Schema Definition files and extract structured data
- **JSON Schema Parsing**: Parse JSON Schema files and convert to flat structure
- **WSDL to XSD Extraction**: Extract XSD schemas from WSDL files
- **Excel Generation**: Create Excel files with schema structure and mapping data
- **Field Mapping**: Create mappings between source and target schemas with similarity scoring
- **Schema Conversion**: Convert between XSD and JSON Schema formats

## API Endpoints

### Health Check
- `GET /api/health` - Check API health and service status

### Schema Operations
- `POST /api/schema-to-excel` - Convert schema files to Excel format
- `POST /api/xsd-to-jsonschema` - Convert XSD to JSON Schema
- `POST /api/jsonschema-to-xsd` - Convert JSON Schema to XSD
- `POST /api/wsdl-to-xsd` - Extract XSD from WSDL files

### Mapping Operations
- `POST /api/mapping` - Create field mapping between source and target schemas

## Installation & Deployment

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd the-forge-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Test the API**
   ```bash
   python test_api.py
   ```

### Render Deployment

The API is configured for deployment on Render with the following specifications:

- **Python Version**: 3.11.18 (specified in `runtime.txt` and `render.yaml`)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### Deployment Files:
- `render.yaml` - Render service configuration
- `runtime.txt` - Python version specification
- `Dockerfile` - Alternative container deployment
- `requirements.txt` - Python dependencies

#### Environment Variables:
- `PYTHON_VERSION`: 3.11.18
- `PYTHONPATH`: /opt/render/project/src

## Usage Examples

### Convert XSD to Excel

```bash
curl -X POST "http://localhost:8000/api/schema-to-excel" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "schema_file=@your_schema.xsd" \
  -F "keep_case=false"
```

### Extract XSD from WSDL

```bash
curl -X POST "http://localhost:8000/api/wsdl-to-xsd" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "wsdl_file=@your_service.wsdl"
```

### Create Field Mapping

```bash
curl -X POST "http://localhost:8000/api/mapping" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "source_file=@source_schema.xsd" \
  -F "target_file=@target_schema.json" \
  -F "threshold=0.7" \
  -F "keep_case=false"
```

## Architecture

The API is built with a modular service architecture:

### Core Services

- **XSDParser**: Parses XSD files and extracts structured data
- **JSONSchemaParser**: Parses JSON Schema files using flattening approach
- **ExcelGenerator**: Creates Excel files with schema structure
- **WSDLExtractor**: Extracts XSD schemas from WSDL files
- **MappingService**: Creates field mappings with similarity scoring

### Data Flow

1. **File Upload**: Clients upload schema files via multipart form data
2. **Parsing**: Services parse the uploaded files into structured data
3. **Processing**: Business logic processes the data according to endpoint requirements
4. **Output Generation**: Results are generated as Excel files or JSON responses
5. **File Download**: Processed files are returned to the client

## Testing

### Run Tests Locally

```bash
# Test all endpoints
python test_api.py

# Test deployment compatibility
python test_deployment.py
```

### Test Files

- `test_api.py` - Comprehensive API endpoint testing
- `test_deployment.py` - Deployment compatibility verification

## Troubleshooting

### Common Deployment Issues

#### 1. Python Version Compatibility
**Issue**: Python 3.13 compatibility problems with older packages
**Solution**: Using Python 3.11.18 as specified in `runtime.txt` and `render.yaml`

#### 2. Package Dependencies
**Issue**: pandas compilation failures on Python 3.13
**Solution**: Removed pandas dependency (not needed for core functionality)

#### 3. Build Timeouts
**Issue**: Large packages taking too long to build
**Solution**: Using pre-compiled packages and minimal dependencies

### Local Development Issues

#### Import Errors
```bash
# Verify all imports work
python test_deployment.py
```

#### Port Conflicts
```bash
# Use different port
uvicorn main:app --host 0.0.0.0 --port 8001
```

## File Structure

```
the-forge-api/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── render.yaml            # Render deployment config
├── runtime.txt            # Python version specification
├── Dockerfile             # Container configuration
├── test_api.py            # API testing script
├── test_deployment.py     # Deployment testing
├── README.md              # Documentation
├── .gitignore             # Git ignore rules
└── services/              # Core service modules
    ├── __init__.py
    ├── xsd_parser.py      # XSD parsing service
    ├── json_schema_parser.py  # JSON Schema parsing
    ├── excel_generator.py     # Excel file generation
    ├── wsdl_extractor.py      # WSDL to XSD extraction
    └── mapping_service.py     # Field mapping service
```

## Dependencies

### Core Dependencies
- `fastapi==0.104.1` - Web framework
- `uvicorn==0.24.0` - ASGI server
- `openpyxl==3.1.2` - Excel file handling
- `jsonschema==4.17.3` - JSON Schema validation
- `python-multipart==0.0.6` - File upload handling
- `pydantic==2.5.0` - Data validation
- `lxml==4.9.3` - XML processing

### System Dependencies
- Python 3.11.18
- GCC compiler (for lxml compilation)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of The Forge ecosystem and follows the same licensing terms.

## Support

For deployment issues or API questions, please check:
1. The troubleshooting section above
2. Render deployment logs
3. Local testing with `test_deployment.py` 