import configparser
import os

env = os.environ

cf = configparser.ConfigParser()
thisdir = os.path.dirname(__file__)
cf.read(os.path.join(thisdir, '.conf'))

# deploy
LOCAL = bool(int(env.get("LOCAL", cf.get('deploy', 'LOCAL'))))
PROXY_URL = env.get("PROXY_URL", cf.get("deploy", "PROXY_URL"))
LOCAL_PROXY_URL = env.get("LOCAL_PROXY_URL", cf.get("deploy", "LOCAL_PROXY_URL"))


if __name__ == "__main__":
    import sys
    mod = sys.modules[__name__]
    attrs = dir(mod)
    attrs = [attr for attr in attrs if not attr.startswith("__") and attr.isupper()]
    for attr in attrs:
        print(attr, ":", getattr(mod, attr))
