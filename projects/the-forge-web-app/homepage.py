import streamlit as st

def show_home_page():
    """
    Display a comprehensive and visually appealing homepage for The Forge.
    """
    # Enhanced CSS for modern styling with specific selectors to avoid conflicts
    st.markdown("""
    <style>
        .homepage-container {
            padding: 2rem;
            text-align: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .homepage-welcome-section {
            background: linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%);
            border-radius: 16px;
            padding: 3rem 2rem;
            margin-bottom: 3rem;
            border: 1px solid #404040;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        .homepage-welcome-title {
            color: #ff6b35;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        .homepage-welcome-subtitle {
            color: #e0e0e0;
            font-size: 1.3rem;
            margin-bottom: 2rem;
            line-height: 1.6;
            opacity: 0.9;
        }
        
        .homepage-welcome-description {
            color: #b0b0b0;
            font-size: 1.1rem;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
        }
        
        .homepage-tool-section {
            margin: 4rem 0;
        }
        
        .homepage-tool-section h2 {
            color: #ff6b35;
            margin-bottom: 2.5rem;
            font-size: 2rem;
            text-align: center;
        }
        
        .homepage-tool-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            margin: 0 auto;
            max-width: 1000px;
        }
        
        .homepage-tool-card {
            background: linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%);
            border: 1px solid #404040;
            border-radius: 16px;
            padding: 2.5rem 2rem;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .homepage-tool-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #ff6b35, #ff8c42);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }
        
        .homepage-tool-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
            border-color: #ff6b35;
        }
        
        .homepage-tool-card:hover::before {
            transform: scaleX(1);
        }
        
        .homepage-tool-card h3 {
            color: #ff6b35;
            margin-bottom: 1.5rem;
            font-size: 1.5rem;
            font-weight: bold;
        }
        
        .homepage-tool-card p {
            color: #b0b0b0;
            line-height: 1.7;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .homepage-tool-features {
            text-align: left;
            margin-top: 1.5rem;
        }
        
        .homepage-tool-features h4 {
            color: #ff8c42;
            font-size: 1.1rem;
            margin-bottom: 0.8rem;
        }
        
        .homepage-tool-features ul {
            color: #c0c0c0;
            font-size: 0.9rem;
            line-height: 1.6;
            padding-left: 1.2rem;
        }
        
        .homepage-tool-features li {
            margin-bottom: 0.5rem;
        }
        
        .homepage-footer {
            margin-top: 4rem;
            padding: 2rem 0;
            color: #808080;
            font-size: 0.9rem;
            border-top: 1px solid #404040;
            text-align: center;
        }
        
        .homepage-stats-section {
            background: linear-gradient(135deg, #2d2d2d 0%, #3a3a3a 100%);
            border-radius: 16px;
            padding: 2rem;
            margin: 3rem 0;
            border: 1px solid #404040;
        }
        
        .homepage-stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        
        .homepage-stat-item {
            text-align: center;
            padding: 1.5rem;
            background: rgba(255, 107, 53, 0.1);
            border-radius: 12px;
            border: 1px solid rgba(255, 107, 53, 0.2);
        }
        
        .homepage-stat-number {
            color: #ff6b35;
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .homepage-stat-label {
            color: #b0b0b0;
            font-size: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Main content
    st.markdown('<div class="homepage-container">', unsafe_allow_html=True)
    
    # Welcome section
    st.markdown("""
    <div class="homepage-welcome-section">
        <div class="homepage-welcome-title">🔨 The Forge</div>
        <div class="homepage-welcome-subtitle">Professional Schema Transformation & Integration Toolkit</div>
        <div class="homepage-welcome-description">
            Transform, convert, and integrate schemas across multiple formats with enterprise-grade precision. 
            From JSON to XML, XSD to JSON Schema, and everything in between - The Forge provides the tools 
            you need for seamless data integration and schema management.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tool section
    st.markdown("""
    <div class="homepage-tool-section">
        <h2>🛠️ Core Integration Tools</h2>
        <div class="homepage-tool-cards">
            
            <div>
                <h3>🔄 Converter</h3>
                <p>Comprehensive format conversion between JSON, XML, XSD, and JSON Schema with intelligent type inference and validation.</p>
                <div class="homepage-tool-features">
                    <h4>Key Features:</h4>
                    <ul>
                        <li>JSON Example ↔ JSON Schema</li>
                        <li>XML Example ↔ XSD Schema</li>
                        <li>XSD ↔ JSON Schema</li>
                        <li>JSON ↔ XML conversion</li>
                        <li>Excel export for all formats</li>
                        <li>Real-time validation</li>
                    </ul>
                </div>
            </div>
            
            <div>
                <h3>📊 Schema Mapping</h3>
                <p>Create intelligent field mappings between different schema formats with configurable similarity thresholds and fuzzy matching.</p>
                <div class="homepage-tool-features">
                    <h4>Key Features:</h4>
                    <ul>
                        <li>XSD to XSD mapping</li>
                        <li>JSON Schema to JSON Schema</li>
                        <li>Mixed schema mapping</li>
                        <li>Fuzzy field matching</li>
                        <li>Excel export with mappings</li>
                        <li>Configurable thresholds</li>
                    </ul>
                </div>
            </div>
            
            <div>
                <h3>🔧 WSDL to XSD</h3>
                <p>Extract and convert WSDL files to XSD schemas for web service integration and documentation.</p>
                <div class="homepage-tool-features">
                    <h4>Key Features:</h4>
                    <ul>
                        <li>WSDL file parsing</li>
                        <li>XSD schema extraction</li>
                        <li>Type definition conversion</li>
                        <li>Namespace handling</li>
                        <li>Multiple service support</li>
                        <li>Clean output formatting</li>
                    </ul>
                </div>
            </div>
            
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistics section
    st.markdown("""
    <div class="homepage-stats-section">
        <h2 style="color: #ff6b35; text-align: center; margin-bottom: 2rem;">📈 Platform Capabilities</h2>
        <div class="homepage-stats-grid">
            <div class="homepage-stat-item">
                <div class="homepage-stat-number">12+</div>
                <div class="homepage-stat-label">Conversion Types</div>
            </div>
            <div class="homepage-stat-item">
                <div class="homepage-stat-number">5</div>
                <div class="homepage-stat-label">Input Formats</div>
            </div>
            <div class="homepage-stat-item">
                <div class="homepage-stat-number">4</div>
                <div class="homepage-stat-label">Output Formats</div>
            </div>
            <div class="homepage-stat-item">
                <div class="homepage-stat-number">100%</div>
                <div class="homepage-stat-label">Validation Coverage</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="homepage-footer">
        <p><strong>The Forge v1.0.0</strong> – Professional Integration Toolkit</p>
        <p>Enterprise-grade schema transformation and integration platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    show_home_page() 