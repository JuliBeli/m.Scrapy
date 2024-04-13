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
from weibom.items import WeibomItem

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

#host用于指定internet主机和端口号，http1.1必须包含，不然系统返回400，


sign=0      #标志是否找到了实时微博以开始

class Weibom_spider(scrapy.Spider):
    name = "weibom_spider"
    headers = {                 #封装请求头  让网站识别自己是浏览器
        'Referer': m_referer+urlsearch,             #告诉服务器自己是哪里来的  从那个页面来的   来路
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 Edg/80.0.361.111',    #包含操作系统和浏览器信息
        'Host':'m.weibo.cn',                #请求服务器的域名和端口号
        'X-Requested-With':'XMLHttpRequest'             #代表是ajax请求
    }
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
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)
            page=int(page)+1
            time.sleep(random.random()+1)
            # print(page)

        # try:
        #     response = requests.get(url, headers=headers)  # request请求  地址和携带请求头
        #     if response.status_code == 200:
        #         return response.json()  # 以json格式返回数据
        # except requests.ConnectionError as e:
        #     print("Error:", e.args)

    # 分析JSON格式的数据，抓取目标信息
    def parse(self,response):
        global sign  # sign是用来标记是否有过title   在格式中从实时微博进行爬取  找到实时微博title之后开始爬取   之后不用进行判断title而用sign来判断
        print(response)
        items = response.json().get('data').get('cards')
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
                        if txtwb.find("全文") + 2 == len(txtwb):  # 利用微博博文进行判断是否结尾有“全文二字”
                            caurl=scheme[scheme.find('mblogid=')+8:scheme.find('mblogid=')+17],scheme
                            datatxt = self.get_txt_page(self,caurl)
                            # 如果有全文那么需要进入其中再次进行爬取全文数据，首先切割链接获取mblogid，scheme对应的是Referer的链接信息
                            # print("datatext=",datatxt)
                            try:
                                txtitem = pq(datatxt.get('data').get('text')).text()
                                weibo['content'] = pq(datatxt.get('data').get('text')).text()  # 用pyquery去处理得到的数据
                            except:
                                pass
                        else:
                            weibo['content'] = pq(itemc.get('text')).text()  # 不需要对全文做处理直接获取text
                        weibo['post_time'] = str(datetime.strptime(pq(itemc.get('created_at')).text(),
                                                                  '%a %b %d %H:%M:%S +0800 %Y'))  # 日期   #修改日期格式   默认微博日期格式是带时区的GMT的格式
                        weibo['thumbs_up'] = itemc.get('attitudes_count')  # 点赞次数
                        weibo['comments'] = itemc.get('comments_count')  # 评论次数
                        weibo['reposts'] = itemc.get('reposts_count')  # 转发次数
                        weibo['userid'] = itemc.get('user').get('id')  # 发布人id
                        weibo['username'] = itemc.get('user').get('screen_name')  # 发布人微博名

                        weibo['user_gender'] = itemc.get('user').get('gender')  # 发布人性别
                        weibo['user_followers'] = itemc.get('user').get('followers_count_str')  # 发布人粉丝数

                        d1 = datetime.strptime(weibo['post_time'], '%Y-%m-%d %H:%M:%S')  # 博文时间
                        d2 = datetime.strptime(dateEnd + ' 23:59:59', '%Y-%m-%d %H:%M:%S')  # 结束时间
                        d3 = datetime.strptime(dateStart + ' 00:00:00', '%Y-%m-%d %H:%M:%S')  # 开始时间
                        if d1 >= d3:
                            if d1 <= d2:
                                yield weibo
                                print("result:", weibo)

                                # save_data_toexcel(result, savepath)
                        else:
                            continue

                        # 一个一个返回weibo
                        # print("weibo=",weibo)
                        # for key in weibo:
                        #     print(key + ':', weibo[key])
                        # print(weibo)


            else:
                continue

    def get_txt_page(self,containerid, referer):
        base_urlx = 'https://m.weibo.cn/statuses/show?'  # 相较于获取搜索结果的url不通
        txtheaders = {
            'Referer': referer,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 Edg/80.0.361.111',
            'Host': 'm.weibo.cn',
            'X-Requested-With': 'XMLHttpRequest'
        }
        para = {
            'id': containerid,  # 只需要一个参数  且参数名为id
        }
        url = base_urlx + urlencode(para)  # 进行url编码添加到地址结尾  连带页数
        try:
            response = requests.get(url, headers=self.headers)  # request请求  地址和携带请求头
            if response.status_code == 200:
                return response.json()  # 以json格式返回数据
        except requests.ConnectionError as e:
            print("Error:", e.args)

    def parse2(self, response):
        pass
    # def main(self): # main函数
    #     ini_book()
    #     page = strat_page  # 页数  从第一页开始  也是需要传入的一个参数
    #     while page <= int(end_page):
    #         data = get_page(page)  # 获取网页的json格式的数据
    #         results = parse_json(data)  # 解析网页的json数据
    #         for result in results:  # 循环去便利数据
    #
    #             d1 = datetime.strptime(result['date'], '%Y-%m-%d %H:%M:%S')  # 博文时间
    #             d2 = datetime.strptime(dateEnd + ' 23:59:59', '%Y-%m-%d %H:%M:%S')  # 结束时间
    #             d3 = datetime.strptime(dateStart + ' 00:00:00', '%Y-%m-%d %H:%M:%S')  # 开始时间
    #
    #             if d1 >= d3:
    #                 if d1 <= d2:
    #                     print("result:", result)
    #                     save_data_toexcel(result, savepath)
    #             else:
    #                 continue
    #         print('第' + str(page) + '页抓取完成')
    #         time.sleep(random.random() * 4 + 1)
    #         page += 1
    #     print('全部网页抓取完成')



