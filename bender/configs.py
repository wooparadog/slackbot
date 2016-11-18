# -*- coding: utf-8 -*-

import os


REDIS_URL = os.environ.get("REDIS_URL", 'redis://127.0.0.1:6379')
