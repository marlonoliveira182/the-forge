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

# Import the microservices
from services.xsd_parser_service import XSDParser
from services.json_schema_parser_service import JSONSchemaParser
from services.excel_export_service import ExcelExporter
from services.wsdl_to_xsd_extractor import merge_xsd_from_wsdl
from services.excel_mapping_service import ExcelMappingService
from services.json_to_excel_service import JSONToExcelService
from services.case_converter_service import pascal_to_camel, camel_to_pascal


# Page configuration
st.set_page_config(
    page_title="The Forge - Schema Transformation Tool",
    page_icon="anvil.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main-header {
        background: #2d2d2d;
        color: #ffffff;
        padding: 2rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid #444444;
    }
    
    .main-header h1 {
        color: #ff6b35;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: #cccccc;
    }
    
    .section-header {
        background: #2d2d2d;
        color: #ffffff;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0 1rem 0;
        border: 1px solid #444444;
    }
    
    .section-header h2, .section-header h3 {
        color: #ff6b35;
        margin: 0;
    }
    .feature-card {
        background: #2d2d2d;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #444444;
        margin: 1rem 0;
        color: #ffffff;
    }
    .feature-card h3 {
        color: #ff6b35;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .feature-card p {
        color: #cccccc;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    .feature-card ul {
        color: #cccccc;
        margin-left: 1rem;
    }
    .feature-card li {
        color: #cccccc;
        margin-bottom: 0.5rem;
    }
    .stButton > button {
        background: #ff6b35;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: #e55a2b;
        transform: translateY(-1px);
    }
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
        margin: 1rem 0;
    }
    .success-message {
        background: #2d2d2d;
        color: #4CAF50;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        border: 1px solid #4CAF50;
    }
    .error-message {
        background: #2d2d2d;
        color: #f44336;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        border: 1px solid #f44336;
    }
    .warning-message {
        background: #2d2d2d;
        color: #ff9800;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        border: 1px solid #ff9800;
    }
    /* Minimalist Forge-Themed Sidebar */
    .sidebar .sidebar-content {
        background: #1a1a1a;
        border-right: 1px solid #333333;
        color: #ffffff;
    }
    
    /* Sidebar Header */
    .sidebar-header {
        background: #2d2d2d;
        color: #ffffff;
        padding: 2rem 1.5rem;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
        border-bottom: 1px solid #444444;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .sidebar-header h2 {
        margin: 0;
        font-size: 1.1rem;
        font-weight: 600;
        color: #ff6b35;
        letter-spacing: 0.5px;
    }
    
    .sidebar-header p {
        margin: 0.25rem 0 0 0;
        font-size: 0.8rem;
        color: #cccccc;
        opacity: 0.8;
    }
    
    /* Navigation Sections */
    .nav-section-title {
        color: #ff6b35;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 2rem 0 1rem 0;
        padding: 0.5rem 0;
        border-bottom: 1px solid #444444;
    }
    
    /* Navigation Buttons */
    .sidebar .stButton > button {
        background: transparent;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        font-weight: 400;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        margin: 0.25rem 0;
        width: 100%;
        text-align: left;
        position: relative;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .sidebar .stButton > button:hover {
        background: #333333;
        transform: translateX(4px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    }
    
    /* Active/Current Page Button */
    .sidebar .stButton > button[data-active="true"] {
        background: #ff6b35;
        color: #ffffff;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);
    }
    
    /* Divider Lines */
    .sidebar-divider {
        height: 1px;
        background: #444444;
        margin: 1.5rem 0;
        border: none;
        opacity: 0.6;
    }
    

    
    /* Footer Section */
    .sidebar-footer {
        margin-top: auto;
        padding: 1.5rem 0;
        text-align: center;
        color: #888888;
        font-size: 0.75rem;
        border-top: 1px solid #444444;
        background: #2d2d2d;
        margin: 2rem -1rem -1rem -1rem;
        padding: 1.5rem 1rem;
    }
    
    .sidebar-footer .version {
        background: #2d2d2d;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        margin-top: 0.5rem;
        font-family: 'Courier New', monospace;
        font-size: 0.7rem;
        color: #ff6b35;
        border: 1px solid #444444;
    }
    /* Dark Theme Styling */
    .main .block-container {
        background: #1a1a1a;
        color: #ffffff;
    }
    .main .block-container p {
        color: #cccccc;
        line-height: 1.6;
    }
    .main .block-container h1, .main .block-container h2, .main .block-container h3 {
        color: #ff6b35;
    }
    .main .block-container ul, .main .block-container ol {
        color: #cccccc;
    }
    .main .block-container li {
        color: #cccccc;
        margin-bottom: 0.5rem;
    }
    
    /* Streamlit Widget Styling */
    .stSelectbox, .stSlider, .stCheckbox {
        background: #2d2d2d;
        border: 1px solid #444444;
        border-radius: 6px;
    }
    
    .stFileUploader {
        background: #2d2d2d;
        border: 1px solid #444444;
        border-radius: 6px;
    }
    
    /* Code blocks */
    .stCode {
        background: #2d2d2d;
        border: 1px solid #444444;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize services with caching
@st.cache_resource
def get_services():
    return {
        'xsd_parser': XSDParser(),
        'json_schema_parser': JSONSchemaParser(),
        'excel_exporter': ExcelExporter(),
        'mapping_service': ExcelMappingService(),
        'json_to_excel': JSONToExcelService()
    }

def main():
    # Header
    st.markdown('''
        <div class="main-header">
            <h1>🔨 The Forge - Schema Transformation Tool</h1>
            <p style="font-size: 1.2rem; margin-top: 0.5rem;">Powerful schema transformation and mapping tool</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # Get services
    services = get_services()
    
    # Professional Sidebar Navigation
    st.sidebar.markdown("""
        <div class="sidebar-header">
            <h2>🔨 The Forge</h2>
            <p>Schema Transformation Tool</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Home"
    
    # Navigation Sections
    st.sidebar.markdown('<div class="nav-section-title">🏠 Navigation</div>', unsafe_allow_html=True)
    
    # Home Button
    home_active = st.session_state.current_page == "🏠 Home"
    if home_active:
        st.sidebar.markdown('<style>.sidebar .stButton > button[key="nav_home"] { background: #ff6b35 !important; color: #ffffff !important; font-weight: 500 !important; box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3) !important; }</style>', unsafe_allow_html=True)
    if st.sidebar.button("🏠 Home", use_container_width=True, key="nav_home"):
        st.session_state.current_page = "🏠 Home"
    
    st.sidebar.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    
    # Tools Section
    st.sidebar.markdown('<div class="nav-section-title">🔧 Tools</div>', unsafe_allow_html=True)
    
    # Schema Mapping
    mapping_active = st.session_state.current_page == "📊 Schema Mapping"
    if mapping_active:
        st.sidebar.markdown('<style>.sidebar .stButton > button[key="nav_mapping"] { background: #ff6b35 !important; color: #ffffff !important; font-weight: 500 !important; box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3) !important; }</style>', unsafe_allow_html=True)
    if st.sidebar.button("📊 Schema Mapping", use_container_width=True, key="nav_mapping"):
        st.session_state.current_page = "📊 Schema Mapping"
    
    # WSDL to XSD
    wsdl_active = st.session_state.current_page == "🔧 WSDL to XSD"
    if wsdl_active:
        st.sidebar.markdown('<style>.sidebar .stButton > button[key="nav_wsdl"] { background: #ff6b35 !important; color: #ffffff !important; font-weight: 500 !important; box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3) !important; }</style>', unsafe_allow_html=True)
    if st.sidebar.button("🔧 WSDL to XSD", use_container_width=True, key="nav_wsdl"):
        st.session_state.current_page = "🔧 WSDL to XSD"
    
    # Schema to Excel
    excel_active = st.session_state.current_page == "📋 Schema to Excel"
    if excel_active:
        st.sidebar.markdown('<style>.sidebar .stButton > button[key="nav_excel"] { background: #ff6b35 !important; color: #ffffff !important; font-weight: 500 !important; box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3) !important; }</style>', unsafe_allow_html=True)
    if st.sidebar.button("📋 Schema to Excel", use_container_width=True, key="nav_excel"):
        st.session_state.current_page = "📋 Schema to Excel"
    

    
    st.sidebar.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    
    # Info Section
    st.sidebar.markdown('<div class="nav-section-title">ℹ️ Information</div>', unsafe_allow_html=True)
    
    # About
    about_active = st.session_state.current_page == "ℹ️ About"
    if about_active:
        st.sidebar.markdown('<style>.sidebar .stButton > button[key="nav_about"] { background: #ff6b35 !important; color: #ffffff !important; font-weight: 500 !important; box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3) !important; }</style>', unsafe_allow_html=True)
    if st.sidebar.button("ℹ️ About", use_container_width=True, key="nav_about"):
        st.session_state.current_page = "ℹ️ About"
    
    # Footer
    st.sidebar.markdown("""
        <div class="sidebar-footer">
            <div>Built with Streamlit</div>
            <div class="version">v1.0.0</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Display current page
    if st.session_state.current_page == "🏠 Home":
        show_home_page()
    elif st.session_state.current_page == "📊 Schema Mapping":
        show_mapping_page(services)
    elif st.session_state.current_page == "🔧 WSDL to XSD":
        show_wsdl_to_xsd_page(services)
    elif st.session_state.current_page == "📋 Schema to Excel":
        show_schema_to_excel_page(services)

    elif st.session_state.current_page == "ℹ️ About":
        show_about_page()

def show_home_page():
    """
    Display the home page with feature overview and quick start guide.
    """
    st.markdown('<div class="section-header"><h2>🏠 Welcome to The Forge</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    **The Forge** is your comprehensive schema transformation toolkit. Transform, map, and analyze schema files with ease.
    """)
    
    # Feature cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Schema Mapping</h3>
            <p>Create field mappings between different schema formats (XSD, JSON Schema). 
            Automatically detect similarities and generate comprehensive mapping documentation.</p>
            <ul>
                <li>Support for XSD and JSON Schema</li>
                <li>Automatic similarity detection</li>
                <li>Excel export with detailed mapping</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>🔧 WSDL to XSD Extraction</h3>
            <p>Extract XSD schemas from WSDL files. Perfect for working with web services and SOAP APIs.</p>
            <ul>
                <li>Parse complex WSDL files</li>
                <li>Extract embedded XSD schemas</li>
                <li>Clean, formatted output</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📋 Schema to Excel</h3>
            <p>Convert schema files to Excel format for easy analysis and documentation.</p>
            <ul>
                <li>Detailed schema structure</li>
                <li>Element properties and types</li>
                <li>Ready for analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""

        """, unsafe_allow_html=True)
    
    # Quick start guide
    st.markdown('<div class="section-header"><h3>🚀 Quick Start</h3></div>', unsafe_allow_html=True)
    
    st.markdown("""
    1. **Schema Mapping**: Upload source and target schema files, then generate mappings
    2. **WSDL to XSD**: Upload a WSDL file to extract embedded XSD schemas
    3. **Schema to Excel**: Upload any schema file to convert it to Excel format

    
    All tools support XSD, XML, JSON Schema, and WSDL file formats.
    """)

def show_mapping_page(services):
    st.markdown('<div class="section-header"><h2>📊 Schema Mapping</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    Create field mappings between different schema formats. Upload source and target schema files to generate comprehensive mapping documentation.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Source Schema")
        source_file = st.file_uploader(
            "Upload source schema file",
            type=['xsd', 'xml', 'json'],
            key="source",
            help="Upload your source schema file (XSD, XML, or JSON Schema)"
        )
        
        if source_file:
            st.markdown(f'<div class="success-message">✅ Uploaded: {source_file.name}</div>', unsafe_allow_html=True)
            # Show file preview
            content = source_file.read()
            source_file.seek(0)  # Reset file pointer
            with st.expander("📄 File Preview"):
                try:
                    decoded_content = content.decode('utf-8')
                    preview = decoded_content[:1000] + "..." if len(decoded_content) > 1000 else decoded_content
                    # Determine language based on file extension
                    if source_file.name.lower().endswith('.json'):
                        st.code(preview, language="json")
                    else:
                        st.code(preview, language="xml")
                except UnicodeDecodeError:
                    st.code(content[:500], language="text")
    
    with col2:
        st.markdown("### 📥 Target Schema")
        target_file = st.file_uploader(
            "Upload target schema file",
            type=['xsd', 'xml', 'json'],
            key="target",
            help="Upload your target schema file (XSD, XML, or JSON Schema)"
        )
        
        if target_file:
            st.markdown(f'<div class="success-message">✅ Uploaded: {target_file.name}</div>', unsafe_allow_html=True)
            # Show file preview
            content = target_file.read()
            target_file.seek(0)  # Reset file pointer
            with st.expander("📄 File Preview"):
                try:
                    decoded_content = content.decode('utf-8')
                    preview = decoded_content[:1000] + "..." if len(decoded_content) > 1000 else decoded_content
                    # Determine language based on file extension
                    if target_file.name.lower().endswith('.json'):
                        st.code(preview, language="json")
                    else:
                        st.code(preview, language="xml")
                except UnicodeDecodeError:
                    st.code(content[:500], language="text")
    
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
    if st.button("🚀 Generate Mapping", type="primary", use_container_width=True):
        if source_file and target_file:
            with st.spinner("🔄 Generating mapping..."):
                try:
                    result = process_mapping(source_file, target_file, services, source_case, target_case, reorder_attributes, min_match_threshold)
                    if result:
                        st.markdown('<div class="success-message">✅ Mapping generated successfully!</div>', unsafe_allow_html=True)
                        st.download_button(
                            label="📥 Download Excel File",
                            data=result,
                            file_name="schema_mapping.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    else:
                        st.markdown('<div class="error-message">❌ Failed to generate mapping</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="error-message">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
            
        else:
            st.markdown('<div class="warning-message">⚠️ Please upload both source and target schema files</div>', unsafe_allow_html=True)

def show_wsdl_to_xsd_page(services):
    st.markdown('<div class="section-header"><h2>🔧 WSDL to XSD Extraction</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    Extract XSD schemas from WSDL files. Perfect for working with web services and SOAP APIs.
    """)
    
    wsdl_file = st.file_uploader(
        "Upload WSDL file",
        type=['wsdl', 'xml'],
        key="wsdl",
        help="Upload your WSDL file to extract embedded XSD schemas"
    )
    
    if wsdl_file:
        st.markdown(f'<div class="success-message">✅ Uploaded: {wsdl_file.name}</div>', unsafe_allow_html=True)
        # Show file preview
        content = wsdl_file.read()
        wsdl_file.seek(0)  # Reset file pointer
        with st.expander("📄 WSDL Preview"):
            try:
                decoded_content = content.decode('utf-8')
                preview = decoded_content[:1000] + "..." if len(decoded_content) > 1000 else decoded_content
                st.code(preview, language="xml")
            except UnicodeDecodeError:
                st.code(content[:500], language="text")
    
    if st.button("🔧 Extract XSD", type="primary", use_container_width=True):
        if wsdl_file:
            with st.spinner("🔄 Extracting XSD..."):
                try:
                    result = process_wsdl_to_xsd(wsdl_file, services)
                    if result:
                        st.markdown('<div class="success-message">✅ XSD extracted successfully!</div>', unsafe_allow_html=True)
                        st.download_button(
                            label="📥 Download XSD File",
                            data=result,
                            file_name="extracted_schema.xsd",
                            mime="application/xml",
                            use_container_width=True
                        )
                    else:
                        st.markdown('<div class="error-message">❌ Failed to extract XSD</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="error-message">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
            
        else:
            st.markdown('<div class="warning-message">⚠️ Please upload a WSDL file</div>', unsafe_allow_html=True)

def show_schema_to_excel_page(services):
    st.markdown('<div class="section-header"><h2>📋 Schema to Excel</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    Convert schema files to Excel format for easy analysis and documentation.
    """)
    
    schema_file = st.file_uploader(
        "Upload schema file",
        type=['xsd', 'xml', 'json'],
        key="schema",
        help="Upload your schema file (XSD, XML, or JSON Schema)"
    )
    
    if schema_file:
        st.markdown(f'<div class="success-message">✅ Uploaded: {schema_file.name}</div>', unsafe_allow_html=True)
        # Show file preview
        content = schema_file.read()
        schema_file.seek(0)  # Reset file pointer
        with st.expander("📄 File Preview"):
            try:
                decoded_content = content.decode('utf-8')
                preview = decoded_content[:1000] + "..." if len(decoded_content) > 1000 else decoded_content
                # Determine language based on file extension
                if schema_file.name.lower().endswith('.json'):
                    st.code(preview, language="json")
                else:
                    st.code(preview, language="xml")
            except UnicodeDecodeError:
                st.code(content[:500], language="text")
    
    if st.button("📋 Convert to Excel", type="primary", use_container_width=True):
        if schema_file:
            with st.spinner("🔄 Converting to Excel..."):
                try:
                    result = process_schema_to_excel(schema_file, services)
                    if result:
                        st.markdown('<div class="success-message">✅ Excel file generated successfully!</div>', unsafe_allow_html=True)
                        st.download_button(
                            label="📥 Download Excel File",
                            data=result,
                            file_name="schema_structure.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    else:
                        st.markdown('<div class="error-message">❌ Failed to generate Excel file</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="error-message">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
            
        else:
            st.markdown('<div class="warning-message">⚠️ Please upload a schema file</div>', unsafe_allow_html=True)



def show_about_page():
    """
    Display the about page with application information and features.
    """
    st.markdown('<div class="section-header"><h2>ℹ️ About The Forge</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    **The Forge** is a powerful schema transformation tool that provides comprehensive capabilities for working with schema files.
    
    ### 🎯 Core Features
    
    - **📊 Schema Mapping**: Create field mappings between different schema formats (XSD, JSON Schema)
    - **🔧 WSDL to XSD Extraction**: Extract XSD schemas from WSDL files
    - **📋 Schema to Excel**: Convert schema files to Excel format for analysis
    
    ### 📁 Supported Formats
    
    **Input Formats:**
    - XSD (.xsd)
    - XML (.xml)
    - JSON Schema (.json)
    - WSDL (.wsdl, .xml)
    
    **Output Formats:**
    - Excel (.xlsx)
    - XSD (.xsd)
    
    ### 🚀 Key Benefits
    
    - ✅ **No compilation issues** - Pure Python implementation
    - ✅ **Lightweight dependencies** - Minimal external requirements
    - ✅ **Cross-platform compatibility** - Works on Windows, macOS, Linux
    - ✅ **Production ready** - Robust error handling and validation
    - ✅ **Modern web interface** - Clean, responsive Streamlit UI
    
    ### 🔧 Technical Details
    
    This web version is based on The Forge v8 desktop application, adapted for online deployment with Streamlit.
    The application uses microservices architecture for modular functionality and easy maintenance.
    
    ### 📞 Support
    
    For issues, questions, or feature requests, please refer to the project documentation or create an issue in the repository.
    """)
    
    # Version info
    st.markdown("### 📋 Version Information")
    st.code("""
    The Forge Web App v1.0.0
    Built with Streamlit
    Based on The Forge v8 Desktop Application
    """)

def process_mapping(source_file, target_file, services, source_case="Original", target_case="Original", reorder_attributes=False, min_match_threshold=20):
    try:
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{source_file.name.split('.')[-1]}") as source_temp:
            source_temp.write(source_file.read())
            source_temp_path = source_temp.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_file.name.split('.')[-1]}") as target_temp:
            target_temp.write(target_file.read())
            target_temp_path = target_temp.name
        
        # --- Unified schema parsing logic for both XSD and JSON Schema ---
        
        # Parse source schema (XSD or JSON Schema)
        src_rows = parse_schema_file(source_temp_path, services)
        
        # Parse target schema (XSD or JSON Schema)
        tgt_rows = []
        if target_temp_path and os.path.exists(target_temp_path):
            tgt_rows = parse_schema_file(target_temp_path, services)
        
        # Group source rows by message/element name for multi-sheet structure
        src_messages = {}
        current_message = "schema"  # Default message name
        
        for row in src_rows:
            # For JSON Schema, we don't have multiple messages like XSD, so group by first level
            if len(row['levels']) > 0 and row['levels'][0]:
                current_message = row['levels'][0]
            
            if current_message not in src_messages:
                src_messages[current_message] = []
            src_messages[current_message].append(row)
        
        # Build Excel file
        wb = openpyxl.Workbook()
        first = True
        
        for msg_name, src_full_rows in src_messages.items():
            if not first:
                ws = wb.create_sheet(title=msg_name[:31])  # Excel sheet name limit
            else:
                ws = wb.active
                ws.title = msg_name[:31]
                first = False
            
            max_src_level = max((len(row['levels']) for row in src_full_rows), default=1)
            max_tgt_level = max((len(row['levels']) for row in tgt_rows), default=1) if tgt_rows else 1
            
            src_cols = [f'Level{i+1}_src' for i in range(max_src_level)] + ['Request Parameter_src', 'GDPR_src', 'Cardinality_src', 'Type_src', 'Base Type_src', 'Details_src', 'Description_src', 'Category_src', 'Example_src']
            tgt_cols = [f'Level{i+1}_tgt' for i in range(max_tgt_level)] + ['Request Parameter_tgt', 'GDPR_tgt', 'Cardinality_tgt', 'Type_tgt', 'Base Type_tgt', 'Details_tgt', 'Description_tgt', 'Category_tgt', 'Example_tgt']
            headers = src_cols + ['Destination Fields'] + tgt_cols
            ws.append(headers)
            ws.append([''] * len(headers))  # Second header row blank for now
            
            def row_path(row):
                return '.'.join(row['levels'])
            
            tgt_path_dict = {row_path(row): row for row in tgt_rows}
            tgt_paths = list(tgt_path_dict.keys())
            
            # Create a mapping of source paths to target paths based on similarity
            # This will help avoid duplicating target fields across multiple source rows
            source_to_target_mapping = {}
            
            for src_row in src_full_rows:
                # Apply case conversion to source levels if needed
                converted_levels = src_row['levels'].copy()
                if source_case == "PascalCase":
                    converted_levels = [camel_to_pascal(level) for level in converted_levels]
                elif source_case == "camelCase":
                    converted_levels = [pascal_to_camel(level) for level in converted_levels]
                
                src_levels = converted_levels + [''] * (max_src_level - len(converted_levels))
                src_vals = src_levels + [
                    src_row.get('Request Parameter',''),
                    src_row.get('GDPR',''),
                    src_row.get('Cardinality',''),
                    src_row.get('Type',''),
                    src_row.get('Base Type',''),
                    src_row.get('Details',''),
                    src_row.get('Description',''),
                    src_row.get('Category','element'),
                    src_row.get('Example','')
                ]
                
                src_path_str = row_path(src_row)
                
                # Check if we already have a mapping for this source path
                if src_path_str in source_to_target_mapping:
                    tgt_row = source_to_target_mapping[src_path_str]
                else:
                    # Try to find a match
                    tgt_row = tgt_path_dict.get(src_path_str)
                    best_match = ''
                    
                    if not tgt_row and tgt_paths:
                        # Use fuzzy matching with a higher threshold for better accuracy
                        matches = difflib.get_close_matches(src_path_str, tgt_paths, n=1, cutoff=0.6)
                        if matches:
                            best_match = matches[0]
                            tgt_row = tgt_path_dict[best_match]
                    
                    # Store the mapping to avoid re-computation
                    source_to_target_mapping[src_path_str] = tgt_row
                
                dest_field = ''  # Initialize destination field as empty
                
                # Apply case conversion to target levels if needed
                converted_tgt_levels = []
                if tgt_row:
                    converted_tgt_levels = tgt_row['levels'].copy()
                    if target_case == "PascalCase":
                        converted_tgt_levels = [camel_to_pascal(level) for level in converted_tgt_levels]
                    elif target_case == "camelCase":
                        converted_tgt_levels = [pascal_to_camel(level) for level in converted_tgt_levels]
                    # Set destination field to the matched target path
                    dest_field = '.'.join([lvl for lvl in converted_tgt_levels if lvl])
                    tgt_levels = converted_tgt_levels + [''] * (max_tgt_level - len(converted_tgt_levels))
                else:
                    tgt_levels = ['']*max_tgt_level
                    # Keep dest_field as empty string for unmatched source fields
                
                tgt_vals = tgt_levels + [
                    tgt_row.get('Request Parameter','') if tgt_row else '',
                    tgt_row.get('GDPR','') if tgt_row else '',
                    tgt_row.get('Cardinality','') if tgt_row else '',
                    tgt_row.get('Type','') if tgt_row else '',
                    tgt_row.get('Base Type','') if tgt_row else '',
                    tgt_row.get('Details','') if tgt_row else '',
                    tgt_row.get('Description','') if tgt_row else '',
                    tgt_row.get('Category','element') if tgt_row else '',
                    tgt_row.get('Example','') if tgt_row else ''
                ]
                
                ws.append(src_vals + [dest_field] + tgt_vals)
            
            # Add summary statistics
            total_source_fields = len(src_full_rows)
            matched_fields = sum(1 for src_row in src_full_rows 
                              if source_to_target_mapping.get(row_path(src_row)) is not None)
            unmatched_fields = total_source_fields - matched_fields
            
            # Check if we have enough matches to generate a meaningful mapping
            match_percentage = (matched_fields / total_source_fields * 100) if total_source_fields > 0 else 0
            
            if match_percentage < min_match_threshold:
                # Clean up temp files before returning
                os.unlink(source_temp_path)
                os.unlink(target_temp_path)
                
                # Provide detailed analysis
                st.warning(f"⚠️ **Schemas don't match well enough to generate a mapping**")
                st.markdown(f"""
                **Analysis Results:**
                - **Source fields:** {total_source_fields}
                - **Matched fields:** {matched_fields}
                - **Unmatched fields:** {unmatched_fields}
                - **Match percentage:** {match_percentage:.1f}%
                - **Minimum threshold:** {min_match_threshold}%
                
                **Possible reasons for low match:**
                - Different schema structures or naming conventions
                - Incompatible data models
                - Different business domains or use cases
                - Missing or extra fields in one of the schemas
                
                **Suggestions:**
                - Check if the schemas are from the same domain/business context
                - Verify that both schemas represent similar data structures
                - Consider using different source/target schemas that are more compatible
                - Review the field names and structure for potential manual mapping
                """)
                return None
            
            # Add summary row at the end
            summary_row = [''] * len(src_vals) + [f'SUMMARY: {matched_fields}/{total_source_fields} fields matched ({match_percentage:.1f}%)'] + [''] * len(tgt_vals)
            ws.append(summary_row)
            
            # Prune unused source level columns
            def last_nonempty_level_col(start_col, num_levels):
                for col in range(start_col + max_src_level - 1, start_col - 1, -1):
                    for row in ws.iter_rows(min_row=3, min_col=col, max_col=col):
                        if any(cell.value not in (None, '') for cell in row):
                            return col
                return start_col - 1
            
            src_level_start = 1
            last_src_col = last_nonempty_level_col(src_level_start, max_src_level)
            for col in range(src_level_start + max_src_level - 1, last_src_col, -1):
                ws.delete_cols(col)
            
            header_row = [cell.value for cell in ws[1]]
            try:
                tgt_level_start = header_row.index('Level1_tgt') + 1
            except ValueError:
                tgt_level_start = len(header_row) + 1
            
            for col in range(tgt_level_start + max_tgt_level - 1, tgt_level_start - 1, -1):
                col_letter = get_column_letter(col)
                if col > tgt_level_start and all((ws.cell(row=row, column=col).value in (None, '')) for row in range(3, ws.max_row + 1)):
                    ws.delete_cols(col)
        
        # Save to buffer
        output_buffer = BytesIO()
        wb.save(output_buffer)
        
        # --- Post-processing QA: Excel Output Validator ---
        xsd_path = source_temp_path if source_temp_path else target_temp_path
        try:
            from services.excel_output_validator import validate_excel_output, _log_messages
            _log_messages.clear()
            # Save to temporary file for validation
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_excel:
                output_buffer.seek(0)
                temp_excel.write(output_buffer.getvalue())
                temp_excel_path = temp_excel.name
            
            validate_excel_output(xsd_path, temp_excel_path)
            
            # Improved validation display
            if _log_messages:
                # Group messages by type
                success_messages = []
                error_messages = []
                warning_messages = []
                info_messages = []
                
                for line in _log_messages:
                    if line.startswith("[SUCCESS]"):
                        success_messages.append(line)
                    elif line.startswith("[ERROR]"):
                        error_messages.append(line)
                    elif line.startswith("[WARNING]"):
                        warning_messages.append(line)
                    elif line.startswith("[VALIDATE]"):
                        info_messages.append(line)
                    else:
                        info_messages.append(line)
                
                # Display validation summary in a compact format
                with st.expander("🔍 Validation Results", expanded=False):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if error_messages:
                            st.error(f"❌ {len(error_messages)} Field Errors")
                        else:
                            st.success("✅ No Field Errors")
                    
                    with col2:
                        if warning_messages:
                            st.warning(f"⚠️ {len(warning_messages)} Field Warnings")
                        else:
                            st.success("✅ No Field Warnings")
                    
                    with col3:
                        if success_messages:
                            st.success(f"✅ {len(success_messages)} Fields Validated")
                    
                    with col4:
                        if info_messages:
                            st.info(f"ℹ️ {len(info_messages)} Validation Steps")
                    
                    # Show detailed messages only if there are issues
                    if error_messages or warning_messages:
                        st.markdown("---")
                        if error_messages:
                            st.markdown("**❌ Field Errors:**")
                            for msg in error_messages[:5]:  # Limit to first 5 errors
                                st.text(f"  • {msg.replace('[ERROR]', '').strip()}")
                            if len(error_messages) > 5:
                                st.text(f"  ... and {len(error_messages) - 5} more field errors")
                        
                        if warning_messages:
                            st.markdown("**⚠️ Field Warnings:**")
                            for msg in warning_messages[:3]:  # Limit to first 3 warnings
                                st.text(f"  • {msg.replace('[WARNING]', '').strip()}")
                            if len(warning_messages) > 3:
                                st.text(f"  ... and {len(warning_messages) - 3} more field warnings")
                    else:
                        st.success("🎉 All validations passed successfully!")
            
            # Clean up temp validation file
            os.unlink(temp_excel_path)
        except Exception as e:
            st.error(f"❌ Error in post-processing validator: {e}")
        
        # --- Attribute reordering if flag is set ---
        if reorder_attributes:
            try:
                from services.reorder_excel_attributes import reorder_attributes_in_excel
                
                # Save to temporary file for reordering
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_excel:
                    output_buffer.seek(0)
                    temp_excel.write(output_buffer.getvalue())
                    temp_excel_path = temp_excel.name
                
                reorder_attributes_in_excel(temp_excel_path)
                
                # Read back the reordered file
                with open(temp_excel_path, 'rb') as f:
                    output_buffer.seek(0)
                    output_buffer.write(f.read())
                    output_buffer.truncate()
                
                # Clean up temp reordering file
                os.unlink(temp_excel_path)
            except Exception as e:
                st.error(f"Failed to reorder attributes: {str(e)}")
                # Continue without reordering rather than failing the entire process
        
        # Clean up temp files
        os.unlink(source_temp_path)
        os.unlink(target_temp_path)
        
        output_buffer.seek(0)
        
        # Show success message with match statistics
        st.success(f"✅ **Mapping generated successfully!** ({match_percentage:.1f}% of fields matched)")
        
        return output_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error in mapping: {str(e)}")
        return None

def process_wsdl_to_xsd(wsdl_file, services):
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

def process_schema_to_excel(schema_file, services):
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{schema_file.name.split('.')[-1]}") as temp_file:
            temp_file.write(schema_file.read())
            temp_path = temp_file.name
        
        # Parse schema
        schema_data = parse_schema_file(temp_path, services)
        
        # Create Excel file
        output_buffer = BytesIO()
        services['excel_exporter'].export({'schema': schema_data}, output_buffer)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        output_buffer.seek(0)
        return output_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error in schema to Excel: {str(e)}")
        return None



def parse_schema_file(file_path, services):
    """
    Parse a schema file (XSD or JSON Schema) and return rows in the same format.
    
    Args:
        file_path: Path to the schema file
        services: Dictionary containing parser services
        
    Returns:
        List of dictionaries with the same structure as XSD parser output
    """
    if file_path.endswith('.json'):
        # Handle JSON Schema
        return services['json_schema_parser'].parse_json_schema_file(file_path)
    else:
        # Handle XSD
        return services['xsd_parser'].parse_xsd_file(file_path)

if __name__ == "__main__":
    main() 