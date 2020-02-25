# -*- coding: utf-8 -*-
import time

import pymysql
import requests
# from configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, LOCAL_MYSQL_HOST, \
#     LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, LOCAL_MYSQL_DB

from PublicOpinion.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, LOCAL_MYSQL_HOST, \
    LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, LOCAL_MYSQL_DB


try:
    # conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=MYSQL_DB)
    conn = pymysql.connect(host=LOCAL_MYSQL_HOST, port=LOCAL_MYSQL_PORT, user=LOCAL_MYSQL_USER, passwd=LOCAL_MYSQL_PASSWORD, db=LOCAL_MYSQL_DB)

except Exception as e:
    raise

cur = conn.cursor()
cur.execute("""select id, link  from  eastmoney_carticle where article is  NULL;""")
delete_info = {r[0]: r[1] for r in cur.fetchall()}
cur.close()
conn.close()


# {1717: 'http://caifuhao.eastmoney.com/news/20200203193311525228570',
# 1719: 'http://caifuhao.eastmoney.com/news/20200203190002919615800',
delete_ids = []
for id, url in delete_info.items():
    status_code = requests.get(url).status_code
    print(status_code)
    if status_code == 200:
        pass
    elif status_code == 404:
        delete_ids.append(id)
    time.sleep(3)


print(delete_ids)
