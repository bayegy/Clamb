# -*-coding:utf-8-*-
from bs4 import BeautifulSoup
from lxml import html
import requests
import re
import sys
import time
import math
import random


class weipu(object):
    """docstring for weipu"""

    def __init__(self, keyword, header):
        self.keyword = keyword
        self.header = self.formdict(file=header, sep=': +')
        self.header['Connection'] = 'close'
        self.headforget = {}
        self.headforget['Host'] = self.header['Host']
        self.headforget['User-Agent'] = self.header['User-Agent']
        self.headforget['Referer'] = self.header['Referer']
        self.headforget['Connection'] = 'close'
        f_page = requests.get(
            url='http://qikan.cqvip.com/zk/search.aspx?from=article_detail&key=U%3D' + self.keyword, headers=self.header)
        tree = html.fromstring(f_page.content)
        totalpage = tree.xpath('//span[@class="total"]/text()')[0]
        print(totalpage)
        self.totalpage = int(re.sub(",", "", re.search("[\d|,]+", totalpage).group()))

    def get_id(self, page):
        while True:
            try:
                res = requests.get(
                    url='http://qikan.cqvip.com/zk/search.aspx?from=zk_search&key=U%3D' +
                        self.keyword + '&page=' + str(page) + '&size=50&ls=1#search-result-list',
                    # url='http://qikan.cqvip.com/zk/search.aspx?from=zk_search&key=U%3D%E5%BE%AE%E7%94%9F%E7%89%A9&page=2&size=50&ls=1#search-result-list',
                    headers=self.header)
                tree = html.fromstring(res.content)
                id_set = tree.xpath(
                    '//input[@name="vcubeid"]/@value')
                id_set = [id.strip() for id in id_set]
                if id_set:
                    return(id_set)
                else:
                    print('Loading Error, please wait to 1 second')
                    time.sleep(1)

            except TimeoutError:
                print('TimeoutError, please wait for 2 seconds')
                time.sleep(2)
        # print(res.text)

    def formdict(self, file, sep):
        d = {}
        for line in open(file, "r", encoding='utf-8'):
            line = re.sub('\n$', '', line)
            if not re.search("  $", line):
                li = re.split(sep, line)
                d[li[0]] = li[1]
        return(d)

    def get_info(self, id):
        while True:
            try:
                res = requests.get(url='http://qikan.cqvip.com/article/detail.aspx?id=%s&from=zk_search' %
                                   (str(id)), headers=self.headforget)
                tree = html.fromstring(res.content)
                title = tree.xpath('//h1/text()')[0].strip()
                if title:
                    break
                else:
                    print('Loading Error, please wait for 1 second')
                    time.sleep(1)
            except TimeoutError:
                print("TimeoutError, please wait for 2 seconds")
                time.sleep(2)

        author = tree.xpath('//p[@class="author"]/a/text()')
        author_s = tree.xpath('//p[@class="author"]/span/a/text()')
        author = author + author_s

        if author:
            organ = tree.xpath('//p[@class="organ"]/a/text()')
            organ_s = tree.xpath('//p[@class="organ"]/span/a/text()')
            organ = organ + organ_s
            if not organ:
                organ = ""

            try:
                info = tree.xpath('//p[@class="abstrack"]/text()')[1].strip()
                info = re.sub('[\n\r]+', '; ', info)
            except IndexError:
                info = ""
            cinfo = info

            info = re.sub("．", ".", info)
            info = re.split("通[讯|信]作者", info.strip())

            def findname(tar):
                for n in author:
                    if re.search(n, tar):
                        return(n)

            f_author = author[0].strip()
            if findname(info[0]):
                f_author = findname(info[0])

            m_author = '无法判断'
            try:
                if findname(info[1]):
                    m_author = findname(info[1])
            except IndexError:
                pass

            f_email = '无'
            if re.search('[a-zA-Z0-9_\-\+.．]+@[a-zA-Z0-9_\-\+.．]+', info[0]):
                f_email = re.search('[a-zA-Z0-9_\-\+.．]+@[a-zA-Z0-9_\-\+.．]+', info[0]).group()
                f_email = f_email.strip('.|．')

            m_email = '无'
            try:
                if re.search('[a-zA-Z0-9_\-\+.．]+@[a-zA-Z0-9_\-\+.．]+', info[1]):
                    m_email = re.search('[a-zA-Z0-9_\-\+.．]+@[a-zA-Z0-9_\-\+.．]+', info[1]).group()
                    m_email = m_email.strip('.|．')
            except IndexError:
                pass

            return('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (f_email, f_author, m_email, m_author, ';'.join(author), cinfo, ';'.join(organ), title))
        else:
            return('无\t无\t无\t无\t无\t无\t无\t%s' % (title))

            # print(res.content)

    def main(self):
        outpath = self.keyword + '_author_infomation.xls'
        try:
            with open(outpath, 'r', encoding='utf-8') as prefile:
                prepmid = []
                for line in prefile:
                    prepmid.append(re.search('\t([^\t\n]+)$', line).group(1).strip())

        except FileNotFoundError:
            prepmid = []

        print('Start to get paper id')
        pmid_list = []
        for p in range(self.totalpage):
            print('get id of page' + str(p + 1))
            pmid_list = pmid_list + self.get_id(page=p + 1)
            time.sleep(random.randint(1, 3))

        totalpaper = len(pmid_list)
        print('Total %s id got' % (str(totalpaper)))

        with open(outpath, 'a', encoding='utf-8') as outff:
            if not prepmid:
                outff.write('作者邮箱\t作者\t通讯作者邮箱\t通讯作者\t所有作者\t所有作者信息\t作者机构\t文章标题\t文章ID\n')
            print('Start to get author information......')
            d = 0
            for perid in pmid_list:
                d = d + 1
                perctg = 100 * d / totalpaper
                done = int(50 * d / totalpaper)
                sys.stdout.write("\r[%s%s] %.3f%%" % ('█' * done, ' ' * (50 - done), perctg))
                sys.stdout.flush()
                if perid not in prepmid:
                    info = self.get_info(id=perid)
                    info = info + '\t' + perid + '\n'
                    outff.write(info)
                    time.sleep(2 + random.randint(1, 4))


if __name__ == '__main__':
    page = weipu(keyword=sys.argv[1], header='header.txt')
    page.main()
