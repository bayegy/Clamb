from selenium import webdriver
from lxml import html
import numpy as np
import re
import requests
import time
import random
import pandas as pd


class Net(object):
    """
    post_headers, get_headers: file path of headers, key and value should be seprated by ':'
    """

    def __init__(self, protocol='http', post_headers=False, get_headers=False):
        self.protocol = protocol
        self.__driver = None
        self.response = None
        self.__ip = self.get_proxy()
        self.proxy = False
        # print(self.__ip.__next__())
        self.post_headers = self.parse_form(post_headers, sep=":") if post_headers else False
        self.get_headers = self.parse_form(get_headers, sep=":") if get_headers else False

    def get_proxy(self):
        self.__driver = self.fox_driver()
        print("Fox driver have been activated, use close method to close it")
        while True:
            try:
                self.__driver.get('http://www.goubanjia.com/')
                res = self.__driver.page_source
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
                    if tp[n, 0] == '高匿' and tp[n, 1] == self.protocol:
                        ipout = {}
                        ipout[self.protocol] = "{}://".format(self.protocol) + ips[n]
                        yield(ipout)
            except Exception as e:
                print(e)
                self.__driver.close()
                newip = self.get_proxy()  # 初始化生成器
                while True:
                    yield(newip.__next__())

    def requests(self, *args, method="post", timeout=20, **kwargs) -> html.HtmlElement:
        """
        Same as requests.post, requests.get;
        *arg and **kwargs will be passed to requests.post or requests.get.
        Please do not use argument proxies
        """
        time.sleep(2 + random.randint(1, 3))
        while True:
            try:
                self.response = requests.post(*args, **kwargs, timeout=timeout, proxies=self.proxy) if method == "post" else requests.get(
                    *args, **kwargs, timeout=timeout, proxies=self.proxy)
                # self.write_reponse(response)
                if self.response.status_code == 200:
                    return html.fromstring(self.response.text)
                else:
                    self.proxy = self.__ip.__next__()
                    return self.requests(*args, method=method, timeout=timeout, **kwargs)
            except Exception as e:
                self.proxy = self.__ip.__next__()
                return self.requests(*args, method=method, timeout=timeout, **kwargs)

    def hrequests(self, *args, method="post", **kwargs):
        """
        Do not use headers in this case, as this function will automatically use the headers passed to class Net (headers path).
        """
        return self.requests(*args, method="post", **kwargs, headers=self.post_headers) if method == "post" else self.requests(*args, method="get", **kwargs, headers=self.get_headers)

    @staticmethod
    def parse_form(file, sep):
        d = {}
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                li = re.split(sep, line)
                if len(li) == 2:
                    d[li[0].strip()] = li[1].strip()
            return(d)

    def fox_driver(self):
        option = webdriver.FirefoxOptions()
        option.set_headless()
        return webdriver.Firefox(firefox_options=option)

    def write_reponse(self):
        with open("current_response_html.html", encoding="utf-8", mode="w") as rf:
            rf.write(self.response.text)

    @staticmethod
    def get_file_column(path, number=2, sep="\t") -> np.array:
        """
        number: number of columns to get, if -1, all colmns will be fetched,
                or use [] to specify specific column
        this method return a array of str
        """
        data = pd.read_csv(path, sep=sep)
        if isinstance(number, list):
            out = data.iloc[:, number]
        else:
            out = data if number == -1 else data.iloc[:, 0:number]
        return out.applymap(lambda x: str(x).strip()).values

    @staticmethod
    def array_in(record, array):
        for e in array:
            if list(e) == list(record):
                return True
        return False

    @staticmethod
    def find_email(string) -> str:
        found = re.search('[a-zA-Z0-9_\-\+.．—]+@[a-zA-Z0-9_\-\+.．—]+', string)
        return found.group().strip('.|．') if found else ""

    @staticmethod
    def find_name(string, refer) -> str:
        for n in refer:
            if not string.find(n) == -1:
                return n
        return ""

    def close(self):
        try:
            self.__driver.close()
        except Exception:
            pass
