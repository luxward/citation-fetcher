from model.clients import GoogleClient


if __name__ == '__main__':
    query = input("请输入要查询的论文名称：")
    client = GoogleClient()
    paper = next(client.search_papers(query))
    print(paper.title)
    print(paper.cite)
    print('-' * 50)
