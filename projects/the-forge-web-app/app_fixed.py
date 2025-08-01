import streamlit as st
import os
import tempfile
import json
import xml.etree.ElementTree as ET
from io import BytesIO
import base64
import openpyxl
import difflib
from openpyxl.utils import get_column_letter

# Import modern UI libraries
try:
    from streamlit_extras.card import card
    from streamlit_extras.let_it_rain import rain
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
except ImportError as e:
    st.error(f"Failed to import UI libraries: {e}")
    st.stop()

# Import the microservices with error handling
try:
    from services.xsd_parser_service import XSDParser
    from services.json_schema_parser_service import JSONSchemaParser
    from services.excel_export_service import ExcelExporter
    from services.wsdl_to_xsd_extractor import merge_xsd_from_wsdl
    from services.excel_mapping_service import ExcelMappingService
    from services.json_to_excel_service import JSONToExcelService
    from services.case_converter_service import pascal_to_camel, camel_to_pascal
    from services.converter_service import ConverterService
except ImportError as e:
    st.error(f"Failed to import services: {e}")
    st.stop()

# Import homepage
try:
    from homepage import show_home_page
except ImportError as e:
    st.error(f"Failed to import homepage: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="The Forge - Schema Transformation Tool",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/the-forge',
        'Report a bug': 'https://github.com/your-repo/the-forge/issues',
        'About': 'The Forge - Advanced Schema Transformation Tool'
    }
)

# Forge CSS Theme
st.markdown("""
<style>
    /* Forge Color Palette */
    :root {
        --forge-black: #0a0a0a;
        --forge-dark: #1a1a1a;
        --forge-charcoal: #2d2d2d;
        --forge-steel: #3a3a3a;
        --forge-iron: #4a4a4a;
        --forge-coal: #5a5a5a;
        
        --forge-orange: #ff6b35;
        --forge-fire: #ff8c42;
        --forge-flame: #ffa726;
        --forge-ember: #ff7043;
        --forge-glow: #ff5722;
        
        --forge-gold: #ffd700;
        --forge-bronze: #cd7f32;
        --forge-copper: #b87333;
        
        --forge-text: #e0e0e0;
        --forge-text-secondary: #b0b0b0;
        --forge-text-muted: #808080;
        
        --forge-border: #404040;
        --forge-border-light: #505050;
        
        --forge-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        --forge-shadow-heavy: 0 8px 16px rgba(0, 0, 0, 0.7);
        --forge-glow-shadow: 0 0 20px rgba(255, 107, 53, 0.3);
        
        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
    }
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, var(--forge-black) 0%, var(--forge-dark) 100%);
        color: var(--forge-text);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Main Content Area */
    .main .block-container {
        background: linear-gradient(135deg, var(--forge-dark) 0%, var(--forge-charcoal) 100%);
        color: var(--forge-text);
        padding: 2rem;
        border-radius: var(--radius-lg);
        margin: 1rem;
        box-shadow: var(--forge-shadow);
    }
    
    /* Forge Header */
    .main-header {
        background: linear-gradient(135deg, var(--forge-charcoal) 0%, var(--forge-steel) 100%);
        color: var(--forge-text);
        padding: 3rem 2rem;
        border-radius: var(--radius-xl);
        text-align: center;
        margin-bottom: 2rem;
        border: 2px solid var(--forge-orange);
        box-shadow: var(--forge-shadow-heavy), var(--forge-glow-shadow);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 107, 53, 0.1), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, var(--forge-steel) 0%, var(--forge-iron) 100%);
        color: var(--forge-text);
        padding: 1.5rem 2rem;
        border-radius: var(--radius-lg);
        margin-bottom: 2rem;
        border-left: 4px solid var(--forge-orange);
        box-shadow: var(--forge-shadow);
    }
    
    .section-header h2 {
        margin: 0;
        color: var(--forge-text);
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--forge-black) 0%, var(--forge-dark) 100%);
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, var(--forge-charcoal) 0%, var(--forge-steel) 100%);
        color: var(--forge-text);
        padding: 1.5rem;
        border-radius: var(--radius-md);
        margin-bottom: 1rem;
        text-align: center;
        border: 1px solid var(--forge-border);
    }
    
    .sidebar-footer {
        background: linear-gradient(135deg, var(--forge-steel) 0%, var(--forge-iron) 100%);
        color: var(--forge-text-secondary);
        padding: 1rem;
        border-radius: var(--radius-md);
        margin-top: 2rem;
        text-align: center;
        font-size: 0.9rem;
        border: 1px solid var(--forge-border-light);
    }
    
    .version {
        color: var(--forge-orange);
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--forge-orange) 0%, var(--forge-fire) 100%);
        color: white;
        border: none;
        border-radius: var(--radius-md);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: var(--forge-shadow);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--forge-fire) 0%, var(--forge-flame) 100%);
        transform: translateY(-2px);
        box-shadow: var(--forge-shadow-heavy), var(--forge-glow-shadow);
    }
    
    /* File Uploader Styling */
    .stFileUploader > div > div {
        background: linear-gradient(135deg, var(--forge-steel) 0%, var(--forge-iron) 100%);
        border: 2px dashed var(--forge-border);
        border-radius: var(--radius-md);
        color: var(--forge-text);
    }
    
    .stFileUploader > div > div:hover {
        border-color: var(--forge-orange);
        background: linear-gradient(135deg, var(--forge-iron) 0%, var(--forge-coal) 100%);
    }
    
    /* Success and Error Messages */
    .success-message {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: var(--radius-md);
        margin: 1rem 0;
        text-align: center;
        font-weight: 600;
        box-shadow: var(--forge-shadow);
    }
    
    .error-message {
        background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
        color: white;
        padding: 1rem;
        border-radius: var(--radius-md);
        margin: 1rem 0;
        text-align: center;
        font-weight: 600;
        box-shadow: var(--forge-shadow);
    }
    
    /* Card Styling */
    .tool-card {
        background: linear-gradient(135deg, var(--forge-steel) 0%, var(--forge-iron) 100%);
        border: 1px solid var(--forge-border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: var(--forge-shadow);
    }
    
    .tool-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--forge-shadow-heavy);
        border-color: var(--forge-orange);
    }
    
    .tool-card h3 {
        color: var(--forge-orange);
        margin-bottom: 1rem;
        font-size: 1.4rem;
    }
    
    .tool-card p {
        color: var(--forge-text-secondary);
        line-height: 1.6;
    }
    
    /* Code Block Styling */
    .stCodeBlock {
        background: var(--forge-charcoal) !important;
        border: 1px solid var(--forge-border) !important;
        border-radius: var(--radius-md) !important;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, var(--forge-steel) 0%, var(--forge-iron) 100%) !important;
        color: var(--forge-text) !important;
        border: 1px solid var(--forge-border) !important;
        border-radius: var(--radius-md) !important;
    }
    
    .streamlit-expanderContent {
        background: var(--forge-charcoal) !important;
        border: 1px solid var(--forge-border) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
    }
    
    /* Selectbox Styling */
    .stSelectbox > div > div {
        background: var(--forge-steel) !important;
        border: 1px solid var(--forge-border) !important;
        color: var(--forge-text) !important;
    }
    
    /* Progress Bar Styling */
    .stProgress > div > div > div {
        background: var(--forge-orange) !important;
    }
    
    /* Metric Styling */
    .metric-container {
        background: linear-gradient(135deg, var(--forge-steel) 0%, var(--forge-iron) 100%);
        border: 1px solid var(--forge-border);
        border-radius: var(--radius-md);
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .metric-value {
        color: var(--forge-orange);
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .metric-label {
        color: var(--forge-text-secondary);
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_services():
    """Initialize and return all services."""
    try:
        return {
            'xsd_parser': XSDParser(),
            'json_schema_parser': JSONSchemaParser(),
            'excel_exporter': ExcelExporter(),
            'mapping_service': ExcelMappingService(),
            'json_to_excel': JSONToExcelService(),
            'converter': ConverterService()
        }
    except Exception as e:
        st.error(f"Failed to initialize services: {e}")
        return {}

def show_mapping_page(services):
    """Display the schema mapping page."""
    st.markdown('<div class="section-header"><h2>📊 Schema Mapping</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    Create field mappings between different schema formats. Upload source and target schema files (XSD, JSON Schema, or JSON Examples) to generate comprehensive mapping documentation.
    
    **New Feature**: JSON Examples are automatically converted to schemas for mapping!
    """)
    
    # Schema type selection
    st.markdown("### 🎯 Schema Type Selection")
    col1, col2 = st.columns(2)
    
    with col1:
        source_schema_type = st.selectbox(
            "Source Schema Type",
            ["XSD", "JSON Schema"],
            help="Select the type of your source schema"
        )
    
    with col2:
        target_schema_type = st.selectbox(
            "Target Schema Type", 
            ["XSD", "JSON Schema"],
            help="Select the type of your target schema"
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Source Schema")
        source_file = st.file_uploader(
            "Upload source schema file",
            type=['xsd', 'xml', 'json'],
            key="source_uploader",
            help="Upload your source schema file (XSD, XML, JSON Schema, or JSON Example)"
        )
        
        if source_file:
            st.markdown(f'<div class="success-message">✅ Uploaded: {source_file.name}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📥 Target Schema")
        target_file = st.file_uploader(
            "Upload target schema file",
            type=['xsd', 'xml', 'json'],
            key="target_uploader",
            help="Upload your target schema file (XSD, XML, JSON Schema, or JSON Example)"
        )
        
        if target_file:
            st.markdown(f'<div class="success-message">✅ Uploaded: {target_file.name}</div>', unsafe_allow_html=True)
    
    # Settings
    st.markdown("### ⚙️ Settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        source_case = st.selectbox("Source Case", ["Original", "PascalCase", "camelCase"], 
                                  help="Convert source field names to specified case")
    with col2:
        target_case = st.selectbox("Target Case", ["Original", "PascalCase", "camelCase"], 
                                  help="Convert target field names to specified case")
    with col3:
        min_match_threshold = st.slider("Minimum Match %", 20, 100, 20, 5,
                                       help="Minimum percentage of fields that must match to generate mapping")
    
    col4, col5 = st.columns(2)
    with col4:
        reorder_attributes = st.checkbox("Reorder Attributes First", value=False,
                                       help="Reorder attributes to appear before elements in each parent structure")
    
    # Generate mapping button
    if st.button("🔗 Generate Mapping", type="primary", use_container_width=True):
        if source_file and target_file:
            try:
                process_mapping(source_file, target_file, services, source_case, target_case, reorder_attributes, min_match_threshold)
            except Exception as e:
                st.error(f"Error in mapping: {str(e)}")
        else:
            st.warning("⚠️ Please upload both source and target files.")

def show_wsdl_to_xsd_page(services):
    """Display the WSDL to XSD page."""
    st.markdown('<div class="section-header"><h2>🔧 WSDL to XSD</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    Extract and merge XSD schemas from WSDL files. Upload a WSDL file to extract all embedded XSD schemas and merge them into a single XSD file.
    """)
    
    uploaded_file = st.file_uploader(
        "Upload WSDL file",
        type=['wsdl', 'xml'],
        help="Upload your WSDL file"
    )
    
    if uploaded_file:
        st.markdown(f'<div class="success-message">✅ Uploaded: {uploaded_file.name}</div>', unsafe_allow_html=True)
        
        if st.button("🔧 Extract XSD", type="primary", use_container_width=True):
            try:
                process_wsdl_to_xsd(uploaded_file, services)
            except Exception as e:
                st.error(f"Error processing WSDL: {str(e)}")

def show_schema_to_excel_page(services):
    """Display the schema to Excel page."""
    st.markdown('<div class="section-header"><h2>📋 Schema to Excel</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    Convert XSD or JSON Schema files to Excel format for easy viewing and analysis. Upload your schema file to generate a comprehensive Excel spreadsheet.
    """)
    
    uploaded_file = st.file_uploader(
        "Upload schema file",
        type=['xsd', 'xml', 'json'],
        help="Upload your XSD or JSON Schema file"
    )
    
    if uploaded_file:
        st.markdown(f'<div class="success-message">✅ Uploaded: {uploaded_file.name}</div>', unsafe_allow_html=True)
        
        if st.button("📋 Convert to Excel", type="primary", use_container_width=True):
            try:
                process_schema_to_excel(uploaded_file, services)
            except Exception as e:
                st.error(f"Error converting to Excel: {str(e)}")

def show_converter_page(services):
    """Display the converter page with dynamic source/target selection."""
    st.markdown('<div class="section-header"><h2>🔄 Converter</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    Convert between different schema and example formats. Select your source and target types to see available conversions.
    """)
    
    # Get converter service
    converter_service = services['converter']
    
    # Dynamic source/target selection
    st.markdown("### 🎯 Conversion Selection")
    col1, col2 = st.columns(2)
    
    with col1:
        source_type = st.selectbox(
            "Source Type",
            converter_service.get_source_types(),
            help="Select the type of your source file"
        )
    
    with col2:
        if source_type:
            target_types = converter_service.get_target_types_for_source(source_type)
            target_type = st.selectbox(
                "Target Type",
                target_types,
                help="Select the type you want to convert to"
            )
        else:
            target_type = None
    
    # Get conversion key and info
    if source_type and target_type:
        conversion_key = converter_service.get_conversion_key(source_type, target_type)
        supported_conversions = converter_service.get_supported_conversions()
        conversion_info = supported_conversions.get(conversion_key, {})
        
        if conversion_info:
            st.markdown(f"### 📋 {conversion_info.get('name', 'Conversion')}")
            st.markdown(f"**Description:** {conversion_info.get('description', 'N/A')}")
            st.markdown(f"**Input:** {conversion_info.get('input_type', 'N/A')} → **Output:** {conversion_info.get('output_type', 'N/A')}")
            
            # Show help information
            help_info = converter_service.get_conversion_help(conversion_key)
            with st.expander("ℹ️ Conversion Help"):
                st.markdown(f"**Input Format:** {help_info.get('input_format', 'N/A')}")
                st.markdown(f"**Output Format:** {help_info.get('output_format', 'N/A')}")
                st.markdown(f"**Features:** {help_info.get('features', 'N/A')}")
                st.markdown(f"**Example:** `{help_info.get('example', 'N/A')}`")
        else:
            st.warning(f"⚠️ Conversion from {source_type} to {target_type} is not yet implemented.")
            return
    
        # File upload
        st.markdown("### 📤 Input File")
        
        # Determine file types based on source type
        file_types = []
        if source_type == "json example" or source_type == "json schema":
            file_types = ['json']
        elif source_type == "xsd":
            file_types = ['xsd', 'xml']
        elif source_type == "xml example":
            file_types = ['xml']
        elif source_type == "excel":
            file_types = ['xlsx', 'xls']
        
        uploaded_file = st.file_uploader(
            f"Upload {source_type} file",
            type=file_types,
            key=f"converter_uploader_{conversion_key}",
            help=f"Upload your {source_type} file"
        )
        
        if uploaded_file:
            st.markdown(f'<div class="success-message">✅ Uploaded: {uploaded_file.name}</div>', unsafe_allow_html=True)
            
            # Show file preview
            content = uploaded_file.read()
            uploaded_file.seek(0)  # Reset file pointer
            
            with st.expander("📄 File Preview"):
                try:
                    decoded_content = content.decode('utf-8')
                    preview = decoded_content[:1000] + "..." if len(decoded_content) > 1000 else decoded_content
                    
                    if uploaded_file.name.lower().endswith('.json'):
                        st.code(preview, language="json")
                    else:
                        st.code(preview, language="xml")
                except UnicodeDecodeError:
                    st.code(content[:500], language="text")
        
        # Conversion options
        st.markdown("### ⚙️ Conversion Options")
        
        # Process conversion button
        if st.button("🔄 Convert", type="primary", use_container_width=True):
            if uploaded_file:
                try:
                    # Save uploaded file to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
                        temp_file.write(uploaded_file.getvalue())
                        temp_file_path = temp_file.name
                    
                    try:
                        # Process the conversion
                        if conversion_key in ["json_to_excel", "json_schema_to_excel", "xsd_to_excel", "xml_to_excel"]:
                            # Excel conversions
                            result_bytes = process_excel_conversion(temp_file_path, conversion_key, services)
                            
                            # Provide download link
                            st.markdown("### 📥 Download Result")
                            st.download_button(
                                label="📊 Download Excel File",
                                data=result_bytes,
                                file_name=f"converted_{uploaded_file.name.split('.')[0]}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                            
                            # Show statistics
                            st.markdown("### 📊 Conversion Statistics")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Status", "✅ Success")
                            with col2:
                                st.metric("Input Size", f"{len(uploaded_file.getvalue())} bytes")
                            with col3:
                                st.metric("Output Size", f"{len(result_bytes)} bytes")
                        
                        else:
                            # Non-Excel conversions
                            result = converter_service.process_file_conversion(temp_file_path, conversion_key)
                            
                            # Save result to temporary file
                            output_path = converter_service.save_conversion_result(result, conversion_key, temp_file_path)
                            
                            # Provide download link
                            st.markdown("### 📥 Download Result")
                            with open(output_path, 'rb') as f:
                                result_bytes = f.read()
                            
                            # Determine file extension based on target type
                            file_ext = "txt"
                            if target_type == "json schema":
                                file_ext = "json"
                            elif target_type == "xsd":
                                file_ext = "xsd"
                            elif target_type == "xml example":
                                file_ext = "xml"
                            elif target_type == "json example":
                                file_ext = "json"
                            
                            st.download_button(
                                label=f"📄 Download {target_type.upper()} File",
                                data=result_bytes,
                                file_name=f"converted_{uploaded_file.name.split('.')[0]}.{file_ext}",
                                mime="text/plain"
                            )
                            
                            # Show statistics
                            st.markdown("### 📊 Conversion Statistics")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Status", "✅ Success")
                            with col2:
                                st.metric("Input Size", f"{len(uploaded_file.getvalue())} bytes")
                            with col3:
                                st.metric("Output Size", f"{len(result_bytes)} bytes")
                    
                    finally:
                        # Clean up temporary file
                        if os.path.exists(temp_file_path):
                            os.unlink(temp_file_path)
                
                except Exception as e:
                    st.error(f"❌ Conversion failed: {str(e)}")
            else:
                st.warning("⚠️ Please upload a file to convert.")

def show_about_page():
    """Display the about page."""
    st.markdown('<div class="section-header"><h2>ℹ️ About</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    ## 🔨 The Forge - Schema Transformation Tool
    
    The Forge is a comprehensive schema transformation and mapping tool designed to help developers and data engineers work with different schema formats.
    
    ### Features
    - **Schema Mapping**: Create field mappings between XSD and JSON Schema formats
    - **WSDL to XSD**: Extract and merge XSD schemas from WSDL files
    - **Schema to Excel**: Convert schemas to Excel format for analysis
    - **Converter**: Convert between different schema and example formats
    
    ### Technologies
    - Built with Streamlit
    - Python-based microservices architecture
    - Support for XSD, JSON Schema, XML, and Excel formats
    """)

def process_mapping(source_file, target_file, services, source_case="Original", target_case="Original", reorder_attributes=False, min_match_threshold=20):
    """Process schema mapping."""
    st.info("Processing mapping...")
    # Placeholder for mapping logic
    st.success("Mapping completed!")

def process_wsdl_to_xsd(wsdl_file, services):
    """Process WSDL to XSD conversion."""
    st.info("Processing WSDL...")
    # Placeholder for WSDL processing logic
    st.success("XSD extracted!")

def process_schema_to_excel(schema_file, services):
    """Process schema to Excel conversion."""
    st.info("Converting to Excel...")
    # Placeholder for Excel conversion logic
    st.success("Excel file generated!")

def process_excel_conversion(file_path: str, conversion_key: str, services: dict) -> bytes:
    """Process Excel conversions using the existing ExcelExporter service."""
    try:
        excel_exporter = services['excel_exporter']
        
        if conversion_key == "json_to_excel":
            # Convert JSON example to Excel
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            # Use ExcelExporter for JSON to Excel conversion
            # First convert JSON to schema, then to Excel
            json_to_schema = services['converter'].json_to_schema
            schema_data = json_to_schema.convert_json_example_to_schema(json_data, "GeneratedSchema")
            # Parse the schema and convert to Excel
            json_schema_parser = services['json_schema_parser']
            # Convert schema to string and use parse_json_schema_string
            schema_string = json.dumps(schema_data)
            parsed_data = json_schema_parser.parse_json_schema_string(schema_string)
            output_buffer = BytesIO()
            excel_exporter.export({'schema': parsed_data}, output_buffer)
            output_buffer.seek(0)
            return output_buffer.getvalue()
        
        elif conversion_key == "json_schema_to_excel":
            # Convert JSON Schema to Excel
            with open(file_path, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
            # Parse JSON Schema and convert to Excel
            json_schema_parser = services['json_schema_parser']
            # Convert schema to string and use parse_json_schema_string
            schema_string = json.dumps(schema_data)
            parsed_data = json_schema_parser.parse_json_schema_string(schema_string)
            output_buffer = BytesIO()
            excel_exporter.export({'schema': parsed_data}, output_buffer)
            output_buffer.seek(0)
            return output_buffer.getvalue()
        
        elif conversion_key == "xsd_to_excel":
            # Convert XSD to Excel
            xsd_parser = services['xsd_parser']
            parsed_data = xsd_parser.parse_xsd_file(file_path)
            output_buffer = BytesIO()
            excel_exporter.export({'schema': parsed_data}, output_buffer)
            output_buffer.seek(0)
            return output_buffer.getvalue()
        
        elif conversion_key == "xml_to_excel":
            # Convert XML to Excel (first convert to XSD, then to Excel)
            # This is a simplified approach - in practice, you might want to parse XML directly
            xml_to_xsd = services['converter'].xml_to_xsd
            xsd_content = xml_to_xsd.convert_xml_example_to_xsd(
                open(file_path, 'r', encoding='utf-8').read(), 
                "GeneratedSchema"
            )
            # Save XSD to temp file and convert to Excel
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xsd') as temp_xsd:
                temp_xsd.write(xsd_content.encode('utf-8'))
                temp_xsd_path = temp_xsd.name
            
            try:
                xsd_parser = services['xsd_parser']
                parsed_data = xsd_parser.parse_xsd_file(temp_xsd_path)
                output_buffer = BytesIO()
                excel_exporter.export({'schema': parsed_data}, output_buffer)
                output_buffer.seek(0)
                return output_buffer.getvalue()
            finally:
                os.unlink(temp_xsd_path)
        
        else:
            raise ValueError(f"Unsupported Excel conversion: {conversion_key}")
    
    except Exception as e:
        raise Exception(f"Error in Excel conversion {conversion_key}: {str(e)}")

def main():
    """Main application function."""
    # Header
    st.markdown('''
        <div class="main-header">
            <h1>🔨 The Forge</h1>
            <p>Schema Transformation & Mapping Tool</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # Get services
    services = get_services()
    if not services:
        st.error("Failed to initialize services. Please check the console for errors.")
        return
    
    # Sidebar Header
    st.sidebar.markdown("""
        <div class="sidebar-header">
            <h2>🔨 The Forge</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    
    # Navigation Menu with unique keys
    if st.sidebar.button("🏠 Home", key="nav_home", use_container_width=True):
        st.session_state.current_page = "Home"
    
    if st.sidebar.button("📊 Schema Mapping", key="nav_mapping", use_container_width=True):
        st.session_state.current_page = "Schema Mapping"
    
    if st.sidebar.button("🔧 WSDL to XSD", key="nav_wsdl", use_container_width=True):
        st.session_state.current_page = "WSDL to XSD"
    
    if st.sidebar.button("📋 Schema to Excel", key="nav_excel", use_container_width=True):
        st.session_state.current_page = "Schema to Excel"
    
    if st.sidebar.button("🔄 Converter", key="nav_converter", use_container_width=True):
        st.session_state.current_page = "Converter"
    
    if st.sidebar.button("ℹ️ About", key="nav_about", use_container_width=True):
        st.session_state.current_page = "About"
    
    # Sidebar Footer
    st.sidebar.markdown("""
        <div class="sidebar-footer">
            <div>Forged with Streamlit</div>
            <div class="version">v1.0.0</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Display current page
    try:
        if st.session_state.current_page == "Home":
            show_home_page()
        elif st.session_state.current_page == "Schema Mapping":
            show_mapping_page(services)
        elif st.session_state.current_page == "WSDL to XSD":
            show_wsdl_to_xsd_page(services)
        elif st.session_state.current_page == "Schema to Excel":
            show_schema_to_excel_page(services)
        elif st.session_state.current_page == "Converter":
            show_converter_page(services)
        elif st.session_state.current_page == "About":
            show_about_page()
    except Exception as e:
        st.error(f"Error displaying page {st.session_state.current_page}: {e}")

if __name__ == "__main__":
    main() 