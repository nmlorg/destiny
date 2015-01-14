# Copyright 2014 Daniel Reed <n@ml.org>

import json
import webapp2
from google.appengine.ext import ndb
import destiny


class DestinyUser(ndb.Model):
  name = ndb.StringProperty()
  accounttype = ndb.IntegerProperty()
  accountid = ndb.IntegerProperty()


class GetUser(webapp2.RequestHandler):
  def get(self, username):
    destiny_user = DestinyUser.query(DestinyUser.name == username.lower()).get()

    if destiny_user:
      user = destiny.User(username, accounttype=destiny_user.accounttype,
                          accountid=destiny_user.accountid)
    else:
      user = destiny.User(username)
      DestinyUser(name=username.lower(), accounttype=user['account_type'], 
                  accountid=user['account_id']).put()

    self.response.content_type = 'application/json'
    json.dump(user, self.response)


app = webapp2.WSGIApplication([
    ('/data/getuser/(.*)', GetUser),
], debug=True)
