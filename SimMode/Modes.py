from enum import Enum
from SimMode.Handlers.NormalModeHandler import NormalModeHandler
from SimMode.Handlers.SearchAndDestroyHandler import SearchAndDestroyModeHandler
from SimMode.Handlers.ReconnaissanceHandler import ReconnaissanceModeHandler
from SimMode.Handlers.PatrolHandler import PatrolModeHandler
from SimMode.Handlers.BombingRunHandler import BombingRunModeHandler
from SimMode.Handlers.SearchAndRescueHandler import SearchAndRescueRunModeHandler


class Modes(Enum):
    """
    Enum for different simulation
    modes in the simulation.
    """
    NORMAL = "normal"
    SEARCH_AND_DESTROY = "search_and_destroy"
    RECONNAISSANCE = "reconnaissance"
    PATROL = "patrol"
    SEARCH_AND_RESCUE = "search_and_rescue"
    BOMBING_RUN = "bombing_run"

class SimModes:
    """
    Class to manage different simulation modes.
    """
    def __init__(self):
        self.current_mode = Modes.NORMAL
        self.mode_handlers = {
            Modes.NORMAL: NormalModeHandler(),
            Modes.SEARCH_AND_DESTROY: SearchAndDestroyModeHandler(),
            Modes.RECONNAISSANCE: ReconnaissanceModeHandler(),
            Modes.PATROL: PatrolModeHandler(),
            Modes.SEARCH_AND_RESCUE: SearchAndRescueRunModeHandler(),
            Modes.BOMBING_RUN: BombingRunModeHandler(),
        }
        self.current_handler = self.mode_handlers[Modes.NORMAL]

    def set_mode(self, mode: Modes):
        """
        Set the current simulation mode.
        """
        if isinstance(mode, Modes) and mode in self.mode_handlers:
            old_handler = self.current_handler
            self.current_mode = mode
            self.current_handler = self.mode_handlers[mode]
            #print(f"Simulation mode set to: {self.current_mode.value}")
            return old_handler, self.current_handler
        else:
            raise ValueError("Invalid simulation mode")
    
    def get_current_handler(self):
        """
        Get the current mode handler.
        """
        return self.current_handler
    
    def apply_mode_to_simulation(self, drones, target):
        """
        Apply current mode settings to simulation objects
        """
        self.current_handler.configure_drones(drones)
        self.current_handler.configure_target(target)
