# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from openpyxl import Workbook
import json
import xlwt

readjsonFile = json.load(open('config.json', 'r', encoding="utf-8"))
savepath = readjsonFile.get('savepath')  # 可以自定义设计最终excel的路径

class ExcelPipeline(object):
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

        self.wb.save(savepath)
        return item

    def close_spider(self, spider):
        # 关闭
        self.wb.close()


class WeibomPipeline:
    def process_item(self, item, spider):
        return item
