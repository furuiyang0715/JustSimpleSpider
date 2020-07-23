import datetime

a = datetime.datetime.now()
print("**** ", a)


class SomeBody(object):

    def __init__(self):
        pass

    def say(self):
        print(a)
