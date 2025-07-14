"""
Main Window - The Forge v2.0.0 Desktop Application
Enhanced with proper drag-and-drop and hierarchical tree view
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTreeWidget, QTreeWidgetItem, QPushButton, QLabel,
    QLineEdit, QFileDialog, QMessageBox, QProgressBar, QTextEdit,
    QSplitter, QGroupBox, QFormLayout, QSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QStatusBar,
    QMenuBar, QMenu, QToolBar, QFrame, QListWidget, QListWidgetItem, QAbstractItemView,
    QDialog, QDialogButtonBox, QTextEdit as QTextEditDialog, QCheckBox,
    QDockWidget, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QAction, QDrag, QDragEnterEvent, QDropEvent, QFont, QPalette, QColor, QIcon
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize, QMimeData, QObject

from core.schema_processor import SchemaProcessor, SchemaField
from core.mapping_engine import MappingEngine, FieldMapping
from core.excel_generator import ExcelGenerator
from .quick_test_dialog import QuickTestDialog
from .quick_test_runner import QuickTestRunner
from .mapping_connector_overlay import MappingConnectorOverlay

class TransformationDialog(QDialog):
    """Dialog for configuring field transformations"""
    
    def __init__(self, source_field: SchemaField, target_field: SchemaField, parent=None):
        super().__init__(parent)
        self.source_field = source_field
        self.target_field = target_field
        self.transformation_rules = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the transformation dialog UI"""
        self.setWindowTitle("Field Transformation")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Field information
        info_group = QGroupBox("Field Information")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("Source Field:", QLabel(self.source_field.path))
        info_layout.addRow("Source Type:", QLabel(self.source_field.type))
        info_layout.addRow("Target Field:", QLabel(self.target_field.path))
        info_layout.addRow("Target Type:", QLabel(self.target_field.type))
        
        layout.addWidget(info_group)
        
        # Transformation options
        transform_group = QGroupBox("Transformation Rules")
        transform_layout = QVBoxLayout(transform_group)
        
        # Type conversion
        self.type_conversion_combo = QComboBox()
        self.type_conversion_combo.addItems([
            "No conversion",
            "String to Integer",
            "Integer to String", 
            "String to Date",
            "Date to String",
            "String to Boolean",
            "Boolean to String",
            "Uppercase",
            "Lowercase",
            "Trim whitespace",
            "Remove special characters"
        ])
        transform_layout.addWidget(QLabel("Type Conversion:"))
        transform_layout.addWidget(self.type_conversion_combo)
        
        # Format options
        self.format_edit = QLineEdit()
        self.format_edit.setPlaceholderText("Format pattern (e.g., yyyy-MM-dd for dates)")
        transform_layout.addWidget(QLabel("Format Pattern:"))
        transform_layout.addWidget(self.format_edit)
        
        # Default value
        self.default_value_edit = QLineEdit()
        self.default_value_edit.setPlaceholderText("Default value if source is empty")
        transform_layout.addWidget(QLabel("Default Value:"))
        transform_layout.addWidget(self.default_value_edit)
        
        # Validation
        self.validation_check = QCheckBox("Apply validation")
        transform_layout.addWidget(self.validation_check)
        
        # Custom transformation
        self.custom_transform_edit = QTextEditDialog()
        self.custom_transform_edit.setMaximumHeight(100)
        self.custom_transform_edit.setPlaceholderText("Custom transformation code (Python)")
        transform_layout.addWidget(QLabel("Custom Transformation:"))
        transform_layout.addWidget(self.custom_transform_edit)
        
        layout.addWidget(transform_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_transformation_rules(self) -> Dict[str, Any]:
        """Get the transformation rules from the dialog"""
        return {
            "type_conversion": self.type_conversion_combo.currentText(),
            "format_pattern": self.format_edit.text(),
            "default_value": self.default_value_edit.text(),
            "apply_validation": self.validation_check.isChecked(),
            "custom_code": self.custom_transform_edit.toPlainText()
        }

class DraggableTreeWidget(QTreeWidget):
    """Tree widget with enhanced drag and drop support for schema mapping"""
    fieldDropped = Signal(object, object)  # event, target_field
    
    def __init__(self, parent=None, is_source=True):
        super().__init__(parent)
        self.is_source = is_source
        self.setDragEnabled(is_source)  # Only source can drag
        self.setAcceptDrops(not is_source)  # Only target can accept drops
        self.setDropIndicatorShown(not is_source)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setExpandsOnDoubleClick(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        expand_action = menu.addAction("Expand Node")
        collapse_action = menu.addAction("Collapse Node")
        expand_all_action = menu.addAction("Expand All Children")
        collapse_all_action = menu.addAction("Collapse All Children")
        action = menu.exec(self.viewport().mapToGlobal(pos))
        item = self.itemAt(pos)
        if not item:
            return
        # Use getattr to avoid attribute errors
        field_data = getattr(item, 'field_data', None)
        if action == expand_action:
            item.setExpanded(True)
        elif action == collapse_action:
            item.setExpanded(False)
        elif action == expand_all_action:
            self.expand_all_children(item)
        elif action == collapse_all_action:
            self.collapse_all_children(item)

    def expand_all_children(self, item):
        item.setExpanded(True)
        for i in range(item.childCount()):
            self.expand_all_children(item.child(i))

    def collapse_all_children(self, item):
        item.setExpanded(False)
        for i in range(item.childCount()):
            self.collapse_all_children(item.child(i))
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        print(f"[DEBUG] dragEnterEvent: hasFormat={event.mimeData().hasFormat('application/x-schema-field')}")
        if event.mimeData().hasFormat("application/x-schema-field"):
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        print(f"[DEBUG] dropEvent: hasFormat={event.mimeData().hasFormat('application/x-schema-field')}")
        if event.mimeData().hasFormat("application/x-schema-field"):
            event.acceptProposedAction()
            # Get the target field from the drop location
            target_item = self.itemAt(event.pos())
            if target_item and hasattr(target_item, 'field_data'):
                print(f"[DEBUG] dropEvent: target_item.field_data.path={getattr(target_item.field_data, 'path', None)}")
                self.fieldDropped.emit(event, target_item.field_data)
    
    def startDrag(self, actions):
        item = self.currentItem()
        # noinspection PyUnresolvedReferences
        if item and hasattr(item, 'field_data'):
            field_data = {
                'path': item.field_data.path,
                'name': item.field_data.name,
                'type': item.field_data.type,
                'description': item.field_data.description
            }
            print(f"[DEBUG] startDrag: field_data={field_data}")
            mime_data = QMimeData()
            mime_data.setData("application/x-schema-field", json.dumps(field_data).encode())
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.MoveAction)

class MainWindow(QMainWindow):
    """Main application window for The Forge v2.0.0 - Visual Schema Mapping"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The Forge v2.0.0 - Visual Schema Mapping")
        self.setMinimumSize(1600, 1000)
        self.current_mode = 'dark'  # Default to dark mode
        
        # Initialize core components
        self.schema_processor = SchemaProcessor()
        self.mapping_engine = MappingEngine()
        self.excel_generator = ExcelGenerator()
        
        # Data storage
        self.source_fields: List[SchemaField] = []
        self.target_fields: List[SchemaField] = []
        self.mappings: List[FieldMapping] = []
        self.transformations: Dict[str, Dict[str, Any]] = {}
        
        self.quick_test_runner = QuickTestRunner()
        self.setup_ui()
        self.setup_quick_test_sidebar()
        self.setup_menu()
        self.setup_status_bar()
        self.apply_styles(self.current_mode)
    
    def setup_ui(self):
        """Setup the main user interface with 3-panel layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header with file selection
        self.setup_file_selection(main_layout)
        
        # Top panel: Source and Target schemas
        top_panel = QHBoxLayout()
        
        # Source schema panel
        source_panel = self.create_schema_panel("Source Schema", True)
        top_panel.addWidget(source_panel)
        
        # Spacer for connector channel
        connector_spacer = QSpacerItem(80, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        top_panel.addSpacerItem(connector_spacer)
        
        # Target schema panel  
        target_panel = self.create_schema_panel("Target Schema", False)
        top_panel.addWidget(target_panel)
        
        main_layout.addLayout(top_panel)
        
        # Add mapping connector overlay as a child of the main window
        self.mapping_connector_overlay = MappingConnectorOverlay(
            self.source_tree, self.target_tree, lambda: self.mappings, parent=self
        )
        self._update_connector_overlay_geometry()
        self.mapping_connector_overlay.show()
        self.mapping_connector_overlay.raise_()
        # Bottom panel: Mapping table
        mapping_panel = self.create_mapping_panel()
        main_layout.addWidget(mapping_panel)
        
        # Control buttons
        self.setup_control_buttons(main_layout)
        
        # Set the application window icon
        self.setWindowIcon(QIcon(str(Path(__file__).parent.parent / 'assets' / 'anvil.ico')))
    
    def setup_file_selection(self, parent_layout):
        """Setup file selection controls"""
        file_group = QGroupBox("Schema Files")
        file_layout = QFormLayout(file_group)
        
        # Source file selection
        self.source_file_edit = QLineEdit()
        self.source_file_edit.setPlaceholderText("Select source schema file (XSD or JSON)")
        source_browse_btn = QPushButton("Browse...")
        source_browse_btn.clicked.connect(lambda: self.browse_file(self.source_file_edit, "Schema Files (*.xsd *.json)"))
        
        source_layout = QHBoxLayout()
        source_layout.addWidget(self.source_file_edit)
        source_layout.addWidget(source_browse_btn)
        file_layout.addRow("Source Schema:", source_layout)
        
        # Target file selection
        self.target_file_edit = QLineEdit()
        self.target_file_edit.setPlaceholderText("Select target schema file (XSD or JSON)")
        target_browse_btn = QPushButton("Browse...")
        target_browse_btn.clicked.connect(lambda: self.browse_file(self.target_file_edit, "Schema Files (*.xsd *.json)"))
        
        target_layout = QHBoxLayout()
        target_layout.addWidget(self.target_file_edit)
        target_layout.addWidget(target_browse_btn)
        file_layout.addRow("Target Schema:", target_layout)
        
        # Load schemas button
        load_btn = QPushButton("Load Schemas")
        load_btn.clicked.connect(self.load_schemas)
        file_layout.addRow("", load_btn)
        
        parent_layout.addWidget(file_group)
    
    def create_schema_panel(self, title: str, is_source: bool) -> QWidget:
        """Create a schema panel with hierarchical tree view and field count"""
        panel = QGroupBox(title)
        layout = QVBoxLayout(panel)
        # Field count label
        count_label = QLabel("Fields: 0")
        count_label.setObjectName(f"count_label_{'source' if is_source else 'target'}")
        layout.addWidget(count_label)
        # Schema tree with hierarchical structure
        tree = DraggableTreeWidget(parent=panel, is_source=is_source)
        tree.setHeaderLabels(["Field Name", "Type", "Cardinality", "Description", "Restrictions"])
        tree.setColumnWidth(0, 200)
        tree.setColumnWidth(1, 100)
        tree.setColumnWidth(2, 80)
        tree.setColumnWidth(3, 150)
        tree.setColumnWidth(4, 150) # Added Restrictions column
        if is_source:
            self.source_tree = tree
            self.source_count_label = count_label
        else:
            self.target_tree = tree
            self.target_count_label = count_label
            # Connect the custom signal to handle_field_drop
            tree.fieldDropped.connect(self.handle_field_drop)
        layout.addWidget(tree)
        # Search/filter
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("Filter fields...")
        search_layout.addWidget(search_edit)
        layout.addLayout(search_layout)
        return panel
    
    def create_mapping_panel(self) -> QWidget:
        """Create the mapping table panel"""
        panel = QGroupBox("Field Mappings")
        layout = QVBoxLayout(panel)
        
        # Mapping table
        self.mapping_table = QTableWidget()
        self.mapping_table.setColumnCount(7)
        self.mapping_table.setHorizontalHeaderLabels([
            "Source Field", "Target Field", "Transformation", "Status", "Similarity", "Notes", "Actions"
        ])
        
        header = self.mapping_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.mapping_table)
        
        # Mapping controls
        controls_layout = QHBoxLayout()
        
        auto_map_btn = QPushButton("Auto Map")
        auto_map_btn.clicked.connect(self.auto_map_schemas)
        controls_layout.addWidget(auto_map_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_mappings)
        controls_layout.addWidget(clear_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        return panel
    
    def setup_control_buttons(self, parent_layout):
        """Setup control buttons"""
        button_layout = QHBoxLayout()
        
        # Export button
        export_btn = QPushButton("Export to Excel")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        export_btn.clicked.connect(self.export_to_excel)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        # Validation button
        validate_btn = QPushButton("Validate Mapping")
        validate_btn.clicked.connect(self.validate_mapping)
        button_layout.addWidget(validate_btn)
        
        parent_layout.addLayout(button_layout)
    
    def setup_menu(self):
        """Setup the application menu"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open Schemas", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_schemas)
        file_menu.addAction(open_action)
        
        export_action = QAction("&Export to Excel", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_to_excel)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu for toggling sidebar
        view_menu = menubar.addMenu("&View")
        toggle_sidebar_action = QAction("Quick Test Sidebar", self, checkable=True)
        toggle_sidebar_action.setChecked(True)
        toggle_sidebar_action.triggered.connect(self.toggle_quick_test_sidebar)
        view_menu.addAction(toggle_sidebar_action)
        self.toggle_sidebar_action = toggle_sidebar_action
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        auto_map_action = QAction("&Auto Map Fields", self)
        auto_map_action.triggered.connect(self.auto_map_schemas)
        tools_menu.addAction(auto_map_action)
        
        validate_action = QAction("&Validate Mapping", self)
        validate_action.triggered.connect(self.validate_mapping)
        tools_menu.addAction(validate_action)
        
        tools_menu.addSeparator()
        
        quick_test_action = QAction("&Quick Test", self)
        quick_test_action.setShortcut("Ctrl+T")
        quick_test_action.triggered.connect(self.open_quick_test_dialog)
        tools_menu.addAction(quick_test_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Load source and target schemas to begin mapping")
    
    def apply_styles(self, mode='dark'):
        """Apply dark or light theme to the application"""
        if mode == 'dark':
            self.setStyleSheet("""
                QMainWindow { background-color: #18191A; }
                QGroupBox { font-weight: bold; border: 2px solid #44484C; border-radius: 8px; margin-top: 10px; padding-top: 10px; background-color: #232526; color: #FFF8E1; }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 8px 0 8px; color: #FFD700; }
                QPushButton { background-color: #FF6F1F; color: #F1F1F1; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
                QPushButton:hover { background-color: #FFD700; color: #232526; }
                QPushButton:pressed { background-color: #C0392B; color: #FFF8E1; }
                QPushButton:disabled { background-color: #44484C; color: #B0B0B0; }
                QLineEdit { padding: 8px; border: 2px solid #44484C; border-radius: 4px; background-color: #282A2D; color: #F1F1F1; }
                QLineEdit:focus { border-color: #FF6F1F; }
                QTreeWidget { border: 2px solid #44484C; border-radius: 4px; background-color: #232526; alternate-background-color: #282A2D; color: #F1F1F1; }
                QTreeWidget::item:selected { background-color: #C0392B; color: #FFF8E1; }
                QTableWidget { border: 2px solid #44484C; border-radius: 4px; background-color: #232526; gridline-color: #44484C; color: #F1F1F1; }
                QTableWidget::item { padding: 8px; }
                QTableWidget::item:selected { background-color: #FF6F1F; color: #232526; }
                QHeaderView::section { background-color: #282A2D; padding: 8px; border: 1px solid #44484C; font-weight: bold; color: #FFD700; }
                QLabel, QListWidget, QListWidgetItem { color: #F1F1F1; }
                QStatusBar { background: #18191A; color: #FFD700; }
            """)
        else:  # light mode
            self.setStyleSheet("""
                QMainWindow { background-color: #F8F9FA; }
                QGroupBox { font-weight: bold; border: 2px solid #CED4DA; border-radius: 8px; margin-top: 10px; padding-top: 10px; background-color: #FFFFFF; color: #333333; }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 8px 0 8px; color: #FF6F1F; }
                QPushButton { background-color: #FF6F1F; color: #232526; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
                QPushButton:hover { background-color: #FFD700; color: #232526; }
                QPushButton:pressed { background-color: #C0392B; color: #FFF8E1; }
                QPushButton:disabled { background-color: #CED4DA; color: #B0B0B0; }
                QLineEdit { padding: 8px; border: 2px solid #CED4DA; border-radius: 4px; background-color: #FFFFFF; color: #232526; }
                QLineEdit:focus { border-color: #FF6F1F; }
                QTreeWidget { border: 2px solid #CED4DA; border-radius: 4px; background-color: #FFFFFF; alternate-background-color: #F8F9FA; color: #232526; }
                QTreeWidget::item:selected { background-color: #FF6F1F; color: #232526; }
                QTableWidget { border: 2px solid #CED4DA; border-radius: 4px; background-color: #FFFFFF; gridline-color: #CED4DA; color: #232526; }
                QTableWidget::item { padding: 8px; }
                QTableWidget::item:selected { background-color: #FF6F1F; color: #232526; }
                QHeaderView::section { background-color: #F8F9FA; padding: 8px; border: 1px solid #CED4DA; font-weight: bold; color: #FF6F1F; }
                QLabel, QListWidget, QListWidgetItem { color: #232526; }
                QStatusBar { background: #F8F9FA; color: #FF6F1F; }
            """)
    
    def browse_file(self, line_edit: QLineEdit, filter_str: str):
        """Browse for a file and update the line edit"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", filter_str
        )
        if file_path:
            line_edit.setText(file_path)
    
    def load_schemas(self):
        """Load source and target schemas"""
        source_path = self.source_file_edit.text()
        target_path = self.target_file_edit.text()
        
        if not source_path or not target_path:
            QMessageBox.warning(self, "Warning", "Please select both source and target schema files.")
            return
        
        try:
            # Load schemas
            self.load_schema_files(source_path, target_path)
            
            # Populate trees with hierarchical structure
            self.populate_schema_trees_hierarchical()
            
            # Auto-map schemas
            self.auto_map_schemas()
            
            self.status_bar.showMessage(f"Schemas loaded: {len(self.source_fields)} source fields, {len(self.target_fields)} target fields")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading schemas: {str(e)}")
    
    def load_schema_files(self, source_path: str, target_path: str):
        """Load source and target schema files"""
        # Determine file types and load schemas
        source_ext = Path(source_path).suffix.lower()
        target_ext = Path(target_path).suffix.lower()
        
        if source_ext == '.xsd':
            self.source_fields = self.schema_processor.extract_fields_from_xsd(source_path)
        elif source_ext == '.json':
            self.source_fields = self.schema_processor.extract_fields_from_json_schema(source_path)
        else:
            raise ValueError(f"Unsupported source file type: {source_ext}")
        
        if target_ext == '.xsd':
            self.target_fields = self.schema_processor.extract_fields_from_xsd(target_path)
        elif target_ext == '.json':
            self.target_fields = self.schema_processor.extract_fields_from_json_schema(target_path)
        else:
            raise ValueError(f"Unsupported target file type: {target_ext}")
    
        # Debug output for extracted fields
        print("\n[DEBUG] Extracted Source Fields:")
        for f in self.source_fields:
            print(f"  path={f.path}, name={f.name}, type={f.type}, parent_path={f.parent_path}, is_complex={f.is_complex}, is_array={f.is_array}")
        print("\n[DEBUG] Extracted Target Fields:")
        for f in self.target_fields:
            print(f"  path={f.path}, name={f.name}, type={f.type}, parent_path={f.parent_path}, is_complex={f.is_complex}, is_array={f.is_array}")
    
    def populate_schema_trees_hierarchical(self):
        """Populate schema trees with hierarchical structure and update field counts"""
        self.source_tree.clear()
        self.target_tree.clear()
        # Build hierarchical structure for source fields
        self._build_hierarchical_tree(self.source_tree, self.source_fields)
        # Build hierarchical structure for target fields
        self._build_hierarchical_tree(self.target_tree, self.target_fields)
        # Update field count labels
        if hasattr(self, 'source_count_label'):
            self.source_count_label.setText(f"Fields: {len(self.source_fields)}")
        if hasattr(self, 'target_count_label'):
            self.target_count_label.setText(f"Fields: {len(self.target_fields)}")
        if hasattr(self, 'mapping_connector_overlay'):
            self.mapping_connector_overlay.update()
    
    def _build_hierarchical_tree(self, tree: QTreeWidget, fields: List[SchemaField]):
        """Build hierarchical tree structure from flat field list (recursive)"""
        # Build a lookup for fields by their parent_path
        field_groups = {}
        for field in fields:
            if field.parent_path not in field_groups:
                field_groups[field.parent_path] = []
            field_groups[field.parent_path].append(field)

        def add_children(parent_item, parent_path):
            for field in field_groups.get(parent_path, []):
                item = self._create_tree_item(field)
                if parent_item is None:
                    tree.addTopLevelItem(item)
                else:
                    parent_item.addChild(item)
                # Recursively add children
                add_children(item, field.path)

        # Start recursion from root (parent_path == "")
        add_children(None, "")
    
    def _create_tree_item(self, field: SchemaField) -> QTreeWidgetItem:
        """Create a tree item for a field"""
        item = QTreeWidgetItem([
            field.name,
            field.type,
            field.cardinality,
            field.description,
            self._format_restrictions(field.constraints)
        ])
        setattr(item, 'field_data', field)
        return item

    def _format_restrictions(self, constraints: dict) -> str:
        if not constraints:
            return ""
        return ", ".join(f"{k}={v}" for k, v in constraints.items())
    
    def handle_field_drop(self, event, target_field: SchemaField):
        """Handle field drop for mapping with target field"""
        try:
            mime_data = event.mimeData()
            print(f"[DEBUG] handle_field_drop: event received, target_field.path={getattr(target_field, 'path', None)}")
            if mime_data.hasFormat("application/x-schema-field"):
                field_data_str = mime_data.data("application/x-schema-field").data().decode()
                print(f"[DEBUG] handle_field_drop: field_data_str={field_data_str}")
                field_data = json.loads(field_data_str)
                # Find the source field
                source_field = next((f for f in self.source_fields if f.path == field_data['path']), None)
                print(f"[DEBUG] handle_field_drop: source_field found={source_field is not None}")
                if not source_field:
                    return
                # Create mapping
                mapping = FieldMapping(
                    source_field=source_field,
                    target_field=target_field,
                    similarity=0.8,  # Default similarity
                    confidence="manual"
                )
                # Check if mapping already exists
                existing_mapping = next((m for m in self.mappings 
                                       if m.source_field.path == source_field.path 
                                       and m.target_field.path == target_field.path), None)
                if existing_mapping:
                    # Update existing mapping
                    existing_mapping.target_field = target_field
                    existing_mapping.confidence = "manual"
                else:
                    # Add new mapping
                    self.mappings.append(mapping)
                print(f"[DEBUG] handle_field_drop: mapping created/updated, total mappings={len(self.mappings)}")
                self.update_mapping_table()
                self.status_bar.showMessage(f"Mapping created: {source_field.name} -> {target_field.name}")
        except Exception as e:
            print(f"Error handling field drop: {e}")
    
    def auto_map_schemas(self):
        """Automatically map schemas based on similarity"""
        if not self.source_fields or not self.target_fields:
            QMessageBox.warning(self, "Warning", "Please load schemas first.")
            return
        
        try:
            # Perform mapping without case conversion
            self.mappings = self.mapping_engine.map_fields(self.source_fields, self.target_fields)
            
            # Update UI
            self.update_mapping_table()
            
            self.status_bar.showMessage(f"Auto-mapping completed: {len(self.mappings)} mappings created")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error during auto-mapping: {str(e)}")
    
    def update_mapping_table(self):
        """Update the mapping table with current mappings"""
        self.mapping_table.setRowCount(len(self.mappings))
        
        for row, mapping in enumerate(self.mappings):
            # Source field
            source_item = QTableWidgetItem(mapping.source_field.name)
            self.mapping_table.setItem(row, 0, source_item)
            
            # Target field
            target_item = QTableWidgetItem(mapping.target_field.name if not mapping.is_unmapped else "")
            self.mapping_table.setItem(row, 1, target_item)
            
            # Transformation
            transform_item = QTableWidgetItem("None")
            if mapping.source_field.path in self.transformations:
                transform_item.setText("Configured")
            self.mapping_table.setItem(row, 2, transform_item)
            
            # Status
            if mapping.is_exact_match:
                status = "Exact Match"
                color = "#28a745"  # Green
            elif mapping.is_good_match:
                status = "Good Match"
                color = "#ffc107"  # Yellow
            elif mapping.is_weak_match:
                status = "Weak Match"
                color = "#dc3545"  # Red
            else:
                status = "Unmapped"
                color = "#6c757d"  # Gray
            
            status_item = QTableWidgetItem(status)
            status_item.setBackground(QColor(color))
            self.mapping_table.setItem(row, 3, status_item)
            
            # Similarity
            similarity_item = QTableWidgetItem(f"{mapping.similarity:.3f}")
            self.mapping_table.setItem(row, 4, similarity_item)
            
            # Notes
            notes_item = QTableWidgetItem(mapping.mapping_notes)
            self.mapping_table.setItem(row, 5, notes_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            if not mapping.is_unmapped:
                transform_btn = QPushButton("Transform")
                transform_btn.setMaximumWidth(80)
                transform_btn.clicked.connect(lambda checked, m=mapping: self.configure_transformation(m))
                actions_layout.addWidget(transform_btn)
            
            self.mapping_table.setCellWidget(row, 6, actions_widget)
        self.mapping_connector_overlay.update()
    
    def configure_transformation(self, mapping: FieldMapping):
        """Configure transformation for a mapping"""
        dialog = TransformationDialog(mapping.source_field, mapping.target_field, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            transformation_rules = dialog.get_transformation_rules()
            self.transformations[mapping.source_field.path] = transformation_rules
            self.update_mapping_table()
    
    def clear_mappings(self):
        """Clear all mappings"""
        self.mappings = []
        self.transformations = {}
        self.update_mapping_table()
        self.status_bar.showMessage("All mappings cleared")
    
    def validate_mapping(self):
        """Validate the current mapping and show results"""
        try:
            if not self.mappings:
                QMessageBox.warning(self, "Warning", "No mappings to validate. Please create mappings first.")
                return
            
            validation = self.mapping_engine.validate_mapping()
            
            # Show validation results
            result_text = f"""
Mapping Validation Results:
==========================

Total Mappings: {validation['total_mappings']}
Exact Matches: {validation['exact_matches']}
Good Matches: {validation['good_matches']}
Weak Matches: {validation['weak_matches']}
Unmapped Fields: {validation['unmapped']}

Coverage:
- Source Coverage: {validation['completeness']['source_coverage']:.1%}
- Target Coverage: {validation['completeness']['target_coverage']:.1%}

Average Similarity: {validation['average_similarity']:.3f}

Issues Found: {len(validation['issues'])}
Warnings: {len(validation['warnings'])}
"""
            
            if validation['issues']:
                result_text += "\nIssues:\n"
                for issue in validation['issues']:
                    result_text += f"- {issue['message']}\n"
            
            if validation['warnings']:
                result_text += "\nWarnings:\n"
                for warning in validation['warnings']:
                    result_text += f"- {warning['message']}\n"
            
            QMessageBox.information(self, "Mapping Validation", result_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error validating mapping: {str(e)}")
    
    def export_to_excel(self):
        """Export mapping to Excel with transformations"""
        if not self.mappings:
            QMessageBox.warning(self, "Warning", "No mappings to export. Please create mappings first.")
            return
        
        try:
            # Get output file path
            output_path, _ = QFileDialog.getSaveFileName(
                self, "Export to Excel", "schema_mapping.xlsx", "Excel Files (*.xlsx)"
            )
            
            if not output_path:
                return
        
            # Create enhanced Excel with transformations
            success = self.create_mapping_excel_with_transformations(output_path)
            
            if success:
                QMessageBox.information(self, "Success", f"Mapping exported successfully to:\n{output_path}")
                self.status_bar.showMessage(f"Mapping exported to: {output_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to export mapping to Excel")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exporting to Excel: {str(e)}")
    
    def create_mapping_excel_with_transformations(self, output_path: str) -> bool:
        """Create Excel file with Request/Response structure and transformations"""
        try:
            # Use the new Request/Response Excel generator
            success = self.excel_generator.create_mapping_excel_request_response(
                self.source_fields, 
                self.target_fields, 
                self.mappings, 
                self.transformations,
                output_path
            )
            
            return success
                
        except Exception as e:
            print(f"Error creating Request/Response Excel: {e}")
            return False
    
    def open_schemas(self):
        """Open schema files"""
        self.load_schemas()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About The Forge",
            "The Forge v2.0.0\n\n"
            "Visual Schema Mapping Tool\n"
            "Create field mappings with drag-and-drop interface\n"
            "Configure transformations and export to Excel\n\n"
            "Built with PySide6 and Python 3.8+"
        ) 

    def open_quick_test_dialog(self):
        dlg = QuickTestDialog(self)
        dlg.exec() 

    def setup_quick_test_sidebar(self):
        """Remove the left sidebar with quick tests. All quick test access is now via the Tools menu."""
        pass

    def on_load_test_clicked(self):
        row = self.quick_test_list.currentRow()
        if row < 0 or row >= len(self.quick_tests):
            return
        test = self.quick_tests[row]
        source_file = test['path'] / 'source.xsd'
        if not source_file.exists():
            source_file = test['path'] / 'source.json'
        target_file = test['path'] / 'target.json'
        if not target_file.exists():
            target_file = test['path'] / 'target.xsd'
        if source_file.exists() and target_file.exists():
            self.load_schema_files_from_quick_test(str(source_file), str(target_file))

    def load_schema_files_from_quick_test(self, source_path, target_path):
        """Load schemas from the given paths and update the UI (for Quick Test integration)"""
        self.load_schema_files(source_path, target_path)
        self.populate_schema_trees_hierarchical()
        self.auto_map_schemas()
        self.status_bar.showMessage(f"Quick Test loaded: {source_path} → {target_path}")

    def on_quick_test_selected(self, row):
        # No auto-load on selection, only highlight
        pass

    def populate_quick_test_list(self):
        # List all tests, including comprehensive
        self.quick_tests = self.quick_test_runner.list_test_cases()
        self.quick_test_list.clear()
        for test in self.quick_tests:
            self.quick_test_list.addItem(test["name"])
        if self.quick_tests:
            self.quick_test_list.setCurrentRow(0)

    def setup_menu(self):
        """Setup the application menu"""
        menubar = self.menuBar()
        # File menu
        file_menu = menubar.addMenu("&File")
        open_action = QAction("&Open Schemas", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_schemas)
        file_menu.addAction(open_action)
        export_action = QAction("&Export to Excel", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_to_excel)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        # View menu for toggling sidebar and theme
        view_menu = menubar.addMenu("&View")
        toggle_sidebar_action = QAction("Quick Test Sidebar", self, checkable=True)
        toggle_sidebar_action.setChecked(True)
        toggle_sidebar_action.triggered.connect(self.toggle_quick_test_sidebar)
        view_menu.addAction(toggle_sidebar_action)
        self.toggle_sidebar_action = toggle_sidebar_action
        # Theme toggle
        toggle_theme_action = QAction("Toggle Dark/Light Mode", self)
        toggle_theme_action.setShortcut("Ctrl+M")
        toggle_theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(toggle_theme_action)
        # Connector toggle
        toggle_connector_action = QAction("Show Mapping Connectors", self, checkable=True)
        toggle_connector_action.setChecked(True)
        toggle_connector_action.triggered.connect(self.toggle_mapping_connectors)
        view_menu.addAction(toggle_connector_action)
        self.toggle_connector_action = toggle_connector_action
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        # --- Quick Test Actions ---
        tools_menu.addSeparator()
        run_all_tests_action = QAction("Run All Quick Tests", self)
        run_all_tests_action.triggered.connect(self.run_all_quick_tests)
        tools_menu.addAction(run_all_tests_action)
        open_quick_test_dialog_action = QAction("Open Quick Test Dialog", self)
        open_quick_test_dialog_action.triggered.connect(self.open_quick_test_dialog)
        tools_menu.addAction(open_quick_test_dialog_action)
        reload_tests_action = QAction("Reload Test Cases", self)
        reload_tests_action.triggered.connect(self.populate_quick_test_list)
        tools_menu.addAction(reload_tests_action)
        export_results_action = QAction("Export Test Results", self)
        export_results_action.setEnabled(False)
        tools_menu.addAction(export_results_action)
        tools_menu.addSeparator()
        # ---
        auto_map_action = QAction("&Auto Map Fields", self)
        auto_map_action.triggered.connect(self.auto_map_schemas)
        tools_menu.addAction(auto_map_action)
        validate_action = QAction("&Validate Mapping", self)
        validate_action.triggered.connect(self.validate_mapping)
        tools_menu.addAction(validate_action)
        tools_menu.addSeparator()
        quick_test_action = QAction("&Quick Test", self)
        quick_test_action.setShortcut("Ctrl+T")
        quick_test_action.triggered.connect(self.open_quick_test_dialog)
        tools_menu.addAction(quick_test_action)
        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def toggle_quick_test_sidebar(self, checked):
        # This action is now handled by the Tools menu
        pass 

    def toggle_theme(self):
        """Toggle between dark and light modes"""
        self.current_mode = 'light' if self.current_mode == 'dark' else 'dark'
        self.apply_styles(self.current_mode)

    def toggle_mapping_connectors(self, checked):
        if hasattr(self, 'mapping_connector_overlay'):
            self.mapping_connector_overlay.setVisible(checked)

    def run_all_quick_tests(self):
        # Placeholder: could call a method in quick_test_runner or open dialog and run all
        self.open_quick_test_dialog()
        # Optionally, implement batch run logic here

    def _resize_overlay_event(self, event):
        self._update_connector_overlay_geometry()
        self.mapping_connector_overlay.raise_()
        event.accept() 

    def _update_connector_overlay_geometry(self):
        # Position and size the overlay to cover the area containing both schema trees and the connector channel
        if hasattr(self, 'source_tree') and hasattr(self, 'target_tree'):
            src_geom = self.source_tree.mapTo(self, self.source_tree.rect().topLeft())
            tgt_geom = self.target_tree.mapTo(self, self.target_tree.rect().topRight())
            y = min(src_geom.y(), tgt_geom.y())
            h = max(self.source_tree.height(), self.target_tree.height())
            x1 = src_geom.x()
            x2 = tgt_geom.x()
            self.mapping_connector_overlay.setGeometry(x1, y, x2 - x1, h) 