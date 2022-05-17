import scrapy
import logging
import time

from scrapy import Request
from CafeF.items import CafefItem, Thumbnail, Vi
from datetime import datetime
from bs4 import BeautifulSoup
from random import randint

class CafefSecuritiesSpider(scrapy.Spider):
    name = 'CafeF'
    start_url = 'https://cafef.vn/timeline/31/trang-{page_num}.chn'

    category_page = 1
    crawl_from = datetime(2022, 4, 1)
    start_crawl_at = datetime.now()
    crawl_status = True

    # read and write last time crawl
    def time_crawl(self, mode, *args):
        # Read
        if mode == 'read':
            with open('time_crawl.txt', 'r', encoding='utf-8') as time:
                last_time = time.readline()
            try:
                return datetime.fromisoformat(last_time)
            except:
                return self.crawl_from
            
        # Write
        elif mode == 'write':
            with open('time_crawl.txt', 'w+', encoding='utf-8') as time:
                time.write(str(*args))

    def start_requests(self):
        yield Request(url=self.start_url.format(page_num=self.category_page), callback=self.parse_category)

    def parse_category(self, response):
        # Check last time crawl set time to start crawl:
        crawl_from = self.time_crawl('read')
        logging.debug(msg = "Start crawl from " + str(crawl_from))

        # Get all StockNew urls and request per url
        stocknews = response.xpath(
            '//li[starts-with(@class, "tlitem clearfix")]')
        for stocknew in stocknews:
            time_upload_stocknew = datetime.strptime(str(stocknew.xpath(
                './/div/p/span[@class = "get-timeago time"]/@title').get()), "%Y-%m-%dT%H:%M:%S")
            if time_upload_stocknew >= crawl_from:
                page_url = 'https://cafef.vn/' + str(stocknew.xpath('.//a/@href').get())
                yield Request(url=page_url, callback=self.parse_stocknew)
                time.sleep(randint(1,3))
            else:
                self.crawl_status = False

        # Next page
        if self.crawl_status == True:
            self.category_page += 1
            yield Request(
                url=self.start_url.format(page_num=self.category_page), callback=self.parse_category)
        else:
            self.time_crawl(
                'write', self.start_crawl_at)
            logging.debug(msg = "Last time crawl record: " + str(self.start_crawl_at))

    def parse_stocknew(self, response):
        try:
            stocknew = CafefItem()
            stocknew['source_link'] = response.url
            stocknew['source_news'] = response.xpath(
                '//a[@class = "link-source-full"]/text()').get().strip()

            Thumbnail_stocknew = Thumbnail()
            Thumbnail_stocknew['display_name'] = response.xpath(
                '//div[@class = "media"]/img/@title').get()
            Thumbnail_stocknew['download_link'] = response.xpath(
                '//div[@class = "media"]/img/@src').get()
            stocknew['thumbnail'] = Thumbnail_stocknew

            Vi_stocknew = Vi()
            Vi_stocknew['title'] = response.xpath(
                '//h1[@class = "title"]/text()').get().strip()
            Vi_stocknew['description'] = response.xpath(
                '//h2[@class = "sapo"]/text()').get().strip()
            # Content
            soup = BeautifulSoup(response.body, 'html.parser')
            Vi_stocknew['content'] = str(soup.find(id="mainContent"))
            Vi_stocknew['slug_url'] = response.url.split('/')[-1]

            stocknew['vi'] = Vi_stocknew
            stocknew['published_at'] = datetime.strptime(
                response.xpath(
                    '//span[@class = "pdate"]/text()').get().strip(),
                "%d-%m-%Y - %H:%M %p"
            )
            return stocknew
        except:
            logging.error(msg = 'Crawl error: ' + str(response.url))