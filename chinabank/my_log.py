import logging.config
import os


log_dir = os.path.dirname(__file__)


logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": True,
    # 规定日志的输出格式
    "formatters": {
        "simple": {
            "format": "[%(levelname)1.1s %(asctime)s|%(module)s|%(funcName)s|%(lineno)d] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        # 位于标准输出的日志
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": 'simple',
            "stream": "ext://sys.stdout"
        },
        # 位于文件的日志
        "chinabank_file_log": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(log_dir, "chinabank.log"),
            "formatter": "simple",
            "when": "D",
            "backupCount": 5
        },
        # "calendar_file_log": {
        #     "level": "DEBUG",
        #     "class": "logging.handlers.TimedRotatingFileHandler",
        #     "filename": os.path.join(log_dir, "calendar.log"),
        #     "formatter": "simple",
        #     "when": "D",
        #     "backupCount": 5   # 日志保存的页数
        # },
    },
    "loggers": {
        "chinabank_log": {
            "level": "DEBUG",
            "handlers": ["console", "chinabank_file_log"]
        },
        # "calendar_log": {
        #     "level": "DEBUG",
        #     "handlers": ["console", "calendar_file_log"]
        # },
    }
})


# print(log_dir)
logger = logging.getLogger("chinabank_log")

logger.info("hello world")