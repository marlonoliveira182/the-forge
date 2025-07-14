"""
Excel Generator - Creates formatted Excel files for schema documentation and mapping
Enhanced for Request/Response structure with detailed metadata
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from .schema_processor import SchemaField
from .mapping_engine import FieldMapping

class ExcelGenerator:
    """Generates formatted Excel files for schema documentation and mapping"""
    
    def __init__(self):
        self.header_font = Font(bold=True, color="FFFFFF")
        self.header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        self.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Color coding for different mapping statuses
        self.exact_match_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # Green
        self.good_match_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")   # Yellow
        self.weak_match_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")   # Red
        self.unmapped_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")    # Gray
    
    def create_mapping_excel_request_response(self, source_fields: List[SchemaField], target_fields: List[SchemaField], 
                                           mappings: List[FieldMapping], transformations: Dict[str, Dict[str, Any]], 
                                           output_path: str) -> bool:
        """Create Excel file with Request/Response structure for confirmed mappings"""
        try:
            wb = Workbook()
            
            # Create Request sheet
            request_ws = wb.active
            if request_ws:
                request_ws.title = "Request"
            self._create_request_response_sheet(request_ws, source_fields, mappings, transformations, "Request")
            
            # Create Response sheet
            response_ws = wb.create_sheet("Response")
            self._create_request_response_sheet(response_ws, target_fields, mappings, transformations, "Response")
            
            # Create Summary sheet
            self._create_summary_sheet(wb, source_fields, target_fields, mappings)
            
            # Create Transformations sheet
            if transformations:
                self._create_transformations_sheet(wb, mappings, transformations)
            
            # Create Unmapped Fields sheet
            self._create_unmapped_sheet(wb, source_fields, target_fields, mappings)
            
            # Save workbook
            wb.save(output_path)
            return True
            
        except Exception as e:
            print(f"Error creating Request/Response Excel: {e}")
            return False
    
    def _create_request_response_sheet(self, ws, fields: List[SchemaField], mappings: List[FieldMapping], 
                                     transformations: Dict[str, Dict[str, Any]], sheet_type: str):
        """Create Request or Response sheet with detailed field information"""
        # Define columns for mapping overview
        columns = [
            "Source Field Path", "Source Field Name", "Source Type",
            "Target Field Path", "Target Field Name", "Target Type",
            "Mapping Status", "Transformation Logic", "Notes"
        ]
        # Add headers
        for col, header in enumerate(columns, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = self.header_font
            cell.fill = self.header_fill
            cell.border = self.border
            cell.alignment = Alignment(horizontal='center', vertical='center')
        row = 2
        for field in fields:
            # Find mapping for this field
            mapping = next((m for m in mappings if m.source_field.path == field.path), None)
            if mapping and not mapping.is_unmapped:
                status = "Mapped"
                row_fill = self.exact_match_fill if mapping.is_exact_match else (
                    self.good_match_fill if mapping.is_good_match else self.weak_match_fill)
                target_field = mapping.target_field
                target_path = target_field.path
                target_name = target_field.name
                target_type = target_field.type
                transformation_logic = self._get_transformation_logic(field.path, transformations)
                notes = mapping.mapping_notes
            else:
                status = "Unmapped"
                row_fill = self.unmapped_fill
                target_path = ""
                target_name = ""
                target_type = ""
                transformation_logic = ""
                notes = ""
            row_data = [
                field.path,
                field.name,
                field.type,
                target_path,
                target_name,
                target_type,
                status,
                transformation_logic,
                notes
            ]
            for col, value in enumerate(row_data, 1):
                cell = ws.cell(row=row, column=col, value=value)
                cell.border = self.border
                cell.fill = row_fill
                cell.alignment = Alignment(vertical='top', wrap_text=True)
            row += 1
        self._auto_adjust_columns(ws)
    
    def _get_transformation_logic(self, field_path: str, transformations: Dict[str, Dict[str, Any]]) -> str:
        """Get transformation logic for a field"""
        if field_path not in transformations:
            return ""
        
        rules = transformations[field_path]
        logic_parts = []
        
        if rules.get("type_conversion") and rules["type_conversion"] != "No conversion":
            logic_parts.append(f"Type: {rules['type_conversion']}")
        
        if rules.get("format_pattern"):
            logic_parts.append(f"Format: {rules['format_pattern']}")
        
        if rules.get("default_value"):
            logic_parts.append(f"Default: {rules['default_value']}")
        
        if rules.get("apply_validation"):
            logic_parts.append("Validation: Yes")
        
        if rules.get("custom_code"):
            logic_parts.append(f"Custom: {rules['custom_code'][:50]}...")
        
        return "; ".join(logic_parts)
    
    def _format_constraints(self, constraints: Dict[str, Any]) -> str:
        """Format constraints dictionary as string"""
        if not constraints:
            return ""
        
        constraint_parts = []
        for key, value in constraints.items():
            if isinstance(value, list):
                constraint_parts.append(f"{key}: {', '.join(map(str, value))}")
            else:
                constraint_parts.append(f"{key}: {value}")
        
        return "; ".join(constraint_parts)
    
    def _create_summary_sheet(self, wb: Workbook, source_fields: List[SchemaField], 
                            target_fields: List[SchemaField], mappings: List[FieldMapping]) -> None:
        """Create summary sheet with mapping statistics"""
        ws = wb.create_sheet("Mapping Summary")
        
        # Summary statistics
        total_source = len(source_fields)
        total_target = len(target_fields)
        exact_matches = len([m for m in mappings if m.is_exact_match])
        good_matches = len([m for m in mappings if m.is_good_match])
        weak_matches = len([m for m in mappings if m.is_weak_match])
        unmapped = len([m for m in mappings if m.is_unmapped])
        mapped_fields = len([m for m in mappings if not m.is_unmapped])
        
        # Headers
        headers = ["Metric", "Value", "Percentage"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = self.header_font
            cell.fill = self.header_fill
            cell.border = self.border
        
        # Data
        data = [
            ["Total Source Fields", total_source, "100%"],
            ["Total Target Fields", total_target, "100%"],
            ["Mapped Fields", mapped_fields, f"{mapped_fields/total_source*100:.1f}%" if total_source > 0 else "0%"],
            ["Exact Matches", exact_matches, f"{exact_matches/total_source*100:.1f}%" if total_source > 0 else "0%"],
            ["Good Matches", good_matches, f"{good_matches/total_source*100:.1f}%" if total_source > 0 else "0%"],
            ["Weak Matches", weak_matches, f"{weak_matches/total_source*100:.1f}%" if total_source > 0 else "0%"],
            ["Unmapped Fields", unmapped, f"{unmapped/total_source*100:.1f}%" if total_source > 0 else "0%"],
            ["Average Similarity", f"{sum(m.similarity for m in mappings)/len(mappings):.3f}" if mappings else "0.000", ""],
            ["Source Coverage", f"{mapped_fields}/{total_source}", f"{mapped_fields/total_source*100:.1f}%" if total_source > 0 else "0%"],
            ["Target Coverage", f"{len(set(m.target_field.path for m in mappings if not m.is_unmapped))}/{total_target}", f"{len(set(m.target_field.path for m in mappings if not m.is_unmapped))/total_target*100:.1f}%" if total_target > 0 else "0%"]
        ]
        
        for row, (metric, value, percentage) in enumerate(data, 2):
            ws.cell(row=row, column=1, value=metric).border = self.border
            ws.cell(row=row, column=2, value=value).border = self.border
            ws.cell(row=row, column=3, value=percentage).border = self.border
        
        # Auto-adjust column widths
        self._auto_adjust_columns(ws)
    
    def _create_transformations_sheet(self, wb: Workbook, mappings: List[FieldMapping], 
                                    transformations: Dict[str, Dict[str, Any]]) -> None:
        """Create transformations sheet with detailed transformation rules"""
        ws = wb.create_sheet("Transformations")
        
        # Headers
        headers = [
            "Source Field", "Target Field", "Type Conversion", "Format Pattern", 
            "Default Value", "Apply Validation", "Custom Code", "Notes"
        ]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = self.header_font
            cell.fill = self.header_fill
            cell.border = self.border
        
        # Data
        row = 2
        for source_path, rules in transformations.items():
            # Find the mapping for this source field
            mapping = next((m for m in mappings if m.source_field.path == source_path), None)
            
            if mapping:
                ws.cell(row=row, column=1, value=source_path).border = self.border
                ws.cell(row=row, column=2, value=mapping.target_field.path).border = self.border
                ws.cell(row=row, column=3, value=rules.get("type_conversion", "")).border = self.border
                ws.cell(row=row, column=4, value=rules.get("format_pattern", "")).border = self.border
                ws.cell(row=row, column=5, value=rules.get("default_value", "")).border = self.border
                ws.cell(row=row, column=6, value="Yes" if rules.get("apply_validation", False) else "No").border = self.border
                ws.cell(row=row, column=7, value=rules.get("custom_code", "")).border = self.border
                ws.cell(row=row, column=8, value=mapping.mapping_notes).border = self.border
            
            row += 1
        
        # Auto-adjust column widths
        self._auto_adjust_columns(ws)
    
    def _create_unmapped_sheet(self, wb: Workbook, source_fields: List[SchemaField], 
                              target_fields: List[SchemaField], mappings: List[FieldMapping]) -> None:
        """Create sheet showing unmapped fields"""
        ws = wb.create_sheet("Unmapped Fields")
        
        # Headers
        headers = ["Schema Type", "Field Path", "Field Name", "Data Type", "Cardinality", "Required", "Description", "Constraints"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = self.header_font
            cell.fill = self.header_fill
            cell.border = self.border
        
        # Unmapped source fields
        row = 2
        for mapping in mappings:
            if mapping.is_unmapped:
                field = mapping.source_field
                ws.cell(row=row, column=1, value="Source").border = self.border
                ws.cell(row=row, column=2, value=field.path).border = self.border
                ws.cell(row=row, column=3, value=field.name).border = self.border
                ws.cell(row=row, column=4, value=field.type).border = self.border
                ws.cell(row=row, column=5, value=field.cardinality).border = self.border
                ws.cell(row=row, column=6, value="Yes" if field.required else "No").border = self.border
                ws.cell(row=row, column=7, value=field.description).border = self.border
                ws.cell(row=row, column=8, value=self._format_constraints(field.constraints)).border = self.border
                row += 1
        
        # Unmapped target fields
        mapped_target_paths = {m.target_field.path for m in mappings if not m.is_unmapped}
        for field in target_fields:
            if field.path not in mapped_target_paths:
                ws.cell(row=row, column=1, value="Target").border = self.border
                ws.cell(row=row, column=2, value=field.path).border = self.border
                ws.cell(row=row, column=3, value=field.name).border = self.border
                ws.cell(row=row, column=4, value=field.type).border = self.border
                ws.cell(row=row, column=5, value=field.cardinality).border = self.border
                ws.cell(row=row, column=6, value="Yes" if field.required else "No").border = self.border
                ws.cell(row=row, column=7, value=field.description).border = self.border
                ws.cell(row=row, column=8, value=self._format_constraints(field.constraints)).border = self.border
                row += 1
        
        # Auto-adjust column widths
        self._auto_adjust_columns(ws)
    
    def _auto_adjust_columns(self, ws):
        """Auto-adjust column widths"""
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
    
    # Legacy methods for backward compatibility
    def create_schema_excel(self, fields: List[SchemaField], output_path: str, schema_name: str = "Schema") -> bool:
        """Create Excel file with schema field documentation (legacy method)"""
        try:
            # Create workbook
            wb = Workbook()
            ws = wb.active
            if ws:
                ws.title = "Schema Fields"
            
            # Define columns
            columns = [
                "Element Level 1", "Element Level 2", "Element Level 3", 
                "Element Level 4", "Element Level 5", "Element Level 6",
                "Type", "Cardinality", "Description", "Details", "JSON Path"
            ]
            
            # Add headers
            for col, header in enumerate(columns, 1):
                if ws:
                    cell = ws.cell(row=1, column=col, value=header)
                    if cell:
                        cell.font = self.header_font
                        cell.fill = self.header_fill
                        cell.border = self.border
                        cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Process fields
            row = 2
            for field in fields:
                # Split path into levels
                path_parts = field.path.split('.')
                levels = path_parts + [''] * (6 - len(path_parts))
                
                # Create row data
                row_data = levels + [
                    field.type,
                    field.cardinality,
                    field.description,
                    field.details,
                    field.path
                ]
                
                # Add row to worksheet
                for col, value in enumerate(row_data, 1):
                    if ws:
                        cell = ws.cell(row=row, column=col, value=value)
                        if cell:
                            cell.border = self.border
                            cell.alignment = Alignment(vertical='top', wrap_text=True)
                
                row += 1
            
            # Auto-adjust column widths
            if ws:
                self._auto_adjust_columns(ws)
            
            # Save workbook
            wb.save(output_path)
            return True
            
        except Exception as e:
            print(f"Error creating schema Excel: {e}")
            return False
    
    def create_mapping_excel(self, source_fields: List[SchemaField], target_fields: List[SchemaField], 
                           mappings: List[FieldMapping], output_path: str) -> bool:
        """Create Excel file with field mappings between schemas (legacy method)"""
        # Use the new Request/Response structure
        return self.create_mapping_excel_request_response(source_fields, target_fields, mappings, {}, output_path) 