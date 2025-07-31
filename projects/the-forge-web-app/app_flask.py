from flask import Flask, render_template, request, send_file, jsonify
import os
import tempfile
import json
import xml.etree.ElementTree as ET
from io import BytesIO
import base64

# Import the microservices
from services.xsd_parser_service import XSDParser
from services.excel_export_service import ExcelExporter
from services.wsdl_to_xsd_extractor import merge_xsd_from_wsdl
from services.excel_mapping_service import ExcelMappingService
from services.json_to_excel_service import JSONToExcelService

app = Flask(__name__)

# Initialize services
xsd_parser = XSDParser()
excel_exporter = ExcelExporter()
mapping_service = ExcelMappingService()
json_to_excel = JSONToExcelService()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>The Forge - Schema Transformation Tool</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { background: linear-gradient(90deg, #212E3E 0%, #2A3647 100%); 
                     color: #28FF52; padding: 20px; border-radius: 10px; text-align: center; }
            .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .button { background: #263CC8; color: white; padding: 10px 20px; border: none; 
                     border-radius: 5px; cursor: pointer; }
            .button:hover { background: #4A90E2; }
            .success { color: green; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔧 The Forge - Schema Transformation Tool</h1>
        </div>
        
        <div class="section">
            <h2>📊 Schema Mapping</h2>
            <form action="/mapping" method="post" enctype="multipart/form-data">
                <p><label>Source Schema: <input type="file" name="source" accept=".xsd,.xml,.json" required></label></p>
                <p><label>Target Schema: <input type="file" name="target" accept=".xsd,.xml,.json" required></label></p>
                <p><label>Similarity Threshold: <input type="range" name="threshold" min="0" max="1" step="0.1" value="0.7"></label></p>
                <p><label><input type="checkbox" name="keep_case"> Keep Original Case</label></p>
                <button type="submit" class="button">Generate Mapping</button>
            </form>
        </div>
        
        <div class="section">
            <h2>🔧 WSDL to XSD Extraction</h2>
            <form action="/wsdl_to_xsd" method="post" enctype="multipart/form-data">
                <p><label>WSDL File: <input type="file" name="wsdl" accept=".wsdl,.xml" required></label></p>
                <button type="submit" class="button">Extract XSD</button>
            </form>
        </div>
        
        <div class="section">
            <h2>📋 Schema to Excel</h2>
            <form action="/schema_to_excel" method="post" enctype="multipart/form-data">
                <p><label>Schema File: <input type="file" name="schema" accept=".xsd,.xml,.json" required></label></p>
                <p><label><input type="checkbox" name="keep_case"> Keep Original Case</label></p>
                <button type="submit" class="button">Convert to Excel</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/mapping', methods=['POST'])
def mapping():
    try:
        source_file = request.files['source']
        target_file = request.files['target']
        threshold = float(request.form.get('threshold', 0.7))
        keep_case = 'keep_case' in request.form
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{source_file.filename.split('.')[-1]}") as source_temp:
            source_file.save(source_temp.name)
            source_temp_path = source_temp.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_file.filename.split('.')[-1]}") as target_temp:
            target_file.save(target_temp.name)
            target_temp_path = target_temp.name
        
        # Parse schemas
        source_data = parse_schema_file(source_temp_path, xsd_parser)
        target_data = parse_schema_file(target_temp_path, xsd_parser)
        
        # Generate mapping
        mapping_data = mapping_service.generate_mapping_from_schemas(source_data, target_data)
        
        # Create Excel file
        output_buffer = BytesIO()
        excel_exporter.export({'mapping': mapping_data}, output_buffer)
        
        # Clean up temp files
        os.unlink(source_temp_path)
        os.unlink(target_temp_path)
        
        output_buffer.seek(0)
        return send_file(
            output_buffer,
            as_attachment=True,
            download_name="schema_mapping.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        return f"Error: {str(e)}", 400

@app.route('/wsdl_to_xsd', methods=['POST'])
def wsdl_to_xsd():
    try:
        wsdl_file = request.files['wsdl']
        
        # Read WSDL content
        wsdl_content = wsdl_file.read().decode('utf-8')
        
        # Extract XSD
        xsd_content = merge_xsd_from_wsdl(wsdl_content)
        
        if not xsd_content or xsd_content.startswith("Error"):
            return f"Error extracting XSD: {xsd_content}", 400
        
        # Return XSD file
        output_buffer = BytesIO()
        output_buffer.write(xsd_content.encode('utf-8'))
        output_buffer.seek(0)
        
        return send_file(
            output_buffer,
            as_attachment=True,
            download_name="extracted_schema.xsd",
            mimetype="application/xml"
        )
        
    except Exception as e:
        return f"Error: {str(e)}", 400

@app.route('/schema_to_excel', methods=['POST'])
def schema_to_excel():
    try:
        schema_file = request.files['schema']
        keep_case = 'keep_case' in request.form
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{schema_file.filename.split('.')[-1]}") as temp_file:
            schema_file.save(temp_file.name)
            temp_path = temp_file.name
        
        # Parse schema
        schema_data = parse_schema_file(temp_path, xsd_parser)
        
        # Create Excel file
        output_buffer = BytesIO()
        excel_exporter.export({'schema': schema_data}, output_buffer)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        output_buffer.seek(0)
        return send_file(
            output_buffer,
            as_attachment=True,
            download_name="schema_structure.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        return f"Error: {str(e)}", 400

def parse_schema_file(file_path, xsd_parser):
    """Parse schema file based on its type"""
    if file_path.endswith('.json'):
        # Handle JSON Schema
        with open(file_path, 'r') as f:
            return json.load(f)
    else:
        # Handle XSD
        return xsd_parser.parse_xsd_file(file_path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 