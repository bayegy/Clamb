# -*-coding:utf-8-*-
from bs4 import BeautifulSoup
from lxml import html
import requests
import re
import sys
import time
import math


class weipu(object):
    """docstring for weipu"""

    def __init__(self, keyword, header):
        self.keyword = keyword
        self.header = self.formdict(file=header, sep=': +')
        #self.form = self.formdict(file=form, sep='  ')
        #print(self.header)

    def get_id(self, page):
        while True:
            try:
                res = requests.get(
                    # url='http://qikan.cqvip.com/zk/search.aspx?from=zk_search&key=U%3D' + self.keyword + '&page=' + str(page) + '&size=50&ls=1#search-result-list',
                    url='http://qikan.cqvip.com/zk/search.aspx?from=zk_search&key=U%3D%E5%BE%AE%E7%94%9F%E7%89%A9&page=2&size=50&ls=1#search-result-list',
                    headers=self.header)
                break
            except TimeoutError:
                print('TimeoutError')
                time.sleep(2)
        print(res.text)
        tree = html.fromstring(res.content)
        id_set = tree.xpath(
            '//input[@name="hfldSelectedIds"]/@value')
        return(id_set)

    def formdict(self, file, sep):
        d = {}
        for line in open(file, "r", encoding='utf-8'):
            line = re.sub('\n$', '', line)
            if not re.search("  $", line):
                li = re.split(sep, line)
                d[li[0]] = li[1]
        return(d)


if __name__ == '__main__':
    page = weipu(keyword='微生物', header='header.txt')
    ids = page.get_id(page=1)
    #print(ids)
