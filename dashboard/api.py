# Copyright 2014 Daniel Reed <n@ml.org>

import json
import pprint
from base import bungie
from base.bungie import auth
from base.bungie import destiny
from base.bungie.destiny import manifest
from base.bungie.destiny import user as destiny_user
from dashboard import base_app


class BlankPage(base_app.RequestHandler):
  def get(self):
    manifest.DestinyDefinition.Blank()


class MePage(base_app.RequestHandler):
  def get(self):
    if self.request.user is None:
      return self.response.render('dashboard/me_login.html')

    user_info = bungie.GetCurrentUser()
    if user_info is None:
      return self.response.render('dashboard/me_connect.html')

    self.response.render('dashboard/me_index.html', {
        'username': user_info['user']['displayName'],
    })

  def post(self):
    try:
      bungled, bungleatk = auth.Auth(self.request.get('email'), self.request.get('password'))
    except:
      pass
    else:
      self.request.user.bungled = bungled
      self.request.user.bungleatk = bungleatk
      self.request.user.put()

    return self.redirect('/')


class TransferPage(base_app.RequestHandler):
  def post(self):
    item_hash = self.request.get('hash')
    item_id = self.request.get('id')
    quantity = long(self.request.get('quantity'))
    accounttype = int(self.request.get('accounttype'))
    from_char = self.request.get('from')
    to_char = self.request.get('to')
    if from_char:
      destiny.TransferItem(accounttype, from_char, item_hash, item_id, quantity, True)
      print 'Transferred from %r to Vault.' % from_char
    if to_char:
      destiny.TransferItem(accounttype, to_char, item_hash, item_id, quantity, False)
      print 'Transferred from Vault to %r.' % to_char
    self.response.write('1')


class UserHTMLPage(base_app.RequestHandler):
  def get(self, username):
    self.response.render('dashboard/user.html', {
        'breadcrumbs': (
            ('/' + username, username),
        ),
        'username': username,
    })


class UserJSONPage(base_app.RequestHandler):
  def get(self, username):
    user = destiny_user.User(username)
    self.response.content_type = 'application/json'
    self.response.write(json.dumps(user, sort_keys=True))


class UserPyPage(base_app.RequestHandler):
  def get(self, username):
    user = destiny_user.User(username)
    self.response.content_type = 'text/plain'
    self.response.write(pprint.pformat(user))


class UserRawPage(base_app.RequestHandler):
  def get(self, username):
    username, accounttype, accountid, summary = destiny_user.GetDestinyUser(username)
    self.response.content_type = 'text/html'
    self.response.render('dashboard/db_object.html', {
        'breadcrumbs': (
            ('/%s.raw' % username, username),
        ),
        'obj': summary,
    })


class Warmup(base_app.RequestHandler):
  def get(self):
    pass


app = base_app.WSGIApplication([
    ('/_ah/warmup', Warmup),
    ('/', MePage),
    ('/admin/blank', BlankPage),
    ('/api/transfer', TransferPage),
    ('/([a-zA-Z0-9-_ ]+)', UserHTMLPage),
    ('/([a-zA-Z0-9-_ ]+)[.]json', UserJSONPage),
    ('/([a-zA-Z0-9-_ ]+)[.]py', UserPyPage),
    ('/([a-zA-Z0-9-_ ]+)[.]raw', UserRawPage),
], debug=True)
