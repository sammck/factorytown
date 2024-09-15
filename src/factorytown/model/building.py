from __future__ import annotations

from ..internal_types import *
from .registry import Record, RecordRef, RecordRegistry, RecordId
from .grid_dim import GridDim
from .research import Research
from .recipe import Recipe
from .game_object import GameObject
    
class Building(GameObject):
    _building_type: str|UnsetType = UNSET
    _grid_size: GridDim|UnsetType = UNSET
    _tech_level: int|UnsetType = UNSET
    _research: Optional[RecordRef[Research]|UnsetType] = UNSET
    _recipe: Optional[RecordRef[Recipe]]|UnsetType = UNSET
    _shared_inventory: bool|UnsetType = UNSET
    _capacity_note: str|UnsetType = UNSET
    
    def __init__(self, registry: RecordRegistry, name: str):
        super().__init__(registry, name)
        self.add_tag("Building")

    @property
    def building_type(self) -> str:
        assert not isinstance(self._building_type, UnsetType)
        return self._building_type
    
    @building_type.setter
    def building_type(self, value: str):
        assert isinstance(self._building_type, UnsetType) or self._building_type == value
        self._building_type = value
        self.add_tag(value)
        
    @property
    def grid_size(self) -> GridDim:
        assert not isinstance(self._grid_size, UnsetType)
        return self._grid_size
    
    @grid_size.setter
    def grid_size(self, value: GridDim):
        assert isinstance(self._grid_size, UnsetType) or self._grid_size == value
        self._grid_size = value
        
    @property
    def tech_level(self) -> int:
        assert not isinstance(self._tech_level, UnsetType)
        return self._tech_level
    
    @tech_level.setter
    def tech_level(self, value: int):
        assert(isinstance(self._tech_level, UnsetType) or self._tech_level == value)
        self._tech_level = value
        
    @property
    def shared_inventory(self) -> bool:
        assert not isinstance(self._shared_inventory, UnsetType)
        return self._shared_inventory
    
    @shared_inventory.setter
    def shared_inventory(self, value: bool):
        assert isinstance(self._shared_inventory, UnsetType) or self._shared_inventory == value
        self._shared_inventory = value
        
    @property
    def capacity_note(self) -> str:
        assert not isinstance(self._capacity_note, UnsetType)
        return self._capacity_note
    
    @capacity_note.setter
    def capacity_note(self, value: str):
        assert isinstance(self._capacity_note, UnsetType) or self._capacity_note == value
        self._capacity_note = value
        
    @property
    def research(self) -> Optional['Research']:
        assert not isinstance(self._research, UnsetType)
        return self._research.get()
    
    @research.setter
    def research(self, value: Optional[RecordId]):
        ref = None if value is None else self._registry.get_ref(value, Research)
        assert isinstance(self._research, UnsetType) or self._research == ref
        self._research = ref
        
    @property
    def recipe(self) -> Optional[Recipe]:
        assert not isinstance(self._recipe, UnsetType)
        return self._recipe.get()
    
    @recipe.setter
    def recipe(self, value: Optional[RecordId]):
        ref = None if value is None else self._registry.get_ref(value, Recipe)
        assert isinstance(self._recipe, UnsetType) or self._recipe == ref
        self._recipe = ref
    
    def __str__(self):
        return (f"{self.__class__.__name__}({self.common_str()}, "
                f"building_type={self._building_type!r}, "
                f"grid_size={self._grid_size}, "
                f"tech_level={self._tech_level}, "
                f"research={self._research}, "
                f"shared_inventory={self._shared_inventory}, "
                f"capacity_note={self._capacity_note!r}, "
                f"recipe={self._recipe.detail_str()}, "
                f")")
