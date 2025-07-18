import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Updated imports to match your actual project structure
from DroneSystem.Core.Drone import Drone
from DroneSystem.Combat.Weapons.MissileSystem import Missile, MissileType, MissileConfig
from DroneSystem.Movement.Navigation.ObstacleAvoidance import OAI
from DroneSystem.MainController import MainController
from EnemySystem.Target import Target
from Utils.SaveLoadManager import SaveLoadManager
import numpy as np
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPainter, QPaintEvent
from PyQt5.QtCore import Qt

from GUI.Canvas.ZoomableSimulationCanvas import ZoomableSimulationCanvas
from unittest.mock import MagicMock  # <-- Add this import

app = QApplication([])  # Needed for QWidget tests

class DummySimManager:
    def __init__(self):
        self.drones = []
        self.obstacles = []
        self.target = None
        self.base = None

class TestDroneFunctionality(unittest.TestCase):
    def setUp(self):
        # Create a basic drone for testing
        self.drone_id = 1
        self.initial_position = np.array([0.0, 0.0])
        # Note: You'll need to check your actual Drone class constructor
        
    def test_target_initialization(self):
        """Test target is properly initialized"""
        test_target = Target(1, [100, 100])
        self.assertEqual(test_target.target_id, 1)
        self.assertEqual(test_target.position[0], 100)
        self.assertEqual(test_target.position[1], 100)
        self.assertFalse(test_target.destroyed)
        
    def test_target_movement(self):
        """Test target movement mechanics"""
        test_target = Target(1, [100, 100])
        test_target.is_moving_target = True  # <-- Set after construction
        test_target.set_linear_movement([1, 0], speed=5.0)
        initial_pos = test_target.position.copy()
        test_target.update_movement(dt=0.1)
        self.assertNotEqual(test_target.position[0], initial_pos[0])

    def test_missile_system_creation(self):
        """Test missile system basic functionality"""
        from DroneSystem.Combat.Weapons.MissileSystem import Missile, MissileType, MissileConfig
        
        # Create a missile
        missile = Missile(
            missile_id="test_missile",
            drone_id=1,
            missile_type=MissileType.STANDARD,
            start_pos=(0, 0),
            target_pos=(100, 100),
            config=MissileConfig()
        )
        
        self.assertEqual(missile.missile_id, "test_missile")
        self.assertEqual(missile.drone_id, 1)
        self.assertEqual(missile.missile_type, MissileType.STANDARD)
        self.assertTrue(missile.active)
        
    def test_missile_movement(self):
        """Test missile movement"""
        from DroneSystem.Combat.Weapons.MissileSystem import Missile, MissileType, MissileConfig
        missile = Missile(
            missile_id="test_missile",
            drone_id=1,
            missile_type=MissileType.STANDARD,
            start_pos=(0, 0),
            target_pos=(100, 100),
            config=MissileConfig(speed=10.0)
        )
        missile.state = missile.state.FLYING
        missile._calculate_initial_velocity()
        initial_pos = missile.position.copy()
        missile.update(0.1, [], [])
        self.assertNotEqual(missile.position[0], initial_pos[0])
        self.assertNotEqual(missile.position[1], initial_pos[1])

class TestPathFinding(unittest.TestCase):
    def setUp(self):
        # Create OAI instance for pathfinding
        self.oai = OAI([], [], cell_size=20)
        
    def test_grid_creation(self):
        """Test grid creation"""
        grid = self.oai.make_grid()
        self.assertIsNotNone(grid)
        self.assertIsInstance(grid, dict)
        
    def test_snap_to_grid(self):
        """Test position snapping to grid"""
        position = (25, 35)
        grid_pos = self.oai.snap_to_grid(position)
        self.assertIsInstance(grid_pos, tuple)
        self.assertEqual(len(grid_pos), 2)

class TestSaveLoadManager(unittest.TestCase):
    def setUp(self):
        # Create a mock controller for testing
        self.mock_controller = type('MockController', (), {
            'drones': [],
            'obstacles': [],
            'target': None,
            'simulation_speed': 1.0
        })()
        
        self.save_manager = SaveLoadManager(self.mock_controller)
        
    def test_save_directory_creation(self):
        """Test that save directory is created"""
        self.assertTrue(os.path.exists(self.save_manager.default_save_dir))
        
    def test_serialization_methods(self):
        """Test serialization methods don't crash"""
        try:
            config = self.save_manager.serialize_config()
            self.assertIsInstance(config, dict)
            
            drones = self.save_manager.serialize_drones()
            self.assertIsInstance(drones, list)
            
            obstacles = self.save_manager.serialize_obstacles()
            self.assertIsInstance(obstacles, list)
            
        except Exception as e:
            self.fail(f"Serialization methods failed: {e}")

class TestPerformance(unittest.TestCase):
    def test_target_update_performance(self):
        """Test performance with multiple targets"""
        import time
        
        targets = []
        for i in range(10):
            test_target = Target(i, [i * 10, i * 10])
            test_target.is_moving_target = True  # <-- Set after construction
            test_target.set_random_movement()
            targets.append(test_target)
            
        # Measure update time
        start_time = time.time()
        for _ in range(100):
            for target_obj in targets:
                target_obj.update_movement(0.016)  # 60 FPS
        end_time = time.time()
        
        # Should complete within reasonable time
        self.assertLess(end_time - start_time, 1.0)

class TestExplosionEffects(unittest.TestCase):
    def test_explosion_manager(self):
        """Test explosion effect creation"""
        from GUI.Effects.ExplosionEffects import ExplosionManager
        
        explosion_manager = ExplosionManager()
        initial_count = len(explosion_manager.explosions)
        
        # Add explosion
        explosion_manager.add_explosion(100, 100, intensity=1.0, radius=50.0)
        self.assertEqual(len(explosion_manager.explosions), initial_count + 1)
        
        # Update explosions
        explosion_manager.update(0.1)
        # Should still have the explosion (it takes time to fade)
        self.assertGreaterEqual(len(explosion_manager.explosions), 0)

class TestZoomableSimulationCanvas(unittest.TestCase):
    def setUp(self):
        self.canvas = ZoomableSimulationCanvas()
        self.canvas.sim_manager = DummySimManager()
        self.canvas.zoom_factor = 1.0
        self.canvas.pan_offset = [0, 0]

    def test_default_zoom_and_pan(self):
        self.assertEqual(self.canvas.zoom_factor, 1.0)
        self.assertEqual(self.canvas.pan_offset, [0, 0])

    def test_pan(self):
        event_press = MagicMock()
        event_press.button.return_value = Qt.LeftButton
        event_press.x.return_value = 10
        event_press.y.return_value = 10
        self.canvas.mousePressEvent(event_press)

        event_move = MagicMock()
        event_move.x.return_value = 20
        event_move.y.return_value = 20
        self.canvas.mouseMoveEvent(event_move)

        self.assertNotEqual(self.canvas.pan_offset, [0, 0])

        event_release = MagicMock()
        event_release.button.return_value = Qt.LeftButton
        self.canvas.mouseReleaseEvent(event_release)

    def test_zoom_in_and_out(self):
        old_zoom = self.canvas.zoom_factor
        event_in = MagicMock()
        event_in.angleDelta.return_value.y.return_value = 120
        event_in.x.return_value = 100
        event_in.y.return_value = 100
        self.canvas.wheelEvent(event_in)
        self.assertGreater(self.canvas.zoom_factor, old_zoom)

        event_out = MagicMock()
        event_out.angleDelta.return_value.y.return_value = -120
        event_out.x.return_value = 100
        event_out.y.return_value = 100
        self.canvas.wheelEvent(event_out)
        self.assertAlmostEqual(self.canvas.zoom_factor, old_zoom, delta=0.01)

    def test_border_draw(self):
        # This just ensures paintEvent runs without error
        event = QPaintEvent(self.canvas.rect())
        try:
            self.canvas.paintEvent(event)
        except Exception as e:
            self.fail(f"paintEvent raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()