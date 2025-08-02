"""
BaseFactory.py
Defines a base interface for all factories in the simulation.
"""

from abc import ABC, abstractmethod

class BaseFactory(ABC):
    @abstractmethod
    def create(self, *args, **kwargs):
        pass

    @abstractmethod
    def create_random(self, *args, **kwargs):
        pass

    def create_from_config(self, config):
        """Optional: Create an object from a config dict or object."""
        raise NotImplementedError("This factory does not support config-based creation.")
