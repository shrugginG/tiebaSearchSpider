# -*- coding = utf-8 -*-
# @Time : 2021/12/24 15:51
# @Author: shrgginG
# @File : run.py
# @Software: PyCharm

from scrapy import cmdline

cmdline.execute("scrapy crawl tieba-search".split())
