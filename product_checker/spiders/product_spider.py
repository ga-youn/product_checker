import scrapy
import logging
from datetime import datetime
import subprocess

class ProductSpider(scrapy.Spider):
    name = "product_spider"
    
    # 도메인, URL, CSS 선택자를 매칭하는 딕셔너리
    domain_mapping = {
        "newpipeb2b" : {
            "url" : "https://newpipeb2b.com/html/goods/goods_new.php",
            "selector" : "div.PJ_goods_border",
            "selector_title" : "strong.block::text",
            "selector_code" : "div.code span::text",
            "selector_availability" : "div.tag-box span.icon_sellout::text",
            "selector_next_page" : "i.fa-angle-right::attr(href)"
        }
    }
    
    # start_urls를 domain_mapping의 URL로 설정
    start_urls = [info["url"] for info in domain_mapping.values()]
    allowed_domains = [domain for domain in domain_mapping.keys()]

    def __init__(self, *args, **kwargs):
        super(ProductSpider, self).__init__(*args, **kwargs)
        self.logger.info(f"Spider started at {datetime.now()}")

    def parse(self, response):
        # 현재 URL에 매칭되는 도메인 이름과 선택자를 찾음
        domain_info = next((info for name, info in self.domain_mapping.items() if info["url"] == response.url), None)
        if domain_info is None:
            self.logger.warning(f"No domain info found for URL: {response.url}")
            return
        
        domain_name = next(name for name, info in self.domain_mapping.items() if info["url"] == response.url)
        selector = domain_info["selector"]
        selector_title = domain_info["selector_title"]
        selector_code = domain_info["selector_code"]
        selector_availability = domain_info["selector_availability"]
        selector_next_page = domain_info["selector_next_page"]

        self.logger.info(f"Parsing page: {response.url} (Domain: {domain_name}) at {datetime.now()}")

        for product in response.css(selector):
            title = product.css(selector_title).get()
            code = product.css(selector_code).get()
            availability = product.css(selector_availability).get()

            if availability and ("품절" in availability or "재고 없음" in availability):
                self.logger.info(f"Product '{title}' is out of stock.")
                yield {
                    'domain': domain_name,
                    'title': title,
                    'code': code,
                    'availability': 'F', # false
                }
                self.logger.info(f"Product '{title}' is out of stock at {datetime.now()}")
            else:
                yield {
                    'domain': domain_name, 
                    'title': title,
                    'code': code,
                    'availability': 'T',
                }
                self.logger.info(f"Product '{title}' is in stock at {datetime.now()}")

        next_page = response.css(selector_next_page).get()
        if next_page is not None:
            self.logger.info(f"Following next page: {next_page} at {datetime.now()}")
            yield response.follow(next_page, self.parse)
        else:
            self.logger.info(f"No more pages to follow at {datetime.now()}")

    #def closed(self, reason):
            # JSON 파일 작성을 완료한 후에 update_product_status.py를 실행
            # subprocess.run(['py', 'update_product_status/update_product_status.py'])