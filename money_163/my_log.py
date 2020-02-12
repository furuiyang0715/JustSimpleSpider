import logging.config
import os


log_dir = os.path.dirname(__file__)


logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "simple": {
            "format": "[%(levelname)1.1s %(asctime)s|%(module)s|%(funcName)s|%(lineno)d] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": 'simple',
            "stream": "ext://sys.stdout"
        },
        "netease_log_file": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(log_dir, "netease.log"),
            "formatter": "simple",
            "when": "D",
            "backupCount": 2
        },
    },
    "loggers": {
        "netease_log": {
            "level": "DEBUG",
            "handlers": ["console", "netease_log_file"]
        },
    }
})


logger = logging.getLogger("netease_log")

# logger.info("hello world")
