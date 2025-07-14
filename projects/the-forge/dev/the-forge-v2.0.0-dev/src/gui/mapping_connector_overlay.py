from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath
from PySide6.QtCore import Qt, QRect, QTimer

class MappingConnectorOverlay(QWidget):
    def __init__(self, source_tree, target_tree, get_mappings_func, parent=None):
        super().__init__(parent)
        self.source_tree = source_tree
        self.target_tree = target_tree
        self.get_mappings = get_mappings_func  # function returning list of FieldMapping
        self.highlighted_mapping = None  # For future: highlight on hover/select
        self.hovered_mapping = None  # Track which mapping is being hovered
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.setMouseTracking(True)  # Enable mouse tracking for hover detection
        self.raise_()
        # Listen for tree scroll/resize events
        self.source_tree.viewport().installEventFilter(self)
        self.target_tree.viewport().installEventFilter(self)
        self.source_tree.verticalScrollBar().valueChanged.connect(self.update)
        self.target_tree.verticalScrollBar().valueChanged.connect(self.update)
        self.source_tree.expanded.connect(self.update)
        self.source_tree.collapsed.connect(self.update)
        self.target_tree.expanded.connect(self.update)
        self.target_tree.collapsed.connect(self.update)
        # Animation timer for pulsing glow
        self._glow_phase = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer)
        self._timer.start(30)  # ~33 FPS

    def set_highlighted_mapping(self, mapping):
        self.highlighted_mapping = mapping
        self.update()

    def mouseMoveEvent(self, event):
        """Handle mouse movement to detect connector hover"""
        pos = event.pos()
        mappings = self.get_mappings()
        hovered_mapping = None
        
        for mapping in mappings:
            if self._is_point_on_connector(pos, mapping):
                hovered_mapping = mapping
                break
        
        if hovered_mapping != self.hovered_mapping:
            self.hovered_mapping = hovered_mapping
            self._update_field_highlights()
            self.update()

    def leaveEvent(self, event):
        """Handle mouse leave to clear highlights"""
        if self.hovered_mapping is not None:
            self.hovered_mapping = None
            self._update_field_highlights()
            self.update()

    def _is_point_on_connector(self, pos, mapping):
        """Check if a point is near a connector path"""
        src_item = self._find_item_by_path(self.source_tree, mapping.source_field.path)
        tgt_item = self._find_item_by_path(self.target_tree, mapping.target_field.path)
        if not src_item or not tgt_item:
            return False
        
        src_rect = self.source_tree.visualItemRect(src_item)
        tgt_rect = self.target_tree.visualItemRect(tgt_item)
        if not src_rect.isValid() or not tgt_rect.isValid():
            return False
        
        # Calculate connector path
        src_center_global = self.source_tree.viewport().mapToGlobal(src_rect.center())
        tgt_center_global = self.target_tree.viewport().mapToGlobal(tgt_rect.center())
        src_pt = self.mapFromGlobal(src_center_global)
        tgt_pt = self.mapFromGlobal(tgt_center_global)
        src_tree_right_global = self.source_tree.mapToGlobal(self.source_tree.rect().topRight())
        tgt_tree_left_global = self.target_tree.mapToGlobal(self.target_tree.rect().topLeft())
        src_pt.setX(self.mapFromGlobal(src_tree_right_global).x())
        tgt_pt.setX(self.mapFromGlobal(tgt_tree_left_global).x())
        
        # Create path and check distance
        mid_x = (src_pt.x() + tgt_pt.x()) // 2
        ctrl1 = src_pt + (tgt_pt - src_pt) * 0.25
        ctrl2 = tgt_pt + (src_pt - tgt_pt) * 0.25
        ctrl1.setX(mid_x)
        ctrl2.setX(mid_x)
        
        path = QPainterPath(src_pt)
        path.cubicTo(ctrl1, ctrl2, tgt_pt)
        
        # Check if point is within threshold distance of path
        threshold = 15  # pixels
        return self._point_distance_to_path(pos, path) <= threshold

    def _point_distance_to_path(self, point, path):
        """Calculate minimum distance from point to path"""
        # Simple approximation: check distance to path segments
        min_distance = float('inf')
        path_length = path.length()
        
        for i in range(0, int(path_length), 5):  # Sample every 5 pixels
            t = i / path_length
            path_point = path.pointAtPercent(t)
            distance = ((point.x() - path_point.x()) ** 2 + (point.y() - path_point.y()) ** 2) ** 0.5
            min_distance = min(min_distance, distance)
        
        return min_distance

    def _update_field_highlights(self):
        """Update field highlights in both schema trees"""
        # Clear previous highlights
        self._clear_tree_highlights(self.source_tree)
        self._clear_tree_highlights(self.target_tree)
        
        if self.hovered_mapping:
            # Highlight corresponding fields
            self._highlight_field_in_tree(self.source_tree, self.hovered_mapping.source_field.path)
            self._highlight_field_in_tree(self.target_tree, self.hovered_mapping.target_field.path)

    def _clear_tree_highlights(self, tree):
        """Clear all highlights in a tree"""
        def clear_item_highlight(item):
            if hasattr(item, 'setBackground'):
                item.setBackground(0, QColor())  # Clear background
            for i in range(item.childCount()):
                clear_item_highlight(item.child(i))
        
        for i in range(tree.topLevelItemCount()):
            clear_item_highlight(tree.topLevelItem(i))

    def _highlight_field_in_tree(self, tree, field_path):
        """Highlight a specific field in a tree"""
        def highlight_item(item):
            if hasattr(item, 'field_data') and getattr(item.field_data, 'path', None) == field_path:
                # Use forge theme colors for highlight
                highlight_color = QColor("#FF6F1F")  # Molten orange
                item.setBackground(0, highlight_color)
                item.setBackground(1, highlight_color)
                item.setBackground(2, highlight_color)
                item.setBackground(3, highlight_color)
                item.setBackground(4, highlight_color)
                return True
            for i in range(item.childCount()):
                if highlight_item(item.child(i)):
                    return True
            return False
        
        for i in range(tree.topLevelItemCount()):
            highlight_item(tree.topLevelItem(i))

    def eventFilter(self, obj, event):
        self.update()
        return False

    def paintEvent(self, event):
        painter = QPainter(self)
        ember_red = QColor("#C0392B")
        molten_orange = QColor("#FF6F1F")
        steel_gray = QColor("#888C8D")
        # Animate glow alpha (pulsing)
        glow_base = 120
        glow_pulse = int(80 * (0.5 + 0.5 * (1 + __import__('math').sin(self._glow_phase * 2 * 3.14159)) / 2))
        glow_alpha = min(255, glow_base + glow_pulse)
        glow_yellow = QColor(255, 223, 80, glow_alpha)
        mappings = self.get_mappings()
        for mapping in mappings:
            src_item = self._find_item_by_path(self.source_tree, mapping.source_field.path)
            tgt_item = self._find_item_by_path(self.target_tree, mapping.target_field.path)
            if not src_item or not tgt_item:
                continue
            src_rect = self.source_tree.visualItemRect(src_item)
            tgt_rect = self.target_tree.visualItemRect(tgt_item)
            if src_rect.isValid() and tgt_rect.isValid():
                src_center_global = self.source_tree.viewport().mapToGlobal(src_rect.center())
                tgt_center_global = self.target_tree.viewport().mapToGlobal(tgt_rect.center())
                src_pt = self.mapFromGlobal(src_center_global)
                tgt_pt = self.mapFromGlobal(tgt_center_global)
                src_tree_right_global = self.source_tree.mapToGlobal(self.source_tree.rect().topRight())
                tgt_tree_left_global = self.target_tree.mapToGlobal(self.target_tree.rect().topLeft())
                src_pt.setX(self.mapFromGlobal(src_tree_right_global).x())
                tgt_pt.setX(self.mapFromGlobal(tgt_tree_left_global).x())
                mid_x = (src_pt.x() + tgt_pt.x()) // 2
                ctrl1 = src_pt + (tgt_pt - src_pt) * 0.25
                ctrl2 = tgt_pt + (src_pt - tgt_pt) * 0.25
                ctrl1.setX(mid_x)
                ctrl2.setX(mid_x)
                path = QPainterPath(src_pt)
                path.cubicTo(ctrl1, ctrl2, tgt_pt)
                
                # Determine connector style based on state
                is_hovered = mapping == self.hovered_mapping
                is_highlighted = mapping == self.highlighted_mapping
                
                # Enhanced glow for hovered connectors
                if is_hovered:
                    hover_glow = QColor(255, 223, 80, min(255, glow_alpha + 60))  # Brighter glow
                    painter.setPen(QPen(hover_glow, 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
                    painter.drawPath(path)
                    pen = QPen(QColor("#FFD700"), 5)  # Bright gold for hovered
                elif is_highlighted:
                    pen = QPen(molten_orange, 4)
                else:
                    pen = QPen(ember_red, 2)
                
                # Draw animated glow (underneath)
                painter.setPen(QPen(glow_yellow, 10, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
                painter.drawPath(path)
                
                # Draw main line with forge theme
                painter.setPen(pen)
                painter.drawPath(path)
                
                # Optionally, add a steel-gray shadow for depth
                painter.setPen(QPen(steel_gray, 1))
                painter.drawPath(path)
        painter.end()

    def _on_timer(self):
        self._glow_phase = (self._glow_phase + 0.03) % 1.0
        self.update()

    def _find_item_by_path(self, tree, path):
        def recurse(item):
            if hasattr(item, 'field_data') and getattr(item.field_data, 'path', None) == path:
                return item
            for i in range(item.childCount()):
                found = recurse(item.child(i))
                if found:
                    return found
            return None
        for i in range(tree.topLevelItemCount()):
            found = recurse(tree.topLevelItem(i))
            if found:
                return found
        return None 