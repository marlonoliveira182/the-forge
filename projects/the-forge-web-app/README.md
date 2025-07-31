# The Forge Web App

A Streamlit-based web application that provides the same functionality as The Forge v8 desktop application, adapted for online deployment.

## Features

- **📊 Schema Mapping**: Create field mappings between different schema formats (XSD, JSON Schema)
- **🔧 WSDL to XSD Extraction**: Extract XSD schemas from WSDL files
- **📋 Schema to Excel**: Convert schema files to Excel format for analysis
- **🔄 Format Conversion**: Convert between XSD and JSON Schema formats

## Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd the-forge-web-app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the application**
   ```
   http://localhost:8501
   ```

## Usage

### Schema Mapping

1. Navigate to the "Mapping" page
2. Upload your source schema file (XSD, JSON, XML)
3. Upload your target schema file (XSD, JSON, XML)
4. Adjust similarity threshold and case settings
5. Click "Generate Mapping" to create the field mapping
6. Download the resulting Excel file

### WSDL to XSD Extraction

1. Navigate to the "WSDL to XSD" page
2. Upload your WSDL file
3. Click "Extract XSD" to extract the schema
4. Download the resulting XSD file

### Schema to Excel

1. Navigate to the "Schema to Excel" page
2. Upload your schema file (XSD, JSON, XML)
3. Adjust conversion options
4. Click "Convert to Excel" to generate the Excel file
5. Download the resulting Excel file

## Deployment

### Streamlit Cloud

1. **Connect your repository to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository

2. **Configure the deployment**
   - **Main file path**: `app.py`
   - **Python version**: 3.11

3. **Deploy**
   - Streamlit Cloud will automatically deploy your application

### Other Platforms

The app can also be deployed on:
- **Heroku**: Use the provided `Procfile`
- **Railway**: Direct deployment from GitHub
- **Render**: Web service deployment
- **Vercel**: Python runtime deployment

## File Structure

```
the-forge-web-app/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                # Documentation
├── .gitignore               # Git ignore rules
└── services/                # Core service modules
    ├── __init__.py
    ├── xsd_parser_service.py      # XSD parsing service
    ├── excel_export_service.py    # Excel file generation
    ├── wsdl_to_xsd_extractor.py  # WSDL to XSD extraction
    ├── excel_mapping_service.py   # Field mapping service
    └── json_to_excel_service.py  # JSON to Excel conversion
```

## Dependencies

### Core Dependencies
- `streamlit==1.28.1` - Web framework
- `openpyxl==3.1.2` - Excel file handling
- `jsonschema==4.17.3` - JSON Schema validation
- `lxml==4.9.3` - XML processing
- `pandas==2.1.4` - Data manipulation

### System Requirements
- Python 3.11+
- 512MB RAM minimum
- 1GB storage space

## Features in Detail

### Schema Mapping
- **Input Formats**: XSD, JSON Schema, XML
- **Output**: Excel file with field mappings
- **Features**: Similarity scoring, case sensitivity options
- **Preview**: Real-time file content preview

### WSDL to XSD Extraction
- **Input**: WSDL files
- **Output**: Clean XSD schema
- **Features**: Namespace handling, import resolution
- **Preview**: Extracted XSD content display

### Schema to Excel
- **Input**: XSD, JSON Schema, XML files
- **Output**: Structured Excel files
- **Features**: Hierarchical data representation
- **Preview**: Schema structure visualization

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Verify all imports work
python -c "import streamlit; import openpyxl; import lxml; print('All imports successful')"
```

#### File Upload Issues
- Ensure files are in supported formats (XSD, JSON, XML, WSDL)
- Check file size (max 200MB for Streamlit Cloud)
- Verify file encoding (UTF-8 recommended)

#### Memory Issues
- Reduce file sizes for large schemas
- Use simpler schema structures
- Consider splitting large files

### Performance Tips

1. **File Size**: Keep uploaded files under 50MB for best performance
2. **Schema Complexity**: Complex nested schemas may take longer to process
3. **Browser**: Use modern browsers (Chrome, Firefox, Safari, Edge)
4. **Network**: Stable internet connection recommended for file uploads

## Development

### Adding New Features

1. **Create new service** in `services/` directory
2. **Add UI components** in `app.py`
3. **Update requirements.txt** if new dependencies needed
4. **Test locally** before deployment

### Testing

```bash
# Run the app locally
streamlit run app.py

# Test specific functionality
python -c "from services.xsd_parser_service import XSDParser; print('XSD Parser works')"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of The Forge ecosystem and follows the same licensing terms.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Streamlit documentation
3. Check the original v8 desktop application for reference
4. Open an issue on the repository

## Version History

- **v1.0.0**: Initial web app based on The Forge v8
- **Features**: Schema mapping, WSDL extraction, Excel conversion
- **Platform**: Streamlit web application
- **Compatibility**: Python 3.11+, modern browsers 