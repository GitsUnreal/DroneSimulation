class Drone:
    def __init__(self, x, y, vx=2, vy=1):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True

    def move_towards_target(self, width, height, target):
        if not self.alive:
            return

        # Move towards the target
        if self.x < target.x():
            self.x += self.vx
        elif self.x > target.x() + target.width():
            self.x -= self.vx
        if self.y < target.y():
            self.y += self.vy
        elif self.y > target.y() + target.height():
            self.y -= self.vy
        
        # Keep within bounds
        self.x = max(0, min(self.x, width - 20))
        self.y = max(0, min(self.y, height - 20))

    def move_to(self, x, y):
        if not self.alive:
            return
        self.x = x
        self.y = y

    def destroy(self):
        self.alive = False

    def is_destroyed(self):
        return not self.alive
    
    def attack(self, target):
        if not self.alive:
            return
        # Logic for attacking the target can be added here
        pass