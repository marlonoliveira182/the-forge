# The Forge Web App (Flask Version)

A Flask-based web application that provides the same functionality as The Forge v8 desktop application, adapted for online deployment.

## Features

- **📊 Schema Mapping**: Create field mappings between different schema formats (XSD, JSON Schema)
- **🔧 WSDL to XSD Extraction**: Extract XSD schemas from WSDL files
- **📋 Schema to Excel**: Convert schema files to Excel format for analysis
- **🔄 Format Conversion**: Convert between XSD and JSON Schema formats

## Installation

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements_flask.txt
   ```

2. **Run the application**
   ```bash
   python app_flask.py
   ```

3. **Access the application**
   ```
   http://localhost:5000
   ```

## Usage

### Schema Mapping

1. Navigate to the "Schema Mapping" section
2. Upload your source schema file (XSD, JSON, XML)
3. Upload your target schema file (XSD, JSON, XML)
4. Adjust similarity threshold and case settings
5. Click "Generate Mapping" to create the field mapping
6. Download the resulting Excel file

### WSDL to XSD Extraction

1. Navigate to the "WSDL to XSD Extraction" section
2. Upload your WSDL file
3. Click "Extract XSD" to extract the schema
4. Download the resulting XSD file

### Schema to Excel

1. Navigate to the "Schema to Excel" section
2. Upload your schema file (XSD, JSON, XML)
3. Adjust conversion options
4. Click "Convert to Excel" to generate the Excel file
5. Download the resulting Excel file

## Deployment

### Local Deployment

```bash
python app_flask.py
```

### Production Deployment

1. **Using Gunicorn (Linux/Mac)**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app_flask:app
   ```

2. **Using Waitress (Windows)**
   ```bash
   pip install waitress
   waitress-serve --host=0.0.0.0 --port=5000 app_flask:app
   ```

3. **Docker Deployment**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements_flask.txt .
   RUN pip install -r requirements_flask.txt
   COPY . .
   EXPOSE 5000
   CMD ["python", "app_flask.py"]
   ```

## File Structure

```
the-forge-web-app/
├── app_flask.py              # Main Flask application
├── requirements_flask.txt     # Flask dependencies
├── README_FLASK.md           # This documentation
├── test_flask.py             # Test script
└── services/                 # Core service modules
    ├── __init__.py
    ├── xsd_parser_service.py      # XSD parsing service
    ├── excel_export_service.py    # Excel file generation
    ├── wsdl_to_xsd_extractor.py  # WSDL to XSD extraction
    ├── excel_mapping_service.py   # Field mapping service
    └── json_to_excel_service.py  # JSON to Excel conversion
```

## Dependencies

### Core Dependencies
- `flask==2.3.3` - Web framework
- `openpyxl==3.1.2` - Excel file handling
- `jsonschema==4.17.3` - JSON Schema validation
- Built-in `xml.etree.ElementTree` - XML processing (no compilation required)

### System Requirements
- Python 3.11+
- 512MB RAM minimum
- 1GB storage space

## Testing

Run the test suite to verify functionality:

```bash
python test_flask.py
```

## Advantages of Flask Version

- ✅ **No compilation issues** - Uses built-in XML parsing
- ✅ **Lightweight** - Minimal dependencies
- ✅ **Fast deployment** - Simple setup
- ✅ **Cross-platform** - Works on Windows, Linux, Mac
- ✅ **Production ready** - Can be deployed with Gunicorn/Waitress

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Verify all imports work
python test_flask.py
```

#### Port Already in Use
```bash
# Change port in app_flask.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

#### File Upload Issues
- Ensure files are in supported formats (XSD, JSON, XML, WSDL)
- Check file size (max 16MB for Flask default)
- Verify file encoding (UTF-8 recommended)

## Development

### Adding New Features

1. **Create new service** in `services/` directory
2. **Add route** in `app_flask.py`
3. **Update requirements_flask.txt** if new dependencies needed
4. **Test locally** before deployment

### Testing

```bash
# Run the app locally
python app_flask.py

# Test specific functionality
python test_flask.py
```

## Comparison with Streamlit Version

| Feature | Flask Version | Streamlit Version |
|---------|---------------|-------------------|
| Dependencies | Minimal, no compilation | Many dependencies, compilation issues |
| Setup | Simple | Complex due to compilation |
| UI | Basic HTML/CSS | Rich interactive UI |
| Deployment | Standard web deployment | Streamlit Cloud specific |
| Performance | Fast | Slower due to overhead |
| Customization | High | Limited |

## Next Steps

1. **Deploy locally** for testing
2. **Set up production deployment** with Gunicorn/Waitress
3. **Configure reverse proxy** (nginx/Apache) for production
4. **Add authentication** if needed
5. **Set up monitoring** and logging

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Flask documentation
3. Check the original v8 desktop application for reference
4. Run `python test_flask.py` to verify functionality 