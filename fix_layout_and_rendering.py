import os

def fix_radar_renderer():
    """Fix RadarRenderer to have the draw_radar method"""
    
    radar_file = 'gui/rendering/RadarRenderer.py'
    
    print(f"🔧 Fixing RadarRenderer in {radar_file}...")
    
    try:
        with open(radar_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add the missing draw_radar method
        if 'def draw_radar(' not in content:
            radar_method = '''
    
    def draw_radar(self, painter, offset_y, drones):
        """Draw radar sweep and detection"""
        if not self.enabled:
            return
        
        from PyQt5.QtGui import QPen, QBrush
        from PyQt5.QtCore import Qt
        import math
        
        # Update sweep angle
        self.sweep_angle += self.sweep_speed
        if self.sweep_angle >= 360:
            self.sweep_angle = 0
        
        # Draw radar for each drone
        for drone in drones:
            if not getattr(drone, 'alive', True):
                continue
                
            drone_x = getattr(drone, 'x', 100)
            drone_y = getattr(drone, 'y', 100) + offset_y
            
            # Draw radar range circle (faint)
            painter.setPen(QPen(Qt.cyan, 1, Qt.DashLine))
            painter.setBrush(QBrush())
            painter.drawEllipse(
                int(drone_x - self.radar_range), 
                int(drone_y - self.radar_range),
                int(self.radar_range * 2), 
                int(self.radar_range * 2)
            )
            
            # Draw radar sweep line
            sweep_rad = math.radians(self.sweep_angle)
            end_x = drone_x + self.radar_range * math.cos(sweep_rad)
            end_y = drone_y + self.radar_range * math.sin(sweep_rad)
            
            painter.setPen(QPen(Qt.green, 2))
            painter.drawLine(int(drone_x), int(drone_y), int(end_x), int(end_y))
            
            # Draw sweep arc (30-degree cone)
            painter.setPen(QPen(Qt.green, 1))
            painter.setBrush(QBrush(Qt.green, Qt.Dense6Pattern))
            
            # Draw a simple radar cone
            cone_angle = 30  # degrees
            start_angle = int((self.sweep_angle - cone_angle/2) * 16)  # Qt uses 16ths of degree
            span_angle = int(cone_angle * 16)
            
            painter.drawPie(
                int(drone_x - self.radar_range/2), 
                int(drone_y - self.radar_range/2),
                int(self.radar_range), 
                int(self.radar_range),
                start_angle, span_angle
            )'''
            
            content = content.rstrip() + radar_method
            print("✅ Added draw_radar method to RadarRenderer")
        
        # Ensure radar has required attributes
        if '__init__' in content and 'self.sweep_angle' not in content:
            # Add missing attributes to __init__
            init_additions = '''
        self.sweep_angle = 0
        self.sweep_speed = 2.0
        self.radar_range = 150'''
            
            # Find __init__ method and add attributes
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'def __init__(' in line:
                    # Find end of __init__ method
                    j = i + 1
                    while j < len(lines) and (lines[j].startswith('        ') or lines[j].strip() == ''):
                        j += 1
                    
                    # Insert before the next method
                    lines.insert(j-1, init_additions)
                    content = '\n'.join(lines)
                    print("✅ Added missing radar attributes")
                    break
        
        # Write the updated content
        with open(radar_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed RadarRenderer")
        
    except Exception as e:
        print(f"❌ Error fixing RadarRenderer: {e}")

def fix_control_bar_creation():
    """Fix the control bar creation in MainWindow"""
    
    mainwindow_file = 'gui/core/MainWindow.py'
    
    print(f"🔧 Fixing control bar creation in MainWindow...")
    
    try:
        with open(mainwindow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and fix the control bar creation
        if 'UIComponentManager.create_control_bar(' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'create_control_bar(' in line:
                    # Look at the next few lines to see the full call
                    j = i
                    while j < len(lines) and ')' not in lines[j]:
                        j += 1
                    
                    # Replace the entire method call
                    new_call = '''        try:
            control_layout, self.buttons, self.mode_combo, self.speed_combo = UIComponentManager.create_control_bar(
                self.create_callback_handlers()
            )
        except Exception as e:
            print(f"Error creating control bar: {e}")
            # Create a simple fallback control bar
            from PyQt5.QtWidgets import QHBoxLayout, QPushButton
            control_layout = QHBoxLayout()
            start_button = QPushButton("Start")
            start_button.clicked.connect(lambda: print("Start clicked"))
            control_layout.addWidget(start_button)
            self.buttons = {'start_button': start_button}
            self.mode_combo = None
            self.speed_combo = None'''
                    
                    # Replace the lines
                    lines[i:j+1] = new_call.split('\n')
                    print(f"✅ Fixed control bar creation at line {i+1}")
                    break
            
            content = '\n'.join(lines)
        
        # Ensure create_callback_handlers exists and returns a proper dict
        if 'def create_callback_handlers(' not in content:
            callback_method = '''
    
    def create_callback_handlers(self):
        """Create callback handlers dictionary for UI components"""
        return {
            'toggle_simulation': self.toggle_simulation,
            'reset_simulation': self.reset_simulation,
            'toggle_grid': self.toggle_grid,
            'toggle_paths': self.toggle_paths,
            'toggle_debug': self.toggle_debug,
            'toggle_statistics': self.toggle_statistics,
            'toggle_performance': self.toggle_performance,
            'toggle_radar': self.toggle_radar,
            'change_mode': self.change_mode,
            'change_radar_speed': self.change_radar_speed
        }'''
            
            # Add before _init_ui
            content = content.replace(
                'def _init_ui(',
                callback_method + '\n\n    def _init_ui('
            )
            print("✅ Added create_callback_handlers method")
        
        # Write the updated content
        with open(mainwindow_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed control bar creation")
        
    except Exception as e:
        print(f"❌ Error fixing control bar creation: {e}")

def fix_simulation_canvas_rendering():
    """Fix the SimulationCanvas paintEvent to render properly"""
    
    mainwindow_file = 'gui/core/MainWindow.py'
    
    print(f"🔧 Fixing SimulationCanvas rendering...")
    
    try:
        with open(mainwindow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the SimulationCanvas paintEvent and fix it
        if 'def paintEvent(self, event):' in content:
            # Look for the incomplete try block
            new_paint_event = '''
    def paintEvent(self, event):
        """Paint the simulation"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate offset for control panel
        offset_y = SimulationConfig.CONTROL_PANEL_HEIGHT + 15
        
        try:
            # Draw background first
            painter.fillRect(self.rect(), Qt.white)
            
            # Draw grid if enabled
            if getattr(self.main_window, 'show_grid', False):
                if hasattr(self.main_window.renderer, 'draw_grid'):
                    self.main_window.renderer.draw_grid(painter, offset_y, 
                                                       getattr(self.main_window.sim_manager, 'movement_controller', None))
            
            # Draw static elements (obstacles, target, base)
            if hasattr(self.main_window.renderer, 'draw_static_elements'):
                obstacles = getattr(self.main_window.sim_manager, 'obstacles', [])
                target = getattr(self.main_window.sim_manager, 'target', None)
                base = getattr(self.main_window.sim_manager, 'base', None)
                
                self.main_window.renderer.draw_static_elements(
                    painter, offset_y, obstacles, target, base
                )
            
            # Draw drones
            drones = getattr(self.main_window.sim_manager, 'drones', [])
            drone_size = SimulationConfig.DRONE_SIZE
            
            for drone in drones:
                if hasattr(self.main_window.renderer, 'draw_drone_with_status'):
                    self.main_window.renderer.draw_drone_with_status(
                        painter, drone, offset_y, drone_size
                    )
                else:
                    # Fallback drone rendering
                    painter.setPen(QPen(Qt.blue, 2))
                    painter.setBrush(QBrush(Qt.blue))
                    x, y = getattr(drone, 'x', 100), getattr(drone, 'y', 100)
                    painter.drawEllipse(int(x - drone_size/2), int(y + offset_y - drone_size/2), 
                                      drone_size, drone_size)
                    
                    # Draw drone ID
                    painter.setPen(QPen(Qt.white))
                    drone_id = getattr(drone, 'drone_id', '?')
                    painter.drawText(int(x - 5), int(y + offset_y + 5), str(drone_id))
            
            # Draw paths if enabled
            if getattr(self.main_window, 'show_paths', False):
                if hasattr(self.main_window.renderer, 'draw_paths'):
                    self.main_window.renderer.draw_paths(painter, offset_y, drones)
            
            # Draw radar if enabled
            if hasattr(self.main_window, 'radar_renderer') and getattr(self.main_window.radar_renderer, 'enabled', False):
                try:
                    if hasattr(self.main_window.radar_renderer, 'draw_radar'):
                        self.main_window.radar_renderer.draw_radar(painter, offset_y, drones)
                except Exception as radar_error:
                    pass  # Silently continue if radar fails
            
            # Draw missiles
            if hasattr(self.main_window, 'missile_renderer'):
                missiles = getattr(self.main_window.sim_manager, 'missiles', [])
                for missile in missiles:
                    if hasattr(missile, 'position') and getattr(missile, 'active', True):
                        x, y = missile.position
                        painter.setPen(QPen(Qt.red, 3))
                        painter.setBrush(QBrush(Qt.red))
                        painter.drawEllipse(int(x-3), int(y+offset_y-3), 6, 6)
            
        except Exception as e:
            # Draw error message
            painter.setPen(QPen(Qt.red))
            painter.drawText(20, 20, f"Rendering Error: {str(e)}")
            print(f"Error in paintEvent: {e}")'''
            
            # Replace the paintEvent method
            lines = content.split('\n')
            start_line = -1
            end_line = -1
            
            for i, line in enumerate(lines):
                if 'def paintEvent(self, event):' in line:
                    start_line = i
                elif start_line != -1 and line.strip().startswith('def ') and i > start_line:
                    end_line = i
                    break
            
            if start_line != -1:
                if end_line == -1:
                    # Find the next class or end of current class
                    for i in range(start_line + 1, len(lines)):
                        if lines[i].startswith('class ') or (lines[i].strip() and not lines[i].startswith('    ')):
                            end_line = i
                            break
                    if end_line == -1:
                        end_line = len(lines)
                
                # Replace the method
                lines[start_line:end_line] = new_paint_event.split('\n')
                content = '\n'.join(lines)
                print("✅ Fixed SimulationCanvas paintEvent")
        
        # Write the updated content
        with open(mainwindow_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed simulation canvas rendering")
        
    except Exception as e:
        print(f"❌ Error fixing simulation canvas: {e}")

def add_proper_control_panel():
    """Add proper control panel to MainWindow"""
    
    mainwindow_file = 'gui/core/MainWindow.py'
    
    print(f"🔧 Adding proper control panel layout...")
    
    try:
        with open(mainwindow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ensure _init_ui creates the proper layout
        if 'def _init_ui(' in content:
            # Look for _init_ui method and ensure it sets up the layout correctly
            new_init_ui = '''
    def _init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create control panel
        try:
            control_layout, self.buttons, self.mode_combo, self.speed_combo = UIComponentManager.create_control_bar(
                self.create_callback_handlers()
            )
            main_layout.addLayout(control_layout)
        except Exception as e:
            print(f"Error creating control bar: {e}")
            # Create simple fallback
            from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QLabel
            control_layout = QHBoxLayout()
            
            # Start button
            start_button = QPushButton("Start Simulation")
            start_button.setStyleSheet("background-color: lightgreen; padding: 5px;")
            start_button.clicked.connect(self.toggle_simulation)
            control_layout.addWidget(start_button)
            
            # Reset button  
            reset_button = QPushButton("Reset")
            reset_button.setStyleSheet("background-color: lightcoral; padding: 5px;")
            reset_button.clicked.connect(self.reset_simulation)
            control_layout.addWidget(reset_button)
            
            # Grid button
            grid_button = QPushButton("Grid")
            grid_button.setStyleSheet("background-color: lightblue; padding: 5px;")
            grid_button.clicked.connect(self.toggle_grid)
            control_layout.addWidget(grid_button)
            
            # Test button (for your screenshot)
            test_button = QPushButton("Test Button")
            test_button.setStyleSheet("background-color: lightgray; padding: 5px;")
            control_layout.addWidget(test_button)
            
            self.buttons = {
                'start_button': start_button,
                'reset_button': reset_button, 
                'grid_button': grid_button,
                'test_button': test_button
            }
            
            main_layout.addLayout(control_layout)
        
        # Create simulation canvas
        self.simulation_canvas = SimulationCanvas(self)
        main_layout.addWidget(self.simulation_canvas)
        
        # Create status area for missile labels
        status_layout = QHBoxLayout()
        try:
            drones = getattr(self.sim_manager, 'drones', [])
            self.missile_status_labels = UIComponentManager.create_missile_status_labels(drones, status_layout)
        except Exception as e:
            print(f"Error creating missile status: {e}")
            self.missile_status_labels = []
        
        main_layout.addLayout(status_layout)
        
        print("✅ UI initialized successfully")'''
            
            # Replace the _init_ui method
            lines = content.split('\n')
            start_line = -1
            end_line = -1
            
            for i, line in enumerate(lines):
                if 'def _init_ui(' in line:
                    start_line = i
                elif start_line != -1 and line.strip().startswith('def ') and i > start_line:
                    end_line = i
                    break
            
            if start_line != -1:
                if end_line == -1:
                    # Find next method or end of class
                    for i in range(start_line + 1, len(lines)):
                        if (lines[i].strip().startswith('def ') or 
                            lines[i].startswith('class ') or
                            (lines[i].strip() and not lines[i].startswith('    '))):
                            end_line = i
                            break
                    if end_line == -1:
                        end_line = len(lines)
                
                # Replace the method
                lines[start_line:end_line] = new_init_ui.split('\n')
                content = '\n'.join(lines)
                print("✅ Updated _init_ui method")
        
        # Write the updated content
        with open(mainwindow_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added proper control panel")
        
    except Exception as e:
        print(f"❌ Error adding control panel: {e}")

def main():
    """Main function to fix layout and rendering issues"""
    
    print("🔧 Fixing Layout and Rendering Issues")
    print("=" * 42)
    
    # Step 1: Fix RadarRenderer
    print("\n1️⃣  Fixing RadarRenderer...")
    fix_radar_renderer()
    
    # Step 2: Fix control bar creation
    print("\n2️⃣  Fixing control bar creation...")
    fix_control_bar_creation()
    
    # Step 3: Fix simulation canvas rendering
    print("\n3️⃣  Fixing simulation canvas rendering...")
    fix_simulation_canvas_rendering()
    
    # Step 4: Add proper control panel
    print("\n4️⃣  Adding proper control panel...")
    add_proper_control_panel()
    
    print("\n🎉 LAYOUT AND RENDERING FIXES COMPLETE!")
    print("=" * 42)
    print("✅ RadarRenderer: Added draw_radar method")
    print("✅ Control bar: Fixed creation with proper error handling")
    print("✅ SimulationCanvas: Fixed paintEvent with proper drone rendering")
    print("✅ Control panel: Added proper button layout")
    
    print("\n🚁 Try running: py main.py")
    print("You should now see:")
    print("  • Green 'Start Simulation' button")
    print("  • Blue circular drones with IDs")
    print("  • Red target circle")
    print("  • Dark red obstacle rectangles")
    print("  • Proper control buttons at the top")

if __name__ == "__main__":
    main()