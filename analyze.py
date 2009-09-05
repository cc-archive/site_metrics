import logparse

def get_data():
    return logparse.process(logparse.load())

def analyze_rest(data):
    urls = [x[1].path for x in data]
    total_num = len(urls)
    rest_urls = [url for url in urls if url.startswith('/rest')]
    rest_num = len(rest_urls)

    print float(rest_num)/total_num


if __name__ == '__main__':
    analyze_rest(get_data())
