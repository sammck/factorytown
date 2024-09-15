from ..internal_types import *

from ..model import (
    FactoryTownModel,
)

from .buildings import scrape_buildings

def scrape_model(*, force: Optional[bool]=False, model: Optional[FactoryTownModel]=None) -> FactoryTownModel:
    if model is None:
        model = FactoryTownModel()
    scrape_buildings(model, force)
    return model
