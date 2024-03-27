# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from datetime import datetime

from itemloaders.processors import TakeFirst
from scrapy.loader import ItemLoader
from dataclasses import dataclass, field


@dataclass
class PriceItem:
    timestamp: datetime = field(default=datetime.now())
    RPC: str = ""
    url: str = ""
    title: str = ""


class PriceLoader(ItemLoader):
    default_output_processor = TakeFirst()
