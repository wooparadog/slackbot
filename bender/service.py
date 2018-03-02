#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from dal import r

ONCALL_SET = "slackbot:oncall:all-teams"
ONCALL_MEMBERS_PREFIX = "slackbot:oncall:team-members:%s"
# deprecated
ONCALL_LIST_PREFIX = "slackbot:oncall:team:%s"


def get_current_week_number():
    return datetime.date.today().isocalendar()[1]


class OnCallService(object):
    def add_oncall(self, team, contact):
        if contact in r.get_all_oncalls(team):
            return True
 
        r.sadd(ONCALL_SET, team)
        r.lpush(ONCALL_MEMBERS_PREFIX % team, contact)
        return True

    def _migrate_if_necessary(self, team):
        old_members_key = ONCALL_LIST_PREFIX % team
        if not r.exists(old_members_key):
            return
        all_members = r.zrange(old_members_key, 0, -1)
        [add_oncall(team, m) for m in all_members]
        r.delete(old_members_key)

    def get_oncall(self, team):
        self._migrate_if_necessary(team)
        current_week = get_current_week_number()
        members_key = ONCALL_MEMBERS_PREFIX % team
        member_count = r.llen(members_key)
        if member_count < 1:
            return None
        return r.lindex(members_key, current_week % member_count)

    def get_all_oncalls(self, team):
        self._migrate_if_necessary(team)
        return list(reversed(r.lrange(ONCALL_MEMBERS_PREFIX % team, 0, -1)))

    def get_other_oncalls(self, team):
        current = self.get_oncall(team)
        all = set(self.get_all_oncalls(team))
        all.remove(current)
        return list(all)

    def clear_oncall_team(self, team):
        self._migrate_if_necessary(team)
        r.delete(ONCALL_MEMBERS_PREFIX % team)
        r.srem(ONCALL_SET, team)

    def get_everyone(self):
        for team in r.smembers(ONCALL_SET):
            self._migrate_if_necessary(team)
            yield team, self.get_oncall(team)

    def skip_oncall(self, team):
        self._migrate_if_necessary(team)
        members_key = ONCALL_MEMBERS_PREFIX % team
        r.rpoplpush(members_key, members_key)


on_call_service = OnCallService()
