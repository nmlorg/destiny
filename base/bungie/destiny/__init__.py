import json
import logging
import urlparse
from base import bungie


BASE = 'Destiny/'


def Fetch(suffix, *args, **kwargs):
  url = urlparse.urljoin(BASE, suffix)
  return bungie.Fetch(url, *args, **kwargs)


def EquipItems(accounttype, charid, itemids):
  return Fetch('EquipItems/', data=json.dumps({
      'membershipType': accounttype,
      'characterId': charid,
      'itemIds': itemids,
  }))


def GetAccount(accounttype, accountid):
  return Fetch('%s/Account/%i/', accounttype, accountid)


def GetAccountSummary(accounttype, accountid):
  return Fetch('%s/Account/%i/Summary/', accounttype, accountid)


def GetActivityHistory(accounttype, accountid, charid, mode, count=15, page=0):
  return Fetch('Stats/ActivityHistory/%s/%s/%s/?mode=%s&count=%i&page=%i', accounttype, accountid,
               charid, mode, count, page)


def GetAdvisorsForCurrentCharacter(accounttype, charid):
  return Fetch('%s/MyAccount/Character/%s/Advisors/', accounttype, charid)


def GetAllItemsSummary(accounttype, accountid):
  return Fetch('%s/Account/%i/Items/', accounttype, accountid)


def GetCharacter(accounttype, accountid, charid):
  return Fetch('%s/Account/%s/Character/%i/Complete/', accounttype, accountid, charid)


def GetCharacterActivities(accounttype, accountid, charid):
  return Fetch('%s/Account/%s/Character/%i/Activities/', accounttype, accountid, charid)


def GetCharacterInventory(accounttype, accountid, charid):
  return Fetch('%s/Account/%s/Character/%i/Inventory/', accounttype, accountid, charid)


def GetCharacterProgression(accounttype, accountid, charid):
  return Fetch('%s/Account/%i/Character/%i/Progression/', accounttype, accountid, charid)


def GetCharacterSummary(accounttype, accountid, charid):
  return Fetch('%s/Account/%s/Character/%i/', accounttype, accountid, charid)


def GetDestinyAggregateActivityStats(accounttype, accountid, charid):
  return Fetch('Stats/AggregateActivityStats/%s/%s/%s/', accounttype, accountid, charid)


def GetDestinyManifest():
  return Fetch('Manifest/')


def GetDestinySingleDefinition(deftype, defid):
  return Fetch('Manifest/%s/%s/', deftype, defid)


def GetGrimoireByMembership(accounttype, accountid):
  return Fetch('Vanguard/Grimoire/%s/%s/', accounttype, accountid)


def GetItemDetail(accounttype, accountid, charid, itemid):
  return Fetch('%s/Account/%s/Character/%s/Inventory/%s/', accounttype, accountid, charid, itemid)


def GetMyGrimoire(accounttype):
  return Fetch('Vanguard/Grimoire/%s/', accounttype)


def GetPostGameCarnageReport(activityid):
  return Fetch('Stats/PostGameCarnageReport/%s/', activityid)


def GetPublicAdvisors():
  return Fetch('Advisors/')


def GetPublicXurVendor():
  return Fetch('Advisors/Xur/')


def SearchDestinyPlayer(username, accounttype=None):
  if not accounttype:
    accounttype = 'all'

  return Fetch('SearchDestinyPlayer/%s/%s', accounttype, username)


def TransferItem(accounttype, charid, item_hash, item_id=0, quantity=1, to_vault=True):
  return Fetch('TransferItem/', data=json.dumps({
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


  class DestinyUser(ndb.Model):
    name = ndb.StringProperty()
    name_lower = ndb.ComputedProperty(lambda self: self.name.lower())
    accounttype = ndb.IntegerProperty()
    accountid = ndb.IntegerProperty()


  _SearchDestinyPlayer = SearchDestinyPlayer


  def SearchDestinyPlayer(username, accounttype=None):
    q = DestinyUser.query(DestinyUser.name_lower == username.lower())
    if accounttype:
      q = q.query(DestinyUser.accounttype == accounttype)
    ret = [{'displayName': user.name, 'membershipType': user.accounttype,
            'membershipId': str(user.accountid)} for user in q]
    if not ret:
      logging.warning('Looking up accounttype=%r username=%r.', accounttype, username)
      ret = _SearchDestinyPlayer(username, accounttype)
      for ent in ret:
        DestinyUser(name=ent['displayName'], accounttype=ent['membershipType'],
                    accountid=long(ent['membershipId'])).put()
    return ret
