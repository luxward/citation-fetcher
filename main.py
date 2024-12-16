import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search papers from Google Scholar or Baidu Scholar')
    parser.add_argument('--query', '-q', type=str, help='The query string to search')
    parser.add_argument('--engine', '-e', type=str, default='baidu',
                        help='The search engine to use, either "google" or "baidu", default is "baidu"')
    args = parser.parse_args()

    if args.engine == 'google':
        from model.clients import GoogleClient
        client = GoogleClient()
    else:
        from model.clients import BaiduClient
        client = BaiduClient()

    if not args.query:
        args.query = input("请输入要查询的论文名称：")

    for paper in client.search_papers(args.query):
        print(f"{paper.title}")
        print(paper.cite)
        print('-' * 50)
