# Copyright 2014 Daniel Reed <n@ml.org>

import json
import webapp2
from google.appengine.ext import ndb
import destiny


class DestinyUser(ndb.Model):
  account = ndb.StringProperty()
  name = ndb.StringProperty()
  accounttype = ndb.IntegerProperty()
  accountid = ndb.IntegerProperty()


class GetUser(webapp2.RequestHandler):
  def get(self, username):
    destiny_user = DestinyUser.query(DestinyUser.account == username.lower()).get()

    if destiny_user:
      user = destiny.User(destiny_user.name, accounttype=destiny_user.accounttype,
                          accountid=destiny_user.accountid)
    else:
      user = destiny.User(username)
      DestinyUser(account=username.lower(), name=user['name'], accounttype=user['account_type'], 
                  accountid=user['account_id']).put()

    self.response.content_type = 'application/json'
    json.dump(user, self.response)


app = webapp2.WSGIApplication([
    ('/data/getuser/(.*)', GetUser),
], debug=True)
