import scrapy
from scrapy.item import Item, Field

class CafefItem(scrapy.Item):
    source_link = Field()
    source_news = Field()
    thumbnail = Field()
    vi = Field()
    published_at = Field()
    created_at = Field()
    created_by = Field()

class Thumbnail(scrapy.Item):
    display_name = Field()
    download_link = Field()

class Vi(scrapy.Item):
    title = Field()
    description  = Field()
    content = Field()
    slug_url = Field()
