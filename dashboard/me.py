# Copyright 2015 Daniel Reed <n@ml.org>

import jinja2
import pprint
import webapp2
from base import bungie
from base.bungie import auth
from base.util import fetch
from google.appengine.api import users
from google.appengine.ext import ndb


JINJA2 = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))


class User(ndb.Model):
  username = ndb.StringProperty()
  bungled = ndb.TextProperty()
  bungleatk = ndb.TextProperty()

  def Activate(self):
    fetch.SetOpener(auth.BuildOpener(self.bungled, self.bungleatk))


class MePage(webapp2.RequestHandler):
  def get(self):
    ae_user = users.get_current_user()
    email = ae_user.email().lower()
    user = User.get_by_id(email)
    if user is None:
      user = User(id=email)
      user.put()

    user.Activate()
    user_info = bungie.GetCurrentUser()

    if user_info is None:
      self.response.content_type = 'text/html'
      self.response.write(JINJA2.get_template('dashboard/me_login.html').render({
          'breadcrumbs': (
              ('/me/', email),
          ),
      }))
    else:
      self.response.content_type = 'text/html'
      self.response.write(JINJA2.get_template('dashboard/me_index.html').render({
          'breadcrumbs': (
              ('/me/', email),
          ),
          'user_info': user_info,
      }))

  def post(self):
    ae_user = users.get_current_user()
    email = ae_user.email().lower()
    user = User.get_by_id(email)
    if user is None:
      user = User(id=email)

    try:
      bungled, bungleatk = auth.Auth(self.request.get('email'), self.request.get('password'))
    except:
      pass
    else:
      user.bungled = bungled
      user.bungleatk = bungleatk
      user.put()

    return self.redirect('/me/')


app = webapp2.WSGIApplication([
    ('/me/?', MePage),
], debug=True)
