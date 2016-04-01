# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.exceptions import DropItem


class EduPipeline(object):
    collection_name = "crawl"

    def __init__(self, uri, db):
        self.mongo_uri = uri
        self.mongo_db = db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            crawler.settings.get('MONGO_URI'),
            crawler.settings.get('MONGO_DB'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.collection_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if self.collection.find({'title': item["title"]}).count() != 0:
            raise DropItem("duplicate title {%s}" % item["title"])
        self.collection.insert(dict(item))
        return item
