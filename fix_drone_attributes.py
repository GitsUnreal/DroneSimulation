import os

def fix_drone_class():
    """Fix Drone class to have all required attributes"""
    
    drone_file = 'drone_system/core/Drone.py'
    
    print(f"🔧 Fixing Drone class in {drone_file}...")
    
    if not os.path.exists(drone_file):
        print("Creating missing Drone class...")
        
        drone_content = '''
"""Main Drone class for the simulation"""
import math
import random

class Drone:
    """Main drone entity for the simulation"""
    
    def __init__(self, drone_id, x=100, y=100):
        # Identity
        self.drone_id = drone_id
        
        # Position and movement
        self.x = x
        self.y = y
        self.velocity = [0, 0]
        self.speed = 2.0
        self.max_speed = 5.0
        
        # State
        self.alive = True
        self.active = True
        self.has_landed = False
        
        # Missiles
        self.missiles_fired = 0
        self.max_missiles = 2
        self.missile_reload_time = 3.0
        self.last_missile_time = 0
        
        # Target tracking
        self.target_found = False
        self.target_position = None
        self.target_distance = float('inf')
        
        # Visual properties
        self.size = 15
        self.color = (0, 255, 0)  # Green
        
        # Path tracking
        self.path_history = []
        self.max_path_length = 100
        
        # AI state
        self.state = "patrol"
        self.last_state_change = 0
        
        # Base information
        self.home_base = (50, 50)
        self.fuel = 100.0
        self.max_fuel = 100.0
        
    def update(self, dt):
        """Update drone state"""
        if not self.alive:
            return
        
        # Update position
        self.x += self.velocity[0] * dt * 60
        self.y += self.velocity[1] * dt * 60
        
        # Update fuel
        if self.velocity[0] != 0 or self.velocity[1] != 0:
            self.fuel -= dt * 10  # Consume fuel when moving
        
        # Check if out of fuel
        if self.fuel <= 0:
            self.fuel = 0
            self.velocity = [0, 0]
        
        # Add to path history
        self.path_history.append((self.x, self.y))
        if len(self.path_history) > self.max_path_length:
            self.path_history.pop(0)
        
        # Update missile reload
        self.last_missile_time += dt
    
    def set_velocity(self, vx, vy):
        """Set drone velocity"""
        # Clamp to max speed
        speed = math.sqrt(vx*vx + vy*vy)
        if speed > self.max_speed:
            vx = vx / speed * self.max_speed
            vy = vy / speed * self.max_speed
        
        self.velocity = [vx, vy]
    
    def move_towards(self, target_x, target_y, speed=None):
        """Move towards a target position"""
        if speed is None:
            speed = self.speed
        
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 1:  # Don't move if very close
            vx = (dx / distance) * speed
            vy = (dy / distance) * speed
            self.set_velocity(vx, vy)
        else:
            self.set_velocity(0, 0)
        
        return distance
    
    def can_fire_missile(self):
        """Check if drone can fire a missile"""
        return (self.alive and 
                self.missiles_fired < self.max_missiles and 
                self.last_missile_time >= self.missile_reload_time)
    
    def fire_missile(self, target_position):
        """Fire a missile at target"""
        if self.can_fire_missile():
            self.missiles_fired += 1
            self.last_missile_time = 0
            return True
        return False
    
    def get_distance_to(self, x, y):
        """Get distance to a point"""
        return math.sqrt((self.x - x)**2 + (self.y - y)**2)
    
    def get_distance_to_base(self):
        """Get distance to home base"""
        return self.get_distance_to(self.home_base[0], self.home_base[1])
    
    def return_to_base(self):
        """Start returning to base"""
        self.state = "returning"
        distance = self.move_towards(self.home_base[0], self.home_base[1])
        
        if distance < 20:  # Close to base
            self.has_landed = True
            self.set_velocity(0, 0)
            return True
        return False
    
    def destroy(self):
        """Destroy the drone"""
        self.alive = False
        self.active = False
        self.velocity = [0, 0]
        print(f"🚁 Drone {self.drone_id} destroyed!")
    
    def refuel(self):
        """Refuel the drone (when at base)"""
        if self.get_distance_to_base() < 30:
            self.fuel = self.max_fuel
            return True
        return False
    
    def get_status(self):
        """Get drone status information"""
        if not self.alive:
            return "DESTROYED"
        elif self.has_landed:
            return "LANDED"
        elif self.fuel <= 20:
            return "LOW_FUEL"
        elif self.missiles_fired >= self.max_missiles:
            return "NO_MISSILES"
        else:
            return "ACTIVE"
    
    def get_missiles_remaining(self):
        """Get number of missiles remaining"""
        return self.max_missiles - self.missiles_fired
    
    def __str__(self):
        """String representation"""
        status = self.get_status()
        return f"Drone {self.drone_id} at ({self.x:.1f}, {self.y:.1f}) - {status}"
'''
        
        try:
            os.makedirs(os.path.dirname(drone_file), exist_ok=True)
            with open(drone_file, 'w', encoding='utf-8') as f:
                f.write(drone_content.strip())
            print("✅ Created complete Drone class")
        except Exception as e:
            print(f"❌ Error creating Drone class: {e}")
    
    else:
        # Fix existing Drone class
        try:
            with open(drone_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if drone_id attribute is missing
            if 'self.drone_id' not in content:
                # Add drone_id to __init__ method
                if 'def __init__(self' in content:
                    content = content.replace(
                        'def __init__(self,',
                        'def __init__(self, drone_id=1,'
                    )
                    
                    # Add drone_id assignment
                    if 'def __init__(self, drone_id' in content:
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'def __init__(self, drone_id' in line:
                                # Insert drone_id assignment after the line
                                lines.insert(i+1, '        self.drone_id = drone_id')
                                break
                        content = '\n'.join(lines)
                
                print("✅ Added drone_id attribute to existing Drone class")
            
            # Add other missing attributes if needed
            missing_attrs = []
            required_attrs = {
                'missiles_fired': '0',
                'max_missiles': '2', 
                'alive': 'True',
                'has_landed': 'False',
                'target_found': 'False'
            }
            
            for attr, default_val in required_attrs.items():
                if f'self.{attr}' not in content:
                    missing_attrs.append(f'        self.{attr} = {default_val}')
            
            if missing_attrs:
                # Add missing attributes after __init__
                init_end = content.find('def __init__(')
                if init_end != -1:
                    # Find the end of __init__ method
                    next_method = content.find('\n    def ', init_end + 1)
                    if next_method == -1:
                        next_method = len(content)
                    
                    # Insert missing attributes
                    insert_pos = content.rfind('\n', init_end, next_method)
                    if insert_pos != -1:
                        content = (content[:insert_pos] + '\n' + 
                                 '\n'.join(missing_attrs) + 
                                 content[insert_pos:])
                
                print(f"✅ Added {len(missing_attrs)} missing attributes")
            
            # Write the updated content
            with open(drone_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Fixed existing Drone class")
            
        except Exception as e:
            print(f"❌ Error fixing existing Drone class: {e}")

def fix_ui_component_manager():
    """Fix UIComponentManager.create_missile_status_labels to handle missing attributes"""
    
    ui_manager_file = 'gui/UIComponentManager.py'
    
    print(f"🔧 Fixing UIComponentManager.create_missile_status_labels...")
    
    try:
        with open(ui_manager_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and fix the create_missile_status_labels method
        if 'def create_missile_status_labels(' in content:
            # Replace the problematic line with a safer version
            old_line = 'label = QLabel(f"Drone {drone.drone_id}: 0/2 missiles fired, 0 active - Alive")'
            new_line = '''label = QLabel(f"Drone {getattr(drone, 'drone_id', '?')}: {getattr(drone, 'missiles_fired', 0)}/{getattr(drone, 'max_missiles', 2)} missiles")'''
            
            if old_line in content:
                content = content.replace(old_line, new_line)
                print("✅ Fixed create_missile_status_labels method")
            
            # Also make the entire method more robust
            better_method = '''
    @staticmethod
    def create_missile_status_labels(drones, layout):
        """Create missile status labels for drones with error handling"""
        labels = []
        
        try:
            for i, drone in enumerate(drones):
                drone_id = getattr(drone, 'drone_id', i+1)
                missiles_fired = getattr(drone, 'missiles_fired', 0)
                max_missiles = getattr(drone, 'max_missiles', 2)
                alive = getattr(drone, 'alive', True)
                
                status = "Alive" if alive else "Destroyed"
                label_text = f"Drone {drone_id}: {missiles_fired}/{max_missiles} missiles - {status}"
                
                label = QLabel(label_text)
                label.setStyleSheet("font-size: 12px; color: green; background-color: rgba(255,255,255,150); padding: 2px; border-radius: 3px;")
                layout.addWidget(label)
                labels.append(label)
        
        except Exception as e:
            print(f"Error creating missile status labels: {e}")
            # Create a fallback label
            fallback_label = QLabel("Drone status unavailable")
            layout.addWidget(fallback_label)
            labels.append(fallback_label)
        
        return labels'''
            
            # Replace the entire method if it exists
            if 'def create_missile_status_labels(' in content:
                lines = content.split('\n')
                start_line = -1
                end_line = -1
                
                for i, line in enumerate(lines):
                    if 'def create_missile_status_labels(' in line:
                        start_line = i
                    elif start_line != -1 and line.strip().startswith('def ') and i > start_line:
                        end_line = i
                        break
                    elif start_line != -1 and line.strip() == '' and i > start_line + 5:
                        # Look for the next method or end of class
                        for j in range(i, len(lines)):
                            if lines[j].strip().startswith('def ') or lines[j].strip().startswith('class '):
                                end_line = j
                                break
                        if end_line != -1:
                            break
                
                if start_line != -1:
                    if end_line == -1:
                        end_line = len(lines)
                    
                    # Replace the method
                    lines[start_line:end_line] = better_method.split('\n')
                    content = '\n'.join(lines)
                    print("✅ Replaced create_missile_status_labels with robust version")
            
            # Write the updated content
            with open(ui_manager_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Fixed UIComponentManager")
            
    except Exception as e:
        print(f"❌ Error fixing UIComponentManager: {e}")

def fix_simulation_manager_drones():
    """Ensure SimulationManager creates drones with proper drone_id"""
    
    sim_manager_file = 'core/simulation/SimulationManager.py'
    
    print(f"🔧 Fixing drone creation in SimulationManager...")
    
    if os.path.exists(sim_manager_file):
        try:
            with open(sim_manager_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for drone creation code and ensure drone_id is passed
            if 'Drone(' in content and 'drone_id=' not in content:
                # Fix drone creation calls
                content = content.replace(
                    'Drone(',
                    'Drone(drone_id=i+1,'
                )
                print("✅ Fixed drone creation to include drone_id")
            
            # Ensure proper import
            if 'from drone_system.core.Drone import Drone' not in content:
                # Add import at the top
                lines = content.split('\n')
                import_added = False
                for i, line in enumerate(lines):
                    if line.startswith('from ') or line.startswith('import '):
                        continue
                    else:
                        lines.insert(i, 'from drone_system.core.Drone import Drone')
                        import_added = True
                        break
                
                if import_added:
                    content = '\n'.join(lines)
                    print("✅ Added Drone import to SimulationManager")
            
            # Write the updated content
            with open(sim_manager_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Fixed SimulationManager drone creation")
            
        except Exception as e:
            print(f"❌ Error fixing SimulationManager: {e}")

def main():
    """Main function to fix drone attribute issues"""
    
    print("🔧 Fixing Drone Attribute Issues")
    print("=" * 35)
    
    # Step 1: Fix Drone class
    print("\n1️⃣  Fixing Drone class...")
    fix_drone_class()
    
    # Step 2: Fix UIComponentManager
    print("\n2️⃣  Fixing UIComponentManager...")
    fix_ui_component_manager()
    
    # Step 3: Fix SimulationManager drone creation
    print("\n3️⃣  Fixing SimulationManager...")
    fix_simulation_manager_drones()
    
    print("\n🎉 DRONE ATTRIBUTE FIXES COMPLETE!")
    print("=" * 35)
    print("✅ Drone class: Added drone_id and all required attributes")
    print("✅ UIComponentManager: Made create_missile_status_labels robust")
    print("✅ SimulationManager: Fixed drone creation with proper drone_id")
    
    print("\n🚁 Try running: py main.py")

if __name__ == "__main__":
    main()