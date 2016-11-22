#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 WooParadog <guohaochuan@gmail.com>
#
# Distributed under terms of the MIT license.

import os
import flask
import logging.conf
from mybot import r, ALL_KEYWORDS

app = flask.Flask(__name__)


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


@app.route('/')
def index():
    return '<body> %s </body>' % '<br/>'.join(r.smembers(ALL_KEYWORDS))


if __name__ == '__main__':
    import sys
    args = sys.argv
    app.run(host="0.0.0.0", port=args[1])
