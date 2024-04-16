import scrapy
import urllib.parse
from urllib.parse import urlencode
import requests
import json
import time
from datetime import datetime
from pyquery import PyQuery as pq
import xlwt   #进行excel操作
import random
from ..items import WeibomItem

# 定义搜索文档
readjsonFile = json.load(open('./config.json', 'r', encoding="utf-8"))
savepath = readjsonFile.get('savepath')  # 可以自定义设计最终excel的路径
search = readjsonFile.get('search')  # 可以自定义设计查询什么内容
start_page=readjsonFile.get('start_page')
end_page = readjsonFile.get('end_page')
dateStart=readjsonFile.get('dateStart')    #日期格式必须是：形如：2022-4-21
dateEnd=readjsonFile.get('dateEnd')

#定义原始url
urlsearch=urllib.parse.quote('=1&q='+search)     #进行url编码
m_referer='https://m.weibo.cn/search?containerid=100103type'   #微博搜索来源界面
base_url = 'https://m.weibo.cn/api/container/getIndex?'     #微博接口
profile_url = 'https://m.weibo.cn/profile/' #个人主页

sign=0      #标志是否找到了实时微博以开始

class Weibom_spider(scrapy.Spider):
    name = "weibom_spider"
    # headers = {                 #封装请求头  让网站识别自己是浏览器
    #     'Referer': m_referer+urlsearch,             #告诉服务器自己是哪里来的  从那个页面来的   来路
    #     'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 Edg/80.0.361.111',    #包含操作系统和浏览器信息
    #     'Host':'m.weibo.cn',                #请求服务器的域名和端口号
    #     'X-Requested-With':'XMLHttpRequest'             #代表是ajax请求
    # }
    # print(page)
    # 获取网页的json（这个是获取搜索之后网页的json数据的函数）
    def start_requests(self):
        page=start_page
        # print(page)
        while int(page) <= int(end_page):
            para = {
                'containerid': m_referer[m_referer.find('100103'):] + urlsearch,
                'page': page
            }
            url = base_url + urlencode(para)  # 进行url编码添加到地址结尾  连带页数
            print("url1:"+url)
            # yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)
            yield scrapy.Request(url=url, callback=self.parse)
            page=int(page)+1
            time.sleep(random.random())


    # 分析JSON格式的数据，抓取目标信息
    def parse(self,response):
        global sign  # sign是用来标记是否有过title   在格式中从实时微博进行爬取  找到实时微博title之后开始爬取   之后不用进行判断title而用sign来判断
        # print(response)
        items = json.loads(response.text).get('data').get('cards')
        # items = response.json().get('data').get('cards')
        for item1 in items:
            item = item1.get("title")
            if (item != None or sign == 1):  # 分析数据发现只有实时微博开始时有一个title  所以可以进行判断是否有title并从title开始爬取
                item2 = item1.get("card_group")
                 # print(item2)
                # print(len(item2))
                for card in item2:
                    if card.get("mblog") != None:  # 如果没有mblog  那么就结束本次循环不尽兴数据爬取   如果有就进行爬取（因为会有一些数据中不包含mblog代表其并不是所需的数据）
                        sign = 1
                        itemc = card.get("mblog")
                        # weibo = {}
                        weibo=WeibomItem()
                        # 抓取信息
                        scheme = str(card.get("scheme"))  # 获取具体博文链接（可以访问具体博文数据）
                        # print("scheme="+scheme)
                        txtwb = pq(itemc.get('text')).text()  # 获取微博博文
                        # print("txtwb="+txtwb)
                        weibo['post_time'] = str(datetime.strptime(pq(itemc.get('created_at')).text(),
                                                                   '%a %b %d %H:%M:%S +0800 %Y'))  # 日期   #修改日期格式   默认微博日期格式是带时区的GMT的格式
                        weibo['thumbs_up'] = itemc.get('attitudes_count')  # 点赞次数
                        weibo['comments'] = itemc.get('comments_count')  # 评论次数
                        weibo['reposts'] = itemc.get('reposts_count')  # 转发次数
                        weibo['userid'] = itemc.get('user').get('id')  # 发布人id
                        weibo['username'] = itemc.get('user').get('screen_name')  # 发布人微博名

                        weibo['user_gender'] = itemc.get('user').get('gender')  # 发布人性别
                        uf = itemc.get('user').get('followers_count_str')  # 发布人粉丝数
                        weibo['user_followers'] = self.convert_chinese_number(uf)#转换成纯数字
                        d1 = datetime.strptime(weibo['post_time'], '%Y-%m-%d %H:%M:%S')  # 博文时间
                        d2 = datetime.strptime(dateEnd + ' 23:59:59', '%Y-%m-%d %H:%M:%S')  # 结束时间
                        d3 = datetime.strptime(dateStart + ' 00:00:00', '%Y-%m-%d %H:%M:%S')  # 开始时间
                        if d1 >= d3:
                            if d1 <= d2:#判断日期是否在指定范围内
                                if txtwb.find("全文") + 2 == len(txtwb):  # 利用微博博文进行判断是否结尾有“全文二字”
                                    caurl = scheme[scheme.find('mblogid=') + 8:scheme.find('mblogid=') + 17]
                                    base_urlx = 'https://m.weibo.cn/statuses/show?'  # 用于构造全文链接
                                    para = {
                                        'id': caurl,
                                    }
                                    second_url = base_urlx + urlencode(para)  # 进行url编码添加到地址结尾  连带页数
                                    print("url2:" + second_url)
                                    # print("weibo1:",weibo)
                                    yield scrapy.Request(second_url, callback=self.get_txt_page,meta={'weiboitem': weibo})#进行全文提取
                                else:
                                    weibo['content'] = pq(itemc.get('text')).text()  # 不需要对全文做处理直接获取text
                                    # print("weibo2_1:" , weibo)
                                    yield weibo

                        else:
                            continue

            else:
                continue

    def get_txt_page(self, response):#获取全文内容
        weibo = response.meta['weiboitem']
        # print("response.text",response.text)
        txtitem = json.loads(response.text).get('data').get('text')
        weibo['content'] = pq(txtitem).text()  # 用pyquery去处理得到的数据
        time.sleep(random.random())
        # print("weibo2_2:", weibo)
        yield weibo

    # @staticmethod
    # def convert_chinese_number(number_str):
    #     if '万' in number_str:
    #         number_str = number_str.replace('万', '')
    #         return float(number_str) * 10000
    #     else:
    #         return int(number_str)

    @staticmethod
    def convert_chinese_number(number_str):
        try:
            if '万' in number_str:
                number_str = number_str.replace('万', '')
                return int(float(number_str) * 10000)
            else:
                return int(number_str)
        except ValueError:
            print(f"Error converting '{number_str}' to integer.")
            return 0