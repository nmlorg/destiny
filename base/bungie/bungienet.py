#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import json
import logging
import urllib
from base.bungie import fetch


def EquipItems(accounttype, charid, itemids):
  return fetch.Fetch('Destiny/EquipItems/', data=json.dumps({
      'membershipType': accounttype,
      'characterId': charid,
      'itemIds': itemids,
  }))


def GetAccount(accounttype, accountid):
  return fetch.Fetch('Destiny/%s/Account/%i/', accounttype, accountid)


def GetAccountSummary(accounttype, accountid):
  return fetch.Fetch('Destiny/%s/Account/%i/Summary/', accounttype, accountid)


def GetActivityHistory(accounttype, accountid, charid, mode, count=15, page=0):
  return fetch.Fetch('Destiny/Stats/ActivityHistory/%s/%s/%s/?mode=%s&count=%i&page=%i',
                     accounttype, accountid, charid, mode, count, page)


def GetAdminsOfGroup(groupid):
  return fetch.Fetch('Group/%s/Admins/', groupid)


def GetAdvisorsForCurrentCharacter(accounttype, charid):
  return fetch.Fetch('Destiny/%s/MyAccount/Character/%s/Advisors/', accounttype, charid)


def GetAllItemsSummary(accounttype, accountid):
  return fetch.Fetch('Destiny/%s/Account/%i/Items/', accounttype, accountid)


def GetAvailableLocales():
  return fetch.Fetch('GetAvailableLocales/')


def GetBungieAccount(profileid):
  return fetch.Fetch('User/GetBungieAccount/%s/0/', profileid)


def GetCharacter(accounttype, accountid, charid):
  return fetch.Fetch('Destiny/%s/Account/%s/Character/%i/Complete/', accounttype, accountid, charid)


def GetCharacterActivities(accounttype, accountid, charid):
  return fetch.Fetch('Destiny/%s/Account/%s/Character/%i/Activities/', accounttype, accountid,
                     charid)


def GetCharacterInventory(accounttype, accountid, charid):
  return fetch.Fetch('Destiny/%s/Account/%s/Character/%i/Inventory/', accounttype, accountid,
                     charid)


def GetCharacterProgression(accounttype, accountid, charid):
  return fetch.Fetch('Destiny/%s/Account/%i/Character/%i/Progression/', accounttype, accountid,
                     charid)


def GetCharacterSummary(accounttype, accountid, charid):
  return fetch.Fetch('Destiny/%s/Account/%s/Character/%i/', accounttype, accountid, charid)


def GetCurrentUser():
  return fetch.Fetch('User/GetBungieNetUser/')


def GetDestinyAggregateActivityStats(accounttype, accountid, charid):
  return fetch.Fetch('Destiny/Stats/AggregateActivityStats/%s/%s/%s/', accounttype, accountid,
                     charid)


def GetDestinyManifest():
  return fetch.Fetch('Destiny/Manifest/')


def GetDestinySingleDefinition(deftype, defid):
  return fetch.Fetch('Destiny/Manifest/%s/%s/', deftype, defid)


def GetGlobalAlerts():
  return fetch.Fetch('GlobalAlerts/')


def GetGrimoireByMembership(accounttype, accountid):
  return fetch.Fetch('Destiny/Vanguard/Grimoire/%s/%s/', accounttype, accountid)


def GetItemDetail(accounttype, accountid, charid, itemid):
  return fetch.Fetch('Destiny/%s/Account/%s/Character/%s/Inventory/%s/', accounttype, accountid,
                     charid, itemid)


def GetMyGrimoire(accounttype):
  return fetch.Fetch('Destiny/Vanguard/Grimoire/%s/', accounttype)


def GetPostGameCarnageReport(activityid):
  return fetch.Fetch('Destiny/Stats/PostGameCarnageReport/%s/', activityid)


def GetPublicAdvisors():
  return fetch.Fetch('Destiny/Advisors/')


def GetPublicXurVendor():
  return fetch.Fetch('Destiny/Advisors/Xur/')


def GetSpecialEventAdvisors():
  return fetch.Fetch('Destiny/Events/')


def HelloWorld():
  return fetch.Fetch('HelloWorld/')


def SearchDestinyPlayer(username, accounttype=None):
  if not accounttype:
    accounttype = 'all'

  return fetch.Fetch('Destiny/SearchDestinyPlayer/%s/%s', accounttype, username)


def SearchUsers(username):
  return fetch.Fetch('User/SearchUsers/?' + urllib.urlencode({'q': username}))


def Settings():
  return fetch.Fetch('Settings/')


def TransferItem(accounttype, charid, item_hash, item_id=0, quantity=1, to_vault=True):
  return fetch.Fetch('Destiny/TransferItem/', data=json.dumps({
      'membershipType': accounttype,
      'itemReferenceHash': item_hash,
      'itemId': item_id,
      'stackSize': quantity,
      'characterId': charid,
      'transferToVault': to_vault,
  }))


try:
  from google.appengine.ext import ndb
except ImportError:
  pass
else:
  class DestinyItem(ndb.Model):
    accounttype = ndb.IntegerProperty()
    accountid = ndb.IntegerProperty()
    data = ndb.JsonProperty()


  _GetItemDetail = GetItemDetail


  def GetItemDetail(accounttype, accountid, charid, itemid):
    accountid = long(accountid)
    charid = long(charid)
    itemid = str(long(itemid))
    ent = DestinyItem.get_by_id(itemid)
    if ent is not None and ent.data:
      assert ent.accounttype == accounttype
      assert ent.accountid == accountid
      return ent.data
    ret = _GetItemDetail(accounttype, accountid, charid, itemid)
    DestinyItem(id=itemid, accounttype=accounttype, accountid=accountid, data=ret).put()
    return ret


  class DestinyPGCR(ndb.Model):
    report = ndb.JsonProperty()
    players = ndb.StringProperty(repeated=True)


  _GetPostGameCarnageReport = GetPostGameCarnageReport


  def GetPostGameCarnageReport(activityid):
    ent = DestinyPGCR.get_by_id(activityid)
    if ent:
      return ent.report
    ret = _GetPostGameCarnageReport(activityid)
    players = sorted(set(player['player']['destinyUserInfo']['displayName']
                         for player in ret['data']['entries']),
                     key=lambda ent: ent.lower())
    DestinyPGCR(id=activityid, report=ret, players=players).put()
    return ret


  class DestinyUser(ndb.Model):
    name = ndb.StringProperty()
    name_lower = ndb.ComputedProperty(lambda self: self.name.lower())
    accounttype = ndb.IntegerProperty()
    accountid = ndb.IntegerProperty()


  _SearchDestinyPlayer = SearchDestinyPlayer


  def SearchDestinyPlayer(username, accounttype=None):
    q = DestinyUser.query(DestinyUser.name_lower == username.lower())
    if accounttype:
      q = q.filter(DestinyUser.accounttype == accounttype)
    ret = [{'displayName': user.name, 'membershipType': user.accounttype,
            'membershipId': str(user.accountid)} for user in q]
    if not ret:
      logging.warning('Looking up accounttype=%r username=%r.', accounttype, username)
      ret = _SearchDestinyPlayer(username, accounttype)
      for ent in ret:
        DestinyUser(name=ent['displayName'], accounttype=ent['membershipType'],
                    accountid=long(ent['membershipId'])).put()
    return ret


if __name__ == '__main__':
  assert HelloWorld() == 'Hello World'
  assert GetAvailableLocales()['English'] == 'en'
