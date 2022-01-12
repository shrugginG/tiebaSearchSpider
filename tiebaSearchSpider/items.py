# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TiebaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()  # 链接标题
    digest = scrapy.Field()  # 内容摘要
    source_tieba = scrapy.Field()  # 来源贴吧
    author_id = scrapy.Field()  # 发帖人ID
    latest_reply_datetime = scrapy.Field()  # 发帖时间
    visit_url = scrapy.Field()  # 链接地址
    reply_list = scrapy.Field()  # 主题帖回复内容
    image_urls = scrapy.Field()
    image_paths = scrapy.Field()
