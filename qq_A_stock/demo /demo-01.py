import pprint
import time

import requests
from gne import GeneralNewsExtractor
from selenium.webdriver import Chrome

# url = 'https://xw.qq.com/cmsid/20200208A0ATTO00'
# url = 'https://new.qq.com/mn/20200207/20200207A0MLE400.html'
# url = 'https://new.qq.com/ch2/Agu'
url = 'https://new.qq.com/omn/FIN20200/20200210A03PUA00.html'

driver = Chrome()
driver.get(url)
# page = requests.get(url).text
time.sleep(3)
extractor = GeneralNewsExtractor()
result = extractor.extract(driver.page_source)
# result = extractor.extract(page)
print(pprint.pformat(result))