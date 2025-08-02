"""
FactoryRegistry.py
Central registry for all factories in the simulation.
"""

from Factory.DroneFactory import DroneFactory

class FactoryRegistry:
    _factories = {}

    @classmethod
    def register_factory(cls, name, factory):
        cls._factories[name] = factory

    @classmethod
    def get_factory(cls, name):
        return cls._factories.get(name)

    @classmethod
    def list_factories(cls):
        return list(cls._factories.keys())

# Register core factories on import
FactoryRegistry.register_factory('drone', DroneFactory)
