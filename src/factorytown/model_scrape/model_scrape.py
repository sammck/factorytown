from ..internal_types import *

from ..model import (
    FactoryTownModel,
)

from .buildings import scrape_buildings
from .coins import scrape_coins

def scrape_model(*, force: Optional[bool]=False, model: Optional[FactoryTownModel]=None) -> FactoryTownModel:
    if model is None:
        model = FactoryTownModel()
    scrape_coins(model, force)
    scrape_buildings(model, force)
    return model
