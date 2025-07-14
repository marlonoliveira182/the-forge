from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QListWidget, 
                               QPushButton, QTextEdit, QHBoxLayout, QComboBox,
                               QGroupBox, QGridLayout, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal
from .quick_test_runner import QuickTestRunner

class TestRunnerThread(QThread):
    """Thread for running tests to avoid blocking UI"""
    test_completed = Signal(object)
    progress_updated = Signal(int, int)
    
    def __init__(self, runner, test_cases):
        super().__init__()
        self.runner = runner
        self.test_cases = test_cases
        
    def run(self):
        for i, test_case in enumerate(self.test_cases):
            result = self.runner.run_test_case(test_case)
            self.test_completed.emit(result)
            self.progress_updated.emit(i + 1, len(self.test_cases))

class QuickTestDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quick Test Runner")
        self.setMinimumSize(800, 600)
        self.runner = QuickTestRunner()
        self.test_runner_thread = None
        self.all_test_cases = []  # Initialize the attribute
        self.setup_ui()
        self.load_test_cases()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Category filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.currentTextChanged.connect(self.filter_tests)
        filter_layout.addWidget(self.category_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Test list
        test_group = QGroupBox("Test Cases")
        test_layout = QVBoxLayout(test_group)
        self.test_list = QListWidget()
        self.test_list.itemDoubleClicked.connect(self.run_selected_test)
        self.test_list.currentRowChanged.connect(lambda _: self.run_selected_test())
        test_layout.addWidget(self.test_list)
        layout.addWidget(test_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.run_all_btn = QPushButton("Run All Tests")
        self.run_all_btn.clicked.connect(self.run_all_tests)
        self.run_comprehensive_btn = QPushButton("Run Comprehensive Suite")
        self.run_comprehensive_btn.clicked.connect(self.run_comprehensive_suite)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.run_all_btn)
        btn_layout.addWidget(self.run_comprehensive_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        results_layout.addWidget(self.result_box)
        layout.addWidget(results_group)

        # Set palette for dark/light mode
        self.apply_list_palette()
        self.apply_dialog_style()

    def load_test_cases(self):
        """Load test cases and populate category filter"""
        # Load categories
        categories = self.runner.get_test_categories()
        self.category_combo.clear()
        self.category_combo.addItem("All Categories", "all")
        for cat_id, cat_name in categories.items():
            self.category_combo.addItem(cat_name, cat_id)
        
        # Load test cases
        self.all_test_cases = self.runner.list_test_cases()
        self.filter_tests()

    def filter_tests(self):
        """Filter test cases by selected category"""
        self.test_list.clear()
        selected_category = self.category_combo.currentData()
        
        if selected_category == "all":
            filtered_tests = self.all_test_cases
        else:
            filtered_tests = self.runner.get_tests_by_category(selected_category)
        
        for test_case in filtered_tests:
            item_text = test_case["name"]
            if test_case.get("description"):
                item_text += f" - {test_case['description']}"
            self.test_list.addItem(item_text)

    def run_selected_test(self):
        """Run the currently selected test case"""
        item = self.test_list.currentItem()
        if not item:
            return
        
        # Find the test case info
        test_name = item.text().split(" - ")[0]  # Remove description
        test_case = next((tc for tc in self.all_test_cases if tc["name"] == test_name), None)
        if not test_case:
            self.result_box.setText("Test case not found.")
            return
        
        result = self.runner.run_test_case(test_case)
        self.display_result(result)

    def run_all_tests(self):
        """Run all visible test cases"""
        visible_tests = []
        for i in range(self.test_list.count()):
            item = self.test_list.item(i)
            test_name = item.text().split(" - ")[0]
            test_case = next((tc for tc in self.all_test_cases if tc["name"] == test_name), None)
            if test_case:
                visible_tests.append(test_case)
        
        if not visible_tests:
            self.result_box.setText("No test cases to run.")
            return
        
        self.run_tests_in_thread(visible_tests)

    def run_comprehensive_suite(self):
        """Run all comprehensive test cases"""
        comprehensive_tests = [tc for tc in self.all_test_cases if tc["type"] == "comprehensive"]
        if not comprehensive_tests:
            self.result_box.setText("No comprehensive test cases found.")
            return
        
        self.run_tests_in_thread(comprehensive_tests)

    def run_tests_in_thread(self, test_cases):
        """Run tests in a separate thread to avoid blocking UI"""
        self.test_runner_thread = TestRunnerThread(self.runner, test_cases)
        self.test_runner_thread.test_completed.connect(self.on_test_completed)
        self.test_runner_thread.progress_updated.connect(self.on_progress_updated)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(test_cases))
        self.progress_bar.setValue(0)
        self.result_box.clear()
        self.result_box.append("Running tests...\n")
        
        self.test_runner_thread.start()

    def on_test_completed(self, result):
        """Handle completed test result"""
        self.display_result(result)

    def on_progress_updated(self, current, total):
        """Update progress bar"""
        self.progress_bar.setValue(current)
        if current == total:
            self.progress_bar.setVisible(False)

    def display_result(self, result, append=False):
        """Display test result with enhanced information"""
        lines = []
        if not append:
            lines.append("=" * 60)
        
        lines.append(f"Test: {result.name}")
        if result.category and result.category != "unknown":
            lines.append(f"Category: {result.category}")
        if result.description:
            lines.append(f"Description: {result.description}")
        lines.append(f"Source: {result.source_file}")
        lines.append(f"Target: {result.target_file}")
        lines.append(f"Source fields: {result.field_count_source}")
        lines.append(f"Target fields: {result.field_count_target}")
        
        # Check expected results for comprehensive tests
        if result.expected:
            expected_fields = result.expected.get("expected_fields")
            expected_mappings = result.expected.get("expected_mappings")
            if expected_fields:
                status = "✓" if result.field_count_source == expected_fields else "✗"
                lines.append(f"Expected source fields: {expected_fields} {status}")
            if expected_mappings:
                status = "✓" if len(result.mappings) == expected_mappings else "✗"
                lines.append(f"Expected mappings: {expected_mappings} {status}")
        
        if result.errors:
            lines.append("Errors:")
            for err in result.errors:
                lines.append(f"  - {err}")
        else:
            lines.append(f"Mappings: {len(result.mappings)}")
            # Show sample mappings with similarity scores
            for m in result.mappings[:5]:
                src = getattr(m.source_field, 'name', '?')
                tgt = getattr(m.target_field, 'name', '?')
                sim = getattr(m, 'similarity', '?')
                lines.append(f"  {src} -> {tgt} (sim={sim:.3f})")
            if len(result.mappings) > 5:
                lines.append(f"  ...and {len(result.mappings)-5} more")
        
        lines.append("=" * 60)
        
        if append:
            self.result_box.append("\n".join(lines))
        else:
            self.result_box.setText("\n".join(lines))
        # Load schemas into main window if possible
        if self.parent() and hasattr(self.parent(), "load_schema_files_from_quick_test"):
            self.parent().load_schema_files_from_quick_test(str(result.source_file), str(result.target_file)) 

    def apply_list_palette(self):
        from PySide6.QtGui import QPalette, QColor
        palette = self.test_list.palette()
        mode = getattr(self.parent(), 'current_mode', 'dark')
        if mode == 'dark':
            palette.setColor(QPalette.Base, QColor('#232526'))
            palette.setColor(QPalette.Text, QColor('#F1F1F1'))
            palette.setColor(QPalette.Highlight, QColor('#C0392B'))
            palette.setColor(QPalette.HighlightedText, QColor('#FFF8E1'))
        else:
            palette.setColor(QPalette.Base, QColor('#FFFFFF'))
            palette.setColor(QPalette.Text, QColor('#232526'))
            palette.setColor(QPalette.Highlight, QColor('#FF6F1F'))
            palette.setColor(QPalette.HighlightedText, QColor('#232526'))
        self.test_list.setPalette(palette) 

    def apply_dialog_style(self):
        mode = getattr(self.parent(), 'current_mode', 'dark')
        if mode == 'dark':
            self.setStyleSheet('''
                QDialog { background-color: #18191A; }
                QGroupBox { background-color: #232526; color: #FFF8E1; border: 2px solid #44484C; border-radius: 8px; }
                QGroupBox::title { color: #FFD700; }
            ''')
        else:
            self.setStyleSheet('''
                QDialog { background-color: #F8F9FA; }
                QGroupBox { background-color: #FFFFFF; color: #232526; border: 2px solid #CED4DA; border-radius: 8px; }
                QGroupBox::title { color: #FF6F1F; }
            ''') 