# -*- coding: utf-8 -*-

import re
import random
import redis

from slackbot.bot import respond_to, listen_to
from google import lucky

from configs import REDIS_URL

r = redis.Redis.from_url(REDIS_URL)

HI_MSGS = [
    "Bite my shiny metal ass",
    "Kill all humans",
]

KEYWORD_PREFIX = "slackbot:bot:keyworkd:%s"
ALL_KEYWORDS = "slackbot:bot:keywords"

LINK_STRIPPER = re.compile("<((http|https)://.*?)>")


@respond_to('^hi$', re.IGNORECASE)
def hi(message):
    message.reply(random.choice(HI_MSGS))
    message.react('+1')


@respond_to('^!([^\s]+)$')
@listen_to('^!([^\s]+)$')
def keyword_lookup(message, keyword):
    resp = r.get(KEYWORD_PREFIX % keyword)
    if not resp:
        return message.send("Such word, so 404")
    message.send(resp)


@respond_to('^!set ([^\s]+) (.+)$')
@listen_to('^!set ([^\s]+) (.+)$')
def set_keyword(message, keyword, value):
    value = LINK_STRIPPER.sub(" \g<1> ", value)
    r.set(KEYWORD_PREFIX % keyword, value)
    message.send("Got it")
    r.sadd(ALL_KEYWORDS, keyword)


@respond_to('^!unset ([^\s]+)$')
@listen_to('^!unset ([^\s]+)$')
def unset_keyword(message, keyword):
    r.delete(KEYWORD_PREFIX % keyword)
    message.send("Done")
    r.srem(ALL_KEYWORDS, keyword)


@listen_to("^!list keywords$")
@respond_to("^!list keywords$")
def all_keywords(message):
    message.send(','.join(r.smembers(ALL_KEYWORDS)))


@respond_to('I love you')
def love(message):
    message.reply('I love you too!')


@listen_to("^!google (.*)$")
@respond_to("^!google (.*)$")
def google(message, keyword):
    message.send("http://lmgtfy.com/?q={}".format("+".join(keyword.split())))


@listen_to("^!g (.*)$")
@respond_to("^!g (.*)$")
def google_lucky(message, keyword):
    r = lucky(keyword)
    if r:
        url, desc = r
        return message.send(u"{} - {}".format(url, desc))
    return message.send("Found nothing")


@respond_to('^!give ([^\s]+) ([^\s]+)$')
@listen_to('^!give ([^\s]+) ([^\s]+)$')
def keyword_lookup(message, person, keyword):
    resp = r.get(KEYWORD_PREFIX % keyword)
    if not resp:
        return message.send("Such word, so 404")
    message.send("%s %s" % (person, resp))
