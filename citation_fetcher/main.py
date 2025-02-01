import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search papers from Google Scholar or Baidu Scholar')
    parser.add_argument('--query', '-q', type=str, help='The query string to search')
    parser.add_argument('--engine', '-e', type=str, default='baidu',
                        help='The search engine to use, either "google" or "baidu", default is "baidu"')
    parser.add_argument('--proxy', '-p', type=str, help='The proxy to use, eg. "http://127.0.0.1:10809"')
    parser.add_argument('--doi', action='store_true', help='Use DOI to get bibtex')
    args = parser.parse_args()

    try:
        if args.engine == 'google':
            from model.clients import GoogleClient

            client = GoogleClient(proxy=args.proxy)
        else:
            from model.clients import BaiduClient

            client = BaiduClient()

        if not args.query:
            args.query = input("请输入要查询的论文名称：")

        for paper in client.search_papers(args.query, use_doi=args.doi):
            print(f"{paper.title}")
            print(paper.cite)
            print('-' * 50)
    finally:
        input("Press any key to exit...")
