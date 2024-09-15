import re

from ..internal_types import *
from ..raw_scrape import get_page_html, get_page_markdown, get_page_asset
from ..mdparse import parse_markdown, WikiText, Table
from ..model import GridDim, RecordRegistry, GameObject
from ..model.recipe import CountedGameObjectRef, CountedGameObjectRefList

item_count_re = re.compile(r"\s*(\d+)\s*x\s+(.*)")
"""A pattern that indicataes a quantity followed by an item name, in the form f"{quantity}x {item_name}"."""

def parse_counted_game_object_ref_list(registry: RecordRegistry, val: str) -> CountedGameObjectRefList:
    val = val.strip()
    result: CountedGameObjectRefList = []
    if val != "" and not val.startswith("N/A"):
        for counted_item in val.split("+"):
            counted_item = counted_item.strip()
            m = item_count_re.match(counted_item)
            if m is None:
                n = 1
                item_template = counted_item
            else:
                n = int(m.group(1))
                item_template = m.group(2).strip()
            item_name = strip_md_item_template(item_template)
            item_ref = registry.get_ref(item_name, GameObject)
            entry = CountedGameObjectRef(item_ref, n)
            result.append(entry)
            
    return result

def split_md_template(val: str) -> Tuple[str, str]:
    val = val.strip()
    if val.startswith("{{") and val.endswith("}}") and '|' in val:
        result = val[2:-2].strip().split("|", 1)
    else:
        result = ("", val)
    
    return result

def strip_md_template(val: str) -> str:
    return split_md_template(val)[1]

def strip_md_item_template(val: str) -> str:
    result = split_md_template(val)
    assert result[0] == "Item"
    return result[1]

def strip_md_icon_template(val: str) -> str:
    result = split_md_template(val)
    assert result[0] == "Icon"
    return result[1]

def parse_counted_game_object_ref_list(registry: RecordRegistry, val: str) -> CountedGameObjectRefList:
    val = val.strip()
    result: CountedGameObjectRefList = []
    if val != "" and not val.startswith("N/A"):
        for counted_item in val.split("+"):
            counted_item = counted_item.strip()
            m = item_count_re.match(counted_item)
            if m is None:
                n = 1
                item_template = counted_item
            else:
                n = int(m.group(1))
                item_template = m.group(2).strip()
            item_name = strip_md_item_template(item_template)
            item_ref = registry.get_ref(item_name, GameObject)
            entry = CountedGameObjectRef(item_ref, n)
            result.append(entry)
            
    return result

def parse_page(page: str, force: Optional[bool]=False) -> WikiText:
    return parse_markdown(get_page_markdown(page, force))

class TableRow:
    reader: 'TableReader'
    index: int
    
    def __init__(self, reader: 'TableReader', index: int):
        self.reader = reader
        self.index = index
        
    @property
    def row_data(self) -> List[str]:
        return self.reader.table_data[self.index]
    
    def __iter__(self) -> Iterator[str]:
        return iter(self.row_data)
        
    def __getitem__(self, col: int|str) -> str:
        if isinstance(col, str):
            col = self.reader._header_map[col]
        return self.row_data[col]
    
    def has_column(self, col: int|str) -> bool:
        return self.reader.has_coluin(col)
    
    def __str__(self):
        return f"TableRow({self.reader.name}[{self.index}] = {self.row_data})"
    
    def __repr__(self):
        return str(self)
    
class TableReader:
    table: Table
    name: str
    _table_headers: List[str]
    _table_data: List[List[str]]
    _header_map: Dict[str, int]
    _rows: List[TableRow]
    
    def __init__(self, table: Table, name: str):
        self.table = table
        self.name = name
        d = table.data()
        self._table_headers = [ self.normalize_header(x) for x in d[0]]
        self._table_data = d[1:]
        self._header_map = {h: i for i, h in enumerate(self._table_headers)}
        self._rows = [TableRow(self, i) for i in range(len(self))]
        
    def normalize_header(self, header: str) -> str:
        result = header.strip()
        result = result.replace("<br>", " ")
        result = ' '.join(result.split())
        return result
        
    @property
    def headers(self) -> List[str]:
        return self._table_headers
    
    @property
    def table_data(self) -> List[List[str]]:
        return self._table_data
    
    @property
    def h(self) -> int:
        return len(self._table_data)
    
    @property
    def w(self) -> int:
        return len(self._table_headers)
    
    def __len__(self) -> int:
        return self.h
    
    def has_coluin(self, col: int|str) -> bool:
        if isinstance(col, str):
            return col in self._header_map
        return 0 <= col < self.w
    
    def has_row(self, row: int) -> bool:
        return 0 <= row < self.h
    
    def __getitem__(self, index: int) -> TableRow:
        return self._rows[index]
    
    def __iter__(self) -> Iterator[TableRow]:
        return iter(self._rows)
    
    def __str__(self):
        return f"TableReader(name={self.name}, v={self.table})"
    
    def __repr__(self):
        return str(self)
