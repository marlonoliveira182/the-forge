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

# Import the core forge functionality
from forge_core import (
    extract_fields_from_json_schema,
    extract_fields_from_xsd,
    map_paths,
    build_mapping_v2_style,
    write_mapping_excel,
    run_schema_to_excel_operation,
    run_xsd_to_jsonschema_operation,
    run_jsonschema_to_xsd_operation
)

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

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "The Forge API v1.0.0",
        "endpoints": {
            "POST /api/mapping": "Create field mapping between schemas",
            "POST /api/schema-to-excel": "Convert schema to Excel format",
            "POST /api/xsd-to-jsonschema": "Convert XSD to JSON Schema",
            "POST /api/jsonschema-to-xsd": "Convert JSON Schema to XSD"
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
        
        if source_ext == '.json':
            source_fields = extract_fields_from_json_schema(str(source_path))
        elif source_ext in ['.xsd', '.xml']:
            source_fields = extract_fields_from_xsd(str(source_path), keep_case)
        else:
            raise HTTPException(status_code=400, detail="Unsupported source file format")
        
        if target_ext == '.json':
            target_fields = extract_fields_from_json_schema(str(target_path))
        elif target_ext in ['.xsd', '.xml']:
            target_fields = extract_fields_from_xsd(str(target_path), keep_case)
        else:
            raise HTTPException(status_code=400, detail="Unsupported target file format")
        
        # Create mapping
        mapping = map_paths(source_fields, target_fields, threshold)
        
        # Generate output file
        output_dir = TEMP_DIR / "mapping_output"
        output_dir.mkdir(exist_ok=True)
        
        src_name = source_path.stem
        tgt_name = target_path.stem
        output_path = output_dir / f"mapping_{src_name}_to_{tgt_name}.xlsx"
        
        build_mapping_v2_style(source_fields, target_fields, mapping, src_name, tgt_name, str(output_path))
        
        # Return the mapping file
        return FileResponse(
            path=str(output_path),
            filename=output_path.name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temporary files
        for path in [source_path, target_path]:
            if path.exists():
                path.unlink()

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
        
        # Generate output
        output_dir = TEMP_DIR / "schema_excel_output"
        output_dir.mkdir(exist_ok=True)
        
        run_schema_to_excel_operation(str(schema_path), str(output_dir))
        
        # Find the generated Excel file
        excel_files = list(output_dir.glob("*.xlsx"))
        if not excel_files:
            raise HTTPException(status_code=500, detail="Failed to generate Excel file")
        
        output_file = excel_files[0]
        
        return FileResponse(
            path=str(output_file),
            filename=output_file.name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temporary files
        if schema_path.exists():
            schema_path.unlink()

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
        
        # Generate output
        output_dir = TEMP_DIR / "xsd_to_json_output"
        output_dir.mkdir(exist_ok=True)
        
        run_xsd_to_jsonschema_operation(str(xsd_path), str(output_dir))
        
        # Find the generated JSON Schema file
        json_files = list(output_dir.glob("*.json"))
        if not json_files:
            raise HTTPException(status_code=500, detail="Failed to generate JSON Schema file")
        
        output_file = json_files[0]
        
        return FileResponse(
            path=str(output_file),
            filename=output_file.name,
            media_type="application/json"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temporary files
        if xsd_path.exists():
            xsd_path.unlink()

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
        
        # Generate output
        output_dir = TEMP_DIR / "json_to_xsd_output"
        output_dir.mkdir(exist_ok=True)
        
        run_jsonschema_to_xsd_operation(str(json_path), str(output_dir))
        
        # Find the generated XSD file
        xsd_files = list(output_dir.glob("*.xsd"))
        if not xsd_files:
            raise HTTPException(status_code=500, detail="Failed to generate XSD file")
        
        output_file = xsd_files[0]
        
        return FileResponse(
            path=str(output_file),
            filename=output_file.name,
            media_type="application/xml"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temporary files
        if json_path.exists():
            json_path.unlink()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 