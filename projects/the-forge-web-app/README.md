# The Forge Web App

A clean, optimized Streamlit web application for schema transformation and mapping.

## Features
- **Schema Mapping**: Transform and map between different schema formats
- **WSDL to XSD Extraction**: Extract XSD schemas from WSDL files
- **Schema to Excel Conversion**: Convert schemas to Excel format for analysis

## Project Structure
```
the-forge-web-app/
├── app.py                 # Main Streamlit application
├── services/              # Core microservices
│   ├── xsd_parser_service.py
│   ├── excel_export_service.py
│   ├── wsdl_to_xsd_extractor.py
│   ├── excel_mapping_service.py
│   ├── json_to_excel_service.py
│   ├── case_converter_service.py
│   ├── excel_output_validator.py
│   └── reorder_excel_attributes.py
├── requirements.txt       # Minimal dependencies
└── test_app.py          # Import testing utility
```

## Installation
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Dependencies
- **streamlit**: Web framework
- **openpyxl**: Excel file handling
- **lxml**: XML processing for WSDL/XSD
- **pandas**: Data validation and analysis 