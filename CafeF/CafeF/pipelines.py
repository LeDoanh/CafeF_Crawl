import pymongo
import logging

from itemadapter import ItemAdapter
from scrapy.utils.project import get_project_settings
from datetime import datetime

class MongoDBPipeline:
    settings = get_project_settings()
    
    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri = crawler.settings.get("URI"),
            mongo_db = crawler.settings.get("DATABASE"),
            mongo_collection = crawler.settings.get("COLLECTION")
        )
    
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri, serverSelectionTimeoutMS = 5000)
        self.db = self.client[self.mongo_db]
    
    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        item['created_at'] = datetime.now()
        item['created_by'] = 'Lê Đình Doanh'
        self.db[self.mongo_collection].insert_one(ItemAdapter(item).asdict())
        logging.debug(msg = "One stocknew added to MongoDB!")
        return item
