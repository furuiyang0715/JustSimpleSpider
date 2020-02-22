import configparser
import os

env = os.environ

cf = configparser.ConfigParser()
thisdir = os.path.dirname(__file__)
cf.read(os.path.join(thisdir, '.conf'))

# mysql
MYSQL_HOST = env.get("MYSQL_HOST", cf.get('mysql', 'MYSQL_HOST'))
MYSQL_PORT = int(env.get("MYSQL_PORT", cf.get('mysql', 'MYSQL_PORT')))
MYSQL_USER = env.get("MYSQL_USER", cf.get('mysql', 'MYSQL_USER'))
MYSQL_PASSWORD = env.get("MYSQL_PASSWORD", cf.get('mysql', 'MYSQL_PASSWORD'))
MYSQL_DB = env.get("MYSQL_DB", cf.get('mysql', 'MYSQL_DB'))

# local mysql
LOCAL_MYSQL_HOST = env.get("LOCAL_MYSQL_HOST", cf.get('mysql', 'LOCAL_MYSQL_HOST'))
LOCAL_MYSQL_PORT = int(env.get("LOCAL_MYSQL_PORT", cf.get('mysql', 'LOCAL_MYSQL_PORT')))
LOCAL_MYSQL_USER = env.get("LOCAL_MYSQL_USER", cf.get('mysql', 'LOCAL_MYSQL_USER'))
LOCAL_MYSQL_PASSWORD = env.get("LOCAL_MYSQL_PASSWORD", cf.get('mysql', 'LOCAL_MYSQL_PASSWORD'))
LOCAL_MYSQL_DB = env.get("LOCAL_MYSQL_DB", cf.get('mysql', 'LOCAL_MYSQL_DB'))

# datacenter
DC_HOST = env.get("DC_HOST", cf.get('dc', 'DC_HOST'))
DC_PORT = int(env.get("DC_PORT", cf.get('dc', 'DC_PORT')))
DC_USER = env.get("DC_USER", cf.get('dc', 'DC_USER'))
DC_PASSWD = env.get("DC_PASSWD", cf.get('dc', 'DC_PASSWD'))
DC_DB = env.get("DC_DB", cf.get('dc', 'DC_DB'))

# deploy
LOCAL = bool(int(env.get("LOCAL", cf.get('deploy', 'LOCAL'))))
FIRST = bool(int(env.get("FIRST", cf.get('deploy', 'FIRST'))))


if __name__ == "__main__":
    import sys
    mod = sys.modules[__name__]
    attrs = dir(mod)
    attrs = [attr for attr in attrs if not attr.startswith("__") and attr.isupper()]
    for attr in attrs:
        print(attr, ":", getattr(mod, attr))
