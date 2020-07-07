import time

import schedule

from Takungpao.takungpao_main import TakungpaoSchedule


class MainSwith(object):

    def start_task(self, cls, dt_str):
        def task():
            cls().start()

        task()
        schedule.every().day.at(dt_str).do(task)

    def run(self):
        self.start_task(TakungpaoSchedule, "00:00")

        while True:
            schedule.run_pending()
            time.sleep(10)


if __name__ == "__main__":
    ms = MainSwith()
    ms.run()
