import streamlit as st
import streamlit_extras as stx
from datetime import datetime

def show_home_page():
    """
    Self-contained homepage component for The Forge app.
    Updates st.session_state.tool for navigation.
    """
    
    # Page configuration
    st.set_page_config(
        page_title="The Forge - Home",
        page_icon="🔨",
        layout="wide",
        initial_sidebar_state="collapsed"
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
        
        .metrics-container {
            background: linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 2rem 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }
        
        .metric-card {
            background: #4a4a4a;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            border: 1px solid #505050;
        }
        
        .metric-value {
            color: #ff6b35;
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
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
    </style>
    """, unsafe_allow_html=True)
    
    # Header Section
    st.markdown('''
        <div class="home-header">
            <h1>🔨 The Forge</h1>
            <p>Advanced Schema Transformation & Mapping Tool</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # Tool Cards Section
    st.markdown("### 🛠️ Available Tools")
    st.markdown("Choose a tool to get started:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Schema to Excel", key="home_schema_excel", use_container_width=True):
            st.session_state.tool = "Schema to Excel"
            st.rerun()
        
        st.markdown("""
        <div class="tool-card">
            <h3>📋 Schema to Excel</h3>
            <p>Convert XSD, XML, and JSON Schema files to Excel format for easy analysis and documentation.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🔧 WSDL to XSD", key="home_wsdl_xsd", use_container_width=True):
            st.session_state.tool = "WSDL to XSD"
            st.rerun()
        
        st.markdown("""
        <div class="tool-card">
            <h3>🔧 WSDL to XSD</h3>
            <p>Extract and convert WSDL files to XSD schemas for web service integration.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("📊 Schema Mapping", key="home_mapping", use_container_width=True):
            st.session_state.tool = "Schema Mapping"
            st.rerun()
        
        st.markdown("""
        <div class="tool-card">
            <h3>📊 Schema Mapping</h3>
            <p>Create mappings between different schema formats with intelligent field matching.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Metrics Section
    st.markdown("### 📊 Usage Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-value">1,247</div>
                <div class="metric-label">Schemas Converted</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-value">856</div>
                <div class="metric-label">Excel Files Generated</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-value">342</div>
                <div class="metric-label">WSDL Files Processed</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-value">189</div>
                <div class="metric-label">Schema Mappings Created</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # What's New Section
    with st.expander("🆕 What's New", expanded=False):
        st.markdown("""
        <div class="whats-new">
            <div class="feature-item">
                <div class="feature-title">🎯 Enhanced Schema Mapping</div>
                <div class="feature-desc">Improved mapping algorithm with configurable minimum match threshold and better field matching accuracy.</div>
            </div>
            
            <div class="feature-item">
                <div class="feature-title">📄 JSON Schema Support</div>
                <div class="feature-desc">All tools now support JSON Schema format alongside XSD and XML schemas.</div>
            </div>
            
            <div class="feature-item">
                <div class="feature-title">🔧 WSDL to XSD Extraction</div>
                <div class="feature-desc">New tool for extracting XSD schemas from WSDL files with improved parsing capabilities.</div>
            </div>
            
            <div class="feature-item">
                <div class="feature-title">📊 Excel Export Improvements</div>
                <div class="feature-desc">Enhanced Excel output with better formatting, nested structure handling, and array type support.</div>
            </div>
            
            <div class="feature-item">
                <div class="feature-title">🎨 Modern UI Design</div>
                <div class="feature-desc">Completely redesigned interface with forge-themed styling and improved user experience.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
        <div class="footer">
            <p>The Forge v1.0.0 – Powered by Streamlit</p>
            <p>Forged with 🔥 for schema transformation</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    show_home_page() 