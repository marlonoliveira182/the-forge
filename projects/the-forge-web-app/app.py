import streamlit as st
import os
import tempfile
import pandas as pd
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from io import BytesIO
import base64

# Import the microservices from v8
from services.xsd_parser_service import XSDParser
from services.excel_export_service import ExcelExporter
from services.wsdl_to_xsd_extractor import merge_xsd_from_wsdl
from services.excel_mapping_service import ExcelMappingService
from services.json_to_excel_service import JSONToExcelService

# Page configuration
st.set_page_config(
    page_title="The Forge - Schema Transformation Tool",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #212E3E 0%, #2A3647 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: #28FF52;
        text-align: center;
        margin: 0;
    }
    .upload-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px dashed #263CC8;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stButton > button {
        background: #263CC8;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: #4A90E2;
    }
    .primary-button {
        background: #28FF52 !important;
        color: #212E3E !important;
    }
    .primary-button:hover {
        background: #1ED760 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def get_services():
    """Initialize and cache the microservices"""
    return {
        'xsd_parser': XSDParser(),
        'excel_exporter': ExcelExporter(),
        'mapping_service': ExcelMappingService(),
        'json_to_excel': JSONToExcelService()
    }

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔧 The Forge - Schema Transformation Tool</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a tool:",
        ["Mapping", "WSDL to XSD", "Schema to Excel", "About"]
    )
    
    # Get services
    services = get_services()
    
    if page == "Mapping":
        show_mapping_page(services)
    elif page == "WSDL to XSD":
        show_wsdl_to_xsd_page(services)
    elif page == "Schema to Excel":
        show_schema_to_excel_page(services)
    elif page == "About":
        show_about_page()

def show_mapping_page(services):
    """Mapping functionality page"""
    st.header("📊 Schema Mapping")
    st.markdown("Create field mappings between different schema formats (XSD, JSON Schema)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Source Schema")
        source_file = st.file_uploader(
            "Upload source schema file",
            type=['xsd', 'xml', 'json'],
            key="source_file"
        )
        
        if source_file:
            st.success(f"✅ Source file uploaded: {source_file.name}")
            
            # Display file preview
            if source_file.name.endswith('.json'):
                try:
                    content = source_file.read()
                    source_file.seek(0)  # Reset file pointer
                    data = json.loads(content.decode('utf-8'))
                    st.json(data)
                except Exception as e:
                    st.error(f"Error reading JSON file: {e}")
    
    with col2:
        st.subheader("Target Schema")
        target_file = st.file_uploader(
            "Upload target schema file",
            type=['xsd', 'xml', 'json'],
            key="target_file"
        )
        
        if target_file:
            st.success(f"✅ Target file uploaded: {target_file.name}")
            
            # Display file preview
            if target_file.name.endswith('.json'):
                try:
                    content = target_file.read()
                    target_file.seek(0)  # Reset file pointer
                    data = json.loads(content.decode('utf-8'))
                    st.json(data)
                except Exception as e:
                    st.error(f"Error reading JSON file: {e}")
    
    # Mapping options
    st.subheader("Mapping Options")
    col1, col2 = st.columns(2)
    
    with col1:
        threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.7, 0.1)
    
    with col2:
        keep_case = st.checkbox("Keep Original Case", value=False)
    
    # Generate mapping button
    if st.button("🚀 Generate Mapping", type="primary", use_container_width=True):
        if source_file and target_file:
            with st.spinner("Generating mapping..."):
                try:
                    # Process the mapping
                    mapping_result = process_mapping(
                        services, source_file, target_file, threshold, keep_case
                    )
                    
                    if mapping_result:
                        st.success("✅ Mapping generated successfully!")
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Mapping Excel",
                            data=mapping_result,
                            file_name="schema_mapping.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                        # Show preview
                        st.subheader("Mapping Preview")
                        # Here you would show a preview of the mapping
                        st.info("Mapping preview would be displayed here")
                        
                except Exception as e:
                    st.error(f"❌ Error generating mapping: {str(e)}")
        else:
            st.warning("⚠️ Please upload both source and target files")

def show_wsdl_to_xsd_page(services):
    """WSDL to XSD extraction page"""
    st.header("🔧 WSDL to XSD Extraction")
    st.markdown("Extract XSD schemas from WSDL files")
    
    # File upload
    wsdl_file = st.file_uploader(
        "Upload WSDL file",
        type=['wsdl', 'xml'],
        key="wsdl_file"
    )
    
    if wsdl_file:
        st.success(f"✅ WSDL file uploaded: {wsdl_file.name}")
        
        # Show file content preview
        content = wsdl_file.read()
        wsdl_file.seek(0)  # Reset file pointer
        
        with st.expander("📄 WSDL Content Preview"):
            st.code(content.decode('utf-8'), language='xml')
    
    # Extract button
    if st.button("🔧 Extract XSD", type="primary", use_container_width=True):
        if wsdl_file:
            with st.spinner("Extracting XSD from WSDL..."):
                try:
                    # Process WSDL to XSD
                    xsd_content = process_wsdl_to_xsd(wsdl_file)
                    
                    if xsd_content:
                        st.success("✅ XSD extracted successfully!")
                        
                        # Download button
                        st.download_button(
                            label="📥 Download XSD",
                            data=xsd_content,
                            file_name="extracted_schema.xsd",
                            mime="application/xml"
                        )
                        
                        # Show XSD content
                        with st.expander("📄 Extracted XSD Content"):
                            st.code(xsd_content, language='xml')
                        
                except Exception as e:
                    st.error(f"❌ Error extracting XSD: {str(e)}")
        else:
            st.warning("⚠️ Please upload a WSDL file")

def show_schema_to_excel_page(services):
    """Schema to Excel conversion page"""
    st.header("📊 Schema to Excel")
    st.markdown("Convert schema files to Excel format for analysis")
    
    # File upload
    schema_file = st.file_uploader(
        "Upload schema file",
        type=['xsd', 'xml', 'json'],
        key="schema_file"
    )
    
    if schema_file:
        st.success(f"✅ Schema file uploaded: {schema_file.name}")
        
        # Show file preview
        content = schema_file.read()
        schema_file.seek(0)  # Reset file pointer
        
        with st.expander("📄 Schema Content Preview"):
            if schema_file.name.endswith('.json'):
                try:
                    data = json.loads(content.decode('utf-8'))
                    st.json(data)
                except Exception as e:
                    st.error(f"Error reading JSON: {e}")
            else:
                st.code(content.decode('utf-8'), language='xml')
    
    # Conversion options
    st.subheader("Conversion Options")
    keep_case = st.checkbox("Keep Original Case", value=False)
    
    # Convert button
    if st.button("📊 Convert to Excel", type="primary", use_container_width=True):
        if schema_file:
            with st.spinner("Converting schema to Excel..."):
                try:
                    # Process schema to Excel
                    excel_data = process_schema_to_excel(
                        services, schema_file, keep_case
                    )
                    
                    if excel_data:
                        st.success("✅ Excel file generated successfully!")
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Excel",
                            data=excel_data,
                            file_name="schema_structure.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                        # Show preview
                        st.subheader("Excel Preview")
                        st.info("Excel preview would be displayed here")
                        
                except Exception as e:
                    st.error(f"❌ Error converting to Excel: {str(e)}")
        else:
            st.warning("⚠️ Please upload a schema file")

def show_about_page():
    """About page"""
    st.header("ℹ️ About The Forge")
    
    st.markdown("""
    ### What is The Forge?
    
    The Forge is a powerful schema transformation and mapping tool that helps you:
    
    - **Map fields** between different schema formats (XSD, JSON Schema)
    - **Extract XSD schemas** from WSDL files
    - **Convert schemas** to Excel format for analysis
    - **Transform data structures** between different formats
    
    ### Features
    
    🔧 **Schema Mapping**: Create intelligent field mappings with similarity scoring
    📊 **Excel Export**: Convert schemas to Excel for easy analysis
    🔄 **Format Conversion**: Convert between XSD and JSON Schema
    📋 **WSDL Processing**: Extract XSD schemas from WSDL files
    
    ### Supported Formats
    
    - **Input**: XSD, JSON Schema, WSDL, XML
    - **Output**: Excel (.xlsx), XSD, JSON Schema
    
    ### Version
    
    This is the web version of The Forge v8, adapted for online deployment using Streamlit.
    """)

def process_mapping(services, source_file, target_file, threshold, keep_case):
    """Process mapping between source and target schemas"""
    try:
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{source_file.name.split('.')[-1]}") as source_temp:
            source_temp.write(source_file.read())
            source_temp_path = source_temp.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_file.name.split('.')[-1]}") as target_temp:
            target_temp.write(target_file.read())
            target_temp_path = target_temp.name
        
        # Parse schemas
        source_data = parse_schema_file(source_temp_path, services['xsd_parser'])
        target_data = parse_schema_file(target_temp_path, services['xsd_parser'])
        
        # Generate mapping
        mapping_data = services['mapping_service'].generate_mapping_from_schemas(
            source_data, target_data
        )
        
        # Create Excel file
        output_buffer = BytesIO()
        services['excel_exporter'].export(
            {'mapping': mapping_data}, output_buffer
        )
        
        # Clean up temp files
        os.unlink(source_temp_path)
        os.unlink(target_temp_path)
        
        return output_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error in mapping process: {str(e)}")
        return None

def process_wsdl_to_xsd(wsdl_file):
    """Process WSDL to XSD extraction"""
    try:
        content = wsdl_file.read()
        wsdl_content = content.decode('utf-8')
        
        # Extract XSD from WSDL
        xsd_content = merge_xsd_from_wsdl(wsdl_content)
        
        return xsd_content.encode('utf-8')
        
    except Exception as e:
        st.error(f"Error in WSDL to XSD process: {str(e)}")
        return None

def process_schema_to_excel(services, schema_file, keep_case):
    """Process schema to Excel conversion"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{schema_file.name.split('.')[-1]}") as temp_file:
            temp_file.write(schema_file.read())
            temp_path = temp_file.name
        
        # Parse schema
        schema_data = parse_schema_file(temp_path, services['xsd_parser'])
        
        # Create Excel file
        output_buffer = BytesIO()
        services['excel_exporter'].export(
            {'schema': schema_data}, output_buffer
        )
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return output_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error in schema to Excel process: {str(e)}")
        return None

def parse_schema_file(file_path, xsd_parser):
    """Parse schema file based on its type"""
    if file_path.endswith('.json'):
        # Handle JSON Schema
        with open(file_path, 'r') as f:
            return json.load(f)
    else:
        # Handle XSD
        return xsd_parser.parse_xsd_file(file_path)

if __name__ == "__main__":
    main() 