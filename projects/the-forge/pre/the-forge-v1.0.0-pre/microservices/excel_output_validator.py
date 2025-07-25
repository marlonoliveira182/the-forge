import pandas as pd
from lxml import etree
import os
import sys
sys.path.append(os.path.dirname(__file__))
from xsd_parser_service import XSDParser

# This function will be replaced by the UI's log function at runtime
# For now, it just collects logs in a list for possible export
_log_messages = []
def log_to_ui(message: str):
    _log_messages.append(message)


def excel_sheet_name(name):
    return name[:31]


def reconstruct_excel_paths(df, prefix):
    """
    Reconstructs hierarchical paths from Level1_src...Level8_src or Level1_tgt...Level8_tgt columns.
    Returns a dict: {path: row_index}
    """
    level_cols = [f'Level{i}_{prefix}' for i in range(1, 9) if f'Level{i}_{prefix}' in df.columns]
    paths = {}
    for idx, row in df.iterrows():
        levels = [str(row[col]) for col in level_cols if pd.notnull(row[col]) and str(row[col]).strip()]
        if levels:
            path = '/'.join(levels)
            paths[path] = idx
    return paths


def validate_excel_output(xsd_path: str, excel_path: str) -> None:
    log_to_ui(f"🔎 Starting validation: XSD='{os.path.basename(xsd_path)}', Excel='{os.path.basename(excel_path)}'")
    # 1. Parse XSD and build message->fields mapping
    try:
        parser = XSDParser()
        xsd_rows = parser.parse_xsd_file(xsd_path)
    except Exception as e:
        log_to_ui(f"❌ Error: Failed to parse XSD: {e}")
        return
    # Group fields by message (top-level element)
    message_fields = {}
    for row in xsd_rows:
        if not row['levels'] or not row['levels'][0]:
            continue
        msg = row['levels'][0]
        path = '/'.join([lvl for lvl in row['levels'] if lvl])
        if msg not in message_fields:
            message_fields[msg] = {}
        message_fields[msg][path] = row
    # 2. Load Excel (all sheets)
    try:
        xl = pd.ExcelFile(excel_path)
    except Exception as e:
        log_to_ui(f"❌ Error: Failed to read Excel: {e}")
        return
    total_errors = 0
    total_warnings = 0
    total_verified = 0
    # 3. For each XSD message, check its corresponding sheet
    for msg, fields in message_fields.items():
        if excel_sheet_name(msg) not in xl.sheet_names:
            log_to_ui(f"❌ Error: Sheet for message '{msg}' is missing in Excel.")
            total_errors += 1
            continue
        try:
            df = xl.parse(excel_sheet_name(msg))
        except Exception as e:
            log_to_ui(f"❌ Error: Failed to read sheet '{msg}': {e}")
            total_errors += 1
            continue
        sheet_errors = 0
        sheet_warnings = 0
        sheet_verified = 0
        log_to_ui(f"\n🗂️ Validating message '{msg}' in sheet '{msg}'")
        src_paths = reconstruct_excel_paths(df, 'src')
        tgt_paths = reconstruct_excel_paths(df, 'tgt')
        for path, meta in fields.items():
            if path not in src_paths:
                log_to_ui(f"❌ Error: Field [{path}] missing from Excel (sheet '{msg}').")
                sheet_errors += 1
                continue
            idx = src_paths[path]
            row = df.iloc[idx]
            excel_type = str(row.get('Type_src', '')).strip()
            if meta['Type'] and excel_type and meta['Type'] != excel_type:
                log_to_ui(f"⚠️ Warning: Type mismatch for [{path}] in sheet '{msg}': expected '{meta['Type']}', found '{excel_type}'")
                sheet_warnings += 1
            excel_card = str(row.get('Cardinality_src', '')).strip()
            expected_card = meta['Cardinality']
            if excel_card and excel_card != expected_card:
                log_to_ui(f"⚠️ Warning: Cardinality mismatch for [{path}] in sheet '{msg}': expected '{expected_card}', found '{excel_card}'")
                sheet_warnings += 1
            log_to_ui(f"✅ Field [{path}] validated successfully in sheet '{msg}'.")
            sheet_verified += 1
        # If source and target XSD are the same, check symmetry
        if set(src_paths.keys()) == set(tgt_paths.keys()) and src_paths:
            for path in src_paths:
                src_idx = src_paths[path]
                tgt_idx = tgt_paths[path]
                src_row = df.iloc[src_idx]
                tgt_row = df.iloc[tgt_idx]
                for col in ['Type', 'Cardinality']:
                    src_val = str(src_row.get(f'{col}_src', '')).strip()
                    tgt_val = str(tgt_row.get(f'{col}_tgt', '')).strip()
                    if src_val != tgt_val:
                        log_to_ui(f"⚠️ Warning: Source/Target mismatch for [{path}] column '{col}' in sheet '{msg}': src='{src_val}', tgt='{tgt_val}'")
                        sheet_warnings += 1
        log_to_ui(f"📝 Message '{msg}' validation: {sheet_errors} errors, {sheet_warnings} warning(s), {sheet_verified} fields verified.")
        total_errors += sheet_errors
        total_warnings += sheet_warnings
        total_verified += sheet_verified
    log_to_ui(f"\n🔎 Validation completed: {total_errors} errors, {total_warnings} warning(s), {total_verified} fields verified across {len(message_fields)} messages.")
    # Optionally export report
    if total_errors or total_warnings:
        report_rows = [msg for msg in _log_messages if msg.startswith('❌') or msg.startswith('⚠️')]
        pd.DataFrame({'issue': report_rows}).to_csv('validation_report.csv', index=False) 