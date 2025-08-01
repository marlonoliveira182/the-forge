import streamlit as st
import streamlit_extras as stx
from datetime import datetime

def show_home_page():
    """
    Self-contained homepage component for The Forge app.
    Focused on integration architect features.
    """
    
    # Page configuration
    st.set_page_config(
        page_title="The Forge - Home",
        page_icon="🔨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for homepage
    st.markdown("""
    <style>
        /* Homepage-specific styles */
        .home-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%);
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.7);
        }
        
        .home-header h1 {
            color: #ff6b35;
            font-size: 3rem;
            margin-bottom: 0.5rem;
            text-shadow: 0 0 20px rgba(255, 107, 53, 0.3);
        }
        
        .home-header p {
            color: #e0e0e0;
            font-size: 1.2rem;
            margin: 0;
        }
        
        .tool-card {
            background: linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%);
            border: 2px solid #404040;
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }
        
        .tool-card:hover {
            border-color: #ff6b35;
            box-shadow: 0 8px 16px rgba(255, 107, 53, 0.3);
            transform: translateY(-2px);
        }
        
        .tool-card h3 {
            color: #ff6b35;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .tool-card p {
            color: #b0b0b0;
            font-size: 0.9rem;
            margin: 0;
        }
        
        .whats-new {
            background: linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 2rem 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }
        
        .feature-item {
            background: #4a4a4a;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #ff6b35;
        }
        
        .feature-title {
            color: #ff6b35;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .feature-desc {
            color: #b0b0b0;
            font-size: 0.9rem;
        }
        
        .footer {
            text-align: center;
            padding: 2rem 0;
            color: #808080;
            font-size: 0.9rem;
            border-top: 1px solid #404040;
            margin-top: 3rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header Section
    st.markdown('''
        <div class="home-header">
            <h1>🔨 The Forge</h1>
            <p>Professional Schema Transformation & Integration Toolkit</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # Tool Cards Section
    st.markdown("### 🛠️ Core Integration Tools")
    st.markdown("Essential tools for schema transformation and integration workflows:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Schema to Excel", key="home_schema_excel", use_container_width=True):
            st.session_state.current_page = "Schema to Excel"
            st.rerun()
        
        st.markdown("""
        <div class="tool-card">
            <h3>📋 Schema to Excel</h3>
            <p>Convert XSD, XML, and JSON Schema files to Excel format for documentation and analysis. Supports complex nested structures and array types.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🔧 WSDL to XSD", key="home_wsdl_xsd", use_container_width=True):
            st.session_state.current_page = "WSDL to XSD"
            st.rerun()
        
        st.markdown("""
        <div class="tool-card">
            <h3>🔧 WSDL to XSD</h3>
            <p>Extract and convert WSDL files to XSD schemas for web service integration and SOAP API development.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("📊 Schema Mapping", key="home_mapping", use_container_width=True):
            st.session_state.current_page = "Schema Mapping"
            st.rerun()
        
        st.markdown("""
        <div class="tool-card">
            <h3>📊 Schema Mapping</h3>
            <p>Create intelligent field mappings between different schema formats with configurable similarity thresholds and comprehensive mapping documentation.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # What's New Section
    with st.expander("🆕 Recent Updates", expanded=False):
        st.markdown("""
        <div class="whats-new">
            <div class="feature-item">
                <div class="feature-title">🎯 Enhanced Schema Mapping</div>
                <div class="feature-desc">Improved mapping algorithm with configurable minimum match threshold (20-100%) and intelligent field matching for better accuracy.</div>
            </div>
            
            <div class="feature-item">
                <div class="feature-title">📄 Multi-Format Schema Support</div>
                <div class="feature-desc">All tools now support XSD, XML, JSON Schema, and WSDL formats for comprehensive schema transformation workflows.</div>
            </div>
            
            <div class="feature-item">
                <div class="feature-title">🔧 Advanced WSDL Processing</div>
                <div class="feature-desc">Enhanced WSDL to XSD extraction with improved parsing capabilities and better handling of complex web service definitions.</div>
            </div>
            
            <div class="feature-item">
                <div class="feature-title">📊 Excel Export Improvements</div>
                <div class="feature-desc">Enhanced Excel output with proper nested structure handling, array type support, and improved formatting for documentation.</div>
            </div>
            
            <div class="feature-item">
                <div class="feature-title">⚡ Performance Optimizations</div>
                <div class="feature-desc">Improved processing speed and memory efficiency for large schema files and complex transformations.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
        <div class="footer">
            <p>The Forge v1.0.0 – Professional Integration Toolkit</p>
            <p>Designed for Integration Architects</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    show_home_page() 