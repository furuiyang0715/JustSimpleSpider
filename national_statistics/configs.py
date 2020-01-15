import configparser
import os

env = os.environ

cf = configparser.ConfigParser()
thisdir = os.path.dirname(__file__)
cf.read(os.path.join(thisdir, 'gov_stats.conf'))

MYSQL_HOST = env.get("MYSQL_HOST", cf.get('mysql', 'MYSQL_HOST'))
MYSQL_PORT = int(env.get("MYSQL_PORT", cf.get('mysql', 'MYSQL_PORT')))
MYSQL_USER = env.get("MYSQL_USER", cf.get('mysql', 'MYSQL_USER'))
MYSQL_PASSWORD = env.get("MYSQL_PASSWORD", cf.get('mysql', 'MYSQL_PASSWORD'))
MYSQL_DB = env.get("MYSQL_DB", cf.get('mysql', 'MYSQL_DB'))
MYSQL_TABLE = env.get("MYSQL_TABLE", cf.get('mysql', 'MYSQL_TABLE'))

# 关于 redis 的配置
# # 但是如果是使用 compose 的话 就不需要使用这里的配置
REDIS_HOST = env.get("REDIS_HOST", cf.get('redis', 'REDIS_HOST'))
REDIS_PORT = int(env.get("REDIS_PORT", cf.get('redis', 'REDIS_PORT')))
REDIS_DATABASE_NAME = int(env.get("REDIS_DATABASE_NAME", cf.get('redis', 'REDIS_DATABASE_NAME')))

# print("MYSQL_HOST: ", MYSQL_HOST)
# print("MYSQL_PORT: ", MYSQL_PORT, type(MYSQL_PORT))
# print("MYSQL_USER: ", MYSQL_USER)
# print("MYSQL_PASSWORD: ", MYSQL_PASSWORD)
# print("MYSQL_DB: ", MYSQL_DB)
# print("MYSQL_TABLE: ", MYSQL_TABLE)

# print("REDIS_HOST: ", REDIS_HOST)
# print("REDIS_PORT: ", REDIS_PORT, type(REDIS_PORT))
# print("REDIS_DATABASE_NAME: ", REDIS_DATABASE_NAME, type(REDIS_DATABASE_NAME))
