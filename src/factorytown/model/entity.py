from ..internal_types import *

class Entity:
    _name: str
    _registry: Dict[str, Self] = {}
    
    @classmethod
    def get(cls: Self, name: str) -> Self:
        entity = cls._registry.get(name)
        if entity is None:
            entity = cls(name)
            cls._registry[name] = entity
        return entity
    
    @classmethod
    def all(cls) -> Iterator[Self]:
        return sorted(cls._registry.values(), key=lambda b: b._name)
    
    def __init__(self, name: str):
        self._name = name
        
    @property
    def name(self) -> str:
        return self._name
    
    def __str__(self):
      return f"Entity(class={self.__class__.__name__!r}, name={self.name!r})"

    def __repr__(self):
        return str(self)
