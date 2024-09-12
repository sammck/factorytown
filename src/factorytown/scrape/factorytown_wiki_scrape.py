from ..internal_types import *
from .fandom_scrape import get_url_markdown, get_url_text

from functools import cache

FACTORYTOWN_WIKI = "https://factorytown.fandom.com/wiki"

def get_page_url(page: str) -> str:
    wiki = FACTORYTOWN_WIKI
    if not wiki.endswith("/"):
        wiki += "/"
    return f"{wiki}{page}"

def get_page_html(page: str, force: bool=False) -> str:
    return get_url_text(get_page_url(page), force)

def get_page_markdown(page: str, force: bool=False) -> str:
    return get_url_markdown(get_page_url(page), force)
