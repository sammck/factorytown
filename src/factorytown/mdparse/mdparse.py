from ..internal_types import *
import wikitextparser as wtp
from wikitextparser import WikiText, Table

def parse_markdown(markdown: str) -> WikiText:
    return wtp.parse(markdown)
