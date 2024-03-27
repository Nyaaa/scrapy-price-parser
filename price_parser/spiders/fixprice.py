import re
from urllib.parse import urlencode

import scrapy

from price_parser.items import PriceLoader, PriceItem


class MainSpider(scrapy.Spider):
    name = 'main'
    allowed_domains = ['fix-price.com']
    base_url = 'https://api.fix-price.com/buyer/v1/product/'
    cookie = {"locality": '{"city":"Екатеринбург","cityId":55,"longitude":60.597474,"latitude":56.838011,"prefix":"г"}'}

    def start_requests(self):
        url = "https://api.fix-price.com/buyer/v1/product/in/kosmetika-i-gigiena/ukhod-za-polostyu-rta"
        querystring = {"page": "1", "limit": "24", "sort": "abc"}

        yield scrapy.Request(url=f'{url}?{urlencode(querystring)}',
                             cookies=self.cookie,
                             method="POST",
                             callback=self.parse_links,
                             meta={"page": 1})

    def parse_links(self, response):
        for item in response.json():
            yield scrapy.Request(url=self.base_url + item.get('url'),
                                 cookies=self.cookie,
                                 callback=self.parse_items)

        # if response.json():
        #     curr_page = response.meta["page"]
        #     page_url = re.sub(rf'page={curr_page}&', rf"page={curr_page + 1}&", response.url)
        #     yield scrapy.Request(url=page_url,
        #                          cookies=self.cookie,
        #                          method="POST",
        #                          callback=self.parse_links,
        #                          meta={"page": curr_page + 1})

    def parse_items(self, response):
        new_item = PriceLoader(item=PriceItem())

        json_response = response.json()

        new_item.add_value('RPC', json_response.get('id'))
        new_item.add_value('url', response.url)

        yield new_item.load_item()
