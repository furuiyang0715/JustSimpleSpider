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

