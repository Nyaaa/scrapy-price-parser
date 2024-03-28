from pathlib import Path

from scrapy.exporters import JsonItemExporter


class SaveJsonPipeline:
    def process_item(self, item, spider):
        folder = Path("data/")
        folder.mkdir(parents=True, exist_ok=True)
        filepath = folder / f'{item["RPC"]}.json'
        JsonItemExporter(filepath.open("wb"), indent=2, encoding="utf-8").export_item(
            item
        )
        return item
