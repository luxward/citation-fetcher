import urllib.parse

import html2text
from curl_cffi import requests
from parsel import Selector

from ..model.logger import create_logger
from ..model.paper import Paper
from ..model.utils import remove_consecutive_spaces

logger = create_logger("client", stream_level='DEBUG')
from functools import lru_cache


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
        # self.converter = BibTexConverter()

    def search_papers(self, q: str, limit=1):
        raise NotImplementedError


class BaiduClient(Client):
    @lru_cache(maxsize=30)
    def search_papers(self, q: str, limit=3, use_doi=False):
        #logger.debug(f'Searching papers for {q}')
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
            success = False
            # if index != -1:
            #     cite, doi = cite[:index], cite[index:]
            #     if use_doi and doi:
            #         logger.debug(f'Using DOI: {doi} to get bibtex...')
            #         url = 'https://api.paperpile.com/api/public/convert'
            #         data = {"fromIds": True, "input": doi, "targetFormat": "Bibtex"}
            #         res = self.ss.post(url, json=data, headers={
            #             'accept': '*/*',
            #             'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            #             'cache-control': 'no-cache',
            #             'content-type': 'application/json',
            #             'origin': 'https://www.bibtex.com',
            #             'pragma': 'no-cache',
            #             'priority': 'u=1, i',
            #             'referer': 'https://www.bibtex.com/',
            #             'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            #             'sec-ch-ua-mobile': '?0',
            #             'sec-ch-ua-platform': '"Windows"',
            #             'sec-fetch-dest': 'empty',
            #             'sec-fetch-mode': 'cors',
            #             'sec-fetch-site': 'cross-site',
            #         })
            #         try:
            #             bibtex = res.json()['output']
            #             cite = self.converter.convert_text(bibtex)
            #             success = True
            #         except KeyError:
            #             logger.error(f'Error getting bibtex for {doi}, fallback to baidu citation. {res.text}')
            if not success:
                cite = remove_consecutive_spaces(cite)[4:]
            yield Paper(title, cite, paper_id, doi)


class GoogleClient(Client):
    HOST = 'sci.673.org'

    # HOST = 'scholar.google.com'

    def __init__(self, proxy=None):
        super().__init__()
        if proxy:
            self.ss.proxies.update({
                'https': proxy,
            })
            logger.debug(f'Using proxy: {proxy}')
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

    def search_papers(self, q: str, limit=1, **kwargs):
        logger.debug(f'Searching papers for {q}')
        url = f'https://{self.HOST}/scholar?hl=zh-CN&as_sdt=0%2C5&btnG='
        res = self.ss.get(url, params={
            'q': q,
        })
        sel = Selector(text=res.text)

        tags = sel.xpath('//div[@id="gs_res_ccl_mid"]/div')[:limit]
        if not tags:
            logger.error(f'No papers found for {q}')
            return
        for a in tags:
            cid = a.xpath('./@data-cid').extract_first()
            title = a.xpath(f'.//a[@id="{cid}"]').get()
            title = self.h.handle(title.replace('\n', '')).strip()
            title = remove_consecutive_spaces(title)

            logger.debug(f'Found paper: {title}, searching for citation...')
            url = f'https://{self.HOST}/scholar?q=info:{cid}:scholar.google.com/&output=cite&scirp=0&hl=zh-CN'
            res = self.ss.get(url)
            if res.status_code != 200:
                logger.error(f'Error getting citation for {title}, {res.text}')
                return
            sel = Selector(text=res.text)
            cite = sel.xpath('//td')[0].xpath('./div/text()').extract_first()

            yield Paper(id=cid, title=title, cite=cite)
