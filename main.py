import dataclasses
import urllib.parse
import html2text
import requests
from parsel import Selector

ss = requests.Session()
ss.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
})


def remove_consecutive_spaces(text: str):
    return ' '.join(text.split())


@dataclasses.dataclass
class Paper:
    title: str
    cite: str
    id: str


def search_papers(wd: str):
    url = 'https://xueshu.baidu.com/s?tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&sc_hit=1'
    res = ss.get(url, params={
        "wd": wd
    })
    text = res.content.decode('utf-8')
    # print(text)
    sel = Selector(text=text)
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_emphasis = True
    h.ignore_tables = True
    data_click = "{'button_tp':'title'}"
    for a in sel.xpath(f'//div[@class="sc_content"]//a[@data-click="{data_click}"]')[:3]:
        href = a.xpath('./@href').extract_first()
        url = urllib.parse.urlparse(href)
        title = h.handle(a.extract()).strip().replace('\n', '')
        paper_id = urllib.parse.parse_qs(url.query)['paperid'][0]

        url = f'https://xueshu.baidu.com/u/citation?type=cite&paperid={paper_id}'
        res = ss.get(url)
        cite = res.json()['data']['sc_GBT7714'].replace(' ,', ',').replace(' .', '.').replace('].', ']. ')
        index = cite.find('DOI:')  # 去掉DOI
        if index != -1:
            cite = cite[:index]
        cite = remove_consecutive_spaces(cite)[4:]
        paper = Paper(title, cite, paper_id)
        yield paper


if __name__ == '__main__':
    query = input("请输入要查询的论文名称：")
    for paper in search_papers(query):
        print(paper.title)
        print(paper.cite)
        print('-' * 50)
