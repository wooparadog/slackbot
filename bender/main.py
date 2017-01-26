# -*- coding: utf-8 -*-

import os
import logging.config


def config_logging():
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,

        'formatters': {
            'console': {
                'format': '[%(asctime)s][%(levelname)s] %(name)s '
                          '%(filename)s:%(funcName)s:%(lineno)d | %(message)s',
                'datefmt': '%H:%M:%S',
                },
            },

        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'console'
                },
            'sentry': {
                'level': 'ERROR',
                'class': 'raven.handlers.logging.SentryHandler',
                'dsn': os.environ.get("SENTRY_DSN", ''),
                },
            },

        'loggers': {
            '': {
                'handlers': ['console', 'sentry'],
                'level': 'DEBUG',
                'propagate': False,
                },
            'bender': {
                'level': 'DEBUG',
                'propagate': True,
            },
        }
    }
    logging.config.dictConfig(LOGGING)


def main():
    from slackbot.bot import Bot
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    config_logging()
    main()
