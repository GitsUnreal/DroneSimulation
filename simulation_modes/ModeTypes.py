"""Simulation mode types"""
from enum import Enum

class ModeTypes(Enum):
    """Available simulation modes"""
    NORMAL = "normal"
    RECON = "recon"
    SEARCH_DESTROY = "search_destroy"

# Legacy alias
class Modes:
    NORMAL = ModeTypes.NORMAL
    RECON = ModeTypes.RECON
    SEARCH_DESTROY = ModeTypes.SEARCH_DESTROY