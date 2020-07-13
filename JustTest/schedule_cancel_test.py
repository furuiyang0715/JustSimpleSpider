import pprint
import time

import schedule


def greet(name):
    print('Hello {}'.format(name))


def main():
    job1 = schedule.every().day.do(greet, 'Andrea')
    job1.tag('daily-tasks', 'friend')
    job2 = schedule.every().hour.do(greet, 'John')
    job2.tag('hourly-tasks', 'friend')
    job3 = schedule.every().hour.do(greet, 'Monica')
    job3.tag('hourly-tasks', 'customer')
    job4 = schedule.every().day.do(greet, 'Derek')
    job4.tag('daily-tasks', 'guest')

    for job in (job1, job2, job3, job4):
        print(job.tags)

    # schedule.every().day.do(greet, 'Andrea').tag('daily-tasks', 'friend')
    # schedule.every().hour.do(greet, 'John').tag('hourly-tasks', 'friend')
    # schedule.every().hour.do(greet, 'Monica').tag('hourly-tasks', 'customer')
    # schedule.every().day.do(greet, 'Derek').tag('daily-tasks', 'guest')

    # schedule.clear('daily-tasks')
    schedule.clear('friend')

    while True:
        schedule.run_pending()
        print(pprint.pformat(schedule.jobs))
        time.sleep(10)


if __name__ == "__main__":
    main()
