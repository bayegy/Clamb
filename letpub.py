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
import urllib3
from selenium import webdriver


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
        self.headforget['Upgrade-Insecure-Requests'] = '1'
        option = webdriver.FirefoxOptions()
        option.set_headless()
        self.driver = webdriver.Firefox(firefox_options=option)
        self.ipchanger = self.changeip()
        self.proxy = self.ipchanger.__next__()
        self.keys = self.getkey()

    def getkey(self):
        # self.driver.get('http://www.letpub.com.cn/index.php?page=grant')
        res = requests.get(url="http://www.letpub.com.cn/index.php?page=grant", headers=self.header, proxies=self.proxy)
        #res = self.driver.page_source
        tree = html.fromstring(res.content)
        key = tree.xpath('//select[@name="addcomment_s1"]/option/@value')
        subkey = tree.xpath('//select[@name="subcategory"]/option/@value')
        # print(res.content)
        key.remove("0")
        subkey.remove("")
        return([key, subkey])

    def changeip(self):
        while True:
            self.driver.get('http://www.goubanjia.com/')
            res = self.driver.page_source
            tree = html.fromstring(res)
            ipnode = tree.xpath("//td[@class='ip']")
            ips = []
            for ipdn in range(len(ipnode)):
                ip = ipnode[ipdn].xpath("*[not(@style='display:none;' or @style='display: none;')]/text()")
                ip = "".join(ip[0:-1]) + ":" + ip[-1]
                ips.append(ip)
            # ip2=tree.xpath("//td[@class='ip']//text()")
            ln = len(ips)
            tp = np.array(tree.xpath("//tbody/tr/td[not(@class='ip')]/a/text()")).reshape(ln, 6)
            for n in range(ln):
                if tp[n, 0] == '高匿' and tp[n, 1] == 'http':
                    ipout = {}
                    ipout['http'] = "http://" + ips[n]
                    yield(ipout)

    def formdict(self, file, sep):
        d = {}
        for line in open(file, "r", encoding='utf-8'):
            line = re.sub('\n$', '', line)
            if not re.search("  $", line):
                li = re.split(sep, line)
                d[li[0]] = li[1]
        return(d)

    def checkid(self, search_id, endyear=False):
        time.sleep(3 + random.randint(4, 10))
        name, year, page, key, subkey = re.split('_', search_id)
        tm = 0
        while True:
            tm += 1
            if tm > 20:
                print("Max retry, please check your code")
                break
            try:
                if not endyear:
                    endyear = year
                res = requests.get(url='http://www.letpub.com.cn/index.php?page=grant&name=%s&person=&no=&company=&startTime=%s&endTime=%s&money1=&money2=&subcategory=%s&addcomment_s1=%s&addcomment_s2=0&addcomment_s3=0&currentpage=%s#fundlisttable' %
                                   (name, year, endyear, subkey, key, page), headers=self.headforget, proxies=self.proxy)
                tree = html.fromstring(res.content)
                totalpage = tree.xpath('//center/div/text()')[0]
                break
            except TimeoutError:
                print("TimeoutError, please wait for 3 seconds")
                time.sleep(3)
            except ConnectionError:
                print("ConnectionError, please wait for 3 seconds")
                time.sleep(3)
            except:
                self.proxy = self.ipchanger.__next__()
                print("Changed ip location to %s" % (self.proxy['http']))

        pages = int(re.search('共(\d+)页', totalpage).group(1))
        records = int(re.search('(\d+)条记录', totalpage).group(1))
        if 0 < pages <= 50:
            print([pages, records])
            return([pages, records])
        elif pages > 50:
            print([False, records])
            return([False, records])
        else:
            print([-1, records])
            return([-1, records])

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
        time.sleep(3 + random.randint(4, 10))
        search_id = '_'.join([name, year, page, key, subkey])
        tm = 0
        while True:
            tm += 1
            if tm > 20:
                print("Max retry, please check your code")
                break
            try:
                if not endyear:
                    endyear = year
                res = requests.get(url='http://www.letpub.com.cn/index.php?page=grant&name=%s&person=&no=&company=&startTime=%s&endTime=%s&money1=&money2=&subcategory=%s&addcomment_s1=%s&addcomment_s2=0&addcomment_s3=0&currentpage=%s#fundlisttable' %
                                   (name, year, endyear, subkey, key, page), headers=self.headforget, proxies=self.proxy)
                tree = html.fromstring(res.content)
                out1 = tree.xpath('//td[@colspan="6"]')
                out1 = self.get_alltxt(out1)
                del out1[0]
                break
            except TimeoutError:
                print("TimeoutError, please wait for 2 seconds")
                time.sleep(3)
            except ConnectionError:
                print("ConnectionError, please wait for 2 seconds")
                time.sleep(3)
            except:
                self.proxy = self.ipchanger.__next__()
                print("Changed ip location to %s" % (self.proxy['http']))

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
        print(out)
        return(out)

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
                                if not is_subclass:
                                    is_subclass = 50
                                    outff.write('Total page out of range, please check searching id:\t%s_%s__%s_%s' % (
                                        name, year, key, subkey))
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


if __name__ == '__main__':
    myhub = letpub(header='header_for_letpub.txt')
    try:
        myhub.main(name=sys.argv[1])
    finally:
        myhub.driver.quit()
