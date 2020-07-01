import requests


class TiebaSpider(object):
    base_url = 'http://tieba.baidu.com/f?kw={}&ie=utf-8&pn={}'

    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

    def get_url_list(self):
        url_list = []
        for i in range(self.start, self.end+1):
            url = self.base_url.format(self.name, (i-1)*50)
            url_list.append(url)

        return url_list

    def get_page_content(self, url: str):
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.content

    def write_to_file(self, filename, content):
        with open(filename, "wb") as f:
            f.write(content)

    def run(self):
        url_list = self.get_url_list()
        for url in url_list:
            content = self.get_page_content(url)
            if content:
                file_name = '{}-{}.html'.format(self.name, url_list.index(url) + 1)
                self.write_to_file(file_name, content)


if __name__ == "__main__":
    tb = TiebaSpider("刘昊然", 1, 10)
    tb.run()
