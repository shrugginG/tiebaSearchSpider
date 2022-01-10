# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import csv
import os

from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
import scrapy.pipelines
from itemadapter import ItemAdapter
import urllib.request


# 通过设置timeout参数用于解决ConnectionResetError问题
def getHtml(url):
    html = urllib.request.urlopen(url, timeout=10).read()
    return html


def saveHtml(file_name, file_content):
    with open('../../datas/html_files/' + file_name.replace('/', '_') + '.html', 'wb') as f:
        f.write(file_content)


class TiebaSearchPipeline:
    def process_item(self, item, spider):
        print(item)
        name = ''.join(item['title'])
        html = getHtml(item['visit_url'][0])
        saveHtml(name, html)
        print("该网页爬取结束")
        return item


class items_ToCSV(object):

    def process_item(self, item, spider):
        # os.seq根据不同的系统指定不同的文件分隔符
        base_dir = '../../results' + os.sep + item['keyword']
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)
        file_path = base_dir + os.sep + item['keyword'] + '.csv'
        if not os.path.isfile(file_path):
            is_first_write = 1
        else:
            is_first_write = 0
        if item:
            # TODO
            with open(file_path, 'a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                if is_first_write:
                    header = ["链接标题", "内容摘要", "来源贴吧", "最近回复用户名", "最近回复时间", "链接地址", "主题帖包含图片链接", "主题帖内容", "图片本地存储地址"]
                    writer.writerow(header)
                writer.writerow(
                    [item['tieba_item'][key] for key in item['tieba_item'].keys()])
        # 必须返回item，否则下一个pipeline无法接收到item
        return item


class ImgsPipline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if len(item['tieba_item']['image_urls']) == 1:
            yield scrapy.Request(item['tieba_item']['image_urls'][0],
                                 meta={
                                     'item': item,
                                     'sign': ''
                                 })
        else:
            sign = 0
            for image_url in item['tieba_item']['image_urls']:
                yield scrapy.Request(image_url,
                                     meta={
                                         'item': item,
                                         'sign': '-' + str(sign)
                                     })
                sign += 1

    def file_path(self, request, response=None, info=None):
        image_url = request.url
        item = request.meta['item']
        sign = request.meta['sign']
        base_dir = '../../results' + os.sep + item['keyword'] + os.sep + 'images'
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)
        image_suffix = image_url[image_url.rfind('.'):]
        file_path = base_dir + os.sep + item['tieba_item'][
            'author_id'] + sign + image_suffix
        return file_path

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        adapter = ItemAdapter(item)
        adapter['tieba_item']['image_paths'] = image_paths
        return item
