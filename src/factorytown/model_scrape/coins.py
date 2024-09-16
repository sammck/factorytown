from ..internal_types import *

from ..model import (
    FactoryTownModel,
    Coins,
)

from logging import getLogger

logger = getLogger(__name__)

def scrape_coins(model: FactoryTownModel, force: Optional[bool]=False) -> None:
    for color in ["Yellow", "Red", "Blue", "Purple", "Star"]:
        record_name = f"{color} Coins"
        logger.debug(f"adding coins: {record_name}")
        record = model.records.get_or_create(record_name, Coins)
        logger.debug(f"  record: {record}")
