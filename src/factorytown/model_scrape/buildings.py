from ..internal_types import *

from ..model import (
    FactoryTownModel,
    Building,
    Item,
    Research,
    GridDim,
    Recipe,
)

from .util import (
    parse_page,
    WikiText,
    Table,
    TableReader,
    TableRow,
    split_md_template,
    strip_md_template,
    strip_md_item_template,
    strip_md_icon_template,
    parse_counted_game_object_ref_list,
)

from logging import getLogger

logger = getLogger(__name__)

def scrape_buildings(model: FactoryTownModel, force: Optional[bool]=False) -> None:
    wt = parse_page("Buildings", force)
    storage = TableReader(wt.tables[0], "Storage")
    production = TableReader(wt.tables[1], "Production")
    market = TableReader(wt.tables[2], "Market")
    
    for group in [storage, production, market]:
        logger.debug(f"Processing group: {group.name}")
        logger.debug(f"Headers: {group.headers}")
        building_type = group.name
        for i, row in enumerate(group):
            name = strip_md_item_template(row["Building"])
            logger.debug(f"{group.name}[{i}] = {row.row_data}")
            if name == "Town Center" and row["Ingredients"].startswith("N/A"):
                logger.debug(f"Skipping {name} with no ingredients as it is a special case")
                continue
            building: Building = model.records.get_or_create(name, Building)
            building.building_type = building_type
            building.grid_size = GridDim.parse(row["Size"])
            building.tech_level = int(row["Tech Lv."])
            research_name = row["Research Required"].strip()
            if research_name == "" or research_name == "N/A":
                research_name = None
            research_record_name = None if research_name is None else Research.get_record_name(research_name)
            building.research = None if research_name is None else model.records.get_or_create(research_record_name, Research)
            
            if row.has_column("Shared Inventory"):
                sistr = row["Shared Inventory"].strip()
                assert sistr in ["Yes", "No"]
                building.shared_inventory = sistr == "Yes"
            else:
                building.shared_inventory = False
            
            if row.has_column("Capacity"):
                building.capacity_note = row["Capacity"].replace('<br>', '\n').strip()
            else:
                building.capacity_note = ""
                
            if row.has_column("Ingredients"):
                ingredients = parse_counted_game_object_ref_list(model.records, row["Ingredients"])
                recipe_record_name = Recipe.create_record_name(None, name)
                recipe = model.records.get_or_create(recipe_record_name, Recipe)
                recipe.ingredients = ingredients
                recipe.set_product(building, 1)
                recipe.work_units = 0
                building.recipe = recipe
            
            logger.debug(f"    Building: {building}")
