# -*- coding = utf-8 -*-
# @Time : 2021/12/24 14:18
# @Author: shrgginG
# @File : baidu_spider.py
# @Software: PyCharm
from copy import deepcopy

import scrapy
import sys
from tiebaSearchSpider.items import TiebaItem


class tiebaSearchSpider(scrapy.Spider):
    name = 'tieba-search'
    allowed_domains = ['tieba.baidu.com', 'tiebapic.baidu.com']
    keyword = input("请输入搜索关键字：")
    page_num = int(input("请输入要爬取的网页数量："))
    start_urls = ['https://tieba.baidu.com/f/search/res?ie=utf-8&qw={}'.format(keyword)]
    base_site = 'https://tieba.baidu.com'
    num = 0
    page = 1
    # priority = 10000
    print("您当前的页码为：" + str(page))

    def parse(self, response):
        # for a in response.xpath('/html/body/div[3]/div/div[2]/div[3]/div[3]/div[1]'):
        for a in response.css(".s_post"):
            self.num += 1
            print("正在爬取第{}个网页".format(self.num))
            # 判断self.num是否超过self.page_num
            if self.num <= self.page_num:
                tieba_item = TiebaItem()
                title = ""
                for i in a.css(".p_title a ::text").extract():
                    title += i
                digest = ""
                for i in a.css(".p_content::text").extract():
                    digest += i
                source_tieba = a.css(".p_violet::text").extract()[0]
                try:
                    author_id = a.css(".p_violet::text").extract()[1]
                except IndexError as e:
                    author_id = ""
                    print("作者ID为空！")
                latest_reply_datetime = a.css(".p_date::text").extract_first()
                url = 'https://tieba.baidu.com' + a.css("a").attrib["href"]
                tieba_item['title'] = title.strip()
                tieba_item['digest'] = digest.strip()
                tieba_item['source_tieba'] = source_tieba
                tieba_item['author_id'] = author_id
                tieba_item['latest_reply_datetime'] = latest_reply_datetime
                tieba_item['visit_url'] = url
                tieba_item['image_urls'] = []

                # yield tieba_item
                # self.priority -= 1
                yield scrapy.Request(response.urljoin(url), callback=self.post_parse,
                                     meta={"tieba_item": deepcopy(tieba_item), "num": deepcopy(self.num)})

            else:
                sys.exit(0)

        # 获取下一页
        # next_page_url = self.base_site + response.xpath(
        #     '//*[@id="page"]/div/a[10]/@href').extract_first()

        next_page_url = self.base_site + response.css(".pager .next::attr(href)").extract_first()
        print("下一页链接为：" + next_page_url)
        # self.priority -= 1
        yield scrapy.Request(next_page_url, callback=self.parse)
        self.page += 1
        print("您当前所在页码：:" + str(self.page))

    def post_parse(self, response):
        print("正在爬取第{}个页面的详情内容".format(response.meta["num"]))
        tieba_item = response.meta["tieba_item"]
        reply_list = []
        for a in response.css(".p_postlist .l_post"):
            content = ""
            for i in a.css(".d_post_content::text"):
                content += i.extract().strip()
            reply_list.append(content)
        tieba_item['reply_list'] = str(reply_list)
        tieba_item['image_urls'] = response.css(".BDE_Image::attr(src)").extract()
        yield {"tieba_item": tieba_item, "keyword": self.keyword}
