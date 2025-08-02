class Zoom:
    def __init__(self, canvas):
        self.canvas = canvas
        self.canvas.zoom_factor = 1.0
        self.canvas.min_zoom = 0.5
        self.canvas.max_zoom = 3.0

    def zoom_in(self):
        """Zoom in the simulation view"""
        if hasattr(self, 'canvas'):
            new_zoom = self.canvas.zoom_factor * 1.2
            self.canvas.zoom_factor = max(self.canvas.min_zoom, min(self.canvas.max_zoom, new_zoom))
            self.canvas.update()
            self.update_zoom_display(self.canvas.zoom_factor)

    def zoom_out(self):
        """Zoom out the simulation view"""
        if hasattr(self, 'canvas'):
            new_zoom = self.canvas.zoom_factor / 1.2
            self.canvas.zoom_factor = max(self.canvas.min_zoom, min(self.canvas.max_zoom, new_zoom))
            self.canvas.update()
            self.update_zoom_display(self.canvas.zoom_factor)

    def reset_view(self):
        """Reset the view to default zoom and position"""
        if hasattr(self, 'canvas'):
            self.canvas.reset_view()
            self.update_zoom_display(1.0)

    def fit_to_view(self):
        """Fit all simulation elements to view"""
        if hasattr(self, 'canvas'):
            self.canvas.fit_to_view()
            self.update_zoom_display(self.canvas.zoom_factor)

    def update_zoom_display(self, zoom_factor):
        """Update zoom display"""
        zoom_percent = int(zoom_factor * 100)
        if hasattr(self, 'zoom_label'):
            self.zoom_label.setText(f"Zoom: {zoom_percent}%")
