from enum import Enum
class Modes(Enum):
    """
    Enum for different simulation
    modes in the simulation.
    """
    SEARCH_AND_DESTROY = "search_and_destroy"
    RECONNAISSANCE = "reconnaissance"
    PATROL = "patrol"
    SEARCH_AND_RESCUE = "search_and_rescue"
    BOMBING_RUN = "bombing_run"
    ASSISTANCE = "assistance"

class SimModes:
    """
    Class to manage different simulation modes.
    """
    def __init__(self):
        self.current_mode = Modes.NORMAL

    def set_mode(self, mode: Modes):
        """
        Set the current simulation mode.
        """
        if isinstance(mode, Modes):
            self.current_mode = mode
            print(f"Simulation mode set to: {self.current_mode.value}")
        else:
            raise ValueError("Invalid simulation mode")
    
    def get_mode(self) -> Modes:
        """
        Get the current simulation mode.
        """
        return self.current_mode
    