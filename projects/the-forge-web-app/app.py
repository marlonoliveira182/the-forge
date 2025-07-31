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
import logging
import sys
from datetime import datetime

# Configure logging to capture logs for frontend display
class StreamlitHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []
    
    def emit(self, record):
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': record.levelname,
            'message': self.format(record)
        }
        self.logs.append(log_entry)
        # Keep only last 100 logs to avoid memory issues
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]

# Create a global handler for frontend logging
frontend_handler = StreamlitHandler()
frontend_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(frontend_handler)

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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .section-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        color: #333333;
    }
    .feature-card h3 {
        color: #2c3e50;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .feature-card p {
        color: #555555;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    .feature-card ul {
        color: #555555;
        margin-left: 1rem;
    }
    .feature-card li {
        color: #555555;
        margin-bottom: 0.5rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
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
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .error-message {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .warning-message {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .sidebar .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        margin: 4px 0;
        width: 100%;
    }
    .sidebar .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    .sidebar .stButton > button[data-baseweb="button"] {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
    }
    .sidebar .stButton > button[data-baseweb="button"]:hover {
        background: linear-gradient(135deg, #20c997 0%, #28a745 100%);
    }
    .sidebar h3 {
        color: #495057;
        font-weight: 600;
        margin: 16px 0 8px 0;
        padding-bottom: 4px;
        border-bottom: 2px solid #e9ecef;
    }
    .sidebar hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 16px 0;
    }
    .current-page-indicator {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: 600;
        text-align: center;
        margin: 8px 0;
    }
    /* Improve text readability */
    .main .block-container {
        color: #333333;
    }
    .main .block-container p {
        color: #555555;
        line-height: 1.6;
    }
    .main .block-container h1, .main .block-container h2, .main .block-container h3 {
        color: #2c3e50;
    }
    .main .block-container ul, .main .block-container ol {
        color: #555555;
    }
    .main .block-container li {
        color: #555555;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize services with caching
@st.cache_resource
def get_services():
    return {
        'xsd_parser': XSDParser(),
        'excel_exporter': ExcelExporter(),
        'mapping_service': ExcelMappingService(),
        'json_to_excel': JSONToExcelService()
    }

def main():
    # Header
    st.markdown('''
        <div class="main-header">
            <h1>🔧 The Forge - Schema Transformation Tool</h1>
            <p style="font-size: 1.2rem; margin-top: 0.5rem;">Powerful schema transformation and mapping tool</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # Get services
    services = get_services()
    
    # Sidebar navigation
    st.sidebar.markdown("## 🧭 Navigation")
    
    # Navigation buttons
    if st.sidebar.button("🏠 Home", use_container_width=True, type="secondary"):
        st.session_state.current_page = "🏠 Home"
    
    st.sidebar.markdown("### 🔧 Tools")
    
    if st.sidebar.button("📊 Schema Mapping", use_container_width=True):
        st.session_state.current_page = "📊 Schema Mapping"
    
    if st.sidebar.button("🔧 WSDL to XSD", use_container_width=True):
        st.session_state.current_page = "🔧 WSDL to XSD"
    
    if st.sidebar.button("📋 Schema to Excel", use_container_width=True):
        st.session_state.current_page = "📋 Schema to Excel"
    
    st.sidebar.markdown("### ℹ️ Info")
    
    if st.sidebar.button("ℹ️ About", use_container_width=True):
        st.session_state.current_page = "ℹ️ About"
    
    # Initialize session state if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Home"
    
    # Show current page indicator
    st.sidebar.markdown("---")
    st.sidebar.markdown(f'<div class="current-page-indicator">📍 {st.session_state.current_page}</div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
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
        <div class="feature-card">
            <h3>🚀 Key Features</h3>
            <ul>
                <li>✅ No compilation issues</li>
                <li>✅ Lightweight dependencies</li>
                <li>✅ Cross-platform compatibility</li>
                <li>✅ Production ready</li>
                <li>✅ Modern web interface</li>
            </ul>
        </div>
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
                    st.code(preview, language="xml")
                except UnicodeDecodeError:
                    st.code(content[:500], language="text")
    
    # Settings
    st.markdown("### ⚙️ Settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.7, 0.1, 
                            help="Minimum similarity score for automatic field matching")
    with col2:
        keep_case = st.checkbox("Keep Original Case", value=False, 
                               help="Preserve original field names case")
    with col3:
        reorder_attributes = st.checkbox("Reorder Attributes First", value=False,
                                       help="Reorder attributes to appear before elements in each parent structure")
    
    # Debug logging section
    st.markdown("### 🔍 Debug Logs")
    show_debug_logs = st.checkbox("Show Debug Logs", value=True, 
                                 help="Display detailed debug logs to track execution")
    
    # Generate mapping button
    if st.button("🚀 Generate Mapping", type="primary", use_container_width=True):
        if source_file and target_file:
            # Clear previous logs
            frontend_handler.logs.clear()
            
            with st.spinner("🔄 Generating mapping..."):
                try:
                    result = process_mapping(source_file, target_file, services, threshold, keep_case, reorder_attributes)
                    if result:
                        st.markdown('<div class="success-message">✅ Mapping generated successfully!</div>', unsafe_allow_html=True)
                        # Download button above logs
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
            
            # Display logs if enabled
            if show_debug_logs and frontend_handler.logs:
                st.markdown("### 📋 Execution Logs")
                
                # Create a scrollable container with fixed height
                log_container = st.container()
                with log_container:
                    # Use HTML to create a scrollable div with fixed height
                    log_html = """
                    <div style="
                        max-height: 300px; 
                        overflow-y: auto; 
                        border: 1px solid #e0e0e0; 
                        border-radius: 8px; 
                        padding: 10px; 
                        background-color: #f8f9fa;
                        font-family: 'Courier New', monospace;
                        font-size: 12px;
                        line-height: 1.4;
                    ">
                    """
                    
                    for log_entry in frontend_handler.logs:
                        timestamp = log_entry['timestamp']
                        message = log_entry['message']
                        level = log_entry['level']
                        
                        # Color code based on log level
                        if level == 'ERROR':
                            color = '#dc3545'
                            icon = '❌'
                        elif level == 'WARNING':
                            color = '#ffc107'
                            icon = '⚠️'
                        elif level == 'DEBUG':
                            color = '#17a2b8'
                            icon = '🔍'
                        else:
                            color = '#6c757d'
                            icon = 'ℹ️'
                        
                        log_html += f'<div style="margin-bottom: 4px;"><span style="color: {color}; font-weight: bold;">{icon} [{timestamp}]</span> <span style="color: #333;">{message}</span></div>'
                    
                    log_html += "</div>"
                    st.markdown(log_html, unsafe_allow_html=True)
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
    
    # Debug logging section
    st.markdown("### 🔍 Debug Logs")
    show_debug_logs = st.checkbox("Show Debug Logs", value=True, key="wsdl_logs",
                                 help="Display detailed debug logs to track execution")
    
    if st.button("🔧 Extract XSD", type="primary", use_container_width=True):
        if wsdl_file:
            # Clear previous logs
            frontend_handler.logs.clear()
            
            with st.spinner("🔄 Extracting XSD..."):
                try:
                    result = process_wsdl_to_xsd(wsdl_file, services)
                    if result:
                        st.markdown('<div class="success-message">✅ XSD extracted successfully!</div>', unsafe_allow_html=True)
                        # Download button above logs
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
            
            # Display logs if enabled
            if show_debug_logs and frontend_handler.logs:
                st.markdown("### 📋 Execution Logs")
                
                # Create a scrollable container with fixed height
                log_container = st.container()
                with log_container:
                    # Use HTML to create a scrollable div with fixed height
                    log_html = """
                    <div style="
                        max-height: 300px; 
                        overflow-y: auto; 
                        border: 1px solid #e0e0e0; 
                        border-radius: 8px; 
                        padding: 10px; 
                        background-color: #f8f9fa;
                        font-family: 'Courier New', monospace;
                        font-size: 12px;
                        line-height: 1.4;
                    ">
                    """
                    
                    for log_entry in frontend_handler.logs:
                        timestamp = log_entry['timestamp']
                        message = log_entry['message']
                        level = log_entry['level']
                        
                        # Color code based on log level
                        if level == 'ERROR':
                            color = '#dc3545'
                            icon = '❌'
                        elif level == 'WARNING':
                            color = '#ffc107'
                            icon = '⚠️'
                        elif level == 'DEBUG':
                            color = '#17a2b8'
                            icon = '🔍'
                        else:
                            color = '#6c757d'
                            icon = 'ℹ️'
                        
                        log_html += f'<div style="margin-bottom: 4px;"><span style="color: {color}; font-weight: bold;">{icon} [{timestamp}]</span> <span style="color: #333;">{message}</span></div>'
                    
                    log_html += "</div>"
                    st.markdown(log_html, unsafe_allow_html=True)
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
                st.code(preview, language="xml")
            except UnicodeDecodeError:
                st.code(content[:500], language="text")
    
    keep_case = st.checkbox("Keep Original Case", value=False, key="schema_case",
                           help="Preserve original field names case")
    
    # Debug logging section
    st.markdown("### 🔍 Debug Logs")
    show_debug_logs = st.checkbox("Show Debug Logs", value=True, key="schema_logs",
                                 help="Display detailed debug logs to track execution")
    
    if st.button("📋 Convert to Excel", type="primary", use_container_width=True):
        if schema_file:
            # Clear previous logs
            frontend_handler.logs.clear()
            
            with st.spinner("🔄 Converting to Excel..."):
                try:
                    result = process_schema_to_excel(schema_file, services, keep_case)
                    if result:
                        st.markdown('<div class="success-message">✅ Excel file generated successfully!</div>', unsafe_allow_html=True)
                        # Download button above logs
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
            
            # Display logs if enabled
            if show_debug_logs and frontend_handler.logs:
                st.markdown("### 📋 Execution Logs")
                
                # Create a scrollable container with fixed height
                log_container = st.container()
                with log_container:
                    # Use HTML to create a scrollable div with fixed height
                    log_html = """
                    <div style="
                        max-height: 300px; 
                        overflow-y: auto; 
                        border: 1px solid #e0e0e0; 
                        border-radius: 8px; 
                        padding: 10px; 
                        background-color: #f8f9fa;
                        font-family: 'Courier New', monospace;
                        font-size: 12px;
                        line-height: 1.4;
                    ">
                    """
                    
                    for log_entry in frontend_handler.logs:
                        timestamp = log_entry['timestamp']
                        message = log_entry['message']
                        level = log_entry['level']
                        
                        # Color code based on log level
                        if level == 'ERROR':
                            color = '#dc3545'
                            icon = '❌'
                        elif level == 'WARNING':
                            color = '#ffc107'
                            icon = '⚠️'
                        elif level == 'DEBUG':
                            color = '#17a2b8'
                            icon = '🔍'
                        else:
                            color = '#6c757d'
                            icon = 'ℹ️'
                        
                        log_html += f'<div style="margin-bottom: 4px;"><span style="color: {color}; font-weight: bold;">{icon} [{timestamp}]</span> <span style="color: #333;">{message}</span></div>'
                    
                    log_html += "</div>"
                    st.markdown(log_html, unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-message">⚠️ Please upload a schema file</div>', unsafe_allow_html=True)

def show_about_page():
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

def process_mapping(source_file, target_file, services, threshold, keep_case, reorder_attributes=False):
    """Process schema mapping using exact v8 logic"""
    logger.debug(f"Starting process_mapping with reorder_attributes={reorder_attributes}")
    try:
        # Create temporary files
        logger.debug("Creating temporary files...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{source_file.name.split('.')[-1]}") as source_temp:
            source_temp.write(source_file.read())
            source_temp_path = source_temp.name
            logger.debug(f"Created source temp file: {source_temp_path}")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_file.name.split('.')[-1]}") as target_temp:
            target_temp.write(target_file.read())
            target_temp_path = target_temp.name
            logger.debug(f"Created target temp file: {target_temp_path}")
        
        # --- v8 logic: parse source and target, multi-message, row matching, column structure ---
        
        XSD_NS = '{http://www.w3.org/2001/XMLSchema}'
        parser = services['xsd_parser']
        
        # Parse source XSD
        tree = ET.parse(source_temp_path)
        root = tree.getroot()
        simple_types = {}
        for simple_type in root.findall(f'.//{{http://www.w3.org/2001/XMLSchema}}simpleType'):
            name = simple_type.get('name')
            if not name:
                continue
            restriction = simple_type.find('{http://www.w3.org/2001/XMLSchema}restriction')
            base = restriction.get('base') if restriction is not None else None
            restrictions = {}
            if restriction is not None:
                for cons in restriction:
                    cons_name = cons.tag.replace('{http://www.w3.org/2001/XMLSchema}', '')
                    val = cons.get('value')
                    if val:
                        restrictions[cons_name] = val
            simple_types[name] = {'base': base, 'restrictions': restrictions}
        
        complex_types = {ct.get('name'): ct for ct in root.findall(f'.//{{http://www.w3.org/2001/XMLSchema}}complexType') if ct.get('name')}
        src_messages = {}
        for elem in root.findall('{http://www.w3.org/2001/XMLSchema}element'):
            name = elem.get('name')
            if name:
                rows = parser.parse_element(elem, complex_types, simple_types, 1, category='message')
                src_messages[name] = rows
        
        # Parse target XSD (single sheet)
        tgt_rows = []
        if target_temp_path and os.path.exists(target_temp_path):
            tgt_tree = ET.parse(target_temp_path)
            tgt_root = tgt_tree.getroot()
            tgt_simple_types = {}
            for simple_type in tgt_root.findall(f'.//{{http://www.w3.org/2001/XMLSchema}}simpleType'):
                name = simple_type.get('name')
                if not name:
                    continue
                restriction = simple_type.find('{http://www.w3.org/2001/XMLSchema}restriction')
                base = restriction.get('base') if restriction is not None else None
                restrictions = {}
                if restriction is not None:
                    for cons in restriction:
                        cons_name = cons.tag.replace('{http://www.w3.org/2001/XMLSchema}', '')
                        val = cons.get('value')
                        if val:
                            restrictions[cons_name] = val
                tgt_simple_types[name] = {'base': base, 'restrictions': restrictions}
            tgt_complex_types = {ct.get('name'): ct for ct in tgt_root.findall(f'.//{{http://www.w3.org/2001/XMLSchema}}complexType') if ct.get('name')}
            for elem in tgt_root.findall('{http://www.w3.org/2001/XMLSchema}element'):
                rows = parser.parse_element(elem, tgt_complex_types, tgt_simple_types, 1, category='message')
                tgt_rows.extend(rows)
        
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
            
            for src_row in src_full_rows:
                src_levels = src_row['levels'] + [''] * (max_src_level - len(src_row['levels']))
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
                tgt_row = tgt_path_dict.get(src_path_str)
                best_match = ''
                if not tgt_row and tgt_paths:
                    matches = difflib.get_close_matches(src_path_str, tgt_paths, n=1, cutoff=0.0)
                    if matches:
                        best_match = matches[0]
                        tgt_row = tgt_path_dict[best_match]
                
                tgt_levels = tgt_row['levels'] + [''] * (max_tgt_level - len(tgt_row['levels'])) if tgt_row else ['']*max_tgt_level
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
                
                dest_field = '.'.join([lvl for lvl in tgt_row['levels'] if lvl]) if tgt_row else ''
                ws.append(src_vals + [dest_field] + tgt_vals)
            
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
            for line in _log_messages:
                if line.startswith("[SUCCESS]"):
                    st.success(line)
                elif line.startswith("[ERROR]"):
                    st.error(line)
                elif line.startswith("[WARNING]"):
                    st.warning(line)
                elif line.startswith("[VALIDATE]"):
                    st.info(line)
                else:
                    st.info(line)
            
            # Clean up temp validation file
            os.unlink(temp_excel_path)
        except Exception as e:
            st.error(f"❌ Error in post-processing validator: {e}")
        
        # --- Attribute reordering if flag is set ---
        if reorder_attributes:
            logger.debug("Starting attribute reordering process...")
            try:
                from services.reorder_excel_attributes import reorder_attributes_in_excel
                logger.debug("Successfully imported reorder_attributes_in_excel")
                
                # Save to temporary file for reordering
                logger.debug("Creating temporary Excel file for reordering...")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_excel:
                    output_buffer.seek(0)
                    temp_excel.write(output_buffer.getvalue())
                    temp_excel_path = temp_excel.name
                    logger.debug(f"Created temp Excel file for reordering: {temp_excel_path}")
                
                logger.debug("Calling reorder_attributes_in_excel...")
                reorder_attributes_in_excel(temp_excel_path)
                logger.debug("reorder_attributes_in_excel completed successfully")
                
                # Read back the reordered file
                logger.debug("Reading back the reordered file...")
                with open(temp_excel_path, 'rb') as f:
                    output_buffer.seek(0)
                    output_buffer.write(f.read())
                    output_buffer.truncate()
                
                # Clean up temp reordering file
                logger.debug("Cleaning up temp reordering file...")
                os.unlink(temp_excel_path)
                logger.debug("Attribute reordering completed successfully")
                st.info("[INFO] Reordered attributes to appear first in each parent structure.")
            except Exception as e:
                logger.error(f"Exception during attribute reordering: {e}", exc_info=True)
                st.error(f"[ERROR] Failed to reorder attributes: {str(e)}")
                # Continue without reordering rather than failing the entire process
        
        # Clean up temp files
        os.unlink(source_temp_path)
        os.unlink(target_temp_path)
        
        output_buffer.seek(0)
        return output_buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Exception in process_mapping: {e}", exc_info=True)
        st.error(f"Error in mapping: {str(e)}")
        return None

def process_wsdl_to_xsd(wsdl_file, services):
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

def process_schema_to_excel(schema_file, services, keep_case):
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
        services['excel_exporter'].export({'schema': schema_data}, output_buffer)
        
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