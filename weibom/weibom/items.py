# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class WeibomItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    userid = scrapy.Field()
    username = scrapy.Field()
    user_gender = scrapy.Field()
    user_followers = scrapy.Field()
    post_time = scrapy.Field()
    thumbs_up = scrapy.Field()
    comments = scrapy.Field()
    reposts = scrapy.Field()
    content = scrapy.Field()


