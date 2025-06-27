class Drone:
    def __init__(self, x, y, vx=2, vy=1):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def update(self, obstacles, width, height):
        # Check obstacles and adjust velocity
        for obs in obstacles:
            if obs.contains(int(self.x + self.vx), int(self.y + self.vy)):
                self.vx = -self.vx
                self.vy = -self.vy
                break
        
        # Update position
        self.x += self.vx
        self.y += self.vy

        # Wrap around window edges
        if self.x > width:
            self.x = 0
        elif self.x < 0:
            self.x = width

        if self.y > height:
            self.y = 0
        elif self.y < 0:
            self.y = height