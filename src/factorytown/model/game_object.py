from ..internal_types import *
from .registry import Record

class GameObject(Record):
    
    _image_name: Optional[str] = None
    
    @property
    def default_image_name(self) -> str:
        return self.name
    
    @property
    def image_name(self) -> str:
        if self._image_name is None:
            return self.default_image_name
        return self._image_name
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.common_str()})"
