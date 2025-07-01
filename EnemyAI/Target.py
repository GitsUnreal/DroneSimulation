
class target:
    def __init__(self, target_id, position, height=20, width=20):
        self.target_id = target_id
        self.position = position
        self.destroyed = False
        self.height = height
        self.width = width

    def destroy(self):
        self.destroyed = True
        print(f"Target {self.target_id} at {self.position} has been destroyed.")
    
    def is_destroyed(self):
        return self.destroyed

    def __repr__(self):
        return f"Target(id={self.target_id}, position={self.position}, destroyed={self.destroyed})"