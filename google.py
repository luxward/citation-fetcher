import html2text
from curl_cffi import requests
from parsel import Selector

from model.bibTexConverter import BibTexConverter
from model.paper import Paper
from model.utils import remove_consecutive_spaces

HOST = 'sci.673.org'
# HOST = 'scholar.google.com'

ss = requests.Session()
ss.impersonate = 'chrome124'
ss.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Referer': 'https://scholar.google.com/',
})

h = html2text.HTML2Text()
h.ignore_tables = True
h.ignore_links = True
h.ignore_emphasis = True

# ss.proxies.update({
#     'https': 'http://127.0.0.1:10809',
# })

converter = BibTexConverter()


def search_papers(q: str):
    print(f'Searching papers for {q}')
    url = f'https://{HOST}/scholar?hl=zh-CN&as_sdt=0%2C5&btnG='
    res = ss.get(url, params={
        'q': q,
    })
    sel = Selector(text=res.text)
    for a in sel.xpath('//div[@id="gs_res_ccl_mid"]/div')[:1]:
        cid = a.xpath('./@data-cid').extract_first()
        title = a.xpath(f'.//a[@id="{cid}"]').get()
        title = h.handle(title.replace('\n', '')).strip()
        title = remove_consecutive_spaces(title)

        print(f'Found paper: {title}, searching for citation...')
        url = f'https://{HOST}/scholar?q=info:{cid}:scholar.google.com/&output=cite&scirp=0&hl=en'
        res = ss.get(url)
        sel = Selector(text=res.content.decode('utf-8'))
        cite_url = sel.xpath('//a[text()="BibTeX"]/@href').get().replace('&amp;', '&')
        res = ss.get(cite_url)
        try:
            text = res.text.replace(r'$\{', '').replace(r'\}$', '').replace('$', '')
            cite = converter.convert_text(text).replace('–', '-')
        except RuntimeError:
            print(f'Error converting citation for {title}, {res.text}')
            return
        return Paper(id=cid, title=title, cite=cite)
    print(f'No papers found. {res.text}')


if __name__ == '__main__':
    query = input("请输入要查询的论文名称：")
    paper = search_papers(query)
    print(paper.title)
    print(paper.cite)
    print('-' * 50)
