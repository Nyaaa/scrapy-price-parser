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
                                 callback=self.parse_items,
                                 meta={"data": item})

        if response.json():
            curr_page = response.meta["page"]
            page_url = re.sub(rf'page={curr_page}&', rf"page={curr_page + 1}&", response.url)
            yield scrapy.Request(url=page_url,
                                 cookies=self.cookie,
                                 method="POST",
                                 callback=self.parse_links,
                                 meta={"page": curr_page + 1})

    def parse_items(self, response):
        new_item = PriceLoader(item=PriceItem(), response=response)
        extra_data = response.meta["data"]

        json_response = response.json()

        new_item.add_value('RPC', json_response.get('id'))
        new_item.add_value('url', response.url)
        new_item.add_value('title', json_response.get('title'))

        if brand := json_response.get('brand'):
            brand = brand.get('title')
        new_item.add_value('brand', brand)

        new_item.add_value('section', extra_data.get('category').get('title'))

        orig_price = float(extra_data.get('price'))
        if curr := extra_data.get('specialPrice'):
            current_price = float(curr.get('price'))
        else:
            current_price = orig_price

        sale_tag = ''
        if current_price != orig_price:
            discount = (orig_price - current_price) / orig_price * 100
            sale_tag = f'Скидка {discount:.2f}%'

        price = {'current': current_price, 'original': orig_price, 'sale_tag': sale_tag}
        new_item.add_value('price_data', price)

        stock = int(extra_data.get('inStock')) or 0
        new_item.add_value('stock', {'in_stock': stock > 0, 'count': stock})

        images = [i.get('src') for i in json_response.get('images')]
        new_item.add_value('assets', {'main_image': images[0], 'set_images': images})

        metadata = {'__description': json_response.get('description')}
        dimensions = json_response.get('variants')[0].get('dimensions')
        new_item.add_value('metadata', metadata | dimensions)

        new_item.add_value('variants', len(json_response.get('variants')))

        yield new_item.load_item()
