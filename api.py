# Copyright 2014 Daniel Reed <n@ml.org>

import jinja2
import json
import pprint
import webapp2
from base import bungie
from base.bungie import destiny
from base.bungie.destiny import manifest
from base.bungie.destiny import user as destiny_user


JINJA2 = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))


class DBPage(webapp2.RequestHandler):
  def get(self):
    defs = manifest.GetDef()
    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('db_index.html').render({
        'breadcrumbs': (
            ('/db/', 'DB'),
        ),
        'defs': defs,
    }))


class DBBucketPage(webapp2.RequestHandler):
  def get(self, bucket_name):
    bucket = manifest.GetDef(bucket_name)
    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('db_bucket.html').render({
        'breadcrumbs': (
            ('/db/', 'DB'),
            ('/db/%s/' % bucket_name, bucket_name),
        ),
        'bucket_name': bucket_name,
        'bucket': bucket,
    }))


class DBObjectPage(webapp2.RequestHandler):
  def get(self, bucket_name, hashcode):
    hashcode = long(hashcode)
    obj = manifest.GetDef(bucket_name, hashcode)
    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('db_object.html').render({
        'breadcrumbs': (
            ('/db/', 'DB'),
            ('/db/%s/' % bucket_name, bucket_name),
            ('/db/%s/%i' % (bucket_name, hashcode), hashcode),
        ),
        'obj': obj,
    }))


class ObjectSearchPage(webapp2.RequestHandler):
  def get(self, hashcode):
    self.response.content_type = 'text/html'
    #self.response.write(JINJA2.get_template('object_search.html').render(
    #    {'object': definitions.Definitions()[long(hashcode)]}))


class UserHTMLPage(webapp2.RequestHandler):
  def get(self, username):
    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('user.html').render({
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


class UserObjectPage(webapp2.RequestHandler):
  def get(self, accounttype, accountid):
    accounttype = int(accounttype)
    accountid = long(accountid)
    all_items = destiny.GetAllItemsSummary(accounttype, accountid)['data']
    summary = destiny.GetAccountSummary(accounttype, accountid)['data']
    summary['inventory']['items'] = all_items['items']
    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('db_object.html').render({
        'breadcrumbs': (
            ('/%s/%s' % (accounttype, accountid), accountid),
        ),
        'obj': summary,
    }))


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
    ('/', DBPage),
    ('/db/?', DBPage),
    ('/db/([a-zA-Z]+)/?', DBBucketPage),
    ('/db/([a-zA-Z]+)/([0-9]+)/?', DBObjectPage),
    ('/([0-9]+)', ObjectSearchPage),
    ('/([0-9]+)/([0-9]+)', UserObjectPage),
    ('/([a-zA-Z0-9]+)', UserHTMLPage),
    ('/([a-zA-Z0-9]+)[.]json', UserJSONPage),
    ('/([a-zA-Z0-9]+)[.]py', UserPyPage),
], debug=True)
