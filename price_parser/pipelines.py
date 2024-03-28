# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class FillTheBlanksPipeline:
    @staticmethod
    def process_item(item, spider):
        adapter = ItemAdapter(item)

        adapter['timestamp'] = datetime.now()

        return item
