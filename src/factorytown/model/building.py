from ..internal_types import *
from .entity import Entity

class Building(Entity):
    _registry: Dict[str, Self] = {}   # buildings have their own registry
    
    _building_type: Optional[str] = None

    @property
    def building_type(self) -> str:
        assert self._building_type is not None
        return self._building_type
    
    @building_type.setter
    def building_type(self, value: str):
        assert self._building_type is None or self._building_type == value
        self._building_type = value

    def __str__(self):
        return f"Building(name={self._name}, type={self._building_type})"
