# -*-coding:utf-8-*-
from lxml import html
import requests
import re
import sys
import os
import time
import random
import numpy as np
import pandas as pd
from utils.net import Net
from utils.progress_bar import ProgressBar
# import pdb


class Weipu(object):
    def __init__(self):
        self.__net = Net()
        self.__headers = self.__net.parse_form("config/weipu_header.conf", sep=":")
        self.__get_headers = self.__net.parse_form("config/weipu_get_header.conf", sep=":")
        # self.__ip = self.__net.get_proxy()
        # self.__url = "http://qikan.cqvip.com/Search/SearchList"
        self.__url = "http://qikan.cqvip.com/Search/SearchList"
        self.__form = self.__net.parse_form("config/weipu_form.conf", sep="\t")

    def form_weipu_search_unit(self, field_name, field_value, pre_logical="AND", exact="0") -> str:
        return '{"FieldIdentifier":"%s","SearchKey":"%s","PreLogicalOperator":"%s","IsExact":"%s"}' % (field_name, field_value, pre_logical, exact)

    def write_reponse(self, response):
        with open("data/current_response_html.html", encoding="utf-8", mode="w") as rf:
            rf.write(response.content)

    def search_id(self, journal, page="1") -> []:
        req_data = dict()
        req_data["searchParamModel"] = '{"ObjectType":1,"SearchKeyList":[{"FieldIdentifier":"J","SearchKey":"%s","PreLogicalOperator":"","IsExact":"1"}],"SearchExpression":"","BeginYear":"2014","EndYear":"2019","JournalRange":"","DomainRange":"","PageSize":"100","PageNum":"%s","Sort":"0","ClusterFilter":"","SType":"","StrIds":"","UpdateTimeType":"","ClusterUseType":"Article","IsNoteHistory":1,"AdvShowTitle":"刊名=%s AND 年份：2014-2019","ObjectId":"","ObjectSearchType":"0","ChineseEnglishExtend":"0","SynonymExtend":"0","ShowTotalCount":"0","AdvTabGuid":"1db1e78c-4454-8675-d5b9-3eb71928b687"}' % (
            journal, page, journal)
        # print(req_data)
        idset = self.__net.requests(self.__url, req_data, headers=self.__headers, timeout=20).xpath("//@articleid")
        return list(set(idset))

#    def find_email(self, string) -> str:
#        found = re.search('[a-zA-Z0-9_\-\+.．]+@[a-zA-Z0-9_\-\+.．]+', string)
#        return found.group() if found else ""

    def all_journal_ids(self, journal):
        page = 1
        while True:
            ids = self.search_id(journal=journal, page=page)
            if len(ids):
                for i in ids:
                    yield i
            else:
                break
            page += 1

    def find_tel(self, string):
        res = re.search("Tel[:： ]*([\d—\-]+)", string, flags=re.I)
        if not res:
            res = re.search("电话[:： ]*([\d—\-]+)", string, flags=re.I)
        return res.group(1) if res else ""

    def find_article_info(self, article_id) -> []:
        tree = self.__net.requests(method="get", timeout=20, headers=self.__get_headers,
                                   url="http://qikan.cqvip.com/Qikan/Article/Detail?id={}".format(article_id))
        all_authors = [a.strip() for a in tree.xpath('//div[@class="author"]/span/a/span/text()')]
        author_info = ''.join(tree.xpath('//div[@class="others"]/text()')
                              ).strip().replace('．', '.').replace('\n', '').replace('\r', '').replace('\t', ';')
        infos = re.split('通[讯信]作者', author_info)
        if len(infos) == 1:
            infos = re.split("Corresponding", author_info, flags=re.I) + [""]

        first_author, com_author = infos[0].strip(), infos[1].strip()
        # print(infos)
        title = self.__net.xpath_first(tree, "//h1/text()")
        organ = ';'.join(tree.xpath('//div[@class="organ"]/span/a/span/text()')).replace('\t', ';')

        first_author_name = self.__net.find_name(first_author, all_authors)
        if not first_author_name and all_authors:
            first_author_name = all_authors[0]
        com_author_name = self.__net.find_name(com_author, all_authors)

        first_author_email = self.__net.find_email(first_author)
        com_author_email = self.__net.find_email(com_author)

        first_author_tel = self.find_tel(first_author)
        com_author_tel = self.find_tel(com_author)

        journal_info = self.__net.xpath_first(tree, '//span[@class="vol"]/text()')

        year = self.__net.search_str("(\d+)年", journal_info, 1)
        issue = self.__net.search_str("(\d+)期", journal_info, 1)
        journal_name = self.__net.xpath_first(tree, '//span[@class="from"]/a/text()')

        keywords = ','.join(tree.xpath('//div[@class="subject"]/span/a/text()'))
        return [article_id, journal_name, year, issue, title, ','.join(all_authors), organ, keywords, author_info, com_author_name, com_author_email, com_author_tel, first_author_name, first_author_email, first_author_tel]

    def run(self, journal_list_file):
        base_path = os.path.dirname(os.path.abspath(__file__)) + '/'
        results_file_name = base_path + "results/" + \
            os.path.splitext(os.path.basename(journal_list_file))[0] + "_article_information.txt"
        done_journal_list_file_name = base_path + "data/done_journals.txt"
        with open(journal_list_file) as jl:
            journal_list = [jn.strip() for jn in jl.read().split('\n') if jn.strip()]

        colnames = ['文章ID', '期刊名', '年份', '期', '论文题目', '作者', '机构', '关键词',
                    '作者简介', '通讯作者姓名', '通讯作者邮箱', '通讯作者电话', '第一作者姓名', '第一作者邮箱', '第一作者电话']

        try:
            print("results stored in {}".format(results_file_name))
            done = self.__net.get_file_column(results_file_name, number=1)
            done = done.tolist()
        except Exception:
            # print(e)
            print("did not found results table, create a new one")
            done = []

        try:
            with open(done_journal_list_file_name) as djl:
                done_journal_list = [jn.strip() for jn in djl.read().split('\n') if jn.strip()]
        except Exception:
            done_journal_list = []

        bar = ProgressBar(len(journal_list))
        with open(results_file_name, mode='a', encoding='utf-8') as results, open(done_journal_list_file_name, mode='a', encoding='utf-8') as done_journal_file:
            if not len(done):
                results.write('\t'.join(colnames) + '\n')
            for journal in journal_list:
                if journal not in done_journal_list:
                    for paper_id in self.all_journal_ids(journal):
                        if paper_id not in done:
                            found_info = self.find_article_info(paper_id)
                            results.write('\t'.join(found_info) + '\n')
                            done.append(paper_id)
                            # results.flush()
                    done_journal_file.write(journal + '\n')
                    done_journal_list.append(journal)
                    # done_journal_file.flush()
                    bar.move()
                else:
                    bar.move()


if __name__ == '__main__':
    w = Weipu()
    w.run(sys.argv[1])
