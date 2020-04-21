# coding=utf-8
import os
import sys
import requests

from urllib.request import urlretrieve
from bs4 import BeautifulSoup

from soug.tools import startChinese, getChinese, byte2str, startPy, getPyTable


class SouGSpider(object):
    def __init__(self):
        self.base_url = "http://pinyin.sogou.com"
        self.homepage_url = "http://pinyin.sogou.com/dict/"
        self.base_dir = "/Users/furuiyang/gitzip/JustSimpleSpider/soug/csv"

    def callbackfunc(self, blocknum, blocksize, totalsize):
        """
        回调函数
        :param blocknum: 已经下载的数据块
        :param blocksize:  数据块的大小
        :param totalsize: 远程文件的大小
        :return:
        """
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100:
            percent = 100
        sys.stdout.write("\r%6.2f%%" % percent)
        sys.stdout.flush()

    def scel2txt(self, in_file, out_file):
        print('-' * 60)
        with open(in_file, 'rb') as f:
            data = f.read()
        print("词库名：", byte2str(data[0x130:0x338]))
        print("词库类型：", byte2str(data[0x338:0x540]))
        print("描述信息：", byte2str(data[0x540:0xd40]))
        print("词库示例：", byte2str(data[0xd40:startPy]))
        getPyTable(data[startPy:startChinese])
        getChinese(data[startChinese:])

        words = getChinese(data[startChinese:])
        for word in words:
            with open(out_file, 'a+', encoding='utf-8') as file:
                file.write(word[2] + '\n')

    def listfiles(self, ldir: str, r: bool = True):
        lst = []
        csv_dirs = os.listdir(ldir)
        for one in csv_dirs:
            one = os.path.join(ldir, one)
            if os.path.isdir(one):
                if r:
                    lst.extend(self.listfiles(one))
                else:
                    pass
            else:
                lst.append(one)
        return lst

    def trans(self, source_dir, target_dir):
        error_list = []
        lst = self.listfiles(source_dir)
        for file in lst:
            n_file = file.replace(source_dir, target_dir).replace(".scel", ".csv")
            n_file_dir = os.path.split(n_file)[0]
            os.makedirs(n_file_dir, exist_ok=True)
            print(file)
            print(n_file)
            try:
                self.scel2txt(file, n_file)
            except:
                error_list.append(file)

            print()
            print()

        print(error_list)

    def load(self):
        html = requests.get(self.homepage_url).text
        soup = BeautifulSoup(html, "html.parser")
        soup = soup.find(id="dict_category_show").find_all('div', class_='dict_category_list')
        fc = 0
        sc = 0
        tc = 0

        for ii in soup:
            fc += 1
            first_class = ii.find(class_='dict_category_list_title').find('a').contents[0]
            print("Level 1 :" + first_class)
            if first_class in ('城市信息大全', '电子游戏'):
                continue

            first_dir = os.path.join(self.base_dir, ii.find(class_='dict_category_list_title').find('a').contents[0])
            os.makedirs(first_dir, exist_ok=True)

            for k in ii.find(class_='catewords').find_all('a'):
                second_class = k.contents[0]
                second_url = self.base_url + "%s" % (k['href'])
                print(" " * 4 + "Level 2 :" + second_class)
                if first_class == "自然科学" and second_class in ("化学", "天文学", "数学", "气象学", "物理", "生物"):
                    continue

                second_dir = os.path.join(first_dir, second_class)
                os.makedirs(second_dir, exist_ok=True)

                sc += 1
                soup2 = BeautifulSoup(requests.get(second_url).text, "html.parser")
                try:
                    totalpagenum = soup2.find(id='dict_page_list').find('ul').find_all('span')[-2].a.contents[0]
                except:
                    totalpagenum = 1

                os.chdir(second_dir)
                for pageind in range(1, int(totalpagenum) + 1):
                    soup2 = BeautifulSoup(requests.get("%s/default/%d" % (second_url.replace("?rf=dictindex", ""), pageind)).text, "html.parser")
                    for kk in soup2.find_all('div', class_='dict_detail_block'):
                        third_class = kk.find(class_='detail_title').find('a').contents[0]
                        third_url = kk.find(class_='dict_dl_btn').a['href']
                        print(" " * 8 + "Level 3 :" + third_class + " " * 10 + "Downloading")
                        tc += 1
                        try:
                            urlretrieve(third_url, "{}.scel".format(third_class), self.callbackfunc)
                        except Exception as e:
                            print(e)
                            print(second_class)
                            print(third_class)

        print("Total :%d, %d, %d" % (fc, sc, tc))


if __name__ == "__main__":

    sg = SouGSpider()
    # sg.load()

    sg.trans("/Users/furuiyang/data/csv", "/Users/furuiyang/data/csv2")
