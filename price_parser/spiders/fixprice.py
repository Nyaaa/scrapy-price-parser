import re
from datetime import datetime

import scrapy

from price_parser.items import PriceLoader, PriceItem


class MainSpider(scrapy.Spider):
    name = "main"
    allowed_domains = ["fix-price.com"]
    base_url = "https://api.fix-price.com/buyer/v1/product/"
    categories_to_parse = [
        "kosmetika-i-gigiena/ukhod-za-polostyu-rta",
        "sad-i-ogorod/instrumenty-dlya-raboty-v-sadu",
        "sad-i-ogorod/tovary-dlya-rassady-i-semena",
    ]
    header = {"x-city": 55}  # 55 = Екатеринбург

    def start_requests(self):
        for category in self.categories_to_parse:
            yield scrapy.Request(
                url=f"{self.base_url}in/{category}?page=1",
                headers=self.header,
                method="POST",
                callback=self.parse_links,
                meta={"page": 1},
            )

    def parse_links(self, response):
        for item in response.json():
            yield scrapy.Request(
                url=self.base_url + item.get("url"),
                headers=self.header,
                callback=self.parse_items,
                meta={"data": item},
            )

        if response.json():
            curr_page = response.meta["page"]
            page_url = re.sub(
                rf"page={curr_page}", rf"page={curr_page + 1}", response.url
            )
            yield scrapy.Request(
                url=page_url,
                headers={"x-city": 55},
                method="POST",
                callback=self.parse_links,
                meta={"page": curr_page + 1},
            )

    def parse_items(self, response):
        new_item = PriceLoader(item=PriceItem(), response=response)
        extra_data = response.meta["data"]

        json_response = response.json()

        new_item.add_value("RPC", json_response.get("id"))
        new_item.add_value("url", response.url)
        new_item.add_value("title", json_response.get("title"))
        new_item.add_value("timestamp", datetime.now())

        if brand := json_response.get("brand"):
            brand = brand.get("title")
        new_item.add_value("brand", brand)

        new_item.add_value("section", extra_data.get("category").get("title"))

        orig_price = float(extra_data.get("price"))
        if curr := extra_data.get("specialPrice"):
            current_price = float(curr.get("price"))
        else:
            current_price = orig_price

        sale_tag = ""
        if current_price != orig_price:
            discount = (orig_price - current_price) / orig_price * 100
            sale_tag = f"Скидка {discount:.2f}%"

        price = {"current": current_price, "original": orig_price, "sale_tag": sale_tag}
        new_item.add_value("price_data", price)

        stock = int(extra_data.get("inStock")) or 0
        new_item.add_value("stock", {"in_stock": stock > 0, "count": stock})

        images = [i.get("src") for i in json_response.get("images")]
        new_item.add_value("assets", {"main_image": images[0], "set_images": images})

        metadata = {"__description": json_response.get("description")}
        if properties := json_response.get("properties"):
            metadata |= {i.get("alias"): i.get("value") for i in properties}
        dimensions = json_response.get("variants")[0].get("dimensions")
        new_item.add_value("metadata", metadata | dimensions)

        new_item.add_value("variants", len(json_response.get("variants")))

        yield new_item.load_item()
