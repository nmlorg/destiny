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


def Manifest():
  return Fetch('Manifest/')


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
    user = q.get()
    if user:
      return [{'displayName': user.name, 'membershipType': user.accounttype,
               'membershipId': str(user.accountid)}]
    ret = _SearchDestinyPlayer(username, accounttype)
    if ret:
      DestinyUser(name=ret[0]['displayName'], accounttype=ret[0]['membershipType'],
                  accountid=long(ret[0]['membershipId'])).put()
    return ret
