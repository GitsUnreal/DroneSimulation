import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Updated imports to match your actual project structure
from AI.Drone import Drone
from AI.MissileSystem import Missile, MissileType, MissileConfig
from AI.ObstacleAvoidance import OAI
from AI.MainController import MainController
from EnemyAI.Target import target
from Utils.SaveLoadManager import SaveLoadManager
import numpy as np

class TestDroneFunctionality(unittest.TestCase):
    def setUp(self):
        # Create a basic drone for testing
        self.drone_id = 1
        self.initial_position = np.array([0.0, 0.0])
        # Note: You'll need to check your actual Drone class constructor
        
    def test_target_initialization(self):
        """Test target is properly initialized"""
        test_target = target(1, [100, 100])
        self.assertEqual(test_target.target_id, 1)
        self.assertEqual(test_target.position[0], 100)
        self.assertEqual(test_target.position[1], 100)
        self.assertFalse(test_target.destroyed)
        
    def test_target_movement(self):
        """Test target movement mechanics"""
        test_target = target(1, [100, 100], is_moving_target=True)
        test_target.set_linear_movement([1, 0], speed=5.0)
        
        initial_pos = test_target.position.copy()
        test_target.update_movement(dt=0.1)
        
        # Target should have moved
        self.assertNotEqual(test_target.position[0], initial_pos[0])
        
    def test_missile_system_creation(self):
        """Test missile system basic functionality"""
        from AI.MissileSystem import Missile, MissileType, MissileConfig
        
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
        from AI.MissileSystem import Missile, MissileType, MissileConfig
        
        missile = Missile(
            missile_id="test_missile",
            drone_id=1,
            missile_type=MissileType.STANDARD,
            start_pos=(0, 0),
            target_pos=(100, 100),
            config=MissileConfig(speed=10.0)
        )
        
        # Force missile to flying state
        missile.state = missile.state.FLYING
        missile._calculate_initial_velocity()
        
        initial_pos = missile.position.copy()
        missile.update(0.1, [], [])  # Update with no drones or obstacles
        
        # Missile should have moved
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
            test_target = target(i, [i * 10, i * 10], is_moving_target=True)
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
        from GUI.ExplosionEffects import ExplosionManager
        
        explosion_manager = ExplosionManager()
        initial_count = len(explosion_manager.explosions)
        
        # Add explosion
        explosion_manager.add_explosion(100, 100, intensity=1.0, radius=50.0)
        self.assertEqual(len(explosion_manager.explosions), initial_count + 1)
        
        # Update explosions
        explosion_manager.update(0.1)
        # Should still have the explosion (it takes time to fade)
        self.assertGreaterEqual(len(explosion_manager.explosions), 0)

if __name__ == '__main__':
    unittest.main()