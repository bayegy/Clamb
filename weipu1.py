# -*-coding:utf-8-*-
from bs4 import BeautifulSoup
from lxml import html
import requests
import re
import sys
import time
import math
import random
from selenium import webdriver
import numpy as np


class weipu(object):
    """docstring for weipu"""

    def __init__(self, keyword, header, year_range=(2013, 2018)):
        self.keyword = keyword
        self.year_range = year_range
        self.header = self.formdict(file=header, sep=': +')
        self.header['Connection'] = 'close'
        self.headforget = {}
        self.headforget['Host'] = self.header['Host']
        self.headforget['User-Agent'] = self.header['User-Agent']
        self.headforget['Connection'] = 'close'
        self.headforget['Upgrade-Insecure-Requests'] = '1'
        option = webdriver.FirefoxOptions()
        option.set_headless()
        self.driver = webdriver.Firefox(firefox_options=option)
        self.ipchanger = self.changeip()
        self.proxy = self.ipchanger.__next__()


#        paper = requests.get(url='http://qikan.cqvip.com/zk/search.aspx?from=zk_search&key=M%3D{}[*]YY%3D{}-{}'.format(
#            self.keyword, self.year_range[0], self.year_range[1]), headers=self.header, proxies=self.proxy, timeout=20)
#        tree = html.fromstring(paper.content)
#        print(paper.content)
#        totalpaper = tree.xpath('//div[@class="search-count"]/i/text()')
#        print(totalpaper)
#        print('共' + str(self.totalpaper) + '篇文章')

    def get_totalpage(self, year):
        time.sleep(3 + random.randint(0, 6))
        while True:
            try:
                f_page = requests.get(url='http://qikan.cqvip.com/zk/search.aspx?from=index&key=M%3D{}[*]YY%3D{}-{}&size=50&page=1&ls=1#search-result-list'.format(
                    self.keyword, year, year), headers=self.header, proxies=self.proxy, timeout=20)
                if f_page.status_code == 200:
                    tree = html.fromstring(f_page.content)
                    totalpage = tree.xpath('//span[@class="total"]/text()')[0]
                    print(str(year) + ':' + totalpage)
                    totalpage = int(re.sub(",", "", re.search("[\d|,]+", totalpage).group()))
                    return(totalpage)
                else:
                    raise(TimeoutError)
            except Exception as e:
                print(str(e))
                self.proxy = self.ipchanger.__next__()
                print("Changed ip location to %s" % (self.proxy['http']))

    def changeip(self):
        while True:
            try:
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
            except Exception as e:
                print('%s, tring another time' % (str(e)))
                time.sleep(3)

    def get_id(self, year, page):
        time.sleep(3 + random.randint(0, 6))
        while True:
            try:
                res = requests.get(
                    url='http://qikan.cqvip.com/zk/search.aspx?from=index&key=M%3D{}[*]YY%3D{}-{}&page={}&ls=1&size=50#search-result-list'.format(
                        self.keyword, year, year, page),
                    # url='http://qikan.cqvip.com/zk/search.aspx?from=zk_search&key=U%3D%E5%BE%AE%E7%94%9F%E7%89%A9&page=2&size=50&ls=1#search-result-list',
                    headers=self.header, timeout=20, proxies=self.proxy)
                if res.status_code == 200:
                    tree = html.fromstring(res.content)
                    id_set = tree.xpath(
                        '//input[@name="vcubeid"]/@value')
                    id_set = [id.strip() for id in id_set]
                    if id_set:
                        return(id_set)
                    else:
                        print('Could not found any ids, tring another time')
                        time.sleep(1)
                else:
                    raise(TimeoutError)

            except Exception as e:
                print(str(e))
                self.proxy = self.ipchanger.__next__()
                print("Changed ip location to %s" % (self.proxy['http']))
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
        time.sleep(3 + random.randint(0, 6))
        while True:
            try:
                res = requests.get(url='http://qikan.cqvip.com/article/detail.aspx?id=%s&from=zk_search' %
                                   (str(id)), headers=self.headforget, proxies=self.proxy, timeout=20)
                if res.status_code == 200:
                    tree = html.fromstring(res.content)
                    title = tree.xpath('//h1/text()')[0].strip()
                    if title:
                        break
                    else:
                        print('Loading problem, tring another time')
                        time.sleep(1)
                else:
                    raise(TimeoutError)
            except Exception as e:
                print(str(e))
                self.proxy = self.ipchanger.__next__()
                print("Changed ip location to %s" % (self.proxy['http']))

        author = tree.xpath('//p[@class="author"]/a/text()')
        author_s = tree.xpath('//p[@class="author"]/span/a/text()')
        author = author + author_s

        if author:
            author = [at.strip() for at in author]
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
                f_email = f_email.strip('\.|．')

            m_email = '无'
            try:
                if re.search('[a-zA-Z0-9_\-\+.．]+@[a-zA-Z0-9_\-\+.．]+', info[1]):
                    m_email = re.search('[a-zA-Z0-9_\-\+.．]+@[a-zA-Z0-9_\-\+.．]+', info[1]).group()
                    m_email = m_email.strip('\.|．')
            except IndexError:
                pass

            f_tel = '无'
            if re.search('Tel：([0-9\-—\+]+)', info[0]):
                f_tel = re.search('Tel：([0-9\-—\+]+)', info[0]).group(1)
                f_tel = f_tel.strip('\.|．|\-')

            m_tel = '无'
            try:
                if re.search('Tel：([0-9\-—\+]+)', info[1]):
                    m_tel = re.search('Tel：([0-9\-—\+]+)', info[1]).group(1)
                    m_tel = m_tel.strip('\.|．|\-')
            except IndexError:
                pass

            return('\t'.join([f_email, f_author, m_email, m_author, f_tel, m_tel, ';'.join(author), cinfo, ';'.join(organ), title]))
        else:
            return('无\t无\t无\t无\t无\t无\t无\t无\t无\t%s' % (title))

            # print(res.content)

    def main(self):
        outpath = '维普_' + self.keyword + '_作者信息.xls'
        try:
            with open(outpath, 'r', encoding='utf-8') as prefile:
                prepmid = []
                for line in prefile:
                    prepmid.append(re.search('\t([^\t\n]+)$', line).group(1).strip())
#                if prepmid:
#                    prepmid.pop(0)

        except FileNotFoundError:
            prepmid = []

        try:
            with open('@维普_' + self.keyword + '_log.txt', 'r', encoding='utf-8') as prefile2:
                found_id = {}
                for line in prefile2:
                    li = re.split(':\t', line.strip())
                    found_id[li[0]] = re.split(':,', li[1])
#                    try:
#                       found_id[li[0]] = found_id[li[0]] + [li[1]]
#                    except KeyError:
#                        found_id[li[0]] = [li[1]]
        except FileNotFoundError:
            found_id = {}
#        print(found_id)

        with open(outpath, 'a', encoding='utf-8') as outff, open('@维普_' + self.keyword + '_log.txt', 'a', encoding='utf-8') as outlog:
            if not prepmid:
                outff.write('作者邮箱\t作者\t通讯作者邮箱\t通讯作者\t作者电话\t通讯作者电话\t所有作者\t所有作者信息\t作者机构\t文章标题\t文章ID\n')

            for year in range(self.year_range[0], self.year_range[1]):
                if str(year) not in found_id.keys():
                    pmid_list = []
                    totalpage = self.get_totalpage(year=year)
                    for p in range(1, totalpage + 1):
                        print('geting id of page' + str(p) + ' in ' + str(year))
                        pmid_list = pmid_list + self.get_id(page=p, year=year)

                    outlog.write(str(year) + ':\t' + ':,'.join(pmid_list) + '\n')
                else:
                    pmid_list = found_id[str(year)]
#               pmid_list = list(set(pmid_list))
                td = len(pmid_list)
                print('Total %s papers in %s' % (td, year))
                d = 0
                for perid in pmid_list:
                    d = d + 1
                    perctg = 100 * d / td
                    done = int(50 * d / td)
                    sys.stdout.write("\r%s: [%s%s] %.3f%%" % (year, '█' * done, ' ' * (50 - done), perctg))
                    sys.stdout.flush()
                    if perid not in prepmid:
                        info = self.get_info(id=perid)
                        info = info + '\t' + perid + '\n'
                        outff.write(info)


if __name__ == '__main__':
    try:
        mysearch = weipu(keyword=sys.argv[1], header='header_for_weipu.txt')
        mysearch.main()
#        print('\n' + str(p))
    finally:
        mysearch.driver.quit()
