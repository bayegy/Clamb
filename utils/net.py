from selenium import webdriver
from lxml import html
import numpy as np
import re


class Net(object):
    """docstring for Net"""

    def __init__(self):
        self.driver = None

    def get_proxy(self):
        print("Activing foxDriver, always remember to close Net.driver if you don't use getProxy anymore.")
        self.driver = self.fox_driver()
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
                print(e)
                yield(self.get_proxy())

    def parse_form(self, file, sep):
        d = {}
        with open(file, "r",encoding="utf-8") as f:
            for line in f:
                li = re.split(sep, line)
                if len(li) == 2:
                    d[li[0].strip()] = li[1].strip()
            return(d)

    def fox_driver(self):
        option = webdriver.FirefoxOptions()
        option.set_headless()
        return webdriver.Firefox(firefox_options=option)

    def close(self):
        try:
            self.driver.close()
        except Exception:
            pass
