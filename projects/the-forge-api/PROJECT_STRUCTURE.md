# The Forge API - Project Structure

## Overview
This is the API version of The Forge v8 application, converted from a desktop GUI application to a web API service. The core functionality remains the same, but is now accessible via HTTP endpoints.

## Project Structure

```
the-forge-api/
├── main.py                 # FastAPI application entry point
├── forge_core.py           # Core business logic extracted from original app
├── requirements.txt        # Python dependencies
├── render.yaml            # Render deployment configuration
├── Dockerfile             # Docker container configuration
├── README.md              # Comprehensive API documentation
├── test_api.py            # Test script with sample data
├── start.py               # Local development startup script
├── .gitignore             # Git ignore rules
└── PROJECT_STRUCTURE.md   # This file
```

## Key Components

### 1. `main.py` - FastAPI Application
- **Purpose**: Main API server with all endpoints
- **Features**:
  - File upload handling
  - CORS middleware
  - Error handling
  - File response generation
  - Temporary file cleanup

### 2. `forge_core.py` - Business Logic
- **Purpose**: Contains all the core functionality from the original application
- **Key Functions**:
  - `extract_fields_from_json_schema()`: Parse JSON Schema files
  - `extract_fields_from_xsd()`: Parse XSD files
  - `map_paths()`: Create field mappings between schemas
  - `build_mapping_v2_style()`: Generate Excel mapping files
  - `run_schema_to_excel_operation()`: Convert schemas to Excel
  - `run_xsd_to_jsonschema_operation()`: Convert XSD to JSON Schema
  - `run_jsonschema_to_xsd_operation()`: Convert JSON Schema to XSD

### 3. API Endpoints

#### Schema Mapping (`/api/mapping`)
- **Input**: Source and target schema files
- **Output**: Excel file with field mappings
- **Parameters**: threshold, keep_case

#### Schema to Excel (`/api/schema-to-excel`)
- **Input**: Schema file (JSON/XSD)
- **Output**: Excel file with schema structure
- **Parameters**: keep_case

#### XSD to JSON Schema (`/api/xsd-to-jsonschema`)
- **Input**: XSD file
- **Output**: JSON Schema file
- **Parameters**: keep_case

#### JSON Schema to XSD (`/api/jsonschema-to-xsd`)
- **Input**: JSON Schema file
- **Output**: XSD file

### 4. Deployment Options

#### Render Deployment
- Uses `render.yaml` for configuration
- Automatic deployment from Git repository
- Free tier available

#### Docker Deployment
- Uses `Dockerfile` for containerization
- Can be deployed to any container platform
- Includes health checks

#### Local Development
- Use `start.py` for easy local development
- Includes test mode
- Auto-reload support

## File Format Support

### Input Formats
- **JSON Schema**: `.json` files
- **XSD**: `.xsd` and `.xml` files

### Output Formats
- **Excel**: `.xlsx` files with formatted data
- **JSON Schema**: `.json` files
- **XSD**: `.xsd` files

## Key Differences from Original

### Original Desktop App
- GUI-based interface using tkinter
- File dialogs for input/output
- Local file system operations
- Single-user desktop application

### API Version
- HTTP-based REST API
- File upload/download via HTTP
- Stateless operations
- Multi-user web service
- Containerized deployment
- Auto-generated API documentation

## Migration Benefits

1. **Accessibility**: Available from anywhere via web
2. **Scalability**: Can handle multiple concurrent users
3. **Integration**: Easy to integrate with other systems
4. **Documentation**: Auto-generated API docs
5. **Deployment**: Easy deployment to cloud platforms
6. **Testing**: Automated testing capabilities

## Security Considerations

- CORS enabled for cross-origin requests
- File upload validation
- Temporary file cleanup
- Error handling without exposing internals

## Performance Optimizations

- Async file operations
- Temporary file management
- Efficient memory usage
- Proper cleanup after operations

## Testing

The `test_api.py` script provides:
- Sample schema files generation
- Endpoint testing
- File download verification
- Error handling validation

## Next Steps

1. **Deploy to Render**: Use the provided configuration
2. **Test the API**: Use the test script
3. **Integrate with frontend**: Create web UI if needed
4. **Monitor usage**: Add logging and monitoring
5. **Scale as needed**: Upgrade Render plan if required 