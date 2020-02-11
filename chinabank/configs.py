import configparser
import os

env = os.environ

cf = configparser.ConfigParser()
thisdir = os.path.dirname(__file__)
cf.read(os.path.join(thisdir, 'bank.conf'))

MYSQL_HOST = env.get("MYSQL_HOST", cf.get('mysql', 'MYSQL_HOST'))
MYSQL_PORT = int(env.get("MYSQL_PORT", cf.get('mysql', 'MYSQL_PORT')))
MYSQL_USER = env.get("MYSQL_USER", cf.get('mysql', 'MYSQL_USER'))
MYSQL_PASSWORD = env.get("MYSQL_PASSWORD", cf.get('mysql', 'MYSQL_PASSWORD'))
MYSQL_DB = env.get("MYSQL_DB", cf.get('mysql', 'MYSQL_DB'))
LOCAL = bool(int(env.get("LOCAL", cf.get('mysql', 'LOCAL'))))

# SELENIUM_HOST = env.get("SELENIUM_HOST", cf.get('selenium', 'SELENIUM_HOST'))

# MYSQL_TABLE = env.get("MYSQL_TABLE", cf.get('mysql', 'MYSQL_TABLE'))

# ALL_PAGES = int(env.get("ALL_PAGES", cf.get('others', 'ALL_PAGES')))

DB_FILE = os.path.join(os.path.dirname(__file__), 'chinabank.db')




# print("MYSQL_HOST: ", MYSQL_HOST)
# print("MYSQL_PORT: ", MYSQL_PORT)
# print("MYSQL_USER: ", MYSQL_USER)
# print("MYSQL_PASSWORD: ", MYSQL_PASSWORD)
# print("MYSQL_DB: ", MYSQL_DB)
# print("SELENIUM_HOST: ", SELENIUM_HOST)
# print("MYSQL_TABLE: ", MYSQL_TABLE)
# print("ALL_PAGES: ", ALL_PAGES)