import openpyxl

class ExcelMappingService:
    def __init__(self, max_structure_depth=8):
        self.max_structure_depth = max_structure_depth
        self.mapping_data = None
        self.headers = None
        self.sheet_names = []
        self.current_sheet = None
        self.header_rows = 2  # Support two header rows as in the template

    def list_sheets(self, file_path):
        wb = openpyxl.load_workbook(file_path, read_only=True)
        return wb.sheetnames

    def load_mapping_file(self, file_path, sheet_name=None):
        wb = openpyxl.load_workbook(file_path, data_only=True)
        self.sheet_names = wb.sheetnames
        if sheet_name is None:
            sheet = wb.active
            self.current_sheet = sheet.title
        else:
            sheet = wb[sheet_name]
            self.current_sheet = sheet_name
        # Read two header rows
        header_rows = list(sheet.iter_rows(min_row=1, max_row=self.header_rows, values_only=True))
        self.headers = [f'{header_rows[0][i] or ""}\n{header_rows[1][i] or ""}' for i in range(len(header_rows[0]))]
        self.mapping_data = []
        for row in sheet.iter_rows(min_row=self.header_rows+1, values_only=True):
            row_dict = dict(zip(self.headers, row))
            self.mapping_data.append(row_dict)
        return self.mapping_data

    def get_structures(self, structure_type='source'):
        if not self.mapping_data:
            return []
        key = 'Source Structure' if structure_type == 'source' else 'Target Structure'
        return sorted(set(row.get(key) for row in self.mapping_data if row.get(key)))

    def get_mapping_rows(self, source_sheet=None, target_sheet=None):
        if not self.mapping_data:
            return []
        return self.mapping_data

    @staticmethod
    def flatten_schema(schema, parent_key='', sep='.'):
        # Recursively flatten a dict (JSON Schema or XSD structure) into dot notation paths
        items = []
        if isinstance(schema, dict):
            for k, v in schema.items():
                new_key = f'{parent_key}{sep}{k}' if parent_key else k
                if isinstance(v, dict):
                    items.extend(ExcelMappingService.flatten_schema(v, new_key, sep=sep))
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        items.extend(ExcelMappingService.flatten_schema(item, f'{new_key}[{i}]', sep=sep))
                else:
                    items.append(new_key)
        return items

    def generate_mapping_from_schemas(self, source_schema, target_schema, source_struct=None, target_struct=None):
        # source_schema/target_schema: dicts representing the schema (already loaded)
        # source_struct/target_struct: root keys to use (if any)
        # Returns: list of mapping rows (dicts)
        if source_struct:
            source_schema = source_schema.get(source_struct, source_schema)
        if target_struct:
            target_schema = target_schema.get(target_struct, target_schema)
        
        source_paths = self.flatten_schema(source_schema)
        target_paths = self.flatten_schema(target_schema)
        
        # Create a more intelligent mapping based on field name similarity
        mapping_rows = []
        used_target_paths = set()
        
        for src_path in source_paths:
            # Try to find the best matching target path
            best_match = None
            best_score = 0
            
            for tgt_path in target_paths:
                if tgt_path in used_target_paths:
                    continue  # Skip already used target paths
                
                # Calculate similarity score based on field names
                src_field = src_path.split('.')[-1] if '.' in src_path else src_path
                tgt_field = tgt_path.split('.')[-1] if '.' in tgt_path else tgt_path
                
                # Simple similarity based on field name
                if src_field.lower() == tgt_field.lower():
                    score = 1.0
                elif src_field.lower() in tgt_field.lower() or tgt_field.lower() in src_field.lower():
                    score = 0.8
                else:
                    # Use difflib for fuzzy matching
                    import difflib
                    score = difflib.SequenceMatcher(None, src_field.lower(), tgt_field.lower()).ratio()
                
                if score > best_score and score > 0.3:  # Minimum threshold
                    best_score = score
                    best_match = tgt_path
            
            if best_match:
                used_target_paths.add(best_match)
                mapping_rows.append({
                    'Source Path': src_path, 
                    'Target Path': best_match,
                    'Match Score': f"{best_score:.2f}"
                })
            else:
                # No match found
                mapping_rows.append({
                    'Source Path': src_path, 
                    'Target Path': '',
                    'Match Score': '0.00'
                })
        
        # Add any remaining target paths as unmapped
        for tgt_path in target_paths:
            if tgt_path not in used_target_paths:
                mapping_rows.append({
                    'Source Path': '', 
                    'Target Path': tgt_path,
                    'Match Score': '0.00'
                })
        
        return mapping_rows 