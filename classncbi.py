# -*-coding:utf-8-*-
from bs4 import BeautifulSoup
from lxml import html
import requests
import re
import sys
import time
import math


class sencbi(object):
    def __init__(self, head, postdata, maxpage=False):
        self.posturl = 'https://www.ncbi.nlm.nih.gov/pubmed'
        self.url = 'https://www.ncbi.nlm.nih.gov/pubmed/{}'
        self.header = self.formdict(file=head, sep=': +')
        self.form = self.formdict(file=postdata, sep='  ')
        self.header['Connection'] = 'close'
        self.headforget = {}
        self.headforget['Host'] = self.header['Host']
        self.headforget['User-Agent'] = self.header['User-Agent']
        self.headforget['Referer'] = self.header['Referer']
        self.headforget['Connection'] = 'close'
        term = self.form['term']
        initurl = self.url.format('?term=' + term)
        resu = requests.get(url=initurl)
        tre = html.fromstring(resu.content)
        totalnumber = tre.xpath('//div[@class="title_and_pager"]/div/h3[@class="result_count left"]/text()')
        self.totalpaper = int(re.search('of ([0-9]+)', str(totalnumber)).group(1))
        self.totalpage = math.ceil(self.totalpaper / 200)
        self.pmid_list = self.get_pmid_from_pmid_page(maxpage=maxpage)
        print('%s pmid got, preparation completed' % (len(self.pmid_list)))

    def formdict(self, file, sep):
        d = {}
        for line in open(file, "r", encoding='utf-8'):
            line = re.sub('\n$', '', line)
            if re.search("  $", line) == None:
                li = re.split(sep, line)
                d[li[0]] = li[1]
        return(d)

    def get_Detail(self, out):
        while True:
            try:
                res = requests.post(url=self.posturl, headers=self.header, data=self.form)
                break
            except:
                time.sleep(3)
        soup = BeautifulSoup(res.text, 'html.parser')
        sumpmid = soup.select('.rprtid')
        for i in range(201):
            try:
                pmid = sumpmid[i].text.lstrip('PMID:').strip()
                self.get_con(pmid=pmid, outfile=out)
            except IndexError:
                break

    def get_con(self, pmid, outfile):
        each_url = self.url.format(pmid)
        while True:  # 一直循环，知道访问站点成功
            try:
                res = requests.get(url=each_url, headers=self.headforget)
                break
            except TimeoutError:
                print('TimeoutError -- please wait 3 seconds')
                time.sleep(3)
            except OSError:
                print('OSError -- please wait 3 seconds')
                time.sleep(3)
            except requests.exceptions.ChunkedEncodingError:
                print('ChunkedEncodingError -- please wait 3 seconds')
                time.sleep(3)
            except requests.exceptions.ConnectionError:
                print('ConnectionError -- please wait 3 seconds')
                time.sleep(3)

        tree = html.fromstring(res.content)
# get email
        dic_email = {}
        authortinfo = tree.xpath(
            '//div[@class="rprt_all"]/div[@class="rprt abstract"]/div[@class="afflist"]/dl[@class="ui-ncbi-toggler-slave"]/dd/text()')
        rga = range(len(authortinfo))
        if authortinfo:
            for index in rga:
                if re.search('[^\t ]+@[^\t ]+', authortinfo[index]):
                    semail = ""
                    for e in re.findall('[^\t ]+@[^\t ]+', authortinfo[index]):
                        e = re.sub(r'\.$', '', e)
                        semail = semail + e + '    '
                    semail = re.sub(' +$', '', semail)
                    dic_email[index] = semail
# get author
        auther = tree.xpath('//div[@class="auths"]/a/text()')
        autherdex = tree.xpath('//div[@class="auths"]/sup/text()')
        for i in range(len(autherdex)):
            autherdex[i] = re.sub('[^,0-9]', '', autherdex[i])

        dic_author = {}
        if autherdex:
            for ea in range(len(autherdex)):
                if not re.search(',', autherdex[ea]):
                    autherdex[ea] = autherdex[ea] + 's'
            mau = ''
            for j in autherdex:
                mau = mau + j
            autherdex = mau
            autherdex = re.sub('s$', '', autherdex)
            autherdex = re.split('s', autherdex)
            for anb in range(len(auther)):
                try:
                    haha = re.split(',[ \t]*', autherdex[anb])
                except IndexError:
                    break
                for index in rga:
                    if str(index + 1) in haha:
                        try:
                            dic_author[index] = dic_author[index] + auther[anb] + '(Author%s); ' % (anb + 1)
                        except KeyError:
                            dic_author[index] = auther[anb] + '(Author%s); ' % (anb + 1)
# get if china
        dic_china = {}
        if authortinfo:
            for index in rga:
                if re.search('china', authortinfo[index], flags=re.IGNORECASE):
                    dic_china[index] = 'China'
                else:
                    dic_china[index] = 'Foreign'

        title = tree.xpath('//h1/text()')
        try:
            title[0]
        except:
            title = "no_title"
        doi = tree.xpath('//dl[@class="rprtid"]/dd/a/text()')
        try:
            doi[0]
        except:
            doi = 'None'

        if dic_email:
            for k in dic_email.keys():
                try:
                    outfile.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %
                                  (dic_email[k], dic_author[k], dic_china[k], authortinfo[k], title[0], doi[0], pmid))
                except:
                    pass
        else:
            try:
                outfile.write('None_email\t%s\tUnknown\t%s\t%s\t%s\t%s\n' %
                              (auther, authortinfo, title[0], doi[0], pmid))
            except:
                pass

    def get_pmid_from_main_page(self):
        l_pmid = []
        for p in range(1, self.totalpage + 1):
            print('Geting page' + str(p))
            self.form['EntrezSystem2.PEntrez.PubMed.Pubmed_ResultsPanel.Pubmed_Pager.CurrPage'] = str(p)
            while True:
                try:
                    res = requests.post(url=self.posturl, headers=self.header, data=self.form)
                    break
                except TimeoutError:
                    print('TimeoutError -- please wait 3 seconds')
                    time.sleep(3)
                except requests.exceptions.ConnectionError:
                    print('ConnectionError -- please wait 3 seconds')
                    time.sleep(3)
            soup = BeautifulSoup(res.text, 'html.parser')
            sumpmid = soup.select('.rprtid')
            for mid in sumpmid:
                mid = mid.text.lstrip('PMID:').strip()
                l_pmid.append(mid)
        return(l_pmid)

    def get_pmid_from_pmid_page(self, maxpage=False):
        l_pmid = []
        for p in range(1, self.totalpage + 1):
            if maxpage:
                if int(maxpage[0]) <= p < int(maxpage[1]):
                    print('Geting the pmid of page' + str(p))
                    self.form['EntrezSystem2.PEntrez.PubMed.Pubmed_ResultsPanel.Pubmed_Pager.CurrPage'] = str(p)
                    while True:
                        try:
                            res = requests.post(url=self.posturl, headers=self.header, data=self.form)
                            break
                        except TimeoutError:
                            print('TimeoutError -- please wait 3 seconds')
                            time.sleep(3)
                        except requests.exceptions.ConnectionError:
                            print('ConnectionError -- please wait 3 seconds')
                            time.sleep(3)
                    tree = html.fromstring(res.content)
                    pmid = tree.xpath('//pre/text()')
                    pmid = re.split('\n', pmid[0])
                    pmid.pop()
                    l_pmid = l_pmid + pmid
            else:
                print('Geting the pmid of page' + str(p))
                self.form['EntrezSystem2.PEntrez.PubMed.Pubmed_ResultsPanel.Pubmed_Pager.CurrPage'] = str(p)
                while True:
                    try:
                        res = requests.post(url=self.posturl, headers=self.header, data=self.form)
                        break
                    except TimeoutError:
                        print('TimeoutError -- please wait 3 seconds')
                        time.sleep(3)
                    except requests.exceptions.ConnectionError:
                        print('ConnectionError -- please wait 3 seconds')
                        time.sleep(3)
                tree = html.fromstring(res.content)
                pmid = tree.xpath('//pre/text()')
                pmid = re.split('\n', pmid[0])
                pmid.pop()
                l_pmid = l_pmid + pmid
        return(l_pmid)

    def main(self, outpath):
        try:
            with open(outpath, 'r', encoding='utf-8') as prefile:
                prepmid = []
                for line in prefile:
                    prepmid.append(re.search('\t([^\t\n]+)$', line).group(1).strip())

        except:
            prepmid = []
        with open(outpath, 'a', encoding='utf-8') as outff:
            if not prepmid:
                outff.write('E-mail\tAuthor\tIf-China\tAuthor_information\tTitle\tDOI\tPMID\n')
            print('Start to get author information......')
            d = 0
            for perid in self.pmid_list:
                d = d + 1
                perctg = 100 * d / self.totalpaper
                done = int(50 * d / self.totalpaper)
                sys.stdout.write("\r[%s%s] %.3f%%" % ('█' * done, ' ' * (50 - done), perctg))
                sys.stdout.flush()
                if perid.strip() not in prepmid:
                    self.get_con(pmid=perid, outfile=outff)


if __name__ == "__main__":
    inter = re.split(',', sys.argv[1])
    test = sencbi(head='header.txt', postdata='form.txt', maxpage=inter)
    termname = re.sub('\"', '', test.form['term'])
    test.main(outpath='ncbi_%s_author_emails.xls' % (termname))
    print('\nGeting author infomation completed! ^_^')
