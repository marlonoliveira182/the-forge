import streamlit as st

def show_home_page():
    """
    Display a simple, clean homepage for The Forge.
    """
    # Set page config
    st.set_page_config(
        page_title="The Forge - Home",
        page_icon="🔨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Simple CSS for clean styling
    st.markdown("""
    <style>
        .home-container {
            padding: 2rem;
            text-align: center;
        }
        
        .welcome-text {
            color: #e0e0e0;
            font-size: 1.2rem;
            margin: 2rem 0;
            line-height: 1.6;
        }
        
        .tool-section {
            margin: 3rem 0;
        }
        
        .tool-section h2 {
            color: #ff6b35;
            margin-bottom: 2rem;
        }
        
        .tool-cards {
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
        }
        
        .tool-card {
            background: linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%);
            border: 1px solid #404040;
            border-radius: 12px;
            padding: 2rem;
            width: 300px;
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }
        
        .tool-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.7);
            border-color: #ff6b35;
        }
        
        .tool-card h3 {
            color: #ff6b35;
            margin-bottom: 1rem;
            font-size: 1.3rem;
        }
        
        .tool-card p {
            color: #b0b0b0;
            line-height: 1.6;
        }
        
        .footer {
            margin-top: 4rem;
            padding: 2rem 0;
            color: #808080;
            font-size: 0.9rem;
            border-top: 1px solid #404040;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Main content
    st.markdown('<div class="home-container">', unsafe_allow_html=True)
    
    # Simple welcome
    st.markdown("""
    <div class="welcome-text">
        Welcome to <strong>The Forge</strong> - Professional Schema Transformation & Integration Toolkit
    </div>
    """, unsafe_allow_html=True)
    
    # Tool section
    st.markdown("""
    <div class="tool-section">
        <h2>🛠️ Core Integration Tools</h2>
        <div class="tool-cards">
            <div class="tool-card">
                <h3>📋 Schema to Excel</h3>
                <p>Convert XSD, XML, and JSON Schema files to Excel format for documentation and analysis.</p>
            </div>
            <div class="tool-card">
                <h3>🔧 WSDL to XSD</h3>
                <p>Extract and convert WSDL files to XSD schemas for web service integration.</p>
            </div>
            <div class="tool-card">
                <h3>📊 Schema Mapping</h3>
                <p>Create intelligent field mappings between different schema formats with configurable similarity thresholds.</p>
            </div>
            <div class="tool-card">
                <h3>🔄 Converter</h3>
                <p>Convert between JSON examples, JSON schemas, XML examples, and XSD schemas with comprehensive validation.</p>
            </div>

        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Simple footer
    st.markdown("""
    <div class="footer">
        <p>The Forge v1.0.0 – Professional Integration Toolkit</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    show_home_page() 