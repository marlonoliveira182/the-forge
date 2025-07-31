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
from streamlit_extras.card import card
from streamlit_extras.let_it_rain import rain
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

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
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/your-repo/the-forge',
        'Report a bug': 'https://github.com/your-repo/the-forge/issues',
        'About': 'The Forge - Advanced Schema Transformation Tool'
    }
)

# Modern CSS with proper color theory and UI/UX best practices
st.markdown("""
<style>
    /* Modern Color Palette - Based on Material Design 3 */
    :root {
        --primary-50: #f0f9ff;
        --primary-100: #e0f2fe;
        --primary-200: #bae6fd;
        --primary-300: #7dd3fc;
        --primary-400: #38bdf8;
        --primary-500: #0ea5e9;
        --primary-600: #0284c7;
        --primary-700: #0369a1;
        --primary-800: #075985;
        --primary-900: #0c4a6e;
        
        --surface-0: #ffffff;
        --surface-50: #f8fafc;
        --surface-100: #f1f5f9;
        --surface-200: #e2e8f0;
        --surface-300: #cbd5e1;
        --surface-400: #94a3b8;
        --surface-500: #64748b;
        --surface-600: #475569;
        --surface-700: #334155;
        --surface-800: #1e293b;
        --surface-900: #0f172a;
        
        --success-500: #10b981;
        --success-600: #059669;
        --warning-500: #f59e0b;
        --warning-600: #d97706;
        --error-500: #ef4444;
        --error-600: #dc2626;
        
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --text-tertiary: #94a3b8;
        --text-on-primary: #ffffff;
        
        --border-light: #e2e8f0;
        --border-medium: #cbd5e1;
        --border-dark: #94a3b8;
        
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
        
        --spacing-xs: 0.25rem;
        --spacing-sm: 0.5rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --spacing-xl: 2rem;
        --spacing-2xl: 3rem;
    }
    
    /* Dark mode variables */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, var(--surface-50) 0%, var(--surface-100) 100%);
    }
    
    /* Global Typography */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        line-height: 1.6;
    }
    
    /* Modern Header */
    .main-header {
        background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
        color: var(--text-on-primary);
        padding: var(--spacing-2xl) var(--spacing-xl);
        border-radius: var(--radius-xl);
        text-align: center;
        margin-bottom: var(--spacing-xl);
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
        opacity: 0.3;
    }
    
    .main-header h1 {
        color: var(--text-on-primary);
        margin-bottom: var(--spacing-sm);
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        color: var(--primary-100);
        font-size: 1.125rem;
        margin-top: var(--spacing-sm);
        position: relative;
        z-index: 1;
    }
    
    /* Modern Section Headers */
    .section-header {
        background: var(--surface-0);
        color: var(--text-primary);
        padding: var(--spacing-lg) var(--spacing-xl);
        border-radius: var(--radius-lg);
        margin: var(--spacing-xl) 0 var(--spacing-lg) 0;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-sm);
        position: relative;
    }
    
    .section-header h2, .section-header h3 {
        color: var(--text-primary);
        margin: 0;
        font-weight: 600;
        font-size: 1.5rem;
        letter-spacing: -0.025em;
    }
    
    /* Modern Cards */
    .modern-card {
        background: var(--surface-0);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        padding: var(--spacing-xl);
        margin: var(--spacing-lg) 0;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }
    
    .modern-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    
    .modern-card h3 {
        color: var(--text-primary);
        margin-bottom: var(--spacing-md);
        font-weight: 600;
        font-size: 1.25rem;
    }
    
    .modern-card p {
        color: var(--text-secondary);
        line-height: 1.6;
        margin-bottom: var(--spacing-md);
    }
    
    /* Modern Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
        color: var(--text-on-primary);
        border: none;
        border-radius: var(--radius-md);
        padding: var(--spacing-md) var(--spacing-lg);
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-700) 0%, var(--primary-800) 100%);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary Button Style */
    .secondary-button {
        background: var(--surface-100) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-medium) !important;
    }
    
    .secondary-button:hover {
        background: var(--surface-200) !important;
        border-color: var(--border-dark) !important;
    }
    
    /* Modern Upload Area */
    .upload-area {
        border: 2px dashed var(--primary-300);
        border-radius: var(--radius-lg);
        padding: var(--spacing-2xl) var(--spacing-xl);
        text-align: center;
        background: linear-gradient(135deg, var(--primary-50) 0%, var(--primary-100) 100%);
        margin: var(--spacing-lg) 0;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .upload-area:hover {
        border-color: var(--primary-500);
        background: linear-gradient(135deg, var(--primary-100) 0%, var(--primary-200) 100%);
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    /* Modern Message Styles */
    .success-message {
        background: linear-gradient(135deg, var(--success-500) 0%, var(--success-600) 100%);
        color: var(--text-on-primary);
        padding: var(--spacing-lg);
        border-radius: var(--radius-lg);
        margin: var(--spacing-lg) 0;
        box-shadow: var(--shadow-sm);
        border-left: 4px solid var(--success-600);
    }
    
    .error-message {
        background: linear-gradient(135deg, var(--error-500) 0%, var(--error-600) 100%);
        color: var(--text-on-primary);
        padding: var(--spacing-lg);
        border-radius: var(--radius-lg);
        margin: var(--spacing-lg) 0;
        box-shadow: var(--shadow-sm);
        border-left: 4px solid var(--error-600);
    }
    
    .warning-message {
        background: linear-gradient(135deg, var(--warning-500) 0%, var(--warning-600) 100%);
        color: var(--text-on-primary);
        padding: var(--spacing-lg);
        border-radius: var(--radius-lg);
        margin: var(--spacing-lg) 0;
        box-shadow: var(--shadow-sm);
        border-left: 4px solid var(--warning-600);
    }
    
    /* Modern Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: var(--spacing-sm);
        background: var(--surface-0);
        border-radius: var(--radius-lg);
        padding: var(--spacing-sm);
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-sm);
        margin-bottom: var(--spacing-lg);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-secondary);
        border-radius: var(--radius-md);
        padding: var(--spacing-md) var(--spacing-lg);
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--surface-100);
        color: var(--text-primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
        color: var(--text-on-primary);
        font-weight: 600;
        box-shadow: var(--shadow-sm);
    }
    
    /* Modern Form Elements */
    .stSelectbox, .stSlider, .stCheckbox {
        background: var(--surface-0);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
    }
    
    .stFileUploader {
        background: var(--surface-0);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        padding: var(--spacing-md);
    }
    
    /* Modern Code blocks */
    .stCode {
        background: var(--surface-800);
        border: 1px solid var(--border-dark);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
        color: var(--surface-100);
    }
    
    /* Modern DataFrames */
    .dataframe {
        background: var(--surface-0);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
    }
    
    /* Modern Progress Bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
        border-radius: var(--radius-sm);
    }
    
    /* Modern Expander */
    .streamlit-expanderHeader {
        background: var(--surface-0);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: var(--spacing-md);
        font-weight: 500;
        color: var(--text-primary);
    }
    
    /* Modern Spinner */
    .stSpinner > div {
        border-color: var(--primary-600);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: var(--spacing-lg) var(--spacing-md);
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .section-header {
            padding: var(--spacing-md);
        }
        
        .modern-card {
            padding: var(--spacing-lg);
        }
    }
    
    /* Accessibility Improvements */
    .stButton > button:focus {
        outline: 2px solid var(--primary-500);
        outline-offset: 2px;
    }
    
    .stTabs [data-baseweb="tab"]:focus {
        outline: 2px solid var(--primary-500);
        outline-offset: 2px;
    }
    
    /* Smooth Scrolling */
    html {
        scroll-behavior: smooth;
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
    # Modern Header
    st.markdown('''
        <div class="main-header">
            <h1>🔨 The Forge</h1>
            <p>Advanced Schema Transformation & Mapping Tool</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # Get services
    services = get_services()
    
    # Initialize session state if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    
    # Tab Navigation Menu
    selected = st.tabs(["Home", "Schema Mapping", "WSDL to XSD", "Schema to Excel", "About"])
    
    # Display current page based on tab selection
    if selected[0]:
        show_home_page()
    elif selected[1]:
        show_mapping_page(services)
    elif selected[2]:
        show_wsdl_to_xsd_page(services)
    elif selected[3]:
        show_schema_to_excel_page(services)
    elif selected[4]:
        show_about_page()

def show_home_page():
    """
    Display the home page with modern UI components and feature overview.
    """
    st.markdown('<div class="section-header"><h2>Welcome to The Forge</h2></div>', unsafe_allow_html=True)
    
    # Modern welcome message
    st.markdown("""
    **The Forge** is your comprehensive schema transformation toolkit. Transform, map, and analyze schema files with ease using our powerful, modern interface.
    """)
    
    # Feature cards using modern design
    col1, col2 = st.columns(2)
    
    with col1:
        # Schema Mapping Card
        card(
            title="Schema Mapping",
            text="Create field mappings between different schema formats (XSD, JSON Schema). Automatically detect similarities and generate comprehensive mapping documentation.",
            styles={
                "card": {
                    "width": "100%",
                    "height": "100%",
                    "background": "var(--surface-0)",
                    "border": "1px solid var(--border-light)",
                    "border-radius": "var(--radius-lg)",
                    "padding": "var(--spacing-xl)",
                    "margin": "var(--spacing-lg) 0",
                    "box-shadow": "var(--shadow-sm)",
                    "transition": "all 0.2s ease"
                },
                "title": {
                    "color": "var(--text-primary)",
                    "font-weight": "600",
                    "font-size": "1.25rem",
                    "margin-bottom": "var(--spacing-md)"
                },
                "text": {
                    "color": "var(--text-secondary)",
                    "line-height": "1.6"
                }
            }
        )
        
        # WSDL to XSD Card
        card(
            title="WSDL to XSD Extraction",
            text="Extract XSD schemas from WSDL files. Perfect for working with web services and SOAP APIs.",
            styles={
                "card": {
                    "width": "100%",
                    "height": "100%",
                    "background": "var(--surface-0)",
                    "border": "1px solid var(--border-light)",
                    "border-radius": "var(--radius-lg)",
                    "padding": "var(--spacing-xl)",
                    "margin": "var(--spacing-lg) 0",
                    "box-shadow": "var(--shadow-sm)",
                    "transition": "all 0.2s ease"
                },
                "title": {
                    "color": "var(--text-primary)",
                    "font-weight": "600",
                    "font-size": "1.25rem",
                    "margin-bottom": "var(--spacing-md)"
                },
                "text": {
                    "color": "var(--text-secondary)",
                    "line-height": "1.6"
                }
            }
        )
    
    with col2:
        # Schema to Excel Card
        card(
            title="Schema to Excel",
            text="Convert schema files to Excel format for easy analysis and documentation.",
            styles={
                "card": {
                    "width": "100%",
                    "height": "100%",
                    "background": "var(--surface-0)",
                    "border": "1px solid var(--border-light)",
                    "border-radius": "var(--radius-lg)",
                    "padding": "var(--spacing-xl)",
                    "margin": "var(--spacing-lg) 0",
                    "box-shadow": "var(--shadow-sm)",
                    "transition": "all 0.2s ease"
                },
                "title": {
                    "color": "var(--text-primary)",
                    "font-weight": "600",
                    "font-size": "1.25rem",
                    "margin-bottom": "var(--spacing-md)"
                },
                "text": {
                    "color": "var(--text-secondary)",
                    "line-height": "1.6"
                }
            }
        )
        
        # Quick Start Card
        card(
            title="Quick Start Guide",
            text="1. **Schema Mapping**: Upload source and target schema files\n2. **WSDL to XSD**: Upload a WSDL file to extract schemas\n3. **Schema to Excel**: Upload any schema file to convert",
            styles={
                "card": {
                    "width": "100%",
                    "height": "100%",
                    "background": "var(--surface-0)",
                    "border": "1px solid var(--border-light)",
                    "border-radius": "var(--radius-lg)",
                    "padding": "var(--spacing-xl)",
                    "margin": "var(--spacing-lg) 0",
                    "box-shadow": "var(--shadow-sm)",
                    "transition": "all 0.2s ease"
                },
                "title": {
                    "color": "var(--text-primary)",
                    "font-weight": "600",
                    "font-size": "1.25rem",
                    "margin-bottom": "var(--spacing-md)"
                },
                "text": {
                    "color": "var(--text-secondary)",
                    "line-height": "1.6"
                }
            }
        )
    
    # Add some visual flair
    if st.button("🎉 Celebrate!", key="celebrate"):
        rain(
            emoji="🔨",
            font_size=54,
            falling_speed=5,
            animation_length="infinite",
        )
    
    st.markdown("""
    All tools support XSD, XML, JSON Schema, and WSDL file formats.
    """)

def show_mapping_page(services):
    st.markdown('<div class="section-header"><h2>Schema Mapping</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    Create field mappings between different schema formats. Upload source and target schema files to generate comprehensive mapping documentation.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Source Schema")
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
        st.markdown("### Target Schema")
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
    st.markdown("### Settings")
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
    if st.button("Generate Mapping", type="primary", use_container_width=True):
        if source_file and target_file:
            with st.spinner("Generating mapping..."):
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
    st.markdown('<div class="section-header"><h2>WSDL to XSD Extraction</h2></div>', unsafe_allow_html=True)
    
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
    
    if st.button("Extract XSD", type="primary", use_container_width=True):
        if wsdl_file:
            with st.spinner("Extracting XSD..."):
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
    st.markdown('<div class="section-header"><h2>Schema to Excel</h2></div>', unsafe_allow_html=True)
    
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
    
    if st.button("Convert to Excel", type="primary", use_container_width=True):
        if schema_file:
            with st.spinner("Converting to Excel..."):
                try:
                    # Convert to Excel
                    result = process_schema_to_excel(schema_file, services)
                    if result:
                        st.markdown('<div class="success-message">✅ Excel file generated successfully!</div>', unsafe_allow_html=True)
                        
                        # Show preview using AgGrid
                        try:
                            import pandas as pd
                            from io import BytesIO
                            
                            # Read the Excel file into a DataFrame
                            df = pd.read_excel(BytesIO(result))
                            
                            st.markdown("### 📊 Data Preview")
                            
                            # Configure AgGrid
                            gb = GridOptionsBuilder.from_dataframe(df)
                            gb.configure_pagination(paginationAutoPageSize=True)
                            gb.configure_side_bar()
                            gb.configure_selection('single', use_checkbox=True)
                            gb.configure_column("Level1", width=120)
                            gb.configure_column("Level2", width=120)
                            gb.configure_column("Level3", width=120)
                            gb.configure_column("Type", width=150)
                            gb.configure_column("Description", width=200)
                            gb.configure_column("Cardinality", width=100)
                            gridOptions = gb.build()
                            
                            # Display the grid
                            grid_response = AgGrid(
                                df,
                                gridOptions=gridOptions,
                                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                                update_mode=GridUpdateMode.SELECTION_CHANGED,
                                fit_columns_on_grid_load=True,
                                theme="streamlit",
                                height=400,
                                allow_unsafe_jscode=True,
                            )
                            
                        except Exception as preview_error:
                            st.warning(f"Could not show preview: {preview_error}")
                        
                        st.download_button(
                            label="📥 Download Excel File",
                            data=result,
                            file_name="schema_structure.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    else:
                        st.markdown('<div class="error-message">❌ Failed to convert to Excel</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="error-message">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
            
        else:
            st.markdown('<div class="warning-message">⚠️ Please upload a schema file</div>', unsafe_allow_html=True)

def show_about_page():
    """
    Display the about page with application information and features.
    """
    st.markdown('<div class="section-header"><h2>About The Forge</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    **The Forge** is a powerful schema transformation tool that provides comprehensive capabilities for working with schema files.
    
    ### Core Features
    
    - **Schema Mapping**: Create field mappings between different schema formats (XSD, JSON Schema)
    - **WSDL to XSD Extraction**: Extract XSD schemas from WSDL files
    - **Schema to Excel**: Convert schema files to Excel format for analysis
    
    ### Supported Formats
    
    **Input Formats:**
    - XSD (.xsd)
    - XML (.xml)
    - JSON Schema (.json)
    - WSDL (.wsdl, .xml)
    
    **Output Formats:**
    - Excel (.xlsx)
    - XSD (.xsd)
    
    ### Key Benefits
    
    - ✅ **No compilation issues** - Pure Python implementation
    - ✅ **Lightweight dependencies** - Minimal external requirements
    - ✅ **Cross-platform compatibility** - Works on Windows, macOS, Linux
    - ✅ **Production ready** - Robust error handling and validation
    - ✅ **Modern web interface** - Clean, responsive Streamlit UI
    
    ### Technical Details
    
    This web version is based on The Forge v8 desktop application, adapted for online deployment with Streamlit.
    The application uses microservices architecture for modular functionality and easy maintenance.
    
    ### Support
    
    For issues, questions, or feature requests, please refer to the project documentation or create an issue in the repository.
    """)
    
    # Version info
    st.markdown("### Version Information")
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