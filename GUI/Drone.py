class Drone:
    def __init__(self, x, y, vx=2, vy=1):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True

    def update(self, width, height):
        if not self.alive:
            return

        self.x += self.vx
        self.y += self.vy

        if self.x > width: self.x = 0
        elif self.x < 0: self.x = width
        if self.y > height: self.y = 0
        elif self.y < 0: self.y = height

    def destroy(self):
        self.alive = False