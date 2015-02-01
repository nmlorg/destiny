# Copyright 2014 Daniel Reed <n@ml.org>

from google.appengine.ext import ndb
import destiny


class DestinyUser(ndb.Model):
  account = ndb.StringProperty()
  name = ndb.StringProperty()
  accounttype = ndb.IntegerProperty()
  accountid = ndb.IntegerProperty()

  @classmethod
  def GetUser(cls, username, bungie=None, defs=None):
    destiny_user = cls.query(cls.account == username.lower()).get()

    if destiny_user:
      user = destiny.User(destiny_user.name, accounttype=destiny_user.accounttype,
                          accountid=destiny_user.accountid, bungie=bungie, defs=defs)
    else:
      user = destiny.User(username, bungie=bungie, defs=defs)
      cls(account=username.lower(), name=user['name'], accounttype=user['account_type'], 
          accountid=user['account_id']).put()

    return user
