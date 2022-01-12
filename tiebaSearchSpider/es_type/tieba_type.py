# -*- coding = utf-8 -*-
# @Time : 2022/1/10 20:56
# @Author: shrgginG
# @File : TiebaType.py
# @Software: PyCharm

from elasticsearch_dsl import *
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts="127.0.0.1")


class TiebaType(Document):
    title = Text(analyzer="ik_max_word")
    digest = Text(analyzer="ik_max_word")
    source_tieba = Keyword()
    author_id = Keyword()
    latest_reply_datetime = Date()  # 发帖时间
    visit_url = Keyword()  # 链接地址
    reply_list = Text(analyzer="ik_max_word")
    image_urls = Keyword()
    image_paths = Keyword()

    class Index:
        name = 'tieba_phishing'


if __name__ == '__main__':
    TiebaType.init()
