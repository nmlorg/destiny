# Copyright 2014 Daniel Reed <n@ml.org>

import jinja2
import json
import pprint
import webapp2
from base import bungie
from base.bungie.destiny import user as destiny_user


JINJA2 = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))


class IndexPage(webapp2.RequestHandler):
  def get(self):
    self.response.content_type = 'text/plain'
    self.response.write('GetAvailableLocales:\n\n%s\n\n\n' %
                        pprint.pformat(bungie.GetAvailableLocales()))
    self.response.write('HelloWorld:\n\n%s\n\n\n' % pprint.pformat(bungie.HelloWorld()))
    self.response.write('Settings:\n\n%s\n\n\n' % pprint.pformat(bungie.Settings()))


class UserHTMLPage(webapp2.RequestHandler):
  def get(self, username):
    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('user.html').render({'username': username}))


class UserJSONPage(webapp2.RequestHandler):
  def get(self, username):
    user = destiny_user.User(username)
    self.response.headers['content-type'] = 'application/json'
    self.response.write(json.dumps(user, indent=4, sort_keys=True))


class UserPyPage(webapp2.RequestHandler):
  def get(self, username):
    user = destiny_user.User(username)
    self.response.headers['content-type'] = 'text/plain'
    self.response.write(pprint.pformat(user))


class Warmup(webapp2.RequestHandler):
  def get(self):
    pass


app = webapp2.WSGIApplication([
    ('/_ah/warmup', Warmup),
    ('/', IndexPage),
    ('/([a-zA-Z0-9]+)', UserHTMLPage),
    ('/([a-zA-Z0-9]+)[.]json', UserJSONPage),
    ('/([a-zA-Z0-9]+)[.]py', UserPyPage),
], debug=True)
