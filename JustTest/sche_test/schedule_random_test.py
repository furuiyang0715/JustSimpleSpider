import time
import schedule

_t = None


def my_job():
    global _t
    _now = time.time()
    if _t:
        print("interval: ", _now - _t)
    else:
        print("first: ")
    _t = _now


def main():

    schedule.every(5).to(10).seconds.do(my_job)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
