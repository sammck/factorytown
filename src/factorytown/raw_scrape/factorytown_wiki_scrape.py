from ..internal_types import *
from .fandom_scrape import get_url_markdown, get_url_text, get_url_bytes

from functools import cache
from urllib.parse import urljoin

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

def get_page_asset(page: Optional[str], asset_url: str) -> bytes:
    if page is None or page == "":
        url = asset_url
    else:
        url = urljoin(get_page_url(page), asset_url)
    return get_url_bytes(url)