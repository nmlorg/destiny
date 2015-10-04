import logging
import urlparse
from base import bungie


BASE = 'Destiny/'


def Fetch(suffix, *args, **kwargs):
  url = urlparse.urljoin(BASE, suffix)
  return bungie.Fetch(url, *args, **kwargs)


def GetAccountSummary(accounttype, accountid):
  return Fetch('%s/Account/%i/Summary/', accounttype, accountid)


def GetAllItemsSummary(accounttype, accountid):
  return Fetch('%s/Account/%i/Items/', accounttype, accountid)


def GetCharacterProgression(accounttype, accountid, charid):
  return Fetch('%s/Account/%i/%i/Progression/', accounttype, accountid, charid)


def GetDestinyManifest():
  return Fetch('Manifest/')


def GetPublicAdvisors():
  return Fetch('Advisors/')


def SearchDestinyPlayer(username, accounttype=None):
  if not accounttype:
    accounttype = 'all'

  return Fetch('SearchDestinyPlayer/%s/%s', accounttype, username)


try:
  from google.appengine.ext import ndb
except ImportError:
  pass
else:
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
