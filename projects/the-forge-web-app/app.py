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
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="forge" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,107,53,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23forge)"/></svg>');
        opacity: 0.5;
    }
    
    .main-header h1 {
        color: var(--forge-orange);
        margin-bottom: 0.5rem;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        color: var(--forge-text);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    /* Ancient Forge Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--forge-black) 0%, var(--forge-dark) 100%);
        border-right: 2px solid var(--forge-orange);
        box-shadow: var(--forge-shadow-heavy);
    }
    
    /* Sidebar Header */
    .sidebar-header {
        background: linear-gradient(135deg, var(--forge-charcoal) 0%, var(--forge-steel) 100%);
        color: var(--forge-text);
        padding: 2rem 1.5rem;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
        border-bottom: 2px solid var(--forge-orange);
        box-shadow: var(--forge-shadow);
        position: relative;
    }
    
    .sidebar-header h2 {
        margin: 0;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--forge-orange);
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
    }
    
    /* Navigation Buttons */
    .sidebar .stButton > button {
        background: linear-gradient(135deg, var(--forge-iron) 0%, var(--forge-coal) 100%);
        color: var(--forge-text);
        border: 1px solid var(--forge-border);
        border-radius: var(--radius-md);
        padding: 1rem 1.25rem;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        margin: 0.5rem 0;
        width: 100%;
        text-align: left;
        position: relative;
        box-shadow: var(--forge-shadow);
    }
    
    .sidebar .stButton > button:hover {
        background: linear-gradient(135deg, var(--forge-orange) 0%, var(--forge-fire) 100%);
        color: var(--forge-text);
        transform: translateX(4px);
        box-shadow: var(--forge-shadow), var(--forge-glow-shadow);
        border-color: var(--forge-orange);
    }
    
    /* Active Navigation Button */
    .sidebar .stButton > button[data-active="true"] {
        background: linear-gradient(135deg, var(--forge-orange) 0%, var(--forge-fire) 100%);
        color: var(--forge-text);
        font-weight: 600;
        box-shadow: var(--forge-shadow), var(--forge-glow-shadow);
        border-color: var(--forge-orange);
        transform: translateX(2px);
    }
    
    /* Sidebar Footer */
    .sidebar-footer {
        margin-top: auto;
        padding: 1.5rem 1rem;
        text-align: center;
        color: var(--forge-text-secondary);
        font-size: 0.8rem;
        border-top: 1px solid var(--forge-border);
        background: linear-gradient(135deg, var(--forge-charcoal) 0%, var(--forge-steel) 100%);
        margin: 2rem -1rem -1rem -1rem;
    }
    
    .sidebar-footer .version {
        background: linear-gradient(135deg, var(--forge-orange) 0%, var(--forge-fire) 100%);
        padding: 0.5rem 1rem;
        border-radius: var(--radius-md);
        margin-top: 0.75rem;
        font-family: 'Courier New', monospace;
        font-size: 0.75rem;
        color: var(--forge-text);
        border: 1px solid var(--forge-orange);
        box-shadow: var(--forge-shadow);
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, var(--forge-charcoal) 0%, var(--forge-steel) 100%);
        color: var(--forge-text);
        padding: 1.5rem 2rem;
        border-radius: var(--radius-lg);
        margin: 2rem 0 1.5rem 0;
        border: 1px solid var(--forge-border);
        box-shadow: var(--forge-shadow);
    }
    
    .section-header h2, .section-header h3 {
        color: var(--forge-orange);
        margin: 0;
        font-weight: 600;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
    }
    
    /* Feature Cards */
    .feature-card {
        background: linear-gradient(135deg, var(--forge-charcoal) 0%, var(--forge-steel) 100%);
        padding: 2rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--forge-border);
        margin: 1.5rem 0;
        color: var(--forge-text);
        box-shadow: var(--forge-shadow);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--forge-shadow-heavy), var(--forge-glow-shadow);
        border-color: var(--forge-orange);
    }
    
    .feature-card h3 {
        color: var(--forge-orange);
        margin-bottom: 1rem;
        font-weight: 600;
        font-size: 1.3rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
    }
    
    .feature-card p {
        color: var(--forge-text-secondary);
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--forge-orange) 0%, var(--forge-fire) 100%);
        color: var(--forge-text);
        border: none;
        border-radius: var(--radius-md);
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: var(--forge-shadow);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--forge-fire) 0%, var(--forge-flame) 100%);
        transform: translateY(-2px);
        box-shadow: var(--forge-shadow), var(--forge-glow-shadow);
    }
    
    /* Upload Area */
    .upload-area {
        border: 2px dashed var(--forge-orange);
        border-radius: var(--radius-lg);
        padding: 3rem 2rem;
        text-align: center;
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.1) 0%, rgba(255, 140, 66, 0.1) 100%);
        margin: 1.5rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: var(--forge-fire);
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.2) 0%, rgba(255, 140, 66, 0.2) 100%);
        transform: translateY(-2px);
        box-shadow: var(--forge-shadow), var(--forge-glow-shadow);
    }
    
    /* Message Styles */
    .success-message {
        background: linear-gradient(135deg, var(--forge-gold) 0%, var(--forge-bronze) 100%);
        color: var(--forge-black);
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        margin: 1.5rem 0;
        border: 1px solid var(--forge-gold);
        box-shadow: var(--forge-shadow);
    }
    
    .error-message {
        background: linear-gradient(135deg, var(--forge-ember) 0%, var(--forge-glow) 100%);
        color: var(--forge-text);
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        margin: 1.5rem 0;
        border: 1px solid var(--forge-ember);
        box-shadow: var(--forge-shadow);
    }
    
    .warning-message {
        background: linear-gradient(135deg, var(--forge-copper) 0%, var(--forge-bronze) 100%);
        color: var(--forge-text);
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        margin: 1.5rem 0;
        border: 1px solid var(--forge-copper);
        box-shadow: var(--forge-shadow);
    }
    
    /* Form Elements */
    .stSelectbox, .stSlider, .stCheckbox {
        background: linear-gradient(135deg, var(--forge-iron) 0%, var(--forge-coal) 100%);
        border: 1px solid var(--forge-border);
        border-radius: var(--radius-md);
        box-shadow: var(--forge-shadow);
        color: var(--forge-text);
    }
    
    .stFileUploader {
        background: linear-gradient(135deg, var(--forge-iron) 0%, var(--forge-coal) 100%);
        border: 1px solid var(--forge-border);
        border-radius: var(--radius-lg);
        box-shadow: var(--forge-shadow);
        padding: 1rem;
    }
    
    /* Code blocks */
    .stCode {
        background: linear-gradient(135deg, var(--forge-black) 0%, var(--forge-dark) 100%);
        border: 1px solid var(--forge-border);
        border-radius: var(--radius-md);
        box-shadow: var(--forge-shadow);
        color: var(--forge-text);
    }
    
    /* DataFrames */
    .dataframe {
        background: linear-gradient(135deg, var(--forge-iron) 0%, var(--forge-coal) 100%);
        border: 1px solid var(--forge-border);
        border-radius: var(--radius-md);
        box-shadow: var(--forge-shadow);
    }
    
    /* Progress Bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, var(--forge-orange) 0%, var(--forge-fire) 100%);
        border-radius: var(--radius-sm);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, var(--forge-iron) 0%, var(--forge-coal) 100%);
        border: 1px solid var(--forge-border);
        border-radius: var(--radius-md);
        padding: 1rem;
        font-weight: 500;
        color: var(--forge-text);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: var(--forge-orange);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .section-header {
            padding: 1rem;
        }
        
        .feature-card {
            padding: 1.5rem;
        }
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
    # Get services
    services = get_services()
    
    # Initialize session state if not exists
    if 'tool' not in st.session_state:
        st.session_state.tool = None
    
    # Import and use the new homepage
    from homepage import show_home_page
    
    # Check if a tool was selected from homepage
    if st.session_state.tool is None:
        # Show the homepage
        show_home_page()
    else:
        # Show the selected tool
        if st.session_state.tool == "Schema to Excel":
            show_schema_to_excel_page(services)
        elif st.session_state.tool == "WSDL to XSD":
            show_wsdl_to_xsd_page(services)
        elif st.session_state.tool == "Schema Mapping":
            show_mapping_page(services)
        else:
            # Fallback to homepage
            show_home_page()



def show_mapping_page(services):
    # Back to Home button
    if st.button("🏠 Back to Home", key="back_home_mapping", use_container_width=True):
        st.session_state.tool = None
        st.rerun()
    
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
            key="source_uploader",
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
            key="target_uploader",
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
    # Back to Home button
    if st.button("🏠 Back to Home", key="back_home_wsdl", use_container_width=True):
        st.session_state.tool = None
        st.rerun()
    
    st.markdown('<div class="section-header"><h2>🔧 WSDL to XSD Extraction</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    Extract XSD schemas from WSDL files. Perfect for working with web services and SOAP APIs.
    """)
    
    wsdl_file = st.file_uploader(
        "Upload WSDL file",
        type=['wsdl', 'xml'],
        key="wsdl_uploader",
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
    # Back to Home button
    if st.button("🏠 Back to Home", key="back_home_excel", use_container_width=True):
        st.session_state.tool = None
        st.rerun()
    
    st.markdown('<div class="section-header"><h2>📋 Schema to Excel</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    Convert schema files to Excel format for easy analysis and documentation.
    """)
    
    schema_file = st.file_uploader(
        "Upload schema file",
        type=['xsd', 'xml', 'json'],
        key="schema_uploader",
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