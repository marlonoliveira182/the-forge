import os
import json
from pathlib import Path
from src.core.schema_processor import SchemaProcessor
from src.core.mapping_engine import MappingEngine

# Fix the path to point to the correct tests directory
QUICK_TEST_DIR = Path(__file__).parent.parent.parent / "tests" / "quick_test_cases"

# Debug output
print(f"[DEBUG] QUICK_TEST_DIR: {QUICK_TEST_DIR}")
print(f"[DEBUG] QUICK_TEST_DIR exists: {QUICK_TEST_DIR.exists()}")

class QuickTestResult:
    def __init__(self, name, source_file, target_file, field_count_source, field_count_target, mappings, errors=None, expected=None, category=None, description=None):
        self.name = name
        self.source_file = source_file
        self.target_file = target_file
        self.field_count_source = field_count_source
        self.field_count_target = field_count_target
        self.mappings = mappings
        self.errors = errors or []
        self.expected = expected or {}
        self.category = category
        self.description = description

class QuickTestRunner:
    def __init__(self):
        self.schema_processor = SchemaProcessor()
        self.mapping_engine = MappingEngine()
        self.comprehensive_config = None
        self.load_comprehensive_config()

    def load_comprehensive_config(self):
        """Load comprehensive test configuration"""
        config_file = QUICK_TEST_DIR / "comprehensive" / "test_config.json"
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    self.comprehensive_config = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load comprehensive test config: {e}")

    def list_test_cases(self):
        """List all available test cases, including comprehensive ones recursively"""
        test_cases = []
        # Standard test cases (direct subdirectories)
        for d in QUICK_TEST_DIR.iterdir():
            if d.is_dir() and d.name != "comprehensive":
                test_cases.append({
                    "name": d.name,
                    "path": d,
                    "type": "standard",
                    "category": "standard"
                })
        # Recursively add all subdirectories in 'comprehensive' as test cases
        comprehensive_dir = QUICK_TEST_DIR / "comprehensive"
        if comprehensive_dir.exists():
            for subdir in comprehensive_dir.iterdir():
                if subdir.is_dir():
                    test_cases.append({
                        "name": subdir.name,
                        "path": subdir,
                        "type": "comprehensive",
                        "category": "comprehensive"
                    })
        return test_cases

    def detect_schema_files(self, test_dir):
        files = list(test_dir.glob("*") )
        source = next((f for f in files if f.name.startswith("source.") and (f.suffix in [".xsd", ".json"])), None)
        target = next((f for f in files if f.name.startswith("target.") and (f.suffix in [".xsd", ".json"])), None)
        expected_mapping = next((f for f in files if f.name == "expected_mapping.json"), None)
        expected_results = next((f for f in files if f.name == "expected_results.json"), None)
        return source, target, expected_mapping, expected_results

    def run_test_case(self, test_case_info):
        """Run a test case with enhanced information"""
        test_dir = test_case_info["path"]
        name = test_case_info["name"]
        category = test_case_info.get("category", "unknown")
        description = test_case_info.get("description", "")
        expected_fields = test_case_info.get("expected_fields", 0)
        expected_mappings = test_case_info.get("expected_mappings", 0)
        
        source, target, expected_mapping, expected_results = self.detect_schema_files(test_dir)
        errors = []
        
        if not source or not target:
            return QuickTestResult(
                name, source, target, 0, 0, [], 
                errors=["Missing source or target schema file."],
                category=category, description=description
            )
        
        # Load schemas
        try:
            if source.suffix == ".xsd":
                source_fields = self.schema_processor.extract_fields_from_xsd(str(source))
            else:
                source_fields = self.schema_processor.extract_fields_from_json_schema(str(source))
            if target.suffix == ".xsd":
                target_fields = self.schema_processor.extract_fields_from_xsd(str(target))
            else:
                target_fields = self.schema_processor.extract_fields_from_json_schema(str(target))
        except Exception as e:
            return QuickTestResult(
                name, source, target, 0, 0, [], 
                errors=[f"Schema load error: {e}"],
                category=category, description=description
            )
        
        # Run mapping
        try:
            mappings = self.mapping_engine.map_fields(source_fields, target_fields)
        except Exception as e:
            return QuickTestResult(
                name, source, target, len(source_fields), len(target_fields), [], 
                errors=[f"Mapping error: {e}"],
                category=category, description=description
            )
        
        # Load expected results if present
        expected = {}
        if expected_mapping and expected_mapping.exists():
            with open(expected_mapping, "r", encoding="utf-8") as f:
                expected["mapping"] = json.load(f)
        if expected_results and expected_results.exists():
            with open(expected_results, "r", encoding="utf-8") as f:
                expected["results"] = json.load(f)
        
        # Add expected field/mapping counts for comprehensive tests
        if expected_fields > 0:
            expected["expected_fields"] = expected_fields
        if expected_mappings > 0:
            expected["expected_mappings"] = expected_mappings
        
        return QuickTestResult(
            name, source, target, len(source_fields), len(target_fields), mappings, 
            errors, expected, category, description
        )

    def run_comprehensive_test_suite(self):
        """Run all comprehensive test cases"""
        results = []
        test_cases = [tc for tc in self.list_test_cases() if tc["type"] == "comprehensive"]
        
        for test_case in test_cases:
            result = self.run_test_case(test_case)
            results.append(result)
        
        return results

    def get_test_categories(self):
        """Get available test categories"""
        if not self.comprehensive_config:
            return {"standard": "Standard Tests"}
        
        categories = {"standard": "Standard Tests"}
        for cat_id, cat_info in self.comprehensive_config.get("categories", {}).items():
            categories[cat_id] = cat_info["name"]
        
        return categories

    def get_tests_by_category(self, category):
        """Get test cases filtered by category"""
        all_tests = self.list_test_cases()
        if category == "all":
            return all_tests
        return [tc for tc in all_tests if tc.get("category") == category] 