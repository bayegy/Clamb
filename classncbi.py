# -*-coding:utf-8-*-
from bs4 import BeautifulSoup
from lxml import html
import requests
import re
import sys
import time
import math
import random


class sencbi(object):
    def __init__(self, head, postdata):
        self.posturl = 'https://www.ncbi.nlm.nih.gov/pubmed'
        self.url = 'https://www.ncbi.nlm.nih.gov/pubmed/{}'
        self.header = self.formdict(file=head, sep=': +')
        self.form = self.formdict(file=postdata, sep='\t+')
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

    def formdict(self, file, sep):
        d = {}
        for line in open(file, "r", encoding='utf-8'):
            line = re.sub('\n$', '', line)
            if not re.search("  $", line):
                li = re.split(sep, line)
                d[li[0]] = li[1]
        return(d)

    def get_con(self, pmid, outfile):
        time.sleep(random.randint(1, 3))
        each_url = self.url.format(pmid)
        while True:  # 一直循环，知道访问站点成功
            try:
                res = requests.get(url=each_url, headers=self.headforget, timeout=20)
                if res.status_code == 200:
                    break
            except Exception as e:
                print(str(e) + ',tring another time')
                time.sleep(1)

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
                    haha = re.split(',[ |\t]*', autherdex[anb])
                except Exception:
                    break
                for index in rga:
                    if str(index + 1) in haha:
                        try:
                            dic_author[index] = dic_author[index] + auther[anb] + '(Author%s); ' % (anb + 1)
                        except Exception:
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
        except Exception:
            title = "no_title"
        doi = tree.xpath('//dl[@class="rprtid"]/dd/a/text()')
        try:
            doi[0]
        except Exception:
            doi = 'None'

        if dic_email:
            for k in dic_email.keys():
                try:
                    outfile.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %
                                  (dic_email[k], dic_author[k], dic_china[k], authortinfo[k], title[0], doi[0], pmid))
                except Exception:
                    pass
        else:
            try:
                outfile.write('None_email\t%s\tUnknown\t%s\t%s\t%s\t%s\n' %
                              (auther, authortinfo, title[0], doi[0], pmid))
            except Exception:
                pass

    def get_pmid_from_pmid_page(self):
        time.sleep(random.randint(1, 3))
        l_pmid = []
        for p in range(1, self.totalpage + 1):
            print('Geting the pmid of page' + str(p))
            self.form['EntrezSystem2.PEntrez.PubMed.Pubmed_ResultsPanel.Pubmed_Pager.CurrPage'] = str(p)
            while True:
                try:
                    res = requests.post(url=self.posturl, headers=self.header, data=self.form, timeout=20)
                    if res.status_code == 200:
                        break
                except Exception as e:
                    print(str(e) + ', \ntring another time')
                    time.sleep(1)

            tree = html.fromstring(res.content)
            pmid = tree.xpath('//pre/text()')
            pmid = re.split('\n', pmid[0])
            pmid.pop()
            pmid = [pd.strip() for pd in pmid]
            l_pmid = l_pmid + pmid
        return(l_pmid)

    def main(self):
        termname = re.sub('\"', '', test.form['term'])
        outpath = 'ncbi_%s_author_emails.xls' % (termname)

        try:
            with open(outpath, 'r', encoding='utf-8') as prefile:
                prepmid = []
                for line in prefile:
                    prepmid.append(re.search('\t([^\t\n]+)$', line).group(1).strip())
        except FileNotFoundError:
            prepmid = []

        try:
            with open('@NCBI_' + termname + '_log.txt', 'r', encoding='utf-8') as prefile2:
                found_id = re.split('\t', prefile2.read())
        except FileNotFoundError:
            found_id = []

        with open(outpath, 'a', encoding='utf-8') as outff, open('@NCBI_' + termname + '_log.txt', 'a', encoding='utf-8') as log:
            if not prepmid:
                outff.write('E-mail\tAuthor\tIf-China\tAuthor_information\tTitle\tDOI\tPMID\n')

            if not found_id:
                found_id = self.get_pmid_from_pmid_page()
                log.write('\t'.join(found_id))
            print('%s pmid got, preparation completed' % (len(found_id)))

            print('Start to get author information......')
            d = 0
            for perid in found_id:
                d = d + 1
                perctg = 100 * d / self.totalpaper
                done = int(50 * d / self.totalpaper)
                sys.stdout.write("\r[%s%s] %.3f%%" % ('█' * done, ' ' * (50 - done), perctg))
                sys.stdout.flush()
                if perid.strip() not in prepmid:
                    self.get_con(pmid=perid, outfile=outff)


if __name__ == "__main__":
    #    inter = re.split(',', sys.argv[1])
    test = sencbi(head='header.txt', postdata='form.txt')
    test.main()
    print('\nGeting author infomation completed! ^_^')
