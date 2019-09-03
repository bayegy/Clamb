# -*-coding:utf-8-*-
import sys
import os
from utils.net import Net
# import pdb


class WeipuJournal(object):
    def __init__(self):
        self.__net = Net()
        self.__headers = self.__net.parse_form(
            "config/weipu_header.conf", sep=":")
        self.__get_headers = self.__net.parse_form(
            "config/weipu_get_header.conf", sep=":")
        # self.__ip = self.__net.get_proxy()
        # self.__url = "http://qikan.cqvip.com/Search/SearchList"
        self.__url = "http://qikan.cqvip.com/Search/SearchList"

    def search_journal(self, ZY, category, page="1") -> []:
        req_data = dict()
        req_data["searchParamModel"] = '{"ObjectType":7,"SearchKeyList":[],"SearchExpression":null,"BeginYear":null,"EndYear":null,"UpdateTimeType":null,"JournalRange":null,"DomainRange":null,"ClusterFilter":"+QK=bdhx2017#北大核心期刊（2017版）[_]ZY=%s#%s", "ClusterLimit":0,"ClusterUseType":"Article","UrlParam":"","Sort":"1","SortField":null,"UserID":"0","PageNum":%s,"PageSize":100,"SType":"","StrIds":"","IsRefOrBy":0,"ShowRules":"","IsNoteHistory":0,"AdvShowTitle":null,"ObjectId":null,"ObjectSearchType":0,"ChineseEnglishExtend":0,"SynonymExtend":0,"ShowTotalCount":0,"AdvTabGuid":""}' % (
            ZY, category, page)
        # print(req_data)
        idset = self.__net.requests(self.__url, req_data, headers=self.__headers, timeout=20).xpath(
            '//dt/a[@target="_blank"]/text()')
        return list(set(idset))

#    def find_email(self, string) -> str:
#        found = re.search('[a-zA-Z0-9_\-\+.．]+@[a-zA-Z0-9_\-\+.．]+', string)
#        return found.group() if found else ""

    def run(self, journal_index_file):
        journal_index = self.__net.parse_form(journal_index_file, sep=" +")
        journal_list_file = os.path.dirname(os.path.abspath(
            __file__)) + '/' + "data/weipu_full_journal_list.txt"
        with open(journal_list_file, 'w', encoding='utf-8') as file:
            for category, ZY in journal_index.items():
                page = 1
                while True:
                    journal_list = self.search_journal(
                        ZY=ZY, category=category, page=page)
                    if journal_list:
                        file.write('\n'.join(journal_list) + '\n')
                    else:
                        break
                    page += 1


if __name__ == '__main__':
    w = WeipuJournal()
    w.run(sys.argv[1])
