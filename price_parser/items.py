# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from itemloaders.processors import TakeFirst
from scrapy import Item, Field
from scrapy.loader import ItemLoader


class PriceItem(Item):
    timestamp = Field()
    RPC = Field()
    url = Field()
    title = Field()
    brand = Field()
    price_data = Field()
    stock = Field()


class PriceLoader(ItemLoader):
    default_output_processor = TakeFirst()
