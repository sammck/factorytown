from ..internal_types import *
from .game_object import GameObject

class Item(GameObject):
    def __str__(self):
        return f"{self.__class__.__name__}({self.common_str()})"
