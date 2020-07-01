import json
import requests


class DoubanMovieSpider(object):
    def __init__(self):
        self.url_pattern = "https://m.douban.com/rexxar/api/v2/subject_collection/movie_showing/items?start={}&count=18&loc_id=108288"
        self.headers = {
            "Referer": "https://m.douban.com/movie/nowintheater?loc_id=108288",
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Mobile Safari/537.36"
        }

    def get_json_from_url(self, url):
        response = requests.get(url, headers=self.headers)
        return response.content.decode()

    def get_movie_list(self, json_str):
        dic = json.loads(json_str)
        movie_list = dic['subject_collection_items']
        return movie_list

    def save_movie_list(self, movie_list):
        with open("movies.csv", 'a', encoding='utf8') as f:
            for movie in movie_list:
                json.dump(movie, f, ensure_ascii=False)
                f.write("\n")

    def run(self):
        url = self.url_pattern.format(0)
        json_str = self.get_json_from_url(url)
        movie_list = self.get_movie_list(json_str)
        self.save_movie_list(movie_list)


if __name__ == "__main__":
    db = DoubanMovieSpider()
    db.run()
