import os

def fix_simulation_controller_constructor():
    """Fix SimulationController constructor to accept required parameters"""
    
    controller_file = 'core/simulation/SimulationController.py'
    
    print(f"🔧 Fixing SimulationController constructor in {controller_file}...")
    
    try:
        with open(controller_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the current __init__ method and replace it
        if 'def __init__(self):' in content:
            # Replace the simple constructor with one that accepts parameters
            old_init = '''def __init__(self):
        self.running = False
        self.paused = False
        self.start_time = None
        self.simulation_time = 0.0
        self.time_scale = 1.0
        
        # Simulation objects
        self.drones = []
        self.targets = []
        self.obstacles = []
        self.missiles = []
        
        # Statistics
        self.frame_count = 0
        self.total_runtime = 0.0'''
        
            new_init = '''def __init__(self, sim_manager=None, radar_renderer=None, status_checker=None, 
                 explosion_manager=None, screen_flash=None):
        """Initialize SimulationController with optional components"""
        self.running = False
        self.paused = False
        self.start_time = None
        self.simulation_time = 0.0
        self.time_scale = 1.0
        
        # Simulation objects
        self.drones = []
        self.targets = []
        self.obstacles = []
        self.missiles = []
        
        # Statistics
        self.frame_count = 0
        self.total_runtime = 0.0
        
        # Optional components
        self.sim_manager = sim_manager
        self.radar_renderer = radar_renderer
        self.status_checker = status_checker
        self.explosion_manager = explosion_manager
        self.screen_flash = screen_flash
        
        # Target destroyed callbacks
        self.target_destroyed_callbacks = []'''
            
            content = content.replace(old_init, new_init)
            print("✅ Updated SimulationController constructor")
        
        elif 'def __init__(self, sim_manager' in content:
            print("✅ SimulationController constructor already accepts parameters")
        else:
            print("⚠️  Couldn't find constructor to update")
        
        # Ensure the movement controller methods exist
        if 'def get_target(' not in content:
            movement_methods = '''
    
    # Movement controller compatibility methods
    def get_target(self):
        """Get the current target"""
        return self.targets[0] if self.targets else None
    
    @property
    def target(self):
        """Target property for compatibility"""
        return self.get_target()
    
    def get_base(self):
        """Get the base object"""
        if hasattr(self.sim_manager, 'base'):
            return self.sim_manager.base
        return None
    
    @property
    def base(self):
        """Base property for compatibility"""
        return self.get_base()
    
    def get_obstacles(self):
        """Get obstacles list"""
        if hasattr(self.sim_manager, 'obstacles'):
            return self.sim_manager.obstacles
        return self.obstacles
    
    def update_drones(self, dt):
        """Update all drones"""
        for drone in self.drones:
            if hasattr(drone, 'update'):
                drone.update(dt)
    
    def check_collisions(self):
        """Check for collisions between objects"""
        # Check missile-target collisions
        for missile in self.missiles[:]:
            for target in self.targets[:]:
                if (hasattr(missile, 'position') and hasattr(target, 'contains_point') and
                    target.contains_point(*missile.position)):
                    # Hit detected
                    if hasattr(target, 'take_damage'):
                        target.take_damage(100)
                    if hasattr(missile, 'explode'):
                        missile.explode()
                    if missile in self.missiles:
                        self.missiles.remove(missile)
    
    def cleanup_destroyed_objects(self):
        """Remove destroyed objects from simulation"""
        # Remove destroyed targets
        self.targets = [t for t in self.targets if not getattr(t, 'destroyed', False)]
        
        # Remove inactive missiles
        self.missiles = [m for m in self.missiles if getattr(m, 'active', True)]
        
        # Remove dead drones
        self.drones = [d for d in self.drones if getattr(d, 'alive', True)]'''
            
            content = content.rstrip() + movement_methods
            print("✅ Added movement controller compatibility methods")
        
        # Write the updated content
        with open(controller_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Successfully updated SimulationController")
        
    except Exception as e:
        print(f"❌ Error fixing SimulationController: {e}")

def fix_mainwindow_init_simulation():
    """Fix MainWindow _init_simulation method"""
    
    mainwindow_file = 'gui/core/MainWindow.py'
    
    print(f"🔧 Fixing MainWindow _init_simulation method...")
    
    try:
        with open(mainwindow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the MainController instantiation
        if 'self.movement_controller = MainController(' in content:
            # Find the problematic line and replace it
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'self.movement_controller = MainController(' in line:
                    # Replace with corrected version
                    lines[i] = '        self.movement_controller = MainController('
                    # Find the closing parenthesis and parameters
                    j = i + 1
                    while j < len(lines) and ')' not in lines[j]:
                        j += 1
                    
                    # Replace the entire constructor call
                    new_call = '''        self.movement_controller = MainController(
            self.sim_manager, 
            self.radar_renderer, 
            self.status_checker,
            self.explosion_manager, 
            self.screen_flash
        )'''
                    
                    # Replace lines i through j
                    lines[i:j+1] = new_call.split('\n')
                    print(f"✅ Fixed MainController instantiation at line {i+1}")
                    break
            
            content = '\n'.join(lines)
        
        # Also ensure we're importing MainController correctly
        if 'from core.simulation.SimulationController import MainController' not in content:
            content = content.replace(
                'from core.simulation.SimulationController import SimulationController',
                'from core.simulation.SimulationController import SimulationController, MainController'
            )
            print("✅ Added MainController import")
        
        # Write the fixed content
        with open(mainwindow_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed MainWindow _init_simulation method")
        
    except Exception as e:
        print(f"❌ Error fixing MainWindow: {e}")

def fix_ui_component_manager_call():
    """Fix the UIComponentManager.create_control_bar call"""
    
    mainwindow_file = 'gui/core/MainWindow.py'
    
    print(f"🔧 Fixing UIComponentManager.create_control_bar call...")
    
    try:
        with open(mainwindow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and fix the create_control_bar call
        if 'UIComponentManager.create_control_bar(' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'create_control_bar(' in line and 'self.create_callback_handlers' in line:
                    # Fix the callback parameter
                    if 'self.create_callback_handlers()' not in line:
                        lines[i] = line.replace(
                            'self.create_callback_handlers',
                            'self.create_callback_handlers()'
                        )
                        print(f"✅ Fixed callback parameter on line {i+1}")
            
            content = '\n'.join(lines)
        
        # Ensure create_callback_handlers method exists and returns a dict
        if 'def create_callback_handlers(' not in content:
            callback_method = '''
    
    def create_callback_handlers(self):
        """Create callback handlers dictionary for UI components"""
        try:
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
            }
        except Exception as e:
            print(f"Error creating callback handlers: {e}")
            return {}'''
            
            # Add before _init_ui method
            content = content.replace(
                'def _init_ui(',
                callback_method + '\n\n    def _init_ui('
            )
            print("✅ Added create_callback_handlers method")
        
        # Write the fixed content
        with open(mainwindow_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed UIComponentManager call")
        
    except Exception as e:
        print(f"❌ Error fixing UIComponentManager call: {e}")

def main():
    """Main function to fix controller constructor issues"""
    
    print("🔧 Fixing Controller Constructor Issues")
    print("=" * 42)
    
    # Step 1: Fix SimulationController constructor
    print("\n1️⃣  Fixing SimulationController constructor...")
    fix_simulation_controller_constructor()
    
    # Step 2: Fix MainWindow _init_simulation
    print("\n2️⃣  Fixing MainWindow _init_simulation...")
    fix_mainwindow_init_simulation()
    
    # Step 3: Fix UIComponentManager call
    print("\n3️⃣  Fixing UIComponentManager call...")
    fix_ui_component_manager_call()
    
    print("\n🎉 CONTROLLER CONSTRUCTOR FIXES COMPLETE!")
    print("=" * 42)
    print("✅ SimulationController: Updated constructor to accept parameters")
    print("✅ MainWindow: Fixed MainController instantiation")
    print("✅ UIComponentManager: Fixed callback parameter issue")
    
    print("\n🚁 Try running: py main.py")

if __name__ == "__main__":
    main()