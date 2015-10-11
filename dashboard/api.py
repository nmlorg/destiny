# Copyright 2014 Daniel Reed <n@ml.org>

import jinja2
import json
import pprint
import webapp2
from base import bungie
from base.bungie import auth
from base.bungie.destiny import user as destiny_user
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
    if ae_user is None:
      self.response.content_type = 'text/html'
      self.response.write(JINJA2.get_template('dashboard/me_login.html').render({
          'breadcrumbs': (),
          'login_url': users.create_login_url(),
      }))
      return

    email = ae_user.email().lower()
    user = User.get_by_id(email) or User(id=email)
    user.Activate()

    user_info = bungie.GetCurrentUser()
    if user_info is None:
      self.response.content_type = 'text/html'
      self.response.write(JINJA2.get_template('dashboard/me_connect.html').render({
          'breadcrumbs': (
              (users.create_login_url(), email),
          ),
      }))
      return

    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('dashboard/me_index.html').render({
        'breadcrumbs': (
            (users.create_login_url(), email),
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


class UserHTMLPage(webapp2.RequestHandler):
  def get(self, username):
    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('dashboard/user.html').render({
        'breadcrumbs': (
            ('/' + username, username),
        ),
        'username': username,
    }))


class UserJSONPage(webapp2.RequestHandler):
  def get(self, username):
    user = destiny_user.User(username)
    self.response.headers['content-type'] = 'application/json'
    self.response.write(json.dumps(user, sort_keys=True))


class UserPyPage(webapp2.RequestHandler):
  def get(self, username):
    user = destiny_user.User(username)
    self.response.headers['content-type'] = 'text/plain'
    self.response.write(pprint.pformat(user))


class UserRawPage(webapp2.RequestHandler):
  def get(self, username):
    username, accounttype, accountid, summary = destiny_user.GetDestinyUser(username)
    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('dashboard/db_object.html').render({
        'breadcrumbs': (
            ('/%s.raw' % username, username),
        ),
        'obj': summary,
    }))


class Warmup(webapp2.RequestHandler):
  def get(self):
    pass


app = webapp2.WSGIApplication([
    ('/_ah/warmup', Warmup),
    ('/', MePage),
    ('/([a-zA-Z0-9-_ ]+)', UserHTMLPage),
    ('/([a-zA-Z0-9-_ ]+)[.]json', UserJSONPage),
    ('/([a-zA-Z0-9-_ ]+)[.]py', UserPyPage),
    ('/([a-zA-Z0-9-_ ]+)[.]raw', UserRawPage),
], debug=True)
