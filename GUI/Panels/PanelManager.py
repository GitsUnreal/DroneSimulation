"""
Centralized panel management system
"""
class PanelManager:
    def __init__(self):
        self.panels = {}
        self.visible_panels = set()
    
    def register_panel(self, name, panel):
        """Register a panel with the manager"""
        self.panels[name] = panel
    
    def show_panel(self, name):
        """Show a specific panel"""
        if name in self.panels:
            self.panels[name].show()
            self.visible_panels.add(name)
    
    def hide_panel(self, name):
        """Hide a specific panel"""
        if name in self.panels:
            self.panels[name].hide()
            self.visible_panels.discard(name)
    
    def toggle_panel(self, name):
        """Toggle a panel's visibility"""
        if name in self.visible_panels:
            self.hide_panel(name)
        else:
            self.show_panel(name)
    
    def update_all_visible_panels(self):
        """Update all currently visible panels"""
        for panel_name in self.visible_panels:
            if panel_name in self.panels:
                panel = self.panels[panel_name]
                if hasattr(panel, 'update'):
                    panel.update()
    
    def hide_all_panels(self):
        """Hide all panels"""
        for name in list(self.visible_panels):
            self.hide_panel(name)
