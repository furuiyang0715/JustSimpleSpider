import requests


def _check_selenium_status():
    """
    检查 selenium 服务端的状态
    :return:
    """
    while True:
        i = 0
        try:
            # 检查本地的 selenium 服务是否已经启动
            resp = requests.get("http://127.0.0.1:4444/wd/hub/status", timeout=0.5)
        except:
            i += 1
            if i > 10:
                raise
        else:
            print(resp.text)
            break


_check_selenium_status()