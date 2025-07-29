import sys
import json
import os
from typing import List, Dict, Optional, Tuple
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QToolBar, QAction, QLabel, QSpinBox, QComboBox, 
                             QGroupBox, QGridLayout, QPushButton, QFileDialog,
                             QMessageBox, QSlider, QCheckBox, QLineEdit,
                             QListWidget, QListWidgetItem, QTextEdit, QSplitter)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRect, QPoint  # Add QPoint here
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QFont

from Config.SimulationConfig import SimulationConfig
from DroneSystem.AI.MissionPlanner import MissionPlanner, MissionObjective, MissionPhase
from DroneSystem.AI.PatternGenerator import PatternGenerator, SearchPattern
from Factory.TargetFactory import TargetFactory
from EnemySystem.Target import Target
from EnemySystem.AntiDrone import AntiDrone
from SimMode.Modes import Modes


class ScenarioItem:
    """Represents an item that can be placed in the scenario"""
    def __init__(self, item_type: str, position: Tuple[int, int], properties: Dict = None):
        self.item_type = item_type  # 'drone', 'target', 'obstacle', 'base', 'waypoint'
        self.position = position
        self.properties = properties or {}
        self.selected = False
        
class ZoomableCanvas(QWidget):
    """Canvas that supports zooming and panning for scenario editing"""
    
    itemSelected = pyqtSignal(object)  # Emitted when an item is selected
    itemMoved = pyqtSignal(object, tuple)  # Emitted when an item is moved
    itemAdded = pyqtSignal(str, tuple)  # Emitted when new item is added
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)
        
        # Zoom and pan settings
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.pan_offset = [0, 0]
        self.last_pan_point = None
        
        # Scenario items
        self.items: List[ScenarioItem] = []
        self.selected_item = None
        self.dragging_item = None
        self.drag_offset = [0, 0]
        
        # Tool settings
        self.current_tool = "select"  # select, drone, target, obstacle, waypoint
        self.grid_size = 20
        self.show_grid = True
        self.snap_to_grid = True
        
        # Drawing settings
        self.colors = {
            'grid': QColor(200, 200, 200),
            'drone': QColor(0, 150, 255),
            'target': QColor(255, 100, 100),
            'obstacle': QColor(100, 100, 100),
            'base': QColor(0, 255, 0),
            'waypoint': QColor(255, 255, 0),
            'selected': QColor(255, 255, 255),
            'background': QColor(50, 50, 50)
        }
        
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        zoom_in = event.angleDelta().y() > 0
        zoom_factor = 1.1 if zoom_in else 1/1.1
        
        new_zoom = self.zoom_factor * zoom_factor
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
        
        if new_zoom != self.zoom_factor:
            # Zoom towards mouse cursor
            mouse_pos = event.pos()
            world_pos_before = self.screen_to_world(mouse_pos.x(), mouse_pos.y())
            
            self.zoom_factor = new_zoom
            
            world_pos_after = self.screen_to_world(mouse_pos.x(), mouse_pos.y())
            
            # Adjust pan to keep mouse position stable
            self.pan_offset[0] += (world_pos_after[0] - world_pos_before[0]) * self.zoom_factor
            self.pan_offset[1] += (world_pos_after[1] - world_pos_before[1]) * self.zoom_factor
            
            self.update()
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MiddleButton:
            # Start panning
            self.last_pan_point = [event.x(), event.y()]
        elif event.button() == Qt.LeftButton:
            world_pos = self.screen_to_world(event.x(), event.y())
            
            if self.current_tool == "select":
                # Try to select an item
                clicked_item = self.get_item_at_position(world_pos)
                if clicked_item:
                    self.select_item(clicked_item)
                    self.dragging_item = clicked_item
                    self.drag_offset = [
                        world_pos[0] - clicked_item.position[0],
                        world_pos[1] - clicked_item.position[1]
                    ]
                else:
                    self.select_item(None)
            else:
                # Add new item
                if self.snap_to_grid:
                    world_pos = self.snap_position_to_grid(world_pos)
                self.itemAdded.emit(self.current_tool, world_pos)
                
    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        if self.last_pan_point and event.buttons() & Qt.MiddleButton:
            # Pan the view
            delta_x = event.x() - self.last_pan_point[0]
            delta_y = event.y() - self.last_pan_point[1]
            
            self.pan_offset[0] += delta_x
            self.pan_offset[1] += delta_y
            
            self.last_pan_point = [event.x(), event.y()]
            self.update()
            
        elif self.dragging_item and event.buttons() & Qt.LeftButton:
            # Drag selected item
            world_pos = self.screen_to_world(event.x(), event.y())
            new_pos = [
                world_pos[0] - self.drag_offset[0],
                world_pos[1] - self.drag_offset[1]
            ]
            
            if self.snap_to_grid:
                new_pos = self.snap_position_to_grid(new_pos)
                
            self.dragging_item.position = tuple(new_pos)
            self.itemMoved.emit(self.dragging_item, self.dragging_item.position)
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.MiddleButton:
            self.last_pan_point = None
        elif event.button() == Qt.LeftButton:
            self.dragging_item = None
            
    def paintEvent(self, event):
        """Paint the canvas"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), self.colors['background'])
        
        # Set up transform for zoom and pan
        painter.translate(self.pan_offset[0], self.pan_offset[1])
        painter.scale(self.zoom_factor, self.zoom_factor)
        
        # Draw grid
        if self.show_grid:
            self.draw_grid(painter)
            
        # Draw scenario items
        for item in self.items:
            self.draw_item(painter, item)
            
    def draw_grid(self, painter):
        """Draw the grid"""
        painter.setPen(QPen(self.colors['grid'], 1))
        
        # Calculate visible area in world coordinates
        visible_rect = self.get_visible_world_rect()
        
        # Draw vertical lines
        start_x = int(visible_rect.left() // self.grid_size) * self.grid_size
        end_x = int(visible_rect.right() // self.grid_size + 1) * self.grid_size
        
        for x in range(start_x, end_x + 1, self.grid_size):
            painter.drawLine(x, visible_rect.top(), x, visible_rect.bottom())
            
        # Draw horizontal lines
        start_y = int(visible_rect.top() // self.grid_size) * self.grid_size
        end_y = int(visible_rect.bottom() // self.grid_size + 1) * self.grid_size
        
        for y in range(start_y, end_y + 1, self.grid_size):
            painter.drawLine(visible_rect.left(), y, visible_rect.right(), y)
    
    def draw_item(self, painter, item: ScenarioItem):
        """Draw a scenario item"""
        x, y = item.position
        size = 15
        
        # Set color and style based on item type
        color = self.colors.get(item.item_type, QColor(255, 255, 255))
        
        if item.selected:
            painter.setPen(QPen(self.colors['selected'], 3))
        else:
            painter.setPen(QPen(color, 2))
            
        painter.setBrush(QBrush(color))
        
        # Draw different shapes for different item types
        if item.item_type == "drone":
            # Draw triangle pointing up
            points = [
                QPoint(x, y - size),
                QPoint(x - size, y + size),
                QPoint(x + size, y + size)
            ]
            painter.drawPolygon(points)
            
        elif item.item_type == "target":
            # Draw circle
            painter.drawEllipse(x - size, y - size, size * 2, size * 2)
            
        elif item.item_type == "obstacle":
            # Draw rectangle
            painter.drawRect(x - size, y - size, size * 2, size * 2)
            
        elif item.item_type == "base":
            # Draw house-like shape
            painter.drawRect(x - size, y - size//2, size * 2, size)
            points = [
                QPoint(x - size, y - size//2),
                QPoint(x, y - size),
                QPoint(x + size, y - size//2)
            ]
            painter.drawPolygon(points)
            
        elif item.item_type == "waypoint":
            # Draw diamond
            points = [
                QPoint(x, y - size),
                QPoint(x + size, y),
                QPoint(x, y + size),
                QPoint(x - size, y)
            ]
            painter.drawPolygon(points)
            
        # Draw item ID or name
        if hasattr(item, 'name') and item.name:
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(x + size + 2, y, item.name)
    
    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_x - self.pan_offset[0]) / self.zoom_factor
        world_y = (screen_y - self.pan_offset[1]) / self.zoom_factor
        return (world_x, world_y)
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = int(world_x * self.zoom_factor + self.pan_offset[0])
        screen_y = int(world_y * self.zoom_factor + self.pan_offset[1])
        return (screen_x, screen_y)
    
    def get_visible_world_rect(self) -> QRect:
        """Get the visible area in world coordinates"""
        top_left = self.screen_to_world(0, 0)
        bottom_right = self.screen_to_world(self.width(), self.height())
        return QRect(int(top_left[0]), int(top_left[1]), 
                    int(bottom_right[0] - top_left[0]), 
                    int(bottom_right[1] - top_left[1]))
    
    def snap_position_to_grid(self, position: Tuple[float, float]) -> Tuple[int, int]:
        """Snap position to grid"""
        x, y = position
        snapped_x = round(x / self.grid_size) * self.grid_size
        snapped_y = round(y / self.grid_size) * self.grid_size
        return (snapped_x, snapped_y)
    
    def get_item_at_position(self, position: Tuple[float, float]) -> Optional[ScenarioItem]:
        """Get item at given position"""
        x, y = position
        for item in self.items:
            ix, iy = item.position
            if abs(x - ix) <= 15 and abs(y - iy) <= 15:
                return item
        return None
    
    def select_item(self, item: Optional[ScenarioItem]):
        """Select an item"""
        if self.selected_item:
            self.selected_item.selected = False
        self.selected_item = item
        if item:
            item.selected = True
        self.itemSelected.emit(item)
        self.update()
    
    def add_item(self, item_type: str, position: Tuple[int, int], properties: Dict = None):
        """Add a new item to the scenario"""
        item = ScenarioItem(item_type, position, properties)
        self.items.append(item)
        self.update()
        return item
    
    def remove_item(self, item: ScenarioItem):
        """Remove an item from the scenario"""
        if item in self.items:
            self.items.remove(item)
            if self.selected_item == item:
                self.selected_item = None
            self.update()
    
    def clear_scenario(self):
        """Clear all items"""
        self.items.clear()
        self.selected_item = None
        self.update()
    
    def set_zoom(self, zoom: float):
        """Set zoom level"""
        self.zoom_factor = max(self.min_zoom, min(self.max_zoom, zoom))
        self.update()
    
    def fit_to_view(self):
        """Fit all items to view"""
        if not self.items:
            return
            
        # Calculate bounding box of all items
        min_x = min(item.position[0] for item in self.items)
        max_x = max(item.position[0] for item in self.items)
        min_y = min(item.position[1] for item in self.items)
        max_y = max(item.position[1] for item in self.items)
        
        # Add padding
        padding = 50
        width = max_x - min_x + 2 * padding
        height = max_y - min_y + 2 * padding
        
        # Calculate zoom to fit
        zoom_x = self.width() / width if width > 0 else 1
        zoom_y = self.height() / height if height > 0 else 1
        zoom = min(zoom_x, zoom_y, self.max_zoom)
        
        # Center the view
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        self.zoom_factor = zoom
        self.pan_offset[0] = self.width() / 2 - center_x * zoom
        self.pan_offset[1] = self.height() / 2 - center_y * zoom
        
        self.update()

class ScenarioEditor(QMainWindow):
    """Main scenario editor window"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DroneSwarp Scenario Editor")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize components
        self.mission_planner = MissionPlanner()
        self.pattern_generator = PatternGenerator()
        self.current_scenario = {
            'metadata': {},
            'mission': {},
            'items': []
        }
        self.scenario_name = None  # Initialize scenario name
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create canvas
        self.canvas = ZoomableCanvas()
        splitter.addWidget(self.canvas)
        
        # Create right panel
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([1000, 400])
        
        # Create toolbar
        self.create_toolbar()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.create_status_bar()
        
    def create_toolbar(self):
        """Create the main toolbar"""
        toolbar = QToolBar("Tools")
        self.addToolBar(toolbar)
        
        # Selection tool
        select_action = QAction("Select", self)
        select_action.setCheckable(True)
        select_action.setChecked(True)
        select_action.triggered.connect(lambda: self.set_tool("select"))
        toolbar.addAction(select_action)
        
        toolbar.addSeparator()
        
        # Item placement tools
        tools = [
            ("Drone", "drone"),
            ("Target", "target"),
            ("Obstacle", "obstacle"),
            ("Base", "base"),
            ("Waypoint", "waypoint")
        ]
        
        self.tool_actions = {"select": select_action}
        
        for name, tool_id in tools:
            action = QAction(name, self)
            action.setCheckable(True)
            action.triggered.connect(lambda checked, t=tool_id: self.set_tool(t))
            toolbar.addAction(action)
            self.tool_actions[tool_id] = action
            
        toolbar.addSeparator()
        
        # View tools
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        fit_view_action = QAction("Fit to View", self)
        fit_view_action.triggered.connect(self.canvas.fit_to_view)
        toolbar.addAction(fit_view_action)
        
        toolbar.addSeparator()
        
        # Grid toggle
        grid_action = QAction("Toggle Grid", self)
        grid_action.setCheckable(True)
        grid_action.setChecked(True)
        grid_action.triggered.connect(self.toggle_grid)
        toolbar.addAction(grid_action)
        
        # Snap to grid toggle
        snap_action = QAction("Snap to Grid", self)
        snap_action.setCheckable(True)
        snap_action.setChecked(True)
        snap_action.triggered.connect(self.toggle_snap)
        toolbar.addAction(snap_action)
        toolbar.addSeparator()
        
        # Export to simulation
        export_action = QAction("Export to Simulation", self)
        export_action.triggered.connect(self.export_to_simulation)
        toolbar.addAction(export_action)
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = file_menu.addAction('New Scenario')
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_scenario)
        
        open_action = file_menu.addAction('Open Scenario')
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_scenario)
        
        save_action = file_menu.addAction('Save Scenario')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_scenario)
        
        save_as_action = file_menu.addAction('Save Scenario As...')
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_scenario_as)
        
        file_menu.addSeparator()
        
        export_action = file_menu.addAction('Export to Simulation')
        export_action.triggered.connect(self.export_to_simulation)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        
        delete_action = edit_menu.addAction('Delete Selected')
        delete_action.setShortcut('Delete')
        delete_action.triggered.connect(self.delete_selected)
        
        clear_action = edit_menu.addAction('Clear All')
        clear_action.triggered.connect(self.clear_scenario)
        
    def create_right_panel(self) -> QWidget:
        """Create the right properties panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Mission settings
        mission_group = self.create_mission_group()
        layout.addWidget(mission_group)
        
        # Item properties
        properties_group = self.create_properties_group()
        layout.addWidget(properties_group)
        
        # Scenario settings
        scenario_group = self.create_scenario_group()
        layout.addWidget(scenario_group)
        
        # Mission preview
        preview_group = self.create_preview_group()
        layout.addWidget(preview_group)
        
        layout.addStretch()
        
        return panel
    
    def create_mission_group(self) -> QGroupBox:
        """Create mission settings group"""
        group = QGroupBox("Mission Settings")
        layout = QGridLayout(group)
        
        # Mission type
        layout.addWidget(QLabel("Mission Type:"), 0, 0)
        self.mission_type_combo = QComboBox()
        self.mission_type_combo.addItems([obj.value for obj in MissionObjective])
        self.mission_type_combo.currentTextChanged.connect(self.update_mission_settings)
        layout.addWidget(self.mission_type_combo, 0, 1)
        
        # Mission name
        layout.addWidget(QLabel("Mission Name:"), 1, 0)
        self.mission_name_edit = QLineEdit("Custom Mission")
        layout.addWidget(self.mission_name_edit, 1, 1)
        
        # Difficulty
        layout.addWidget(QLabel("Difficulty:"), 2, 0)
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Normal", "Hard", "Expert"])
        self.difficulty_combo.setCurrentText("Normal")
        layout.addWidget(self.difficulty_combo, 2, 1)
        
        # Time limit
        layout.addWidget(QLabel("Time Limit (s):"), 3, 0)
        self.time_limit_spin = QSpinBox()
        self.time_limit_spin.setRange(0, 3600)
        self.time_limit_spin.setValue(300)
        self.time_limit_spin.setSpecialValueText("No Limit")
        layout.addWidget(self.time_limit_spin, 3, 1)
        
        return group
    
    def create_properties_group(self) -> QGroupBox:
        """Create item properties group"""
        group = QGroupBox("Item Properties")
        self.properties_layout = QVBoxLayout(group)
        
        self.no_selection_label = QLabel("Select an item to edit properties")
        self.properties_layout.addWidget(self.no_selection_label)
        
        return group
    
    def create_scenario_group(self) -> QGroupBox:
        """Create scenario settings group"""
        group = QGroupBox("Scenario Settings")
        layout = QGridLayout(group)
        
        # Map size
        layout.addWidget(QLabel("Map Width:"), 0, 0)
        self.map_width_spin = QSpinBox()
        self.map_width_spin.setRange(800, 5000)
        self.map_width_spin.setValue(1080)
        layout.addWidget(self.map_width_spin, 0, 1)
        
        layout.addWidget(QLabel("Map Height:"), 1, 0)
        self.map_height_spin = QSpinBox()
        self.map_height_spin.setRange(600, 3000)
        self.map_height_spin.setValue(720)
        layout.addWidget(self.map_height_spin, 1, 1)
        
        # Grid size
        layout.addWidget(QLabel("Grid Size:"), 2, 0)
        self.grid_size_spin = QSpinBox()
        self.grid_size_spin.setRange(10, 100)
        self.grid_size_spin.setValue(20)
        self.grid_size_spin.valueChanged.connect(self.update_grid_size)
        layout.addWidget(self.grid_size_spin, 2, 1)
        
        # Validation button
        validate_btn = QPushButton("Validate Scenario")
        validate_btn.clicked.connect(self.validate_scenario)
        layout.addWidget(validate_btn, 3, 0, 1, 2)
        
        return group
    
    def create_preview_group(self) -> QGroupBox:
        """Create mission preview group"""
        group = QGroupBox("Mission Preview")
        layout = QVBoxLayout(group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(200)
        self.preview_text.setReadOnly(True)
        layout.addWidget(self.preview_text)
        
        update_btn = QPushButton("Update Preview")
        update_btn.clicked.connect(self.update_preview)
        layout.addWidget(update_btn)
        
        return group
    
    def create_status_bar(self):
        """Create status bar"""
        status = self.statusBar()
        
        self.zoom_label = QLabel("Zoom: 100%")
        status.addPermanentWidget(self.zoom_label)
        
        self.position_label = QLabel("Position: (0, 0)")
        status.addPermanentWidget(self.position_label)
        
        self.item_count_label = QLabel("Items: 0")
        status.addPermanentWidget(self.item_count_label)
        
    def setup_connections(self):
        """Setup signal connections"""
        self.canvas.itemSelected.connect(self.on_item_selected)
        self.canvas.itemMoved.connect(self.on_item_moved)
        self.canvas.itemAdded.connect(self.on_item_added)
        
        # Update status bar on mouse move
        self.canvas.setMouseTracking(True)
        
    def set_tool(self, tool: str):
        """Set the current tool"""
        # Uncheck all tool actions
        for action in self.tool_actions.values():
            action.setChecked(False)
            
        # Check the selected tool
        if tool in self.tool_actions:
            self.tool_actions[tool].setChecked(True)
            
        self.canvas.current_tool = tool
        
    def zoom_in(self):
        """Zoom in"""
        new_zoom = self.canvas.zoom_factor * 1.2
        self.canvas.set_zoom(new_zoom)
        self.update_zoom_label()
        
    def zoom_out(self):
        """Zoom out"""
        new_zoom = self.canvas.zoom_factor / 1.2
        self.canvas.set_zoom(new_zoom)
        self.update_zoom_label()
        
    def toggle_grid(self):
        """Toggle grid visibility"""
        self.canvas.show_grid = not self.canvas.show_grid
        self.canvas.update()
        
    def toggle_snap(self):
        """Toggle snap to grid"""
        self.canvas.snap_to_grid = not self.canvas.snap_to_grid
        
    def update_grid_size(self):
        """Update grid size"""
        self.canvas.grid_size = self.grid_size_spin.value()
        self.canvas.update()
        
    def update_zoom_label(self):
        """Update zoom label in status bar"""
        zoom_percent = int(self.canvas.zoom_factor * 100)
        self.zoom_label.setText(f"Zoom: {zoom_percent}%")
        
    def on_item_selected(self, item: Optional[ScenarioItem]):
        """Handle item selection"""
        self.update_properties_panel(item)
        
    def on_item_moved(self, item: ScenarioItem, position: Tuple[int, int]):
        """Handle item movement"""
        # Update any dependent properties
        self.update_preview()
        
    def on_item_added(self, item_type: str, position: Tuple[int, int]):
        """Handle item addition"""
        properties = self.get_default_properties(item_type)
        item = self.canvas.add_item(item_type, position, properties)
        self.update_item_count()
        self.update_preview()
        
    def get_default_properties(self, item_type: str) -> Dict:
        """Get default properties for item type"""
        defaults = {
            'drone': {
                'drone_id': len([i for i in self.canvas.items if i.item_type == 'drone']),
                'max_missiles': 2,
                'speed': 1.0,
                'formation_role': 'assault'
            },
            'target': {
                'target_type': 'standard',
                'health': 100,
                'movement_pattern': 'stationary',
                'hidden': False
            },
            'obstacle': {
                'size': 40,
                'destructible': False
            },
            'base': {
                'capacity': 10,
                'repair_rate': 1.0
            },
            'waypoint': {
                'waypoint_type': 'patrol',
                'wait_time': 0
            }
        }
        return defaults.get(item_type, {})
        
    def update_properties_panel(self, item: Optional[ScenarioItem]):
        """Update the properties panel for selected item"""
        # Clear existing widgets
        for i in reversed(range(self.properties_layout.count())):
            child = self.properties_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
                
        if not item:
            self.properties_layout.addWidget(QLabel("Select an item to edit properties"))
            return
            
        # Create property editors based on item type
        self.create_property_editors(item)
        
    def create_property_editors(self, item: ScenarioItem):
        """Create property editors for the given item"""
        # Item type label
        type_label = QLabel(f"Type: {item.item_type.title()}")
        type_label.setStyleSheet("font-weight: bold;")
        self.properties_layout.addWidget(type_label)
        
        # Position
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("Position:"))
        
        x_spin = QSpinBox()
        x_spin.setRange(-5000, 5000)
        x_spin.setValue(item.position[0])
        x_spin.valueChanged.connect(lambda v: self.update_item_position(item, v, item.position[1]))
        pos_layout.addWidget(x_spin)
        
        y_spin = QSpinBox()
        y_spin.setRange(-5000, 5000)
        y_spin.setValue(item.position[1])
        y_spin.valueChanged.connect(lambda v: self.update_item_position(item, item.position[0], v))
        pos_layout.addWidget(y_spin)
        
        pos_widget = QWidget()
        pos_widget.setLayout(pos_layout)
        self.properties_layout.addWidget(pos_widget)
        
        # Type-specific properties
        if item.item_type == 'drone':
            self.create_drone_properties(item)
        elif item.item_type == 'target':
            self.create_target_properties(item)
        elif item.item_type == 'obstacle':
            self.create_obstacle_properties(item)
        elif item.item_type == 'base':
            self.create_base_properties(item)
        elif item.item_type == 'waypoint':
            self.create_waypoint_properties(item)
            
        # Delete button
        delete_btn = QPushButton("Delete Item")
        delete_btn.clicked.connect(lambda: self.delete_item(item))
        self.properties_layout.addWidget(delete_btn)
        
    def create_drone_properties(self, item: ScenarioItem):
        """Create drone-specific property editors"""
        props = item.properties
        
        # Drone ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Drone ID:"))
        id_spin = QSpinBox()
        id_spin.setValue(props.get('drone_id', 0))
        id_spin.valueChanged.connect(lambda v: self.update_property(item, 'drone_id', v))
        id_layout.addWidget(id_spin)
        
        id_widget = QWidget()
        id_widget.setLayout(id_layout)
        self.properties_layout.addWidget(id_widget)
        
        # Max missiles
        missiles_layout = QHBoxLayout()
        missiles_layout.addWidget(QLabel("Max Missiles:"))
        missiles_spin = QSpinBox()
        missiles_spin.setRange(1, 10)
        missiles_spin.setValue(props.get('max_missiles', 2))
        missiles_spin.valueChanged.connect(lambda v: self.update_property(item, 'max_missiles', v))
        missiles_layout.addWidget(missiles_spin)
        
        missiles_widget = QWidget()
        missiles_widget.setLayout(missiles_layout)
        self.properties_layout.addWidget(missiles_widget)
        
        # Formation role
        role_layout = QHBoxLayout()
        role_layout.addWidget(QLabel("Role:"))
        role_combo = QComboBox()
        role_combo.addItems(['leader', 'assault', 'support', 'scout', 'escort', 'guardian'])
        role_combo.setCurrentText(props.get('formation_role', 'assault'))
        role_combo.currentTextChanged.connect(lambda v: self.update_property(item, 'formation_role', v))
        role_layout.addWidget(role_combo)
        
        role_widget = QWidget()
        role_widget.setLayout(role_layout)
        self.properties_layout.addWidget(role_widget)
        
    def create_target_properties(self, item: ScenarioItem):
        """Create target-specific property editors"""
        props = item.properties
        
        # Target type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Target Type:"))
        type_combo = QComboBox()
        type_combo.addItems(['standard', 'armored', 'fast', 'stealth'])
        type_combo.setCurrentText(props.get('target_type', 'standard'))
        type_combo.currentTextChanged.connect(lambda v: self.update_property(item, 'target_type', v))
        type_layout.addWidget(type_combo)
        
        type_widget = QWidget()
        type_widget.setLayout(type_layout)
        self.properties_layout.addWidget(type_widget)
        
        # Health
        health_layout = QHBoxLayout()
        health_layout.addWidget(QLabel("Health:"))
        health_spin = QSpinBox()
        health_spin.setRange(1, 1000)
        health_spin.setValue(props.get('health', 100))
        health_spin.valueChanged.connect(lambda v: self.update_property(item, 'health', v))
        health_layout.addWidget(health_spin)
        
        health_widget = QWidget()
        health_widget.setLayout(health_layout)
        self.properties_layout.addWidget(health_widget)
        
        # Movement pattern
        movement_layout = QHBoxLayout()
        movement_layout.addWidget(QLabel("Movement:"))
        movement_combo = QComboBox()
        movement_combo.addItems(['stationary', 'patrol', 'random', 'escape'])
        movement_combo.setCurrentText(props.get('movement_pattern', 'stationary'))
        movement_combo.currentTextChanged.connect(lambda v: self.update_property(item, 'movement_pattern', v))
        movement_layout.addWidget(movement_combo)
        
        movement_widget = QWidget()
        movement_widget.setLayout(movement_layout)
        self.properties_layout.addWidget(movement_widget)
        
        # Hidden checkbox
        hidden_check = QCheckBox("Hidden (requires radar)")
        hidden_check.setChecked(props.get('hidden', False))
        hidden_check.toggled.connect(lambda v: self.update_property(item, 'hidden', v))
        self.properties_layout.addWidget(hidden_check)
        
    def create_obstacle_properties(self, item: ScenarioItem):
        """Create obstacle-specific property editors"""
        props = item.properties
        
        # Size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Size:"))
        size_spin = QSpinBox()
        size_spin.setRange(10, 200)
        size_spin.setValue(props.get('size', 40))
        size_spin.valueChanged.connect(lambda v: self.update_property(item, 'size', v))
        size_layout.addWidget(size_spin)
        
        size_widget = QWidget()
        size_widget.setLayout(size_layout)
        self.properties_layout.addWidget(size_widget)
        
        # Destructible checkbox
        destructible_check = QCheckBox("Destructible")
        destructible_check.setChecked(props.get('destructible', False))
        destructible_check.toggled.connect(lambda v: self.update_property(item, 'destructible', v))
        self.properties_layout.addWidget(destructible_check)
        
    def create_base_properties(self, item: ScenarioItem):
        """Create base-specific property editors"""
        props = item.properties
        
        # Capacity
        capacity_layout = QHBoxLayout()
        capacity_layout.addWidget(QLabel("Capacity:"))
        capacity_spin = QSpinBox()
        capacity_spin.setRange(1, 50)
        capacity_spin.setValue(props.get('capacity', 10))
        capacity_spin.valueChanged.connect(lambda v: self.update_property(item, 'capacity', v))
        capacity_layout.addWidget(capacity_spin)
        
        capacity_widget = QWidget()
        capacity_widget.setLayout(capacity_layout)
        self.properties_layout.addWidget(capacity_widget)
        
    def create_waypoint_properties(self, item: ScenarioItem):
        """Create waypoint-specific property editors"""
        props = item.properties
        
        # Waypoint type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Waypoint Type:"))
        type_combo = QComboBox()
        type_combo.addItems(['patrol', 'formation', 'search', 'rally'])
        type_combo.setCurrentText(props.get('waypoint_type', 'patrol'))
        type_combo.currentTextChanged.connect(lambda v: self.update_property(item, 'waypoint_type', v))
        type_layout.addWidget(type_combo)
        
        type_widget = QWidget()
        type_widget.setLayout(type_layout)
        self.properties_layout.addWidget(type_widget)
        
    def update_item_position(self, item: ScenarioItem, x: int, y: int):
        """Update item position"""
        item.position = (x, y)
        self.canvas.update()
        
    def update_property(self, item: ScenarioItem, property_name: str, value):
        """Update item property"""
        item.properties[property_name] = value
        self.update_preview()
        
    def delete_item(self, item: ScenarioItem):
        """Delete the given item"""
        self.canvas.remove_item(item)
        self.update_properties_panel(None)
        self.update_item_count()
        
    def delete_selected(self):
        """Delete selected item"""
        if self.canvas.selected_item:
            self.delete_item(self.canvas.selected_item)
            
    def update_item_count(self):
        """Update item count in status bar"""
        count = len(self.canvas.items)
        self.item_count_label.setText(f"Items: {count}")
        
    def update_mission_settings(self):
        """Update mission settings"""
        self.update_preview()
        
    def update_preview(self):
        """Update mission preview"""
        # Count items by type
        item_counts = {}
        for item in self.canvas.items:
            item_counts[item.item_type] = item_counts.get(item.item_type, 0) + 1
            
        # Generate preview text
        preview = f"Mission: {self.mission_name_edit.text()}\n"
        preview += f"Type: {self.mission_type_combo.currentText()}\n"
        preview += f"Difficulty: {self.difficulty_combo.currentText()}\n"
        
        if self.time_limit_spin.value() > 0:
            preview += f"Time Limit: {self.time_limit_spin.value()}s\n"
        else:
            preview += "Time Limit: None\n"
            
        preview += "\nScenario Elements:\n"
        for item_type, count in item_counts.items():
            preview += f"  {item_type.title()}s: {count}\n"
            
        # Add mission phases
        preview += f"\nMission Phases:\n"
        mission_obj = getattr(MissionObjective, self.mission_type_combo.currentText().upper(), 
                             MissionObjective.SEARCH_AND_DESTROY)
        
        # Create temporary mission plan
        temp_planner = MissionPlanner()
        temp_planner.mission_objective = mission_obj
        phases = temp_planner._create_phase_plan()
        
        for phase, details in phases.items():
            preview += f"  {phase.value.title()}: {details['description']}\n"
            
        self.preview_text.setText(preview)
        
    def validate_scenario(self):
        """Validate the current scenario"""
        errors = []
        warnings = []
        
        # Check for required elements
        drone_count = len([i for i in self.canvas.items if i.item_type == 'drone'])
        target_count = len([i for i in self.canvas.items if i.item_type == 'target'])
        base_count = len([i for i in self.canvas.items if i.item_type == 'base'])
        
        if drone_count == 0:
            errors.append("At least one drone is required")
        if target_count == 0 and self.mission_type_combo.currentText() in ['search_and_destroy', 'reconnaissance']:
            errors.append("Target required for this mission type")
        if base_count == 0:
            warnings.append("No base defined - drones may not be able to land")
            
        # Check drone IDs are unique
        drone_ids = [item.properties.get('drone_id', 0) for item in self.canvas.items if item.item_type == 'drone']
        if len(drone_ids) != len(set(drone_ids)):
            errors.append("Drone IDs must be unique")
            
        # Show results
        if errors:
            QMessageBox.critical(self, "Validation Errors", 
                               "Scenario has errors:\n" + "\n".join(f"• {e}" for e in errors))
        elif warnings:
            QMessageBox.warning(self, "Validation Warnings",
                              "Scenario has warnings:\n" + "\n".join(f"• {w}" for w in warnings))
        else:
            QMessageBox.information(self, "Validation Success", "Scenario is valid!")
            
    def new_scenario(self):
        """Create a new scenario"""
        self.canvas.clear_scenario()
        self.mission_name_edit.setText("New Mission")
        self.mission_type_combo.setCurrentIndex(0)
        self.difficulty_combo.setCurrentText("Normal")
        self.time_limit_spin.setValue(300)
        self.update_item_count()
        self.update_preview()
        
    def open_scenario(self):
        """Open a scenario file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Scenario", 
            "saves/",  # Start in saves directory
            "Scenario Files (*.scenario *.sim *.json);;All Files (*)"  # Support all formats
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
            
                # Check if it's a simulation file (.sim) or scenario file (.scenario)
                if 'metadata' in data and 'drones' in data and 'config' in data:
                    # It's a .sim file - convert to scenario format
                    self.load_simulation_as_scenario(data)
                else:
                    # It's a .scenario file
                    self.load_scenario_data(data)
                
                QMessageBox.information(self, "Success", f"Scenario loaded from {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load scenario: {str(e)}")

    def load_simulation_as_scenario(self, sim_data):
        """Convert .sim file to scenario format and load it"""
        # Clear current scenario
        self.canvas.clear_scenario()
        
        # Load metadata from sim file
        metadata = sim_data.get('metadata', {})
        config = sim_data.get('config', {})
        
        self.mission_name_edit.setText(metadata.get('mission_name', 'Loaded Mission'))
        
        # Map mission type
        mission_type = metadata.get('mission_type', 'search_and_destroy')
        index = self.mission_type_combo.findText(mission_type)
        if index >= 0:
            self.mission_type_combo.setCurrentIndex(index)
    
        self.difficulty_combo.setCurrentText('Normal')  # Default
        self.time_limit_spin.setValue(300)  # Default
        self.map_width_spin.setValue(config.get('map_width', 1080))
        self.map_height_spin.setValue(config.get('map_height', 720))
        self.grid_size_spin.setValue(config.get('grid_size', 20))
        
        # Load drones
        for drone_data in sim_data.get('drones', []):
            item = ScenarioItem(
                item_type="drone",
                position=tuple(drone_data['position']),
                properties={
                    'drone_id': drone_data.get('drone_id', 0),
                    'max_missiles': drone_data.get('max_missiles', 2),
                    'formation_role': drone_data.get('formation_role', 'assault')
                }
            )
            self.canvas.items.append(item)
    
        # Load targets
        for target_data in sim_data.get('targets', []):
            item = ScenarioItem(
                item_type="target",
                position=tuple(target_data['position']),
                properties={
                    'target_type': target_data.get('target_type', 'standard'),
                    'health': target_data.get('health', 100),
                    'hidden': target_data.get('hidden', False)
                }
            )
            self.canvas.items.append(item)
    
        # Load obstacles
        for obstacle_data in sim_data.get('obstacles', []):
            item = ScenarioItem(
                item_type="obstacle",
                position=tuple(obstacle_data['position']),
                properties={
                    'size': obstacle_data.get('size', 40),
                    'destructible': obstacle_data.get('destructible', False)
                }
            )
            self.canvas.items.append(item)
    
        # Load bases
        for base_data in sim_data.get('bases', []):
            item = ScenarioItem(
                item_type="base",
                position=tuple(base_data['position']),
                properties={
                    'capacity': base_data.get('capacity', 10)
                }
            )
            self.canvas.items.append(item)
    
        # Update UI
        self.canvas.update()
        self.update_item_count()
        self.update_preview()
        
    def save_scenario(self):
        """Save current scenario to file"""
        if not self.scenario_name:
            self.scenario_name = "Untitled Scenario"
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Scenario", 
            f"scenarios/{self.scenario_name}.scenario",  # Use .scenario extension
            "Scenario Files (*.scenario);;JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            # Ensure proper extension
            if not filename.endswith(('.scenario', '.json')):
                filename += '.scenario'
                
            try:
                scenario_data = self.export_scenario_data()
                with open(filename, 'w') as f:
                    json.dump(scenario_data, f, indent=2)
                QMessageBox.information(self, "Success", f"Scenario saved: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save scenario: {str(e)}")

    def export_scenario_data(self):
        """Export current scenario as data structure"""
        scenario_data = {
            'metadata': {
                'name': self.scenario_name,
                'mission_type': self.mission_type,
                'difficulty': getattr(self, 'difficulty', 'Normal'),
                'time_limit': getattr(self, 'time_limit', 300),
                'map_width': self.width(),
                'map_height': self.height(),
                'grid_size': getattr(self, 'grid_size', 20),
                'created_at': self.get_current_timestamp()
            },
            'items': []
        }
        
        # Export all items
        for item in self.items:
            item_data = {
                'type': item.item_type,
                'position': list(item.position),
                'properties': item.properties.copy() if hasattr(item, 'properties') else {}
            }
            scenario_data['items'].append(item_data)
        
        return scenario_data
    
    def save_scenario_as(self):
        """Save scenario with new filename"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Scenario", "", "Scenario Files (*.scenario);;All Files (*)")
        
        if filename:
            if not filename.endswith('.scenario'):
                filename += '.scenario'
            self.save_scenario_to_file(filename)
            self.current_filename = filename
            
    def save_scenario_to_file(self, filename: str):
        """Save scenario to specific file"""
        try:
            scenario_data = self.get_scenario_data()
            with open(filename, 'w') as f:
                json.dump(scenario_data, f, indent=2)
            QMessageBox.information(self, "Success", f"Scenario saved: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save scenario: {str(e)}")
            
    def get_scenario_data(self) -> Dict:
        """Get current scenario as data dictionary"""
        return {
            'metadata': {
                'name': self.mission_name_edit.text(),
                'mission_type': self.mission_type_combo.currentText(),
                'difficulty': self.difficulty_combo.currentText(),
                'time_limit': self.time_limit_spin.value(),
                'map_width': self.map_width_spin.value(),
                'map_height': self.map_height_spin.value(),
                'grid_size': self.grid_size_spin.value()
            },
            'items': [
                {
                    'type': item.item_type,
                    'position': item.position,
                    'properties': item.properties
                }
                for item in self.canvas.items
            ]
        }
        
    def load_scenario_data(self, data: Dict):
        """Load scenario from data dictionary"""
        # Clear current scenario
        self.canvas.clear_scenario()
        
        # Load metadata
        metadata = data.get('metadata', {})
        self.mission_name_edit.setText(metadata.get('name', 'Loaded Mission'))
        
        mission_type = metadata.get('mission_type', 'search_and_destroy')
        index = self.mission_type_combo.findText(mission_type)
        if index >= 0:
            self.mission_type_combo.setCurrentIndex(index)
            
        self.difficulty_combo.setCurrentText(metadata.get('difficulty', 'Normal'))
        self.time_limit_spin.setValue(metadata.get('time_limit', 300))
        self.map_width_spin.setValue(metadata.get('map_width', 1080))
        self.map_height_spin.setValue(metadata.get('map_height', 720))
        self.grid_size_spin.setValue(metadata.get('grid_size', 20))
        
        # Load items
        for item_data in data.get('items', []):
            item = ScenarioItem(
                item_data['type'],
                tuple(item_data['position']),
                item_data['properties']
            )
            self.canvas.items.append(item)
            
        self.canvas.update()
        self.update_item_count()
        self.update_preview()
        
    def export_to_simulation(self):
        """Export scenario to simulation format"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export to Simulation", "", "Simulation Files (*.sim);;All Files (*)")
        
        if filename:
            try:
                if not filename.endswith('.sim'):
                    filename += '.sim'
                    
                sim_data = self.convert_to_simulation_format()
                with open(filename, 'w') as f:
                    json.dump(sim_data, f, indent=2)
                    
                QMessageBox.information(self, "Success", 
                                      f"Scenario exported to simulation format: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
                
    def convert_to_simulation_format(self) -> Dict:
        """Convert scenario to simulation format"""
        # This would create a format compatible with your SaveLoadManager
        drones = [item for item in self.canvas.items if item.item_type == 'drone']
        targets = [item for item in self.canvas.items if item.item_type == 'target']
        obstacles = [item for item in self.canvas.items if item.item_type == 'obstacle']
        bases = [item for item in self.canvas.items if item.item_type == 'base']
        
        return {
            'metadata': {
                'version': '1.0',
                'saved_at': '2025-07-16T12:00:00',
                'drone_count': len(drones),
                'scenario_created': True,
                'mission_type': self.mission_type_combo.currentText(),
                'mission_name': self.mission_name_edit.text()
            },
            'config': {
                'grid_size': self.grid_size_spin.value(),
                'mode': self.mission_type_combo.currentText(),
                'simulation_speed': 1.0,
                'map_width': self.map_width_spin.value(),
                'map_height': self.map_height_spin.value()
            },
            'drones': [
                {
                    'drone_id': item.properties.get('drone_id', i),
                    'position': list(item.position),
                    'max_missiles': item.properties.get('max_missiles', 2),
                    'formation_role': item.properties.get('formation_role', 'assault'),
                    'alive': True,
                    'has_attacked': False
                }
                for i, item in enumerate(drones)
            ],
            'targets': [
                {
                    'position': list(item.position),
                    'target_type': item.properties.get('target_type', 'standard'),
                    'health': item.properties.get('health', 100),
                    'movement_pattern': item.properties.get('movement_pattern', 'stationary'),
                    'hidden': item.properties.get('hidden', False)
                }
                for item in targets
            ],
            'obstacles': [
                {
                    'position': list(item.position),
                    'size': item.properties.get('size', 40),
                    'destructible': item.properties.get('destructible', False)
                }
                for item in obstacles
            ],
            'bases': [
                {
                    'position': list(item.position),
                    'capacity': item.properties.get('capacity', 10)
                }
                for item in bases
            ],
            'simulation_state': {
                'running': False,
                'step': 0,
                'mission_complete': False
            }
        }
        
    def clear_scenario(self):
        """Clear the current scenario"""
        reply = QMessageBox.question(self, 'Clear Scenario', 
                                   'Are you sure you want to clear the current scenario?',
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.new_scenario()

def main():
    """Run the scenario editor"""
    app = QApplication(sys.argv)
    editor = ScenarioEditor()
    editor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()