# coding=utf-8
import sys
import requests

from urllib.request import urlretrieve
from bs4 import BeautifulSoup


def callbackfunc(blocknum, blocksize, totalsize):
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


def main():
    base_url = "http://pinyin.sogou.com"
    homepage_url = "http://pinyin.sogou.com/dict/"
    html = requests.get(homepage_url).text
    soup = BeautifulSoup(html, "html.parser")
    soup = soup.find(id="dict_category_show").find_all('div', class_='dict_category_list')
    fc = 0
    sc = 0
    tc = 0
    for ii in soup:
        fc += 1
        print("Level 1 :" + ii.find(class_='dict_category_list_title').find('a').contents[0])
        for k in ii.find(class_='catewords').find_all('a'):
            secondclass = k.contents[0]
            second_url = base_url + "%s" % (k['href'])
            print(" " * 4 + "Level 2 :" + secondclass)
            sc += 1
            soup2 = BeautifulSoup(requests.get(second_url).text, "html.parser")
            totalpagenum = soup2.find(id='dict_page_list').find('ul').find_all('span')[-2].a.contents[0]
            # print(totalpagenum)   # 该分类下词库的总页数

            for pageind in range(1, int(totalpagenum) + 1):
                soup2 = BeautifulSoup(requests.get("%s/default/%d" % (second_url.replace("?rf=dictindex", ""), pageind)).text, "html.parser")
                for kk in soup2.find_all('div', class_='dict_detail_block'):
                    thirdclass = kk.find(class_='detail_title').find('a').contents[0]
                    third_url = kk.find(class_='dict_dl_btn').a['href']
                    print(" " * 8 + "Level 3 :" + thirdclass + " " * 10 + "Downloading.....")
                    tc += 1
                    urlretrieve(third_url, "csv/%s-%s.scel" % (secondclass, thirdclass), callbackfunc)

    print("Total :%d, %d, %d" % (fc, sc, tc))


def demo():
    url = 'http://download.pinyin.sogou.com/dict/download_cell.php?id=20647&name=%E4%B8%AD%E5%9B%BD%E9%AB%98%E7%AD%89%E9%99%A2%E6%A0%A1%EF%BC%88%E5%A4%A7%E5%AD%A6%EF%BC%89%E5%A4%A7%E5%85%A8%E3%80%90%E5%AE%98%E6%96%B9%E6%8E%A8%E8%8D%90%E3%80%91'
    ret = urlretrieve(url, "demo.scel", callbackfunc)
    print(ret)


# demo()


main()