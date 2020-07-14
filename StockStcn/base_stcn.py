import requests
from gne import GeneralNewsExtractor
from retrying import retry

from base import SpiderBase


class STCNBase(SpiderBase):
    def __init__(self):
        super(STCNBase, self).__init__()
        self.table_name = "stcn_info"
        self.extractor = GeneralNewsExtractor()

    @retry(stop_max_attempt_number=5)
    def _get(self, url):
        resp = requests.get(url, headers=self.headers)
        return resp

    def get(self, url):
        resp = None
        try:
            resp = self._get(url)
        except:
            return None
        else:
            if resp and resp.status_code == 200:
                return resp.text
            else:
                return None
