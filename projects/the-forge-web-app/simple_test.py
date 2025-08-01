#!/usr/bin/env python3
"""
Simple Streamlit test to isolate the issue.
"""

import streamlit as st

st.title("Simple Test")
st.write("If you can see this, Streamlit is working.")

try:
    from services.converter_service import ConverterService
    st.success("✅ ConverterService imported successfully")
except Exception as e:
    st.error(f"❌ ConverterService import failed: {e}")

try:
    from services.xsd_parser_service import XSDParser
    st.success("✅ XSDParser imported successfully")
except Exception as e:
    st.error(f"❌ XSDParser import failed: {e}")

try:
    from services.json_schema_parser_service import JSONSchemaParser
    st.success("✅ JSONSchemaParser imported successfully")
except Exception as e:
    st.error(f"❌ JSONSchemaParser import failed: {e}")

try:
    from services.excel_export_service import ExcelExporter
    st.success("✅ ExcelExporter imported successfully")
except Exception as e:
    st.error(f"❌ ExcelExporter import failed: {e}")

st.write("Test completed!") 