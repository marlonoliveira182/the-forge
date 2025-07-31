import streamlit as st
import os
import tempfile
import json
import xml.etree.ElementTree as ET
from io import BytesIO

# Import the microservices
from services.xsd_parser_service import XSDParser
from services.excel_export_service import ExcelExporter
from services.wsdl_to_xsd_extractor import merge_xsd_from_wsdl
from services.excel_mapping_service import ExcelMappingService
from services.json_to_excel_service import JSONToExcelService

# Page configuration
st.set_page_config(
    page_title="The Forge - Schema Transformation Tool",
    page_icon="🔧",
    layout="wide"
)

def main():
    # Header
    st.title("🔧 The Forge - Schema Transformation Tool")
    st.write("A powerful schema transformation tool based on The Forge v8")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a tool:",
        ["Schema Mapping", "WSDL to XSD Extraction", "Schema to Excel", "About"]
    )
    
    if page == "Schema Mapping":
        show_mapping_page()
    elif page == "WSDL to XSD Extraction":
        show_wsdl_to_xsd_page()
    elif page == "Schema to Excel":
        show_schema_to_excel_page()
    elif page == "About":
        show_about_page()

def show_mapping_page():
    st.header("📊 Schema Mapping")
    st.write("Create field mappings between different schema formats")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Source Schema")
        source_file = st.file_uploader(
            "Upload source schema file",
            type=['xsd', 'xml', 'json'],
            key="source"
        )
    
    with col2:
        st.subheader("Target Schema")
        target_file = st.file_uploader(
            "Upload target schema file",
            type=['xsd', 'xml', 'json'],
            key="target"
        )
    
    # Settings
    threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.7, 0.1)
    keep_case = st.checkbox("Keep Original Case", value=False)
    
    # Generate mapping button
    if st.button("Generate Mapping", type="primary"):
        if source_file and target_file:
            with st.spinner("Generating mapping..."):
                try:
                    result = process_mapping(source_file, target_file, threshold, keep_case)
                    if result:
                        st.success("✅ Mapping generated successfully!")
                        st.download_button(
                            label="Download Excel File",
                            data=result,
                            file_name="schema_mapping.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.error("❌ Failed to generate mapping")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please upload both source and target schema files")

def show_wsdl_to_xsd_page():
    st.header("🔧 WSDL to XSD Extraction")
    st.write("Extract XSD schemas from WSDL files")
    
    wsdl_file = st.file_uploader(
        "Upload WSDL file",
        type=['wsdl', 'xml'],
        key="wsdl"
    )
    
    if st.button("Extract XSD", type="primary"):
        if wsdl_file:
            with st.spinner("Extracting XSD..."):
                try:
                    result = process_wsdl_to_xsd(wsdl_file)
                    if result:
                        st.success("✅ XSD extracted successfully!")
                        st.download_button(
                            label="Download XSD File",
                            data=result,
                            file_name="extracted_schema.xsd",
                            mime="application/xml"
                        )
                    else:
                        st.error("❌ Failed to extract XSD")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please upload a WSDL file")

def show_schema_to_excel_page():
    st.header("📋 Schema to Excel")
    st.write("Convert schema files to Excel format for analysis")
    
    schema_file = st.file_uploader(
        "Upload schema file",
        type=['xsd', 'xml', 'json'],
        key="schema"
    )
    
    keep_case = st.checkbox("Keep Original Case", value=False, key="schema_case")
    
    if st.button("Convert to Excel", type="primary"):
        if schema_file:
            with st.spinner("Converting to Excel..."):
                try:
                    result = process_schema_to_excel(schema_file, keep_case)
                    if result:
                        st.success("✅ Excel file generated successfully!")
                        st.download_button(
                            label="Download Excel File",
                            data=result,
                            file_name="schema_structure.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.error("❌ Failed to generate Excel file")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please upload a schema file")

def show_about_page():
    st.header("ℹ️ About The Forge")
    
    st.write("""
    **The Forge** is a powerful schema transformation tool that provides:
    
    - **📊 Schema Mapping**: Create field mappings between different schema formats
    - **🔧 WSDL to XSD Extraction**: Extract XSD schemas from WSDL files
    - **📋 Schema to Excel**: Convert schema files to Excel format for analysis
    
    This web version is based on The Forge v8 desktop application, adapted for online deployment.
    
    ### Supported Formats:
    - **Input**: XSD, XML, JSON Schema, WSDL
    - **Output**: Excel (.xlsx), XSD (.xsd)
    
    ### Features:
    - ✅ No compilation issues
    - ✅ Lightweight dependencies
    - ✅ Cross-platform compatibility
    - ✅ Production ready
    """)

def process_mapping(source_file, target_file, threshold, keep_case):
    """Process schema mapping"""
    try:
        # Initialize services
        xsd_parser = XSDParser()
        mapping_service = ExcelMappingService()
        excel_exporter = ExcelExporter()
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{source_file.name.split('.')[-1]}") as source_temp:
            source_file.save(source_temp.name)
            source_temp_path = source_temp.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_file.name.split('.')[-1]}") as target_temp:
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
        return output_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error in mapping: {str(e)}")
        return None

def process_wsdl_to_xsd(wsdl_file):
    """Process WSDL to XSD extraction"""
    try:
        # Read WSDL content
        wsdl_content = wsdl_file.read().decode('utf-8')
        
        # Extract XSD
        xsd_content = merge_xsd_from_wsdl(wsdl_content)
        
        if not xsd_content or xsd_content.startswith("Error"):
            st.error(f"Error extracting XSD: {xsd_content}")
            return None
        
        return xsd_content.encode('utf-8')
        
    except Exception as e:
        st.error(f"Error in WSDL extraction: {str(e)}")
        return None

def process_schema_to_excel(schema_file, keep_case):
    """Process schema to Excel conversion"""
    try:
        # Initialize services
        xsd_parser = XSDParser()
        excel_exporter = ExcelExporter()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{schema_file.name.split('.')[-1]}") as temp_file:
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
        return output_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error in schema to Excel: {str(e)}")
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