# Copyright 2014 Daniel Reed <n@ml.org>

import json
import webapp2

import db


class GetUser(webapp2.RequestHandler):
  def get(self, username):
    user = db.DestinyUser.GetUser(username)
    self.response.content_type = 'application/json'
    json.dump(user, self.response)


app = webapp2.WSGIApplication([
    ('/data/getuser/(.*)', GetUser),
], debug=True)
