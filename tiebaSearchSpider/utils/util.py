# -*- coding = utf-8 -*-
# @Time : 2022/1/6 14:21
# @Author: shrgginG
# @File : util.py
# @Software: PyCharm
import sys


def get_keyword_list(file_name):
    """Get the keyword list from the file."""
    with open(file_name, 'rb') as f:
        try:
            lines = f.read().splitlines()
            lines = [line.decode('utf-8-sig') for line in lines]
        except UnicodeDecodeError:
            print(u'%s文件应为utf-8编码，请先将文件编码转为utf-8再运行程序', file_name)
            sys.exit()
        keyword_list = []
        for line in lines:
            if line:
                keyword_list.append(line)
    return keyword_list


def convert_sorted_type(sorted_type):
    """将排序方式转换为字符串"""
    if sorted_type == 0:
        return '&sm=1'
    elif sorted_type == 1:
        return '&sm=0'
    elif sorted_type == 2:
        return '&sm=2'
    else:
        return '&sm=1&only_thread=1'
