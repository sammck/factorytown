from ..internal_types import *
from ..proj_dir import get_project_dir

from functools import cache
import os
import hashlib
import re
import requests
import subprocess

@cache
def get_markdown_scrape_script() -> str:
    return os.path.join(get_project_dir(), "scripts", "extract_wikitext.sh")

@cache
def get_cache_dir() -> str:
    return os.path.join(get_project_dir(), "data", "cache", "scrape")

@cache
def get_http_cache_dir() -> str:
    return os.path.join(get_cache_dir(), "http")

@cache
def get_markdown_cache_dir() -> str:
    return os.path.join(get_cache_dir(), "md")

def get_url_filename(url: str) -> str:
    """Maps an arbitrary URL into a unique but readable filename.
       
       All non-alphanumeric characters are replaced with underscores.
       
       Then ".{hash}" is appended to the end, where {hash} is a hex SHA256 hash of the URL.

    Args:
        url (str): The original URL

    Returns:
        str: A unique but readable filename for the URL
    """
    # Replace all non-alphanumeric characters with underscores
    filename = re.sub(r'\W', '_', url)
    # Append a hash of the URL
    h = hashlib.sha256()
    h.update(url.encode('utf-8'))
    return f"{filename}.{h.hexdigest()}"

def get_url_bytes(url: str, force: bool=False) -> bytes:
    """Fetch the raw binary content at the given URL, either from cache or by downloading.
       Updates the cache if the content is downloaded.

    Args:
        url (str): The URL to fetch
        force (bool, optional): Fetch a new copy even if already in cache. Defaults to False.

    Returns:
        bytes: The raw content at the location
    """
    filename = get_url_filename(url)
    cache_dir = get_http_cache_dir()
    cache_path = os.path.join(cache_dir, filename)
    if not force and os.path.exists(cache_path):
        with open(cache_path, 'rb') as f:
            return f.read()
    # Download the content
    r = requests.get(url)
    r.raise_for_status()
    content = r.content
    # Write to cache
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_path, 'wb') as f:
        f.write(content)
    return content

def get_url_text(url: str, force: bool=False) -> str:
    """Fetch the text content at the given URL, either from cache or by downloading.
       Updates the cache if the content is downloaded.

    Args:
        url (str): The URL to fetch
        force (bool, optional): Fetch a new copy even if already in cache. Defaults to False.

    Returns:
        str: The text content at the location
    """
    return get_url_bytes(url, force).decode('utf-8')

def get_url_markdown(url: str, force: bool=False) -> str:
    """Fetch the wikitext markdown content at the given URL, either from cache or by downloading.
       Updates the cache if the content is downloaded.
    Args:
        url (str):
            The URL to fetch. Must be a Fandom wiki page. "?action=edit" is appended to the URL
            to get the edit page, which is then scraped for the Markdown content.
        force (bool, optional): Fetch a new copy even if already in cache. Defaults to False.

    Returns:
        str: The Markdown text at the location
    """
    if not url.endswith("?action=edit"):
        url += "?action=edit"
    filename = get_url_filename(url)
    cache_dir = get_markdown_cache_dir()
    cache_path = os.path.join(cache_dir, filename)
    if not force and os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return f.read()
        
    html = get_url_text(url, force)
    script = get_markdown_scrape_script()
    
    # Run the script with fetched html as input
    
    markdown_utf8 = subprocess.check_output([script], input=html.encode('utf-8'))
    markdown = markdown_utf8.decode('utf-8')
    
    # Write to cache
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_path, 'w') as f:
        f.write(markdown)
    return markdown
