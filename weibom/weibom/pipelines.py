# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from openpyxl import Workbook
import json
import xlwt


class MySQLPipeline:
    def __init__(self):
        self.conn = pymysql.Connect(host=****,
                                    port=****,
                                    user=****,
                                    password=****,
                                    database=****,
                                    charset=****)

        # 创建一个游标对象
        self.cursor = self.conn.cursor()

    # 每次开启爬虫的时候
    def open_spider(self, spider):
        # 把数据表的数据清空掉
        sql1 = 'TRUNCATE TABLE weibo_raw'
        self.cursor.execute(sql1)
        self.conn.commit()

    # 每次爬取数据如何处理
    def process_item(self, item, spider):
        # 这里的item就是我们刚才yield的数据
        # 开始将数据存储到数据库ugcp的m.weibo_raw整个表
        sql = 'INSERT INTO weibo_raw VALUES(null,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        self.cursor.execute(sql, (item['userid'], item['username'], item['user_gender'],item['user_followers'],
                                  item['post_time'], item['thumbs_up'],item['comments'], item['reposts'],item['content']))
        self.conn.commit()
        print(item)
        return item

    # 爬虫结束之后的操作
    def close_spider(self, spider):

        # self.conn.commit()
        # 统计 结束
        self.cursor.close()
        # pass



class ExcelPipeline(object):
    readjsonFile = json.load(open('config.json', 'r', encoding="utf-8"))
    savepath = readjsonFile.get('savepath')  # 可以自定义设计最终excel的路径
    def __init__(self):
        self.countn=1
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(["userid", "username", "user_gender", "user_followers", "post_time", "thumbs_up", "comments", "reposts",
                    "content"])
        # self.file_name = savepath

    def process_item(self, item, spider):
        line = [item['userid'], item['username'], item['user_gender'],item['user_followers'], item['post_time'], item['thumbs_up'],item['comments'], item['reposts'],item['content']]
        # print(item['userid'])
        # print(type(self.ws))
        print(self.ws)
        self.ws.append(line)

        self.wb.save(self.savepath)
        return item

    def close_spider(self, spider):
        # 关闭
        self.wb.close()


class WeibomPipeline:
    def process_item(self, item, spider):
        return item
