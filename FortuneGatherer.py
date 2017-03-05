# -*- coding: utf-8 -*-

import urllib2, requests
from unidecode import unidecode
from bs4 import BeautifulSoup

class FortuneGatherer(object):

    def __init__(self):
        self.fortunes = []
        self.online_txt_files = ['http://cs.jhu.edu/~kevinduh/projects/fortunecookie/fortune.txt',
                                'http://www.cs.cmu.edu/~kristen/yes.txt',
                                'http://www.cs.cmu.edu/~kristen/no.txt']
        self.url_scrape_once_A = 'http://www.fortunecookiemessage.com/archive.php'
        self.url_scrape_once_B = 'http://www.chinese-fortune-cookie.com/fortune-cookie-quotes.html'
        self.url_scrape_once_C = 'http://www.myfortunecookie.co.uk/fortunes/'
        self.url_scrape_daily = 'http://www.astrology-online.com/daily.htm'

    def load_existing(self, filename='fortune_corpus.txt'):
        with open(filename, 'rb') as f:
            self.fortunes = f.read().splitlines()

    def gather_once(self):
        self._scrape_once_A
        self._scrape_once_B
        for url in self.online_txt_files:
            data = urllib2.urlopen(url)
            self.fortunes.extend(data.read().splitlines())

    def _scrape_once_A(self):
        url = self.url_scrape_once_A

        while True:
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html.parser')

            table = soup.find('table', 'table1')
            self.fortunes.extend(tag.text for tag in table.findAll('a') if tag['href'].startswith('/cookie/'))

            # next page
            footerlinks = soup.find('span', {'class': 'footerlinks'})
            nextlink = footerlinks.findAll('a')[-1]
            nexturl = self.url_scrape_once_A + nextlink['href']

            if url == nexturl:
                break
            url = nexturl

    def _scrape_once_B(self):
        r = requests.get(self.url_scrape_once_B)
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table', {'width': '550', 'border': '0', 'cellpadding': '8', 'cellspacing': '0'})
        self.fortunes.extend([p.text.strip() for p in table.findAll('p')])

    def _scrape_once_C(self):
        ind = 0
        while True:
            ind += 1
            url = self.url_scrape_once_C + '{}/'.format(ind)
            try:
                r = requests.get(url)
                soup = BeautifulSoup(r.content, 'html.parser')
                self.fortunes.append(soup.find('h1').text)
            except:
                break

    def scrape_daily(self):
        r = requests.get(self.url_scrape_daily)
        soup = BeautifulSoup(r.content, 'html.parser')
        horoscopes = [p.text for p in soup.findAll('p')[:-3]]
        for h in horoscopes:
            h = h.replace('\n\n\n\n\n\n\n\n(adsbygoogle = window.adsbygoogle || []).push({});\n\n\n\n', '')
            startind = h.index('\n\n') + 2
            new_h = h[startind:]
            if new_h[0] == '(':
                startind = new_h.index('\n\n') + 2
                new_h = new_h[startind:]
            self.fortunes.extend([line.encode("utf-8") for line in new_h.strip().split(' \n') if line])

    def save_fortunes(self, filename='fortune_corpus.txt'):
        for i, f in enumerate(self.fortunes):
            f = f.decode('utf-8')
            self.fortunes[i] = unidecode(f)

        self.fortunes = list(set(self.fortunes))
        print len(self.fortunes)

        with open(filename, 'wb') as f:
            for fortune in self.fortunes:
                try:
                    f.write('{}\n'.format(fortune))
                except UnicodeEncodeError:
                    print fortune
                    continue

def first_time_only_main():
    fg = FortuneGatherer()
    fg.gather_once()
    fg.scrape_daily()
    fg.save_fortunes()
    with open('fortune_corpus.txt', 'rb') as f:
        print len(f.read().splitlines())

def main():
    fg = FortuneGatherer()
    fg.load_existing()
    print 'Old corpus length: {}'.format(len(fg.fortunes))
    fg.scrape_daily()
    print 'New corpus length: {}'.format(len(fg.fortunes))
    fg.save_fortunes()

if __name__ == '__main__':
    main()
