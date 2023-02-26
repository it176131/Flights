from datetime import datetime
from pathlib import Path

from scrapy import Spider

from ..http import SeleniumRequest


class GoogleSpider(Spider):
    name = "google"
    allowed_domains = "google.com/travel/flights"
    start_urls = ["https://www.google.com/travel/flights"]

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(url=url)

    def parse(self, response, **kwargs):
        dttm = datetime.now().strftime("%Y%m%d_%H%M%S")
        response_html = Path(f"response_html")
        response_html.mkdir(parents=True, exist_ok=True)
        path = response_html / f"response_{dttm}.html"
        with path.open(mode="w", encoding="utf-8") as f:
            f.write(response.text)
