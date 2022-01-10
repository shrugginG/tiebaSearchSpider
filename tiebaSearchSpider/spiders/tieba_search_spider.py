# -*- coding = utf-8 -*-
# @Time : 2021/12/24 14:18
# @Author: shrgginG
# @File : baidu_spider.py
# @Software: PyCharm
import os.path
from copy import deepcopy

import scrapy
import sys
from tiebaSearchSpider.items import TiebaItem
from scrapy.utils.project import get_project_settings
import tiebaSearchSpider.utils.util as util


class TiebaSearchSpider(scrapy.Spider):
    name = 'tieba-search'
    allowed_domains = ['tieba.baidu.com', 'tiebapic.baidu.com']
    settings = get_project_settings()
    keyword_list = settings.get('KEYWORD_LIST')
    if not isinstance(keyword_list, list):
        if not os.path.isabs(keyword_list):
            keyword_list = os.getcwd() + os.sep + keyword_list
        if not os.path.isfile(keyword_list):
            sys.exit('不存在%s文件' % keyword_list)
        keyword_list = util.get_keyword_list(keyword_list)
    # print(keyword_list)
    # keyword = input("请输入搜索关键字：")

    # 这里是微博话题的搜索并不适用于贴吧
    # for i, keyword in enumerate(keyword_list):
    #     if len(keyword) > 2and keyword[0]=='#'and keyword[-1]=='#':
    #         keyword_list[i] = '%23' + keyword[1:-1] + '%23'
    sorted_type = util.convert_sorted_type(settings.get('SORTED_TYPE'))
    base_url = 'https://tieba.baidu.com'

    # keyword = keyword_list[0]
    # page_num = int(input("请输入要爬取的网页数量："))
    base_site = 'https://tieba.baidu.com'
    num = 0
    page = 1

    # priority = 10000
    # print("您当前的页码为：" + str(page))

    def start_requests(self):
        for keyword in self.keyword_list:
            base_url = 'https://tieba.baidu.com/f/search/res?ie=utf-8&qw=%s' % keyword
            url = base_url + self.sorted_type
            yield scrapy.Request(url=url,
                                 callback=self.parse,
                                 meta={
                                     'base_url': base_url,
                                     'keyword': keyword
                                 })

    def parse(self, response):
        base_url = response.meta.get('base_url')
        keyword = response.meta.get('keyword')
        is_empty = response.xpath('//div[@class="search_noresult"]')
        page_num = response.xpath('//span[@class="cur"]/text()').get()
        print("当前爬虫所在页码：" + page_num)
        if is_empty:
            print('当前页面搜索结果为空！')
        else:
            for post in self.parse_post(response):
                yield post
            next_url = response.css(".pager .next::attr(href)").extract_first()
            if next_url:
                next_url = self.base_url + next_url
                yield scrapy.Request(url=next_url,
                                     callback=self.parse,
                                     meta={'keyword': keyword})

    # def parse_page(self, response):
    #     # TODO: 这个函数貌似没有存在的必要
    #     """解析一页搜索结果的信息"""
    #     keyword = response.meta.get('keyword')
    #     is_empty = response.xpath('//div[@class="search_noresult"]')
    #     if is_empty:
    #         print('当前页面搜索结果为空！')
    #     else:
    #         for post in self.parse_post(response):
    #             yield post
    #         next_url = response.css(".pager .next::attr(href)").extract_first()
    #         if next_url:
    #             next_url = self.base_url + next_url
    #             yield scrapy.Request(url=next_url,
    #                                  callback=self.parse_page,
    #                                  meta={'keyword': keyword})

    def parse_post(self, response):
        """解析网页中的帖子信息"""
        keyword = response.meta.get('keyword')
        for sel in response.xpath("//div[@class='s_post']"):
            tieba = TiebaItem()

            title = ""
            for i in sel.css(".p_title a ::text").extract():
                title += i
            tieba['title'] = title.strip()

            digest = ""
            for i in sel.css(".p_content::text").extract():
                digest += i
            tieba['digest'] = digest.strip()

            tieba['source_tieba'] = sel.css(".p_violet::text").extract()[0]

            try:
                author_id = sel.css(".p_violet::text").extract()[1]
            except IndexError as e:
                author_id = ""
                print("作者ID为空！")
            tieba['author_id'] = author_id
            tieba['latest_reply_datetime'] = sel.css(".p_date::text").extract_first()
            visit_url = 'https://tieba.baidu.com' + sel.css("a").attrib["href"]
            tieba['visit_url'] = visit_url
            yield scrapy.Request(url=visit_url, callback=self.parse_detail,
                                 meta={"tieba_item": tieba,
                                       "keyword": keyword,
                                       "post_url": visit_url})

            # print(tieba)
            # yield {"tieba_item": tieba, "keyword": keyword}

        # def parse(self, response):
        #     # for a in response.xpath('/html/body/div[3]/div/div[2]/div[3]/div[3]/div[1]'):
        #     for a in response.css(".s_post"):
        #         self.num += 1
        #         print("正在爬取第{}个网页".format(self.num))
        #         # 判断self.num是否超过self.page_num
        #         if self.num <= self.page_num:
        #             tieba_item = TiebaItem()
        #             title = ""
        #             for i in a.css(".p_title a ::text").extract():
        #                 title += i
        #             digest = ""
        #             for i in a.css(".p_content::text").extract():
        #                 digest += i
        #             source_tieba = a.css(".p_violet::text").extract()[0]
        #             try:
        #                 author_id = a.css(".p_violet::text").extract()[1]
        #             except IndexError as e:
        #                 author_id = ""
        #                 print("作者ID为空！")
        #             latest_reply_datetime = a.css(".p_date::text").extract_first()
        #             url = 'https://tieba.baidu.com' + a.css("a").attrib["href"]
        #             tieba_item['title'] = title.strip()
        #             tieba_item['digest'] = digest.strip()
        #             tieba_item['source_tieba'] = source_tieba
        #             tieba_item['author_id'] = author_id
        #             tieba_item['latest_reply_datetime'] = latest_reply_datetime
        #             tieba_item['visit_url'] = url
        #             tieba_item['image_urls'] = []
        #
        #             # yield tieba_item
        #             # self.priority -= 1
        #             yield scrapy.Request(response.urljoin(url), callback=self.post_parse,
        #                                  meta={"tieba_item": deepcopy(tieba_item), "num": deepcopy(self.num)})
        #
        #         else:
        #             sys.exit(0)
        #
        #     # 获取下一页
        #     next_page_url = self.base_site + response.xpath(
        #         '//*[@id="page"]/div/a[10]/@href').extract_first()
        #
        #     next_page_url = self.base_site + response.css(".pager .next::attr(href)").extract_first()
        #     print("下一页链接为：" + next_page_url)
        #     # self.priority -= 1
        #     yield scrapy.Request(next_page_url, callback=self.parse)
        #     self.page += 1
        #     print("您当前所在页码：:" + str(self.page))

        # def post_parse(self, response):
        #     print("正在爬取第{}个页面的详情内容".format(response.meta["num"]))
        #     tieba_item = response.meta["tieba_item"]
        #     reply_list = []
        #     for a in response.css(".p_postlist .l_post"):
        #         content = ""
        #         for i in a.css(".d_post_content::text"):
        #             content += i.extract().strip()
        #         reply_list.append(content)
        #     tieba_item['reply_list'] = str(reply_list)
        #     tieba_item['image_urls'] = response.css(".BDE_Image::attr(src)").extract()
        #     yield {"tieba_item": tieba_item, "keyword": self.keyword}

    def parse_detail(self, response):
        post_url = response.meta.get('post_url')
        keyword = response.meta.get('keyword')
        tieba = response.meta.get('tieba_item')
        print("正在爬取%s的详细内容" % post_url)

        reply_list = []
        for a in response.css(".p_postlist .l_post"):
            content = ""
            for i in a.css(".d_post_content::text"):
                content += i.extract().strip()
            reply_list.append(content)
        tieba['reply_list'] = str(reply_list)
        tieba['image_urls'] = response.css(".BDE_Image::attr(src)").extract()
        print(tieba)
        yield {"tieba_item": tieba, "keyword": keyword}
