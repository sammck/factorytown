from .common import *

page_url = 'https://factorytown.gamepedia.com/Buildings'
page = requests.get(page_url)

print(page.content)
