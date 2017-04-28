#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from dal import r

ONCALL_SET = "slackbot:oncall:all-teams"
ONCALL_LIST_PREFIX = "slackbot:oncall:team:%s"


def get_current_week_number():
    return datetime.date.today().isocalendar()[1]


class OnCallService(object):
    def add_oncall(self, team, contact):
        r.sadd(ONCALL_SET, team)
        r.zadd(ONCALL_LIST_PREFIX % team, 0.0, contact)
        return True

    def get_oncall(self, team):
        current_week = get_current_week_number()
        on_call_key = ONCALL_LIST_PREFIX % team
        current = r.zrangebyscore(on_call_key,
                                  current_week,
                                  "({}".format(current_week + 1))
        if not current:
            lowest_member = r.zrange(on_call_key, 0, 1)
            if not lowest_member:
                return
            lowest_member = lowest_member[0]
            r.zincrby(on_call_key, lowest_member,
                      current_week - r.zscore(on_call_key, lowest_member))
            current = r.zrangebyscore(on_call_key,
                                      current_week,
                                      "({}".format(current_week + 1))
        return current and current[0]

    def get_all_oncalls(self, team):
        on_call_key = ONCALL_LIST_PREFIX % team
        all_members = r.zrange(on_call_key, 0, -1)
        return all_members

    def get_other_oncalls(self, team):
        return self.get_all_oncalls(team)[:-1]

    def clear_oncall_team(self, team):
        r.delete(ONCALL_LIST_PREFIX % team)
        r.srem(ONCALL_SET, team)

    def get_everyone(self):
        for team in r.smembers(ONCALL_SET):
            yield team, self.get_oncall(team)



on_call_service = OnCallService()
