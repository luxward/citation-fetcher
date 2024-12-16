import urllib.parse

import html2text
from curl_cffi import requests
from parsel import Selector

from model.bibTexConverter import BibTexConverter
from model.paper import Paper
from model.utils import remove_consecutive_spaces


class Client:
    def __init__(self):
        self.ss = requests.Session()
        self.ss.impersonate = 'chrome124'
        self.ss.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        })
        self.h = html2text.HTML2Text()
        self.h.ignore_tables = True
        self.h.ignore_links = True
        self.h.ignore_emphasis = True

    def search_papers(self, q: str, limit=1):
        raise NotImplementedError


class BaiduClient(Client):
    def search_papers(self, q: str, limit=3):
        url = 'https://xueshu.baidu.com/s?tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&sc_hit=1'
        res = self.ss.get(url, params={
            "wd": q
        })
        text = res.content.decode('utf-8')
        # print(text)
        sel = Selector(text=text)
        data_click = "{'button_tp':'title'}"
        for a in sel.xpath(f'//div[@class="sc_content"]//a[@data-click="{data_click}"]')[:limit]:
            href = a.xpath('./@href').extract_first()
            url = urllib.parse.urlparse(href)
            title = self.h.handle(a.extract()).strip().replace('\n', '')
            paper_id = urllib.parse.parse_qs(url.query)['paperid'][0]

            url = f'https://xueshu.baidu.com/u/citation?type=cite&paperid={paper_id}'
            res = self.ss.get(url)
            cite = res.json()['data']['sc_GBT7714'].replace(' ,', ',').replace(' .', '.').replace('].', ']. ')
            index = cite.find('DOI:')  # 去掉DOI
            doi = ""
            if index != -1:
                cite = cite[:index]
                doi = cite[index:]
            cite = remove_consecutive_spaces(cite)[4:]
            yield Paper(title, cite, paper_id, doi)


class GoogleClient(Client):
    HOST = 'sci.673.org'
    # HOST = 'scholar.google.com'

    def __init__(self):
        super().__init__()
        # self.ss.proxies.update({
        #     'https': 'http://127.0.0.1:10809',
        # })
        self.ss.headers.update({
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://scholar.google.com/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-full-version-list': '"Google Chrome";v="131.0.6778.140", "Chromium";v="131.0.6778.140", "Not_A Brand";v="24.0.0.0"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"19.0.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'x-browser-channel': 'stable',
            'x-browser-copyright': 'Copyright 2024 Google LLC. All rights reserved.',
            'x-browser-validation': 'Nbt54E7jcg8lQ4EExJrU2ugNG6o=',
            'x-browser-year': '2024'
        })
        self.converter = BibTexConverter()

    def search_papers(self, q: str, limit=1):
        print(f'Searching papers for {q}')
        url = f'https://{self.HOST}/scholar?hl=zh-CN&as_sdt=0%2C5&btnG='
        res = self.ss.get(url, params={
            'q': q,
        })
        sel = Selector(text=res.text)
        for a in sel.xpath('//div[@id="gs_res_ccl_mid"]/div')[:limit]:
            cid = a.xpath('./@data-cid').extract_first()
            title = a.xpath(f'.//a[@id="{cid}"]').get()
            title = self.h.handle(title.replace('\n', '')).strip()
            title = remove_consecutive_spaces(title)

            print(f'Found paper: {title}, searching for citation...')
            url = f'https://{self.HOST}/scholar?q=info:{cid}:scholar.google.com/&output=cite&scirp=0&hl=en'
            res = self.ss.get(url)
            sel = Selector(text=res.content.decode('utf-8'))
            cite_url = sel.xpath('//a[text()="BibTeX"]/@href').get().replace('&amp;', '&')
            res = self.ss.get(cite_url)
            try:
                text = res.text.replace(r'$\{', '').replace(r'\}$', '').replace('$', '')
                cite = self.converter.convert_text(text).replace('–', '-').replace('等', 'et al')
            except RuntimeError:
                print(f'Error converting citation for {title}, {res.text}')
                return
            yield Paper(id=cid, title=title, cite=cite)
        print(f'No papers found. {res.text}')
