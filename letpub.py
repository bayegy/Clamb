# -*-coding:utf-8-*-
from bs4 import BeautifulSoup
from lxml import html
import requests
import re
import sys
import time
import math
import random
import numpy as np


class letpub(object):
    """docstring for weipu"""

    def __init__(self, header):
        self.header = self.formdict(file=header, sep=': +')
        self.header['Connection'] = 'close'
        self.headforget = {}
        self.headforget['Host'] = self.header['Host']
        self.headforget['User-Agent'] = self.header['User-Agent']
        #self.headforget['Referer'] = self.header['Referer']
        self.headforget['Connection'] = 'close'
        self.keys = self.getkey()

    def getkey(self):
        res = requests.get(url='http://www.letpub.com.cn/index.php?page=grant')
        tree = html.fromstring(res.content)
        key = tree.xpath('//select[@name="addcomment_s1"]/option/@value')
        subkey = tree.xpath('//select[@name="subcategory"]/option/@value')
        key.remove("0")
        subkey.remove("")
        return([key, subkey])

    def formdict(self, file, sep):
        d = {}
        for line in open(file, "r", encoding='utf-8'):
            line = re.sub('\n$', '', line)
            if not re.search("  $", line):
                li = re.split(sep, line)
                d[li[0]] = li[1]
        return(d)

    def checkid(self, search_id, endyear=False):
        time.sleep(1 + random.randint(1, 4))
        name, year, page, key, subkey = re.split('_', search_id)
        while True:
            try:
                if endyear:
                    res = requests.get(url='http://www.letpub.com.cn/index.php?page=grant&name=%s&person=&no=&company=&startTime=%s&endTime=%s&money1=&money2=&subcategory=%s&addcomment_s1=%s&addcomment_s2=0&addcomment_s3=0&currentpage=%s#fundlisttable' %
                                       (name, year, endyear, subkey, key, page), headers=self.header)
                else:
                    res = requests.get(url='http://www.letpub.com.cn/index.php?page=grant&name=%s&person=&no=&company=&startTime=%s&endTime=%s&money1=&money2=&subcategory=%s&addcomment_s1=%s&addcomment_s2=0&addcomment_s3=0&currentpage=%s#fundlisttable' %
                                       (name, year, year, subkey, key, page), headers=self.header)
                tree = html.fromstring(res.content)
                tree = html.fromstring(res.content)
                totalpage = tree.xpath('//center/div/text()')[0]
                pages = int(re.search('共(\d+)页', totalpage).group(1))
                records = int(re.search('(\d+)条记录', totalpage).group(1))
                if pages <= 50:
                    return([pages, records])
                else:
                    return([False, records])
            except TimeoutError:
                print("TimeoutError, please wait for 2 seconds")
                time.sleep(2)
            except ConnectionError:
                print("ConnectionError, please wait for 2 seconds")
                time.sleep(2)
            except ConnectionAbortedError:
                print("ConnectionAbortedError, please wait for 2 seconds")
                time.sleep(2)

    def get_alltxt(self, xpath_out):
        outa = []
        for ne in range(len(xpath_out)):
            el = xpath_out[ne].xpath('text()')
            if el:
                el = el[0]
            else:
                el = ""
            outa.append(el)
        return(outa)

    def get_info(self, name="微生", year="2012", endyear=False, page="1", key="0", subkey=""):
        time.sleep(1 + random.randint(1, 4))
        search_id = '_'.join([name, year, page, key, subkey])
        while True:
            try:
                if endyear:
                    res = requests.get(url='http://www.letpub.com.cn/index.php?page=grant&name=%s&person=&no=&company=&startTime=%s&endTime=%s&money1=&money2=&subcategory=%s&addcomment_s1=%s&addcomment_s2=0&addcomment_s3=0&currentpage=%s#fundlisttable' %
                                       (name, year, endyear, subkey, key, page), headers=self.header)
                else:
                    res = requests.get(url='http://www.letpub.com.cn/index.php?page=grant&name=%s&person=&no=&company=&startTime=%s&endTime=%s&money1=&money2=&subcategory=%s&addcomment_s1=%s&addcomment_s2=0&addcomment_s3=0&currentpage=%s#fundlisttable' %
                                       (name, year, year, subkey, key, page), headers=self.header)
                tree = html.fromstring(res.content)

                out1 = tree.xpath('//td[@colspan="6"]')
                out1 = self.get_alltxt(out1)
                #out1.remove(' ')
                del out1[0]
                out1 = np.array(out1).reshape(int(len(out1) / 2), 2, order='C')

                out2 = tree.xpath('//tr[@style="background:#EFEFEF;"]/td')
                out2 = self.get_alltxt(out2)
                ln = int(len(out2) / 7)
                out2 = np.array(out2).reshape(ln, 7, order='C')
                ap = np.array(ln * [search_id])
                ap.shape = ln, 1
                out = np.append(out1, out2, axis=1)
                out = np.append(out, ap, axis=1)
                out = out.tolist()
                return(out)
            except TimeoutError:
                print("TimeoutError, please wait for 2 seconds")
                time.sleep(2)
            except ConnectionError:
                print("ConnectionError, please wait for 2 seconds")
                time.sleep(2)
            except ConnectionAbortedError:
                print("ConnectionAbortedError, please wait for 2 seconds")
                time.sleep(2)

    def main(self, name, year_range=(2012, 2018)):
        outpath = name + '_project_leader.xls'
        try:
            with open(outpath, 'r', encoding='utf-8') as prefile:
                prepmid = []
                for line in prefile:
                    prepmid.append(re.search('\t([^\t\n]+)$', line).group(1).strip())

        except FileNotFoundError:
            prepmid = []

        with open(outpath, 'a', encoding='utf-8') as outff:
            if not prepmid:
                outff.write('题目\t学科分类\t负责人\t单位\t金额(万)\t项目编号\t项目类型\t所属学部\t批准年份\t查询编码\n')
            print('Start to get leader information......')
            d = len(prepmid)
            td = self.checkid(search_id='%s_%s_1_0_' % (name, year_range[0]), endyear=year_range[1])[1]
            for year in range(year_range[0], year_range[1] + 1):
                isok = self.checkid(search_id='%s_%s_1_0_' % (name, year))[0]
                if isok:
                    if isok > 0:
                        for page in range(1, isok + 1):
                            if '%s_%s_%s_0_' % (name, str(year), str(page)) not in prepmid:
                                found_info = self.get_info(name=name, year=str(year), page=str(page))
                                for rd in found_info:
                                    fd = '\t'.join(rd)
                                    outff.write(fd + '\n')
                                d = d + len(found_info)
                                perctg = 100 * d / td
                                done = int(50 * d / td)
                                sys.stdout.write("\r[%s%s] %.3f%%" % ('█' * done, ' ' * (50 - done), perctg))
                                sys.stdout.flush()
                else:
                    for key in self.keys[0]:
                        is_class = self.checkid(search_id='%s_%s_1_%s_' % (name, year, key))[0]
                        if is_class:
                            if is_class > 0:
                                for page in range(1, is_class + 1):
                                    if '%s_%s_%s_%s_' % (name, str(year), str(page), key) not in prepmid:
                                        found_info = self.get_info(name=name, year=str(year), page=str(page), key=key)
                                        for rd in found_info:
                                            fd = '\t'.join(rd)
                                            outff.write(fd + '\n')
                                        d = d + len(found_info)
                                        perctg = 100 * d / td
                                        done = int(50 * d / td)
                                        sys.stdout.write("\r[%s%s] %.3f%%" % ('█' * done, ' ' * (50 - done), perctg))
                                        sys.stdout.flush()
                        else:
                            for subkey in self.keys[1]:
                                is_subclass = self.checkid(search_id='%s_%s_1_%s_%s' % (name, year, key, subkey))[0]
                                if is_subclass:
                                    if is_subclass > 0:
                                        for page in range(1, is_subclass + 1):
                                            if '%s_%s_%s_%s_%s' % (name, str(year), str(page), key, subkey) not in prepmid:
                                                found_info = self.get_info(
                                                    name=name, year=str(year), page=str(page), key=key, subkey=subkey)
                                                for rd in found_info:
                                                    fd = '\t'.join(rd)
                                                    outff.write(fd + '\n')
                                                d = d + len(found_info)
                                                perctg = 100 * d / td
                                                done = int(50 * d / td)
                                                sys.stdout.write("\r[%s%s] %.3f%%" %
                                                                 ('█' * done, ' ' * (50 - done), perctg))
                                                sys.stdout.flush()
                                else:
                                    outff.write('Total page out of range, please check searching id: %s_%s_1_%s_%s' % (
                                        name, year, key, subkey))


if __name__ == '__main__':
    myhub = letpub(header='header_for_letpub.txt')
    myhub.main(name=sys.argv[1])
