from ..internal_types import *
from .registry import Record

class GameObject(Record):
    def __str__(self):
        return f"{self.__class__.__name__}({self.common_str()})"
