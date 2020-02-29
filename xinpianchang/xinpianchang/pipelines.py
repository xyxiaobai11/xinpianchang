# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
from twisted.enterprise import adbapi
import MySQLdb.cursors


class XinpianchangPipeline(object):
    def process_item(self, item, spider):
        return item


class XPCTwistMysqlPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        params = dict(
            host=settings.get('HOST'),
            db=settings.get('DBNAME'),
            user=settings.get('USER'),
            passwd=settings.get('PASSWD'),
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **params)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 将mysql插入变成异步操作
        query = self.dbpool.runInteraction(self.insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        print(failure)

    def insert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)