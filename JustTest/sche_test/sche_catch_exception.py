import functools
import time
import traceback

import schedule


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                print(traceback.format_exc())
                # sentry.captureException(exc_info=True)
                if cancel_on_failure:
                    print("异常 任务结束: {}".format(schedule.CancelJob))
                    schedule.cancel_job(job_func)
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator


# def catch_exceptions(job_func, cancel_on_failure=False):
#     @functools.wraps(job_func)
#     def wrapper(*args, **kwargs):
#         try:
#             return job_func(*args, **kwargs)
#         except:
#             import traceback
#             print(traceback.format_exc())
#             if cancel_on_failure:
#                 return schedule.CancelJob
#     return wrapper


@catch_exceptions(cancel_on_failure=True)
def bad_task():
    return 1 / 0


def main():
    schedule.every(5).seconds.do(bad_task)
    while True:
        print("jobs: ", schedule.jobs)
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":

    main()
