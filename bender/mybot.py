# -*- coding: utf-8 -*-

import re
import random

from slackbot.bot import respond_to, listen_to
from google import lucky
from bender.service import on_call_service
from dal import r


HI_MSGS = [
    "hello to you",
    "cheers",
    "howdy",
    "greatings",
]

KEYWORD_PREFIX = "slackbot:bot:keyworkd:%s"
ALL_KEYWORDS = "slackbot:bot:keywords"
LINK_STRIPPER = re.compile("<((http|https)://.*?)>")


@respond_to('^hi$', re.IGNORECASE)
def hi(message):
    message.reply(random.choice(HI_MSGS))
    message.react('doge')


@respond_to('^!([^\s]+)$')
@listen_to('^!([^\s]+)$')
def keyword_lookup(message, keyword):
    if keyword == 'help':
        return
    resp = r.get(KEYWORD_PREFIX % keyword)
    if not resp:
        return message.send("Such word, so 404")
    message.send(resp)


@respond_to('^!set +([^\s]+) +(.+)$')
@listen_to('^!set +([^\s]+) +(.+)$')
def set_keyword(message, keyword, value):
    value = LINK_STRIPPER.sub(" \g<1> ", value)
    r.set(KEYWORD_PREFIX % keyword, value)
    message.send("Got it")
    r.sadd(ALL_KEYWORDS, keyword)


@respond_to('^!unset +([^\s]+)$')
@listen_to('^!unset +([^\s]+)$')
def unset_keyword(message, keyword):
    r.delete(KEYWORD_PREFIX % keyword)
    message.send("Done")
    r.srem(ALL_KEYWORDS, keyword)


@listen_to("^!list +keywords$")
@respond_to("^!list +keywords$")
def all_keywords(message):
    message.send(','.join(r.smembers(ALL_KEYWORDS)))


@listen_to("^!list +keywords +([^\s]+)$")
@respond_to("^!list +keywords +([^\s]+)$")
def all_keywords_with_prefix(message, prefix):
    keys = [k for k in r.smembers(ALL_KEYWORDS) if k.startswith(prefix)]
    message.send('\n'.join(keys))


@respond_to('I love you')
def love(message):
    message.reply('I love you too!')


@listen_to("^!google +(.*)$")
@respond_to("^!google +(.*)$")
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


@respond_to('^!give ([^\s]+) +([^\s]+)$')
@listen_to('^!give ([^\s]+) +([^\s]+)$')
def give_person_keyword(message, person, keyword):
    resp = r.get(KEYWORD_PREFIX % keyword)
    if not resp:
        return message.send("Such word, so 404")
    message.send("%s %s" % (person, resp))


@listen_to("^!help$")
@respond_to("^!help$")
def help_message(message):
    message.send("""Hello there:

```
- hi: say hi
- !<keyword>: return content identified by keyword
- !set <keyword> <content>: set keyword content
- !unset <keyword>: unset keyword
- !list keywords: list all keywords
- !list keywords <prefix>: list all keywords starts with <prefix>
- !love: love you too
- !google <keyword>: give lmgtfy link to google keyword
- !g <keyword>: Google I'm feeling lucky
- !give @people <keyword>: give @people content of <keyword>
- !help: this msg
- !roll <keyword>: pick an option from <keyword>, seperated by space
- !s <keyword>: search keyword
- !oncall-add <team> <contact info>: add contact to team's on call list
- !oncall-get <team>: get current week's oncall contact
- !oncall-clear <team>: clear oncall team entirely
- !oncall: get EVERYONE!!!!!!!!!!!!
- !oncall-skip <team>: skip current oncall, let the next one on.
```""")


@listen_to("^!roll ([^\s]+)$")
@respond_to("^!roll ([^\s]+)$")
def roll_keyword(message, keyword):
    resp = r.get(KEYWORD_PREFIX % keyword)
    if not resp:
        return message.send("Such word, so 404")
    message.send(random.choice(resp.split()))


@listen_to("^!s ([^\s]+)$")
@respond_to("^!s ([^\s]+)$")
def search_keyword(message, keyword):
    all_keywords = r.smembers(ALL_KEYWORDS)
    result = []
    for word in all_keywords:
        if keyword in word:
            result.append(word)
    if result:
        message.send(",".join(result))
    else:
        message.send("Not found")


@listen_to("^!oncall-add ([^\s]+) +(.+)$")
@respond_to("^!oncall-add ([^\s]+) +(.+)$")
def add_oncall(message, team, oncall):
    if isinstance(oncall, unicode):
        oncall = oncall.encode('utf8')
    if on_call_service.add_oncall(team, oncall):
        message.send("{} is added to oncall list of {}".format(oncall, team))
    else:
        message.send("{} is added to oncall list of {}".format(oncall, team))


@listen_to("^!oncall-get ([^\s]+)$")
@respond_to("^!oncall-get ([^\s]+)$")
def get_oncall(message, team):
    on_call = on_call_service.get_oncall(team)
    if on_call:
        all_members = on_call_service.get_other_oncalls(team)
        return message.send(
            "On call for {} is:\n *{}*\nOther oncalls:\n{}".format(
                team,
                on_call,
                '\n'.join(map(lambda x: '*%s*' % x, all_members))
                ))
    else:
        return message.send("No available On Call for {}".format(team))


@listen_to("^!oncall-clear ([^\s]+)$")
@respond_to("^!oncall-clear ([^\s]+)$")
def clear_oncall_team(message, team):
    on_call_service.clear_oncall_team(team)
    return message.send("Cleared: {}".format(team))


@respond_to("^!oncall$")
@listen_to("^!oncall$")
def get_all_oncalls(message):
    return message.send(
        '本周 Oncall: \n' +
        '\n'.join(
            '{}: *{}*'.format(team, oncall)
            for team, oncall in on_call_service.get_everyone()
            )
        )


@listen_to("^!oncall-skip ([^\s]+)$")
@respond_to("^!oncall-skip ([^\s]+)$")
def skip_oncall(message, team):
    current_oncall = on_call_service.get_oncall(team)
    on_call_service.skip_oncall(team)
    return message.send("Skipping current oncall: {}, new one is: *{}*".format(
            current_oncall,
            on_call_service.get_oncall(team)
            )
        )
