from ..internal_types import *
from .game_object import GameObject
from .registry import RecordRegistry

class Coins(GameObject):
    _color: str
    
    def __init__(self, registry: RecordRegistry, record_name: str):
        super().__init__(registry, record_name)
        parts = record_name.split(" ", 1)
        assert len(parts) == 2 and parts[1] == "Coins"
        self._color = parts[0]
        self.add_tag("Coins")
        
    @property
    def default_image_name(self) -> str:
        return f"Coin {self._color}"
 