# The Forge Web App

A clean, optimized Streamlit web application for schema transformation and mapping with AI-powered description generation.

## Features
- **Schema Mapping**: Transform and map between different schema formats
- **WSDL to XSD Extraction**: Extract XSD schemas from WSDL files
- **Schema to Excel Conversion**: Convert schemas to Excel format for analysis
- **🤖 AI Description Generator**: Automatically generate functional descriptions for integration artifacts

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
│   ├── reorder_excel_attributes.py
│   └── ai_description_generator.py  # AI-powered description generator
├── requirements.txt       # Minimal dependencies
├── test_app.py          # Import testing utility
└── test_ai_description.py # AI description generator test
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
- **transformers**: AI text generation (optional)
- **torch**: PyTorch for AI models (optional)

## AI Description Generator

The AI Description Generator uses free AI libraries to automatically analyze integration artifacts and generate functional descriptions:

### Supported Formats
- **WSDL**: Web Service Definition Language files
- **XSD**: XML Schema Definition files
- **JSON**: JSON data files
- **XML**: XML document files
- **JSON Schema**: JSON Schema specification files

### Features
- **Short Description**: Concise functional overview
- **Detailed Description**: Comprehensive business context analysis
- **Schema Analysis**: Field-level structure breakdown
- **Download Reports**: Export descriptions as Markdown files

### AI Capabilities
- Uses Hugging Face Transformers for text generation
- Falls back to rule-based generation if AI models unavailable
- Focuses on business context rather than technical details
- Provides integration workflow insights 