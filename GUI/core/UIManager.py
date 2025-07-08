# gui/core/UIManager.py
from gui.components.ButtonManager import ButtonManager
from gui.panels.ControlPanel import ControlPanel
from config.UIConfig import UIConfig

class UIManager:
    """Manages all UI components"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.button_manager = ButtonManager()
        self.control_panel = ControlPanel()
        
        self.panels = {}
        self.render_flags = {
            'grid': False,
            'paths': False,
            'debug': False,
            'radar': False
        }
    
    def setup_ui(self):
        """Setup complete UI"""
        self._create_control_bar()
        self._create_panels()
        self._setup_callbacks()
    
    def _create_control_bar(self):
        """Create main control bar"""
        callbacks = self._get_callbacks()
        self.control_bar = self.button_manager.create_control_bar(callbacks)
    
    def _get_callbacks(self):
        """Get UI callback functions"""
        return {
            'toggle_simulation': self.main_window.toggle_simulation,
            'reset_simulation': self.main_window.reset_simulation,
            'toggle_grid': self.toggle_grid,
            'toggle_paths': self.toggle_paths,
            'toggle_debug': self.toggle_debug,
            'toggle_radar': self.toggle_radar,
        }
    
    def toggle_grid(self):
        """Toggle grid display"""
        self.render_flags['grid'] = not self.render_flags['grid']
        self.button_manager.update_button_state('grid', self.render_flags['grid'])
    
    def toggle_paths(self):
        """Toggle path display"""
        self.render_flags['paths'] = not self.render_flags['paths']
        self.button_manager.update_button_state('paths', self.render_flags['paths'])
    
    # Similar methods for other toggles...