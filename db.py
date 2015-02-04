# Copyright 2014 Daniel Reed <n@ml.org>

import datetime
import logging
from google.appengine.ext import ndb
from base.bungie import platform
from base.bungie.destiny import definitions
import destiny


class DestinyPGCR(ndb.Model):
  report = ndb.JsonProperty()
  players = ndb.StringProperty(repeated=True)
  start = ndb.IntegerProperty()
  activity = ndb.IntegerProperty()


def ISO8601(s):
  return long(datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').strftime('%s'))


class CachingBungie(platform.Bungie):
  def DestinyStatsPostGameCarnageReport(self, activityid):
    pgcr = DestinyPGCR.get_by_id(activityid)
    if pgcr:
      return pgcr.report

    report = super(CachingBungie, self).DestinyStatsPostGameCarnageReport(activityid=activityid)
    players = sorted(set(player['player']['destinyUserInfo']['displayName']
                         for player in report['data']['entries']),
                     key=lambda ent: ent.lower())
    start = ISO8601(report['data']['period'])
    activity = report['data']['activityDetails']['referenceId']
    logging.info('Caching activity %r.', activityid)
    DestinyPGCR(key=ndb.Key(DestinyPGCR, activityid), report=report, players=players, start=start,
                activity=activity).put()
    return report


BUNGIE = CachingBungie()
DEFS = definitions.Definitions(bungie=BUNGIE)


class DestinyUser(ndb.Model):
  name = ndb.StringProperty()
  accounttype = ndb.IntegerProperty()
  accountid = ndb.IntegerProperty()

  @classmethod
  def GetUser(cls, username):
    destiny_user = cls.get_by_id(username.lower())

    if destiny_user:
      user = destiny.User(destiny_user.name, accounttype=destiny_user.accounttype,
                          accountid=destiny_user.accountid, bungie=BUNGIE, defs=DEFS)
    else:
      user = destiny.User(username, bungie=BUNGIE, defs=DEFS)
      cls(key=ndb.Key(cls, username.lower()), name=user['name'], accounttype=user['account_type'],
          accountid=user['account_id']).put()

    return user
