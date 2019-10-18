import logging
from logging.config import dictConfig
import sys

import six


APP_NAME = 'sigprocessutils'
COLOR_LOGS = sys.stdout.isatty()


class CWColorFormatter(logging.Formatter):
    """Special Formatter adding color to logs.
    """
    LEVEL_COLORS = {
        logging.NOTSET: '\033[01;0m',     # Reset color
        logging.DEBUG: '\033[00;32m',     # GREEN
        logging.INFO: '\033[00;36m',      # CYAN
        # Where did this one go?:
        # logging.AUDIT: '\033[01;36m',     # BOLD CYAN
        logging.WARN: '\033[01;33m',      # BOLD YELLOW
        logging.ERROR: '\033[01;31m',     # BOLD RED
        logging.CRITICAL: '\033[01;31m',  # BOLD RED
    }

    reset_color = '\033[01;0m'

    def format(self, record):
        if COLOR_LOGS:
            record.reset_color = self.reset_color
            record.color = self.LEVEL_COLORS[record.levelno]
        else:
            # We do not want colors in non ttys.
            record.reset_color = ''
            record.color = ''
        return super(CWColorFormatter, self).format(record)


FORMATS = {
    logging.DEBUG: '%(color)s%(levelname)s: %(pathname)s %(funcName)s %(lineno)d:%(reset_color)s %(message)s',  # noqa
    logging.INFO: '%(color)s%(levelname)s:%(reset_color)s %(message)s'
}


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            '()': CWColorFormatter,
            'format': FORMATS[logging.DEBUG]
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
        'sigprocessutils': {
            'handlers': ['default'],
            # This can be overriden in the config's logging section
            'level': 'INFO',
            'propagate': False
        },
    }
}


def set_log_level(level, logger=None):
    if not logger:
        logger = logging.getLogger(APP_NAME)
    logger.setLevel(level)


def get_log_level(level):
    if isinstance(level, six.string_types):
        level = level.strip().upper()
        level = logging.getLevelName(level)
    if not isinstance(level, int):
        level = logging.INFO
    return level


def configure_logging(level=None, fmt_str=None):
    log_level = get_log_level(level)
    if log_level in FORMATS and not fmt_str:
        LOGGING_CONFIG['formatters']['standard']['format'] = FORMATS[log_level]
    if isinstance(fmt_str, six.string_types):
        LOGGING_CONFIG['formatters']['standard']['format'] = fmt_str
    dictConfig(LOGGING_CONFIG)
    set_log_level(log_level)
