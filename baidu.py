from model.clients import BaiduClient

if __name__ == '__main__':
    query = input("请输入要查询的论文名称：")
    client = BaiduClient()
    for paper in client.search_papers(query):
        print(f"{paper.title} ({paper.doi})")
        print(paper.cite)
        print('-' * 50)
