# Copyright 2014 Daniel Reed <n@ml.org>

import json
import pprint
from base import bungie
from base.bungie import auth
from base.bungie.destiny import user as destiny_user
from dashboard import base_app


class MePage(base_app.RequestHandler):
  def get(self):
    if self.request.user is None:
      return self.response.render('dashboard/me_login.html')

    self.request.user.Activate()

    user_info = bungie.GetCurrentUser()
    if user_info is None:
      return self.response.render('dashboard/me_connect.html')

    username, accounttype, accountid, summary = destiny_user.GetDestinyUser(
        user_info['user']['displayName'])

    stores = [ent['characterBase']['characterId'] for ent in summary['characters']]
    stores.append(None)
    buckets = {}
    for item in summary['inventory']['items']:
      item_info = destiny_user.manifest.GetDef('InventoryItem', item['itemHash'])
      if item_info is None:
        continue
      bucket_name = destiny_user.GetBucketName(item_info['bucketTypeHash'])
      bucket = buckets.get(bucket_name)
      if bucket is None:
        bucket = buckets[bucket_name] = {}
      item_name = item_info['itemName']
      item_data = bucket.get(item_name)
      if item_data is None:
        item_data = bucket[item_name] = {
            'equippable': item_info['equippable'],
            'ids': {ent['characterBase']['characterId']: None for ent in summary['characters']},
            'stores': {place: {'count': 0, 'id': None} for place in stores},
            'total': 0,
            'transferrable': not item_info['nonTransferrable'],
        }
      characterid = summary['characters'][item['characterIndex']]['characterBase']['characterId']
      store = item_data['stores'][stores[item['characterIndex']]]
      store['count'] += item['quantity']
      store['id'] = item['itemId']
      item_data['total'] += item['quantity']

    self.response.render('dashboard/me_index.html', {
        'accountid': accountid,
        'accounttype': accounttype,
        'buckets': buckets,
        'username': username,
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
    ('/([a-zA-Z0-9-_ ]+)', UserHTMLPage),
    ('/([a-zA-Z0-9-_ ]+)[.]json', UserJSONPage),
    ('/([a-zA-Z0-9-_ ]+)[.]py', UserPyPage),
    ('/([a-zA-Z0-9-_ ]+)[.]raw', UserRawPage),
], debug=True)
