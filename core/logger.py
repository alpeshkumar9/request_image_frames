import colorlog

from settings import settings

LOG_FORMAT = (
    "%(log_color)s%(levelname)-8s%(reset)s "
    "%(blue)s%(asctime)s%(reset)s "
    "%(name)-15s "
    "%(white)s%(message)s%(reset)s"
)

LOG_DEFAULT_HANDLERS = ['console',]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
    },
    'formatters': {
        'verbose': {
            '()': 'colorlog.ColoredFormatter',
            'format': LOG_FORMAT,
            'log_colors': {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if settings.debug_mode else settings.log_level,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': '',
        },
    },
    'loggers': {
        '': {
            'handlers': LOG_DEFAULT_HANDLERS,
            'level': 'DEBUG' if settings.debug_mode else settings.log_level,
        },
    },
    'root': {
        'level': 'DEBUG' if settings.debug_mode else settings.log_level,
        'formatter': 'verbose',
        'handlers': LOG_DEFAULT_HANDLERS
    }
}
