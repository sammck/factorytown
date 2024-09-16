from ..internal_types import *
from .registry import Record, RecordRef, RecordRegistry, RecordId
from .util import get_record_name
from .game_object import GameObject

if TYPE_CHECKING:
    from .building import Building
    from .item import Item
else:
    # pragma: no cover
    Building = Any
    Item = Any

class CountedGameObject(NamedTuple):
    """A GameObject type with a quantity."""
    
    obj: GameObject
    quantity: int

    @classmethod
    def create(cls, registry: RecordRegistry, obj_id: RecordId, quantity: int) -> "CountedGameObjectRef":
        obj = registry.get(obj_id, GameObject)
        return cls(obj, quantity)
    
    def __str__(self):
        return f"{self.quantity}x {self.obj.record_name!r}"
    
    def __repr__(self):
        return str(self)

class CountedGameObjectRef(NamedTuple):
    """A GameObjectRef type with a quantity."""
    
    obj_ref: RecordRef[GameObject]
    quantity: int

    @classmethod
    def create(cls, registry: RecordRegistry, obj_id: RecordId, quantity: int) -> "CountedGameObjectRef":
        obj_ref = registry.get_ref(obj_id, GameObject)
        return cls(obj_ref, quantity)
    
    def get(self) -> CountedGameObject:
        return CountedGameObject(self.obj_ref.get(), self.quantity)    
    
    def __str__(self):
        return f"{self.quantity}x {self.obj_ref.record_name!r}"
    
    def __repr__(self):
        return str(self)

CountedGameObjectRefList = List[CountedGameObjectRef]
CountedGameObjectList = List[CountedGameObject]

class Recipe(Record):
    """A recipe for producing a game object from ingredients.
    
       The record name of a recipe is f"{building}.{product_name}.{variant}" where building is the name of the building that produces the recipe,
       product_name is the record name of the first produced product GameObject, and variant is a unique identifier for the recipe if there are multiple recipes that
       produce the same product.
       
       If the recipe is a user recipe, the building will be "user".
       
       If the recipe does not have any variants, the variant name will be "default".
       
       The display name of the recipe is product_name if there are no variants; otherwise it is f"{product_name} ({variant}).
    """

    _product_refs: List[CountedGameObjectRef]|UnsetType = UNSET
    """The products produced by this recipe, and the quantities of each"""
    
    _ingredient_refs: List[CountedGameObjectRef]|UnsetType = UNSET
    """The ingredients required to produce this recipe, and the quantities of each"""
    
    _building: Optional[RecordRef[Building]] = UNSET
    """The building that produces this recipe.  If None, it is a user recipe"""
    
    _work_units: int|UnsetType = UNSET
    """The number of work units to produce this recipe. If a user recipe, set to 0"""

    _products: List[CountedGameObject]|UnsetType = UNSET
    """Cached realized products with quantities"""
    
    _ingredients: List[CountedGameObject]|UnsetType = UNSET
    """Cached realized ingredients with quantities"""
    
    _variant: Optional[str]
    _primary_product_name: str
    
    def __init__(self, registry: RecordRegistry, record_name: str):
        super().__init__(registry, record_name)
        building_name, product_name, variant = self.parse_record_name(record_name)
        self._primary_product_name = product_name
        self._variant = variant
        self.add_tag("Recipe")
        self.building = None if building_name is None else self._registry.get_ref(building_name, Building)
    
    @classmethod
    def create_record_name(cls, building_id: Optional[RecordId], primary_product_id: RecordId, variant: Optional[str]=None) -> str:
        building_name = "[User]" if building_id is None else get_record_name(building_id)
        primary_product_name = get_record_name(primary_product_id)
        if variant is None:
            variant_name = "default"
        else:
            variant_name = variant
        return f"{building_name}.{primary_product_name}.{variant_name}"
    
    @classmethod
    def parse_record_name(cls, record_name: str) -> Tuple[Optional[str], str, Optional[str]]:
        building_name, product_name, variant = record_name.split(".")
        if building_name == "[User]":
            building_name = None
        if variant == "default":
            variant = None
        return building_name, product_name, variant
    
    @property
    def default_image_name(self) -> str:
        return self._primary_product_name
     
    @property
    def variant(self) -> Optional[str]:
        return self._variant
    
    @property
    def display_name(self) -> str:
        if self._variant is None:
            return self._primary_product_name
        return f"{self._primary_product_name} ({self._variant})"
    
    @property
    def product_refs(self) -> List[CountedGameObjectRef]:
        assert not isinstance(self._product_refs, UnsetType)
        return self._product_refs
    
    @property
    def products(self) -> List[CountedGameObject]:
        if isinstance(self._products, UnsetType):
            self._products = [ x.get() for x in self.product_refs ]
        return self._products
    
    @property
    def product_ref(self) -> CountedGameObjectRef|UnsetType:
        if isinstance(self._product_refs, UnsetType):
            return UNSET
        assert len(self._product_refs) == 1
        return self._product_refs[0]
    
    @property
    def product(self) -> GameObject:
        return self.products[0].obj
    
    @property
    def product_quantity(self) -> int:
        return self.products[0].quantity
    
    @property
    def n_products(self) -> int:
        if self._product_refs is UNSET:
            return 0
        return len(self._product_refs)
    
    def add_product(self, obj_id: RecordId, quantity: int=1):
        obj_ref = self._registry.get_ref(obj_id, GameObject)
        if isinstance(self._product_refs, UnsetType):
            self._product_refs = []
        for product in self._product_refs:
            if product.obj_ref == obj_ref:
                assert product.quantity == quantity
                return
        if len(self._product_refs) == 0:
            assert obj_ref.record_name == self._primary_product_name
        self._product_refs.append(CountedGameObjectRef(obj_ref, quantity))
        self._products = UNSET
    
    def set_product(self, obj_id: RecordId, quantity: int=1):
        assert self.n_products <= 1
        obj_ref = self._registry.get_ref(obj_id, GameObject)
        if self.n_products > 0:
            assert self.product_ref == obj_ref and self.product_quantity == quantity
        else:
            self.add_product(obj_ref, quantity)
        
    @property
    def ingredient_refs(self) -> List[CountedGameObjectRef]:
        assert not isinstance(self._ingredient_refs, UnsetType)
        return self._ingredient_refs
    
    @property
    def ingredients(self) -> List[CountedGameObject]:
        if isinstance(self._ingredients, UnsetType):
            self._ingredients = [ x.get() for x in self.ingredient_refs ]
        return self._ingredients
    
    @ingredients.setter
    def ingredients(self, value: CountedGameObjectRefList):
        assert isinstance(self._ingredient_refs, UnsetType)
        self._ingredient_refs = list(value)
        self._ingredients = UNSET
    
    @property
    def n_ingredients(self) -> int:
        if self._ingredient_refs is UNSET:
            return 0
        return len(self._ingredient_refs)
    
    def add_ingredient(self, obj_id: RecordId, quantity: int=1):
        if isinstance(self._ingredient_refs, UnsetType):
            self._ingredient_refs = []
        obj_ref = self._registry.get_ref(obj_id, GameObject)
        for ingredient in self._ingredient_refs:
            if ingredient.obj_ref == obj_ref:
                assert ingredient.quantity == quantity
                return
        self._ingredient_refs.append(CountedGameObjectRef(obj_ref, quantity))
        self._ingredients = UNSET
        
    def set_no_ingredients(self):
        if not isinstance(self._ingredient_refs, UnsetType):
            assert len(self._ingredient_refs) == 0
            return
        self._ingredient_refs = []
        self._ingredients = []
    
    @property
    def building(self) -> Optional[Building]:
        assert not isinstance(self._building, UnsetType)
        return None if self._building is None else self._building.get()
    
    @building.setter
    def building(self, building_id: Optional[RecordId]):
        building_ref = None if building_id is None else self._registry.get_ref(building_id, Building)
        assert isinstance(self._building, UnsetType) or self._building == building_ref
        self._building = building_ref
        
    @property
    def work_units(self) -> int:
        assert not isinstance(self._work_units, UnsetType)
        return self._work_units
    
    @work_units.setter
    def work_units(self, value: int):
        assert isinstance(self._work_units, UnsetType) or self._work_units == value
        self._work_units = value

    def __str__(self):
        return (f"{self.__class__.__name__}({self.common_str()}, "
            f"display_name={self.display_name}, "
            f"products={self._product_refs}, "
            f"ingredients={self._ingredient_refs}, "
            f"building={self._building}, "
            f"work_units={self._work_units}, "
            f")")
