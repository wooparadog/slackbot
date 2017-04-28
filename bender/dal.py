# -*- coding: utf-8 -*-

import redis
from configs import REDIS_URL

r = redis.StrictRedis.from_url(REDIS_URL)
