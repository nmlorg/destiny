# Copyright 2014 Daniel Reed <n@ml.org>

import json
import pprint
from base.bungie import auth
from base.bungie import bungienet
from base.bungie import destiny_user
from dashboard import base_app


NETWORK_ICONS = {
    1: 'https://www.bungie.net/img/theme/destiny/icons/icon_xbl.png',
    2: 'https://www.bungie.net/img/theme/destiny/icons/icon_psn.png',
}


class AccountInfo(base_app.RequestHandler):
  def get(self, username, account_type, account_id):
    account_type = long(account_type)
    account_id = long(account_id)
    summary = bungienet.GetAccountSummary(account_type, account_id)['data']

    self.response.render('dashboard/user/account_info.html', {
        'account': {
            'icon': NETWORK_ICONS.get(account_type),
            'id': account_id,
            'type': account_type,
            'name': username,
        },
        'breadcrumbs': (
            ('/new/%s/' % username, username),
            ('/new/%s/%i/%i/' % (username, account_type, account_id),
             '%i/%i' % (account_type, account_id)),
        ),
        'summary': summary,
    })


class AccountList(base_app.RequestHandler):
  def get(self, username):
    accounts = [{
        'icon': NETWORK_ICONS.get(ent['membershipType']),
        'id': long(ent['membershipId']),
        'type': ent['membershipType'],
        'name': ent['displayName'],
    } for ent in bungienet.SearchDestinyPlayer(username)]

    if len(accounts) == 1:
      account = accounts[0]
      return self.redirect('/new/%s/%i/%i/' % (account['name'], account['type'], account['id']))

    if accounts:
      username = accounts[0]['name']

    self.response.render('dashboard/user/account_list.html', {
        'accounts': accounts,
        'breadcrumbs': (
            ('/new/%s/' % username, username),
        ),
        'username': username,
    })


class IndexPage(base_app.RequestHandler):
  def get(self):
    self.response.render('dashboard/user/index.html')

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


class ItemPage(base_app.RequestHandler):
  def get(self, itemid):
    item = bungienet.DestinyItem.get_by_id(itemid)
    self.response.render('dashboard/object.html', {
        'obj': item and item.to_dict(),
    })


class UserHTMLPage(base_app.RequestHandler):
  def get(self, username):
    self.response.render('dashboard/user/character_sheet.html', {
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
    self.response.render('dashboard/object.html', {
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
    ('/', IndexPage),
    ('/items/([0-9]+)/?', ItemPage),
    ('/new/([a-zA-Z0-9-_ ]+)/?', AccountList),
    ('/new/([a-zA-Z0-9-_ ]+)/([0-9]+)/([0-9]+)/?', AccountInfo),
    ('/([a-zA-Z0-9-_ ]+)', UserHTMLPage),
    ('/([a-zA-Z0-9-_ ]+)[.]json', UserJSONPage),
    ('/([a-zA-Z0-9-_ ]+)[.]py', UserPyPage),
    ('/([a-zA-Z0-9-_ ]+)[.]raw', UserRawPage),
], debug=True)
