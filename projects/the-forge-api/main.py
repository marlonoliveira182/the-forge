from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import shutil
import json
from typing import List, Optional
import uvicorn
from pathlib import Path

# Import services
from services.xsd_parser import XSDParser
from services.json_schema_parser import JSONSchemaParser
from services.excel_generator import ExcelGenerator
from services.wsdl_extractor import WSDLExtractor
from services.mapping_service import MappingService

app = FastAPI(
    title="The Forge API",
    description="API for schema transformation and mapping operations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create temporary directory for file operations
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

# Initialize services
xsd_parser = XSDParser()
json_parser = JSONSchemaParser()
excel_generator = ExcelGenerator()
wsdl_extractor = WSDLExtractor()
mapping_service = MappingService()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "The Forge API v1.0.0",
        "endpoints": {
            "POST /api/mapping": "Create field mapping between schemas",
            "POST /api/schema-to-excel": "Convert schema to Excel format",
            "POST /api/xsd-to-jsonschema": "Convert XSD to JSON Schema",
            "POST /api/jsonschema-to-xsd": "Convert JSON Schema to XSD",
            "POST /api/wsdl-to-xsd": "Extract XSD from WSDL"
        }
    }

@app.post("/api/mapping")
async def create_mapping(
    source_file: UploadFile = File(...),
    target_file: UploadFile = File(...),
    threshold: float = Form(0.7),
    keep_case: bool = Form(False)
):
    """
    Create field mapping between source and target schemas
    """
    try:
        # Save uploaded files
        source_path = TEMP_DIR / f"source_{source_file.filename}"
        target_path = TEMP_DIR / f"target_{target_file.filename}"
        
        with open(source_path, "wb") as buffer:
            shutil.copyfileobj(source_file.file, buffer)
        
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(target_file.file, buffer)
        
        # Determine file types and extract fields
        source_ext = source_path.suffix.lower()
        target_ext = target_path.suffix.lower()
        
        source_fields = []
        target_fields = []
        
        # Parse source file
        if source_ext == '.json':
            source_fields = json_parser.parse_json_schema_file(str(source_path))
        elif source_ext in ['.xsd', '.xml']:
            source_fields = xsd_parser.parse_xsd_file(str(source_path))
        else:
            raise HTTPException(status_code=400, detail="Unsupported source file format")
        
        # Parse target file
        if target_ext == '.json':
            target_fields = json_parser.parse_json_schema_file(str(target_path))
        elif target_ext in ['.xsd', '.xml']:
            target_fields = xsd_parser.parse_xsd_file(str(target_path))
        else:
            raise HTTPException(status_code=400, detail="Unsupported target file format")
        
        # Create mapping
        mapping = mapping_service.create_field_mapping(source_fields, target_fields, threshold)
        
        # Generate output file
        output_dir = TEMP_DIR / "mapping_output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"mapping_{source_path.stem}_to_{target_path.stem}.xlsx"
        
        excel_generator.create_mapping_excel(source_fields, target_fields, mapping, str(output_path))
        
        # Clean up input files
        source_path.unlink(missing_ok=True)
        target_path.unlink(missing_ok=True)
        
        return FileResponse(
            path=str(output_path),
            filename=f"mapping_{source_file.filename.split('.')[0]}_to_{target_file.filename.split('.')[0]}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

@app.post("/api/schema-to-excel")
async def schema_to_excel(
    schema_file: UploadFile = File(...),
    keep_case: bool = Form(False)
):
    """
    Convert schema to Excel format
    """
    try:
        # Save uploaded file
        schema_path = TEMP_DIR / f"schema_{schema_file.filename}"
        
        with open(schema_path, "wb") as buffer:
            shutil.copyfileobj(schema_file.file, buffer)
        
        # Parse schema based on file type
        schema_ext = schema_path.suffix.lower()
        fields = []
        
        if schema_ext == '.json':
            fields = json_parser.parse_json_schema_file(str(schema_path))
        elif schema_ext in ['.xsd', '.xml']:
            fields = xsd_parser.parse_xsd_file(str(schema_path))
        else:
            raise HTTPException(status_code=400, detail="Unsupported schema file format")
        
        # Create data dictionary for Excel export (matching v8 format)
        schema_name = schema_path.stem
        data_dict = {schema_name: fields}
        
        # Generate Excel file
        output_dir = TEMP_DIR / "excel_output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"schema_{schema_path.stem}.xlsx"
        
        excel_generator.export(data_dict, str(output_path))
        
        # Clean up input file
        schema_path.unlink(missing_ok=True)
        
        return FileResponse(
            path=str(output_path),
            filename=f"schema_{schema_file.filename.split('.')[0]}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing schema: {str(e)}")

@app.post("/api/xsd-to-jsonschema")
async def xsd_to_jsonschema(
    xsd_file: UploadFile = File(...),
    keep_case: bool = Form(False)
):
    """
    Convert XSD to JSON Schema
    """
    try:
        # Save uploaded file
        xsd_path = TEMP_DIR / f"xsd_{xsd_file.filename}"
        
        with open(xsd_path, "wb") as buffer:
            shutil.copyfileobj(xsd_file.file, buffer)
        
        # Parse XSD
        fields = xsd_parser.parse_xsd_file(str(xsd_path))
        
        # Convert to JSON Schema format
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {}
        }
        
        # Convert fields to JSON Schema properties
        for field in fields:
            _add_field_to_json_schema(field, json_schema["properties"])
        
        # Generate output file
        output_dir = TEMP_DIR / "jsonschema_output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"schema_{xsd_path.stem}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_schema, f, indent=2, ensure_ascii=False)
        
        # Clean up input file
        xsd_path.unlink(missing_ok=True)
        
        return FileResponse(
            path=str(output_path),
            filename=f"schema_{xsd_file.filename.split('.')[0]}.json",
            media_type="application/json"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting XSD: {str(e)}")

@app.post("/api/jsonschema-to-xsd")
async def jsonschema_to_xsd(
    json_schema_file: UploadFile = File(...)
):
    """
    Convert JSON Schema to XSD
    """
    try:
        # Save uploaded file
        json_path = TEMP_DIR / f"json_{json_schema_file.filename}"
        
        with open(json_path, "wb") as buffer:
            shutil.copyfileobj(json_schema_file.file, buffer)
        
        # Parse JSON Schema
        fields = json_parser.parse_json_schema_file(str(json_path))
        
        # Convert to XSD format
        xsd_content = _generate_xsd_from_fields(fields)
        
        # Generate output file
        output_dir = TEMP_DIR / "xsd_output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"schema_{json_path.stem}.xsd"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xsd_content)
        
        # Clean up input file
        json_path.unlink(missing_ok=True)
        
        return FileResponse(
            path=str(output_path),
            filename=f"schema_{json_schema_file.filename.split('.')[0]}.xsd",
            media_type="application/xml"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting JSON Schema: {str(e)}")

@app.post("/api/wsdl-to-xsd")
async def wsdl_to_xsd(
    wsdl_file: UploadFile = File(...)
):
    """
    Extract XSD from WSDL
    """
    try:
        # Save uploaded file
        wsdl_path = TEMP_DIR / f"wsdl_{wsdl_file.filename}"
        
        with open(wsdl_path, "wb") as buffer:
            shutil.copyfileobj(wsdl_file.file, buffer)
        
        # Extract XSD from WSDL
        xsd_content = wsdl_extractor.extract_xsd_from_wsdl_file(str(wsdl_path))
        
        if not xsd_content:
            raise HTTPException(status_code=400, detail="No XSD schemas found in WSDL file")
        
        # Generate output file
        output_dir = TEMP_DIR / "wsdl_output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"schema_{wsdl_path.stem}.xsd"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xsd_content)
        
        # Clean up input file
        wsdl_path.unlink(missing_ok=True)
        
        return FileResponse(
            path=str(output_path),
            filename=f"schema_{wsdl_file.filename.split('.')[0]}.xsd",
            media_type="application/xml"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting XSD: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "xsd_parser": "available",
            "json_parser": "available",
            "excel_generator": "available",
            "wsdl_extractor": "available",
            "mapping_service": "available"
        }
    }

def _add_field_to_json_schema(field: dict, properties: dict):
    """Helper method to add field to JSON Schema properties"""
    # Extract field name from the first level
    field_name = field.get('levels', [''])[0] if field.get('levels') else ''
    field_type = field.get('Type', 'string')
    
    # Map XSD types to JSON Schema types
    type_mapping = {
        'string': 'string',
        'integer': 'integer',
        'int': 'integer',
        'long': 'integer',
        'double': 'number',
        'float': 'number',
        'decimal': 'number',
        'boolean': 'boolean',
        'date': 'string',
        'datetime': 'string',
        'array': 'array',
        'object': 'object'
    }
    
    json_type = type_mapping.get(field_type.lower(), 'string')
    
    if json_type == 'array':
        properties[field_name] = {
            "type": "array",
            "items": {"type": "string"}  # Default to string items
        }
    else:
        properties[field_name] = {
            "type": json_type
        }
        
        # Add description if available
        if field.get('Description'):
            properties[field_name]['description'] = field['Description']

def _generate_xsd_from_fields(fields: List[dict]) -> str:
    """Helper method to generate XSD from fields"""
    xsd_template = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="root">
        <xs:complexType>
            <xs:sequence>
                {elements}
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''
    
    elements = []
    for field in fields:
        field_name = field.get('levels', [''])[0] if field.get('levels') else ''
        field_type = field.get('Type', 'string')
        
        # Map JSON Schema types to XSD types
        type_mapping = {
            'string': 'xs:string',
            'integer': 'xs:integer',
            'number': 'xs:decimal',
            'boolean': 'xs:boolean',
            'array': 'xs:string'  # Default for arrays
        }
        
        xsd_type = type_mapping.get(field_type, 'xs:string')
        elements.append(f'<xs:element name="{field_name}" type="{xsd_type}"/>')
    
    return xsd_template.format(elements='\n                '.join(elements))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 