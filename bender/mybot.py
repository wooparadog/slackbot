# -*- coding: utf-8 -*-

import re
import random

from slackbot.bot import respond_to, listen_to
from slackbot.manager import PluginsManager

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
VOTE_PREFIX = "slackbot:bot:vote:%s"
VOTE_WORDS = "slackbot:bot:vote:words"


@listen_to('^!vote ([^\s]+)$')
def vote(message, keyword):
    """Vote a keyword"""
    r.sadd(VOTE_WORDS, keyword)
    count = r.incr(VOTE_PREFIX.format(keyword))
    message.send('{} is voted to {}'.format(keyword, count))


@listen_to('^!get-vote$')
def show_all_vote(message):
    """Show all voted keywords"""
    keywords = r.smembers(VOTE_WORDS)
    counts = r.mget(VOTE_PREFIX.format(keyword) for keyword in keywords)
    counts = sorted(zip(keywords, map(lambda x: x or 0, counts)))
    message.send(
        '\n'.join('{} is voted to {}'.format(k, c) for k, c in counts)
        )


@respond_to('^hi$', re.IGNORECASE)
def hi(message):
    """say hi."""
    message.reply(random.choice(HI_MSGS))
    message.react('doge')


@respond_to('^!([^\s]+)$')
@listen_to('^!([^\s]+)$')
def keyword_lookup(message, keyword):
    """return content identified by keyword."""
    if keyword == 'help':
        return
    resp = r.get(KEYWORD_PREFIX % keyword)
    if not resp:
        return message.send("Such word, so 404")
    message.send(resp)


@respond_to('^!set +([^\s]+) +(.+)$')
@listen_to('^!set +([^\s]+) +(.+)$')
def set_keyword(message, keyword, value):
    """set keyword content."""
    value = LINK_STRIPPER.sub(" \g<1> ", value)
    r.set(KEYWORD_PREFIX % keyword, value)
    message.send("Got it")
    r.sadd(ALL_KEYWORDS, keyword)


@respond_to('^!unset +([^\s]+)$')
@listen_to('^!unset +([^\s]+)$')
def unset_keyword(message, keyword):
    """unset keyword."""
    r.delete(KEYWORD_PREFIX % keyword)
    message.send("Done")
    r.srem(ALL_KEYWORDS, keyword)


@listen_to("^!list +keywords$")
@respond_to("^!list +keywords$")
def all_keywords(message):
    """list all keywords."""
    message.send(','.join(r.smembers(ALL_KEYWORDS)))


@listen_to("^!list +keywords +([^\s]+)$")
@respond_to("^!list +keywords +([^\s]+)$")
def all_keywords_with_prefix(message, prefix):
    """list all keywords starts with <prefix>."""
    keys = [k for k in r.smembers(ALL_KEYWORDS) if k.startswith(prefix)]
    message.send('\n'.join(keys))


@respond_to('I love you')
def love(message):
    """love you too."""
    message.reply('I love you too!')


@listen_to("^!google +(.*)$")
@respond_to("^!google +(.*)$")
def google(message, keyword):
    """give lmgtfy link to google keyword."""
    message.send("http://lmgtfy.com/?q={}".format("+".join(keyword.split())))


@listen_to("^!g (.*)$")
@respond_to("^!g (.*)$")
def google_lucky(message, keyword):
    """Google I'm feeling lucky."""
    r = lucky(keyword)
    if r:
        url, desc = r
        return message.send(u"{} - {}".format(url, desc))
    return message.send("Found nothing")


@respond_to('^!give ([^\s]+) +([^\s]+)$')
@listen_to('^!give ([^\s]+) +([^\s]+)$')
def give_person_keyword(message, person, keyword):
    """give @people content of <keyword>."""
    resp = r.get(KEYWORD_PREFIX % keyword)
    if not resp:
        return message.send("Such word, so 404")
    message.send("%s %s" % (person, resp))


@listen_to("^!help$")
@respond_to("^!help$")
def help_message(message):
    """Print help message"""
    handlers = sorted(PluginsManager.commands['listen_to'].items(),
                      key=lambda (k, v): k.pattern)
    message.send(
        "Help:\n\n```" + "\n".join(
            "%s: %s" % (cmd.pattern, handler.__doc__)
            for cmd, handler in handlers
        ) + "```")


@listen_to("^!roll ([^\s]+)$")
@respond_to("^!roll ([^\s]+)$")
def roll_keyword(message, keyword):
    """pick an option from <keyword>, seperated by space."""
    resp = r.get(KEYWORD_PREFIX % keyword)
    if not resp:
        return message.send("Such word, so 404")
    message.send(random.choice(resp.split()))


@listen_to("^!a (.+)$")
@respond_to("^!a (.+)$")
def display_all_keywords(message, keywords):
    """search keyword and show them all at once."""
    all_keywords = r.smembers(ALL_KEYWORDS)
    result = []
    for word in all_keywords:
        if all(keyword in word for keyword in keywords.split()):
            result.append(word)
    if result:
        texts = zip(result, r.mget(KEYWORD_PREFIX % w for w in result))
        message.send(
            "".join("---- %s ----\n\n%s\n\n\n" % seg for seg in texts)
            )
    else:
        message.send("Not found")


@listen_to("^!s ([^\s]+)$")
@respond_to("^!s ([^\s]+)$")
def search_keyword(message, keyword):
    """search keyword."""
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
    """add contact to team's on call list."""
    if isinstance(oncall, unicode):
        oncall = oncall.encode('utf8')
    if on_call_service.add_oncall(team, oncall):
        message.send("{} is added to oncall list of {}".format(oncall, team))
    else:
        message.send("{} is added to oncall list of {}".format(oncall, team))


@listen_to("^!oncall-get ([^\s]+)$")
@respond_to("^!oncall-get ([^\s]+)$")
def get_oncall(message, team):
    """get current week's oncall contact."""
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
    """clear oncall team entirely."""
    on_call_service.clear_oncall_team(team)
    return message.send("Cleared: {}".format(team))


@respond_to("^!oncall$")
@listen_to("^!oncall$")
def get_all_oncalls(message):
    """get EVERYONE!!!!!!!!!!!!."""
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
    """skip current oncall, let the next one on.."""
    current_oncall = on_call_service.get_oncall(team)
    on_call_service.skip_oncall(team)
    return message.send("Skipping current oncall: {}, new one is: *{}*".format(
            current_oncall,
            on_call_service.get_oncall(team)
            )
        )
