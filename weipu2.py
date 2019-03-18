# -*-coding:utf-8-*-
from lxml import html
import requests
import re
import sys
import time
import random
import numpy as np
import pandas as pd
from utils.net import Net
from utils.progress_bar import ProgressBar


class Weipu(object):
    def __init__(self):
        self.__net = Net()
        self.__headers = self.__net.parse_form("config/weipu_header.conf", sep=":")
        self.__get_headers = self.__net.parse_form("config/weipu_get_header.conf", sep=":")
        # self.__ip = self.__net.get_proxy()
        self.__url = "http://qikan.cqvip.com/Search/SearchList"
        self.__form = self.__net.parse_form("config/weipu_form.conf", sep="\t")

    def form_weipu_search_unit(self, field_name, field_value, pre_logical="AND", exact="0") -> str:
        return '{"FieldIdentifier":"%s","SearchKey":"%s","PreLogicalOperator":"%s","IsExact":"%s"}' % (field_name, field_value, pre_logical, exact)

    def write_reponse(self, response):
        with open("data/current_response_html.html", encoding="utf-8", mode="w") as rf:
            rf.write(response.text)

    def search_id(self, author=None, organ=None, title=None, only_first_author=False, page="1") -> []:
        req_data = self.__form.copy()
        flag = "F" if only_first_author else "A"
        author = self.form_weipu_search_unit(flag, author, exact="1") if author else ""
        organ = self.form_weipu_search_unit("S", organ) if organ else ""
        title = self.form_weipu_search_unit("M", title) if title else ""
        searchbody = ','.join([author, organ, title]).strip(',')
        searchbody = re.sub(',+', ',', searchbody)
        SearchKeyList = "[%s]" % (searchbody)
        req_data["searchParamModel"] = req_data["searchParamModel"] % (SearchKeyList, page)
        # print(req_data)
        idset = self.__net.requests(self.__url, req_data, headers=self.__headers, timeout=20).xpath("//@articleid")
        return list(set(idset))

    def find_email(self, string) -> str:
        found = re.search('[a-zA-Z0-9_\-\+.．]+@[a-zA-Z0-9_\-\+.．]+', string)
        return found.group() if found else ""

    def find_name(self, string, refer) -> str:
        for n in refer:
            if not string.find(n) == -1:
                return n
        return ""

    def find_author_email_in_article(self, author, article_id) -> []:
        tree = self.__net.requests(method="get", timeout=20, headers=self.__get_headers,
                                   url="http://qikan.cqvip.com/Qikan/Article/Detail?id={}".format(article_id))
        # authors = tree.xpath('//div[@class="author"]/span/a/span/text()')
        author_info = ''.join(tree.xpath('//div[@class="others"]/text()')
                              ).strip().replace('．', '.').replace('\n', '').replace('\r', '')
        infos = re.split('通[讯|信]作者', author_info)
        # print(infos)
        email = ''
        for info in infos:
            if not info.find(author) == -1:
                email = self.find_email(info)
        if email:
            title = tree.xpath("//h1/text()")[0].strip()
            organ = ';'.join(tree.xpath('//div[@class="organ"]/span/a/span/text()'))
            return [email, author_info, organ, title]
        else:
            return []

    def iter_find_author_email(self, author=None, organ=None):
        ids = self.search_id(author, organ)
        if ids:
            for id in ids:
                email = self.find_author_email_in_article(author, id)
                if email:
                    return email + ["通过名字和机构查找"]
        ids = self.search_id(author)
        if ids:
            for id in ids:
                email = self.find_author_email_in_article(author, id)
                if email:
                    return email + ["仅通过名字查找"]
        return ["无法找到邮箱"]

    def get_column(self, path, number=2, sep="\t"):
        return pd.read_csv(path, sep=sep).values if number == -1 else pd.read_csv(path, sep=sep).iloc[:, 0:number].values

    def array_in(self, record, array):
        for e in array:
            if list(e) == list(record):
                return True
        return False

    def run(self, data):
        results_file_name = "results/" + re.sub(".*/", "", data) + "_email_found.txt"
        data = pd.read_csv(data, sep="\t")
        colnames = list(data.columns) + ["邮箱", "作者信息", "作者机构", "文章标题", "查找方式"]
        data = data.values
        try:
            done = self.get_column(results_file_name)
            done = [list(i) for i in done]
        except Exception:
            done = []

        bar = ProgressBar(data.shape[0])
        with open(results_file_name, mode='a', encoding='utf-8') as results:
            if not len(done):
                results.write('\t'.join(colnames) + '\n')
            for row in data:
                row = [str(i) for i in row]
                author, organ = (row[0].strip(), row[1].strip())
                if not self.array_in([author, organ], done):
                    email = self.iter_find_author_email(author, organ)
                    results.write('\t'.join(list(row) + email) + '\n')
                    done.append([author, organ])
                    results.flush()
                    bar.move()
                else:
                    bar.move()

    def close(self):
        try:
            self.__net.close()
        except Exception:
            pass


if __name__ == '__main__':
    w = Weipu()
    try:
        w.run('data/medical_sciences_funds_2014-2018_new.txt')
    finally:
        w.close()
