import time

from JustTest.import_test.d1 import SomeBody


sb = SomeBody()

sb.say()
time.sleep(3)
sb.say()
time.sleep(3)
sb.say()

print("- " * 10)

sb = SomeBody()
sb.say()
