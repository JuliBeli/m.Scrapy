# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from openpyxl import Workbook
import pandas as pd
import json
import xlwt

class MySQLPipeline:
    def __init__(self):
        self.conn = pymysql.Connect(host='localhost',
                                    port=3306,
                                    user='root',
                                    password='root',
                                    database='ugcp',
                                    charset='utf8mb4')

        # 创建一个游标对象
        self.cursor = self.conn.cursor()

    # 每次开启爬虫的时候
    def open_spider(self, spider):
        # 把数据表的数据清空掉
        sql1 = 'TRUNCATE TABLE weibo_raw1'
        self.cursor.execute(sql1)
        sql2 = 'TRUNCATE TABLE weibo_top10f'
        self.cursor.execute(sql2)
        self.conn.commit()

    # 每次爬取数据如何处理
    def process_item(self, item, spider):
        # 这里的item就是我们刚才yield的数据
        # 开始将数据存储到数据库ugcp的m.weibo_raw整个表
        user_followers_int = int(item['user_followers'])
        thumbs_up_int = int(item['thumbs_up'])
        reposts_int = int(item['reposts'])
        comments_int = int(item['comments'])
        sql = 'INSERT INTO weibo_raw1 VALUES(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        self.cursor.execute(sql, (item['userid'], item['username'], item['user_gender'],item['user_followers'],
                                  item['post_time'], item['thumbs_up'],item['comments'], item['reposts'],item['content'],
                                  comments_int,reposts_int,thumbs_up_int,user_followers_int))

        self.conn.commit()
        print(item)
        return item

    # 爬虫结束之后的操作
    def close_spider(self, spider):
        self.weibo_df = pd.read_sql('select * from weibo_raw1', self.conn)
        # Create a new DataFrame by dropping duplicates based on 'username' column
        distinct_users_df = self.weibo_df.drop_duplicates(subset='username', keep='first')
        # 统计1，粉丝数最多的前10个用户的排名，用户名，粉丝数
        order_df = distinct_users_df.sort_values(by='user_followers_int', ascending=False).head(10)
        for index, row in order_df.iterrows():
            sql = 'INSERT INTO weibo_top10f VALUES(null,%s,%s)'
            self.cursor.execute(sql, (str(row['username']), str(row['user_followers'])))


# ...................
        self.conn.commit()
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
