import configparser
import os

env = os.environ

cf = configparser.ConfigParser()
thisdir = os.path.dirname(__file__)
cf.read(os.path.join(thisdir, 'tgb.conf'))

DC_HOST = env.get("DC_HOST", cf.get('mysql', 'DC_HOST'))
DC_PORT = 3306
DC_USER = 'dcr'
DC_PASSWD = env.get("DC_HOST", cf.get('mysql', 'DC_PASSWD'))
DC_DB = 'datacenter'

MYSQL_HOST = env.get("MYSQL_HOST", cf.get('mysql', 'MYSQL_HOST'))
MYSQL_PORT = int(env.get("MYSQL_PORT", cf.get('mysql', 'MYSQL_PORT')))
MYSQL_USER = env.get("MYSQL_USER", cf.get('mysql', 'MYSQL_USER'))
MYSQL_PASSWORD = env.get("MYSQL_PASSWORD", cf.get('mysql', 'MYSQL_PASSWORD'))
MYSQL_DB = env.get("MYSQL_DB", cf.get('mysql', 'MYSQL_DB'))
MYSQL_TABLE = env.get("MYSQL_TABLE", cf.get('mysql', 'MYSQL_TABLE'))
