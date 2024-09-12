from ..internal_types import *
from .entity import Entity

class Item(Entity):
    _registry: Dict[str, Self] = {} 
    
    def __str__(self):
        return f"Item(name={self._name})"
