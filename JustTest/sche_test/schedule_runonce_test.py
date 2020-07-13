import time

import schedule


def job_that_executes_once():
    # Do some work ...
    print("我是只运行一次的任务.. ")
    return schedule.CancelJob


def main():
    schedule.every().day.at('13:35').do(job_that_executes_once)
    while True:
        print(schedule.jobs)
        schedule.run_pending()
        time.sleep(10)


if __name__ == "__main__":
    main()
