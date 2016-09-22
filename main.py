#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 WooParadog <guohaochuan@gmail.com>
#
# Distributed under terms of the MIT license.


import re
import random
import json as simplejson
import urllib
import requests

import redis

from slackbot.bot import respond_to, listen_to

r = redis.Redis(host="10.0.38.51", port=8889)

HI_MSGS = [
    "Bite my shiny metal ass",
    "Kill all humans",
]

KEYWORD_PREFIX = "slackbot:eleme:keyworkd:%s"


@respond_to('^hi$', re.IGNORECASE)
def hi(message):
    message.reply(random.choice(HI_MSGS))
    message.react('+1')


@respond_to('^!(\w+)$')
@listen_to('^!(\w+)$')
def keyword_lookup(message, keyword):
    resp = r.get(KEYWORD_PREFIX % keyword)
    if not resp:
        return message.send("Such word, so 404")
    message.send(resp)


@respond_to('^!set (\w+) (.+)$')
@listen_to('^!set (\w+) (.+)$')
def set_keyword(message, keyword, value):
    r.set(KEYWORD_PREFIX % keyword, value)
    message.send("Got it")


@respond_to('I love you')
def love(message):
    message.reply('I love you too!')


@listen_to("^!google (.*)$")
@respond_to("^!google (.*)$")
def google(message, keyword):
    message.send("http://lmgtfy.com/?q={}".format("+".join(keyword.split())))


@listen_to("^!g (.*)$")
@respond_to("^!g (.*)$")
def google(message, keyword):
    data = self.search(text, msg.args[0], dict(optlist))
    bold = self.registryValue('bold', msg.args[0])
    max = self.registryValue('maximumResults', msg.args[0])
    # We don't use supybot.reply.oneToOne here, because you generally
    # do not want @google to echo ~20 lines of results, even if you
    # have reply.oneToOne enabled.
    onetoone = self.registryValue('oneToOne', msg.args[0])
    for result in self.formatData(data,
                              bold=bold, max=max, onetoone=onetoone):
        irc.reply(result)
