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
        "gov_stats_log_file": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(log_dir, "gov_stats.log"),
            "formatter": "simple",
            "when": "D",
            "backupCount": 5
        },
    },
    "loggers": {
        "gov_stats_log": {
            "level": "DEBUG",
            "handlers": ["console", "gov_stats_log_file"]
        },
    }
})


logger = logging.getLogger("gov_stats_log")

# logger.info("hello world")
