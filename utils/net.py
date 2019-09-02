from selenium import webdriver
from lxml import html
import numpy as np
import re
import requests
import time
import random
import pandas as pd
import sys


class Net(object):
    """
    This class is synchronized

    arguments:
        post_headers, get_headers: file path of headers, key and value should be seprated by ':'

    """

    def __init__(self, protocol='http', post_headers=False, get_headers=False, proxies=False):
        self.protocol = protocol
        # response = None
        self.proxies = proxies or self.get_proxy_from_myserver()
        self.proxy = False
        # self.tried_times = 0
        # print(self.proxies.__next__())
        self.post_headers = self.parse_form(post_headers, sep=":") if post_headers else False
        self.get_headers = self.parse_form(get_headers, sep=":") if get_headers else False

    def get_proxy(self, pdriver=False):
        driver = pdriver or self.fox_driver()
        print("Fox driver have been activated")
        while True:
            time.sleep(2 + random.randint(1, 3))
            try:
                driver.get('http://www.goubanjia.com/')
                res = driver.page_source
                tree = html.fromstring(res)
                rows = tree.xpath('//tbody/tr')
                for row in rows:
                    try:
                        ip = row.xpath('td[@class="ip"]/*[not(contains(@style,"none"))]/text()')
                        ip = [i.strip() for i in ip]
                        ip = "".join(ip[0:-1]) + ":" + ip[-1]
                        degree = row.xpath('td[2]/a/text()')[0].strip()
                        protocol = row.xpath('td[3]/a/text()')[0].strip()
                        if protocol == self.protocol and degree == '高匿':
                            proxy_out = dict([(protocol, "{}://{}".format(protocol, ip))])
                            print("proxy found: " + str(proxy_out))
                            yield proxy_out
                    except IndexError:
                        print('\n#################bad proxy, skip it...#################')
                        # continue
            except KeyboardInterrupt:
                driver.close()
                sys.exit()
            except Exception as e:
                print(str(e) + '\n#################tring to get proxy another time...#################')
            finally:
                if not pdriver:
                    driver.close()

    @staticmethod
    def get_proxy_from_myserver(host="192.168.1.197"):
        while True:
            proxy = requests.get(f"http://{host}:5010/get/").content.decode()
            proxy_out = {"http": "http://{}".format(proxy)}
            print("proxy found: " + str(proxy_out))
            yield proxy_out
            requests.get(f"http://{host}:5010/delete/?proxy={proxy}")
            print(f"{proxy} deleted!")

    def requests(self, *args, method="post", timeout=20, return_tree=True, **kwargs) -> html.HtmlElement:
        """
        Same as requests.post, requests.get;
        *arg and **kwargs will be passed to requests.post or requests.get.
        Please do not use argument proxies
        """
        time.sleep(2 + random.randint(1, 3))
        while True:
            try:
                response = requests.post(*args, **kwargs, timeout=timeout, proxies=self.proxy) if method == "post" else requests.get(
                    *args, **kwargs, timeout=timeout, proxies=self.proxy)
                # self.write_reponse(response)
                if response.status_code == 200:
                    # breakpoint()
                    print(f"request {args or kwargs} succeed!")
                    return html.fromstring(response.content) if return_tree else response.text
                else:
                    raise TypeError("status_code is wrong")
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                print(e)
                self.proxy = self.proxies.__next__()
                time.sleep(2 + random.randint(1, 3))
                print("\n#################changed proxy and trying again...#################")

    def lrequests(self, *args, method="post", timeout=20, return_tree=True, **kwargs) -> html.HtmlElement:
        """
        Same as requests.post, requests.get;
        *arg and **kwargs will be passed to requests.post or requests.get.
        """
        time.sleep(2 + random.randint(1, 3))
        # tried_times = 0
        for _ in range(6):
            try:
                response = requests.post(*args, **kwargs, timeout=timeout) if method == "post" else requests.get(
                    *args, **kwargs, timeout=timeout)
                # self.write_reponse(response)
                if response.status_code == 200:
                    return html.fromstring(response.content) if return_tree else response.text
            except Exception as e:
                print(e)
            # tried_times += 1
                time.sleep(2 + random.randint(1, 3))
        raise RuntimeError(
            "Exceed max retry times, arguments used: {}, key word arguments used: {}".format(str(args), str(kwargs)))

    def hrequests(self, *args, method="post", **kwargs):
        """
        Do not use headers in this case, as this function will automatically use the headers passed to class Net (headers path).
        """
        return self.requests(*args, method="post", **kwargs, headers=self.post_headers) if method == "post" else self.requests(*args, method="get", **kwargs, headers=self.get_headers)

    @staticmethod
    def parse_form(file, sep=":"):
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
        df = out.applymap(lambda x: str(x).strip())
        return df.iloc[:, 0].values if number == 1 else df.values

    @staticmethod
    def array_in(record, array) -> bool:
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

    @staticmethod
    def xpath_first(tree, path) -> str:
        res = tree.xpath(path)
        return res[0].strip() if res else ""

    @staticmethod
    def search_str(pattern, string, nr=0, **kwargs) -> str:
        res = re.search(pattern, string, **kwargs)
        return res.group(nr) if res else ""
