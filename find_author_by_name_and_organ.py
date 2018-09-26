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

    def __init__(self, header):
        self.header = self.formdict(file=header, sep=': +')
        self.header['Connection'] = 'close'
        self.headforget = {}
        self.headforget['Host'] = self.header['Host']
        self.headforget['User-Agent'] = self.header['User-Agent']
        self.headforget['Referer'] = self.header['Referer']
        self.headforget['Connection'] = 'close'

    def get_id(self, page, keyword):
        tm = 0
        out = False
        while tm < 3:
            try:
                res = requests.get(
                    url='http://qikan.cqvip.com/zk/search.aspx?from=zk_search&key=' +
                        keyword + '&page=' + str(page) + '&size=50&ls=1#search-result-list',
                    # url='http://qikan.cqvip.com/zk/search.aspx?from=zk_search&key=U%3D%E5%BE%AE%E7%94%9F%E7%89%A9&page=2&size=50&ls=1#search-result-list',
                    headers=self.header)
                tree = html.fromstring(res.content)
                id_set = tree.xpath(
                    '//input[@name="vcubeid"]/@value')
                id_set = [id.strip() for id in id_set]
                try:
                    totalpage = tree.xpath('//span[@class="total"]/text()')[0]
                    totalpage = int(re.sub(",", "", re.search("[\d|,]+", totalpage).group()))
                except IndexError:
                    pass
                tm += 1
                out = [totalpage, id_set]
                if id_set:
                    return(out)
                else:
                    print('Loading Error, please wait to 1 second')
                    time.sleep(3)

            except TimeoutError:
                print('TimeoutError, please wait for 2 seconds')
                time.sleep(2)
        return(out)
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
        time.sleep(1 + random.randint(1, 4))
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

            return([f_email, f_author, m_email, m_author, ';'.join(author), cinfo, ';'.join(organ), title])
        else:
            return(False)

            # print(res.content)

    def formkeyword(self, table):
        keyword = []
        with open(table, 'r') as infile:
            for line in enumerate(infile):
                li = re.split('\t', line[1].strip('\n'))
                if line[0] == 0:
                    for w in enumerate(li):
                        if w[1].strip() == '负责人':
                            an = w[0]
                        elif w[1].strip() == '依托单位':
                            on = w[0]
                        elif w[1].strip() == '邮箱':
                            en = w[0]
                    # print(an)
                    # print(on)
                    # print(en)
                else:
                    keyword.append(['\t'.join(li), li[an], 'A%3D' + li[an], 'A%3D' +
                                    li[an] + '[*]' + 'S%3D' + li[on], li[en]])
        return(keyword)

    def main(self, table):
        outpath = table + '_search_for_email.xls'
        try:
            with open(outpath, 'r', encoding='utf-8') as prefile:
                prepmid = []
                for line in prefile:
                    prepmid.append(re.search('\t([^\t\n]+)$', line).group(1).strip())

        except FileNotFoundError:
            prepmid = []

        pre_table = self.formkeyword(table=table)
        with open(outpath, 'a', encoding='utf-8') as outff:
            if not prepmid:
                outff.write('跟进助理\t备注\t项目名\t负责人\t职称\t依托单位\t经费\t起始时间\t领域\t电话\t邮箱\t维普邮箱\t附加信息\n')
            print('Start to get author information......')
            d = 0
            for origin, name, short_key, long_key, pre_email in pre_table:
                d = d + 1
                perctg = 100 * d / len(pre_table)
                done = int(50 * d / len(pre_table))
                sys.stdout.write("\r[%s%s] %.3f%%" % ('█' * done, ' ' * (50 - done), perctg))
                sys.stdout.flush()
                if long_key not in prepmid:
                    finded_email = '无法找到邮箱'
                    if pre_email:
                        finded_email = pre_email
                    else:
                        page = 0
                        totalpage = 1
                        id_set = []
                        ifound = True
                        while page < totalpage and ifound:
                            page += 1
                            finded_id = self.get_id(page=page, keyword=long_key)
                            id_set = id_set + finded_id[1]
                            totalpage = finded_id[0]
                            ifound = finded_id
                        for eachid in id_set:
                            finded_info = self.get_info(id=eachid)
                            if finded_info:
                                if not finded_info[0] == '无' and name == finded_info[1]:
                                    finded_email = finded_info[0] + '\t' + finded_info[5]
                                    break
                                elif not finded_info[2] == '无' and name == finded_info[3]:
                                    finded_email = finded_info[2] + '\t' + finded_info[5]
                                    break
                        if finded_email == '无法找到邮箱':
                            page = 0
                            totalpage = 1
                            id_set = []
                            ifound = True
                            while page < totalpage and ifound:
                                page += 1
                                finded_id = self.get_id(page=page, keyword=short_key)
                                id_set = id_set + finded_id[1]
                                totalpage = finded_id[0]
                                ifound = finded_id
                            for eachid in id_set:
                                finded_info = self.get_info(id=eachid)
                                if finded_info:
                                    if not finded_info[0] == '无' and name == finded_info[1]:
                                        finded_email = finded_info[0] + '\t' + finded_info[5] + '\t' + '只根据名字查找'
                                        break
                                    elif not finded_info[2] == '无' and name == finded_info[3]:
                                        finded_email = finded_info[0] + '\t' + finded_info[5] + '\t' + '只根据名字查找'
                                        break
                outff.write('%s\t%s\t%s\n' % (origin, finded_email, long_key))


if __name__ == '__main__':
    page = weipu(header='header.txt')
    a = page.main(table=sys.argv[1])
