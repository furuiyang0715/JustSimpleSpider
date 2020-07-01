import traceback

import requests

from retrying import retry

headers = {}


@retry(stop_max_attempt_number=3)
def _parse_url(url):
    print(">>> ")
    response = requests.get(url, headers=headers, timeout=3)
    assert response.status_code == 200
    return response


def parse_url(url):
    try:
        response = _parse_url(url)
    except Exception:
        print(traceback.format_exc())
        response = None
    return response


print(parse_url("http://www.google.com"))
