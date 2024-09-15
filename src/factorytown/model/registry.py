from ..internal_types import *
if TYPE_CHECKING:
    from .model import FactoryTownModel
else:
    FactoryTownModel = Any

class Record:
    """Base class for a factorytown metadata record that can be stored in a registry."""
    _registry: 'RecordRegistry'
    _record_name: str
    """The unique name of the record within the registry."""
    
    _display_name: Optional[str] = None
    """The display name of the record. If None, the record name is used."""
    
    _tags: Set[str]
    """Set of tags for grouping records (e.g., "Building", etc.)"""
    
    def __init__(self, registry: 'RecordRegistry', record_name: str):
        if type(self) is Record:
            raise TypeError("Record is an abstract class and cannot be instantiated directly.")
        self._registry = registry
        self._record_name = record_name
        self._tags = set()
        
    @property
    def record_name(self) -> str:
        return self._record_name
    
    @property
    def display_name(self) -> str:
        return self._record_name if self._display_name is None else self._display_name
    
    @property
    def registry(self) -> 'RecordRegistry':
        return self._registry
    
    @property
    def model(self) -> FactoryTownModel:
        return self._registry.model
    
    def create_ref(self) -> 'RecordRef[Self]':
        return RecordRef[Self](self._registry, self.record_name)
    
    def has_tag(self, tag: str) -> bool:
        return tag in self._tags
    
    def add_tag(self, tag: str):
        self._tags.add(tag)
        
    def add_tags(self, tags: Iterable[str]):
        self._tags.update(tags)
        
    @property
    def tags(self) -> Set[str]:
        return self._tags
    
    def common_str(self) -> str:
        name_desc = f"name={self.record_name!r}" if self._display_name is None else f"record_name={self.record_name!r}, display_name={self.display_name!r}"
        return f"{name_desc}, tags={self.tags}"
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.common_str()})"

    def __repr__(self):
        return str(self)

T = TypeVar('T', bound=Record)
TTYPE = TypeVar('TTYPE', bound=Type[Record])

class RecordRef(Generic[T]):
    """A reference to a record in a registry. Allows for lazy loading of records and circular
       references between records."""
    _registry: 'RecordRegistry'
    _record_name: str
    _record_class: Type[T]
    
    _record: Optional[T]
    """A cache of the instantiated record, if it has been resolved."""
        
    def __init__(self, registry: 'RecordRegistry', record_name: str, record_class: Type[T]=Record, existing: Optional[T]=None):
        self._registry = registry
        self._record_name = record_name
        self._record_class = record_class
        assert existing is None or isinstance(existing, record_class)
        self._record = existing
        
    @property
    def record_name(self) -> str:
        return self._record_name
    
    @property
    def record_class(self) -> Type[T]:
        return self._record_class
    
    @property
    def registry(self) -> 'RecordRegistry':
        return self._registry
    
    @property
    def model(self) -> 'FactoryTownModel':
        return self._registry.model
    
    def try_get(self) -> Optional[T]:
        if self._record is None:
            self._record = self._registry.try_get(self._record_name, self._record_class)
        return self._record
    
    def get(self) -> T:
        record = self.try_get()
        if record is None:
            raise ValueError(f"Record {self._record_name!r} has not been instantiated in {self._registry.name!r}")
        return record
    
    def _instantiate(self) -> T:
        """Called internally by the registry to create the real instance of the record."""
        if self._record is None:
            self._record = self._record_class(self._registry, self._record_name)
        return self._record
    
    def __call__(self) -> T:
        return self.get()
    
    def __str__(self):
        return f"RecordRef(class={self._record_class.__name__!r}, record_name={self._record_name!r})"
    
    def detail_str(self) -> str:
        record = self.try_get()
        if record is None:
            return str(self)
        return f"RecordRef({record})"
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, RecordRef):
            return self._record_name == other._record_name and self.registry == other.registry
        return False
    
    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash((self.registry, self._record_name))
    
    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, RecordRef):
            raise TypeError(f"Cannot compare RecordRef to {type(other)}")
        return (self.registry, self._record_name) > (other.registry, other._record_name)
    
    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, RecordRef):
            raise TypeError(f"Cannot compare RecordRef to {type(other)}")
        return (self.registry, self._record_name) < (other.registry, other._record_name)
    
    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, RecordRef):
            raise TypeError(f"Cannot compare RecordRef to {type(other)}")
        return (self.registry, self._record_name) >= (other.registry, other._record_name)
    
    def __le__(self, other: Any) -> bool:
        if not isinstance(other, RecordRef):
            raise TypeError(f"Cannot compare RecordRef to {type(other)}")
        return (self.registry, self._record_name) <= (other.registry, other._record_name)

RecordId = Union[str, Record, RecordRef]

class RecordRegistry:
    model: FactoryTownModel
    name: str
    _registry: Dict[str, Optional[Record]]
    """The registry of instantiated or referenced records, indexed by record name. If a record
       is referenced but has not been instantiated, the value is None."""
    _len: int = 0
    """The number of records in the registry (not including uninstantiated references)."""
    
    def __init__(self, model: 'FactoryTownModel', name: str):
        self.model = model
        self.name = name
        self._registry = {}
    
    def get_record_name(self, id: RecordId) -> str:
        """Get the name of a record, given the name, the record, or a reference to the record."""
        if isinstance(id, str):
            record_name = id
        elif isinstance(id, RecordRef):
            record_name = id.record_name
        else:
            assert isinstance(id, Record)
            record_name = id.record_name
        return record_name

    def create(self, id: RecordId, record_class: Type[T]) -> T:
        """Create a new record in the registry. Raises an exception if the record already exists."""
        record_name = self.get_record_name(id)
        if self._registry.get(record_name) is not None:
            raise ValueError(f"Record {record_name!r} already exists in registry {self.name!r}")
        record = RecordRef[T](self, record_name, record_class)._instantiate()
        self._registry[record_name] = record
        self._len += 1
        return record
        
    def get_ref(self, id: RecordId, record_class: Type[T]=Record) -> RecordRef[T]:
        """Gets a reference to a record in the registry, given the name of the record, a reference
           to it, or the record itself. If the record does not exist and is not already referenced,
           marks the record name as referenced--the record must be created later."""
        name = self.get_record_name(id)
        if not name in self._registry:
            self._registry[name] = None
        existing = self._registry.get(name)
        assert existing is None or isinstance(existing, record_class)
        ref = RecordRef[T](self, name, record_class, existing)
        return ref
    
    def try_get(self, id: RecordId, record_class: Type[T]=Record) -> Optional[T]:
        """Gets a record from the registry, given the name of the record, a reference to it,
           or the record itself. If the record is not yet instanciated or referenced, an undefined reference to it is created and
           None is returned."""
        name = self.get_record_name(id)        
        record = self._registry.get(name)
        assert record is None or isinstance(record, record_class)
        if record is None:
            self._registry[name] = None
        return record
    
    def get(self, id: RecordId, record_class: Type[T]=Record) -> T:
        """Gets a record from the registry, given the name of the record, a reference to it,
           or the record itself. If the record is not yet instanciated, an exception is raised."""
        record = self.try_get(id, record_class)
        if record is None:
            raise FactoryTownError(f"Record {id!r} referenced butnot instantiated in registry {self.name!r}")
    
    def get_or_create(self, id: RecordId, record_class: Type[T]) -> T:
        name = self.get_record_name(id)
        record = self.try_get(name, record_class=record_class)
        if record is None:
            record = self.create(name, record_class)
        return record
    
    def __getitem__(self, record_name: str) -> Record:
        record = self.get(record_name)
        return record
    
    def contains_ref(self, record_name: str) -> bool:
        """Returns True if the record exists or is referenced"""
        return record_name in self._registry
    
    def ref_len(self) -> int:
        """Returns the number of records that are referenced or instantiated."""
        return len(self._registry)
    
    def __contains__(self, record_name: str) -> bool:
        """Returns True if the record exists, not including uninstantiated references."""
        return self._registry.get(record_name) is not None
    
    def __len__(self) -> int:
        """Returns the number of instantiated records in the registry."""
        return self._len
    
    def __iter__(self) -> Iterator[str]:
        """Iterates over the names of instantiated records in the registry."""
        for k in self._registry:
            if self._registry[k] is not None:
                yield k
                
    def keys(self) -> KeysView[str]:
        """Returns the names of instantiated records in the registry."""
        result = set(k for k, v in self._registry.items() if v is not None)
        return result
    
    def values(self, record_class: Type[T]=Record) -> ValuesView[T]:
        """Returns the instantiated records in the registry."""
        result = set(v for v in self._registry.values() if isinstance(v, record_class))
        return result
    
    def items(self, record_class: Type[T]=Record) -> ItemsView[str, Record]:
        """Returns the names and records of instantiated records in the registry"""
        result = set((k, v) for k, v in self._registry.items() if isinstance(v, record_class))
        return result
        
    def referenced_keys(self) -> KeysView[str]:
        """Returns the names of records that are referenced or instantiated."""
        result = self._registry.keys()
        return result
    
    def referenced_items(self) -> ItemsView[str, Optional[Record]]:
        """Returns the names and records of records that are referenced or instantiated."""
        result = self._registry.items()
        return result

    def missing_keys(self) -> KeysView[str]:
        """Returns the names of records that are referenced but not instantiated"""
        result = set(k for k, v in self._registry.items() if v is None)
        return result
    
