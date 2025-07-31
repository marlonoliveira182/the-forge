# The Forge Web App

A powerful schema transformation tool built with Streamlit, providing comprehensive capabilities for working with schema files.

## 🚀 Features

- **📊 Schema Mapping**: Create field mappings between different schema formats (XSD, JSON Schema)
- **🔧 WSDL to XSD Extraction**: Extract XSD schemas from WSDL files
- **📋 Schema to Excel**: Convert schema files to Excel format for analysis

## 📁 Supported Formats

**Input Formats:**
- XSD (.xsd)
- XML (.xml)
- JSON Schema (.json)
- WSDL (.wsdl, .xml)

**Output Formats:**
- Excel (.xlsx)
- XSD (.xsd)

## 🛠️ Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd the-forge-web-app
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

### Option 1: Run with Python script
```bash
python run_app.py
```

### Option 2: Run directly with Streamlit
```bash
streamlit run app.py
```

### Option 3: Run with custom port
```bash
streamlit run app.py --server.port 8501
```

The app will be available at: **http://localhost:8501**

## 📱 Usage

### Home Page
The home page provides an overview of all available tools and features.

### Schema Mapping
1. Upload source schema file (XSD, XML, or JSON)
2. Upload target schema file (XSD, XML, or JSON)
3. Adjust similarity threshold and case settings
4. Click "Generate Mapping" to create field mappings
5. Download the Excel file with detailed mapping information

### WSDL to XSD Extraction
1. Upload a WSDL file
2. Click "Extract XSD" to extract embedded XSD schemas
3. Download the extracted XSD file

### Schema to Excel
1. Upload a schema file (XSD, XML, or JSON)
2. Choose whether to keep original case
3. Click "Convert to Excel" to generate Excel format
4. Download the Excel file for analysis

## 🏗️ Architecture

The application uses a microservices architecture:

- **`services/xsd_parser_service.py`**: XSD parsing and analysis
- **`services/excel_export_service.py`**: Excel file generation
- **`services/wsdl_to_xsd_extractor.py`**: WSDL to XSD extraction
- **`services/excel_mapping_service.py`**: Schema mapping generation
- **`services/json_to_excel_service.py`**: JSON Schema processing

## 🎨 UI Features

- **Modern Design**: Clean, responsive interface with gradient backgrounds
- **File Previews**: View uploaded files before processing
- **Progress Indicators**: Real-time feedback during processing
- **Error Handling**: Comprehensive error messages and validation
- **Download Integration**: Direct file downloads after processing

## 🔧 Technical Details

- **Framework**: Streamlit 1.28.1
- **Dependencies**: Minimal external requirements
- **Compatibility**: Cross-platform (Windows, macOS, Linux)
- **Performance**: Optimized with caching and efficient processing

## 🚀 Key Benefits

- ✅ **No compilation issues** - Pure Python implementation
- ✅ **Lightweight dependencies** - Minimal external requirements
- ✅ **Cross-platform compatibility** - Works on Windows, macOS, Linux
- ✅ **Production ready** - Robust error handling and validation
- ✅ **Modern web interface** - Clean, responsive Streamlit UI

## 📋 Requirements

- Python 3.7+
- Streamlit 1.28.1
- openpyxl 3.1.2
- jsonschema 4.17.3

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   streamlit run app.py --server.port 8502
   ```

2. **Dependencies not found**:
   ```bash
   pip install -r requirements.txt
   ```

3. **File upload issues**: Ensure files are in supported formats (XSD, XML, JSON, WSDL)

### Error Messages

- **"Failed to generate mapping"**: Check file formats and content
- **"Error extracting XSD"**: Verify WSDL file structure
- **"Failed to generate Excel file"**: Ensure schema file is valid

## 📞 Support

For issues, questions, or feature requests:
1. Check the troubleshooting section above
2. Review the error messages in the application
3. Ensure all dependencies are properly installed

## 📄 License

This project is based on The Forge v8 desktop application, adapted for web deployment.

## 🔄 Version History

- **v1.0.0**: Initial web app release with unified interface
- Based on The Forge v8 desktop application
- Streamlit-based web interface
- Comprehensive schema transformation tools 