from ..internal_types import *

class GridDim(NamedTuple):
    """A (width, height) tuple representing the dimensions of a building or structure on the game grid."""
    w: int
    h: int
    
    def __str__(self):
        return f"{self.w}x{self.h}"
    
    @classmethod
    def parse(cls, s: str) -> Self:
        w, h = map(int, s.split("x"))
        return cls(w, h)
